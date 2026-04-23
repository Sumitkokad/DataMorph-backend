
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .file.upload import handle_uploaded_file
from .file.download import download_file

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .logic.preprocessing_routes import run_preprocessing_pipeline
from .logic.llm_logic import LLMAgent
from django.core.files.storage import default_storage
import pandas as pd
import traceback
import json
import numpy as np

# ===============================
# 🔹 File Upload + AI Analysis + Auto Download API
# ===============================
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def upload_with_ai_view(request):
    """
    Upload file + analyze dataset + auto execute column operations + auto download
    """
    if request.method == "POST" and request.FILES.get("file"):
        try:
            uploaded_file = request.FILES["file"]
            print(f"📥 Received file: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            # Validate file type
            if not uploaded_file.name.lower().endswith('.csv'):
                return JsonResponse({
                    "error": "Only CSV files are supported",
                    "received_file": uploaded_file.name
                }, status=400)
            
            # Save file
            saved_path = handle_uploaded_file(uploaded_file)
            print(f"💾 File saved at: {saved_path}")

            # Read CSV for analysis using Django storage
            try:
                with default_storage.open(saved_path, 'rb') as f:
                    df = pd.read_csv(f)
                print(f"📊 CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")
                
                # Context loading
                context = request.POST.get("context")
                context_data = {}
                if context:
                    request.session["context"] = context
                    try:
                        context_data = json.loads(context)
                    except:
                        pass
                
                request.session["file_path"] = saved_path
                
                # Generate Profile Data
                profile_data = []
                for col in df.columns:
                    missing = int(df[col].isnull().sum())
                    unique = int(df[col].nunique())
                    dtype = str(df[col].dtype)
                    profile_data.append({
                        "name": col,
                        "type": dtype,
                        "missing": missing,
                        "unique": unique
                    })
                
                automation = context_data.get('automation', 'auto')
                llm = LLMAgent()
                
                if automation == 'manual':
                    print("⚙️ Manual mode selected. Skipping AI analysis.")
                    ai_result = {"status": "skipped", "operations": [], "column_operations": {}}
                else:
                    # Perform AI analysis - ONLY ONCE
                    ai_result = llm.analyze_dataset(df, "column_wise", context=context_data)
                    print(f"🤖 AI analysis completed. Status: {ai_result.get('status')}")
                
                # Get operations from AI result
                operations = ai_result.get("operations", [])
                column_operations = ai_result.get("column_operations", {})
                
                print(f"🔧 Operations suggested by AI: {operations}")
                
                response_data = {
                    "message": "File uploaded and analyzed successfully!",
                    "file_info": {
                        "filename": uploaded_file.name,
                        "file_path": saved_path, # Return file_path for frontend fallback
                        "rows": df.shape[0],
                        "columns": df.shape[1],
                        "columns_list": df.columns.tolist()
                    },
                    "profile": profile_data,
                    "ai_analysis": {
                        "status": ai_result.get("status", "unknown"),
                        "suggestions": operations,
                        "column_operations": column_operations,
                        "reasoning": ai_result.get("reasoning", ""),
                        "connection_verified": ai_result.get("connection_verified", False),
                        "analysis_type": ai_result.get("analysis_type", "column_wise"),
                        "generation_time": ai_result.get("generation_time", 0),
                        "is_fallback": ai_result.get("is_fallback", False)
                    }
                }
                
                return JsonResponse(response_data)

            except pd.errors.EmptyDataError:
                return JsonResponse({"error": "The CSV file is empty"}, status=400)
            except pd.errors.ParserError:
                return JsonResponse({"error": "Invalid CSV format"}, status=400)
            except Exception as e:
                print(f"❌ CSV processing error: {str(e)}")
                print(traceback.format_exc())
                return JsonResponse({"error": f"Error processing CSV: {str(e)}"}, status=500)

        except Exception as e:
            print(f"❌ Upload error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                "error": f"Upload failed: {str(e)}"
            }, status=500)

    return JsonResponse({
        "error": "No file uploaded",
        "hint": "Send a POST request with a CSV file"
    }, status=400)

# ===============================
# 🔹 Apply Selected Operations API
# ===============================
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def apply_selected_operations_view(request):
    """
    Apply operations selected by the user on the uploaded file
    """
    try:
        # Support fallback from decoupled SPA architectures using payload data
        body = request.data if hasattr(request, 'data') else {}
        file_path = request.session.get("file_path") or body.get("file_path")

        if not file_path:
            return JsonResponse({
                "error": "No file found. Make sure you uploaded a file, or provide 'file_path' in the request."
            }, status=400)

        operations = body.get("operations", [])
        column_operations = body.get("column_operations", {})

        print(f"🔧 Applying selected operations: {operations}")

        processed_df, logs, download_info = run_preprocessing_pipeline(
            file_path,
            operations=operations,
            column_operations=column_operations,
            original_filename="processed.csv"
        )

        response_data = {
            "status": "success",
            "message": "Operations applied successfully",
            "logs": logs,
            "processed_info": {
                "rows": processed_df.shape[0] if not processed_df.empty else 0,
                "columns": processed_df.shape[1] if not processed_df.empty else 0,
                "columns_list": processed_df.columns.tolist() if not processed_df.empty else []
            }
        }
        
        if download_info:
            response_data["download"] = download_info

        return JsonResponse(response_data)

    except Exception as e:
        print(f"❌ Apply operations error: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)

# ===============================
# 🔹 File Download API
# ===============================
def download_view(request, filename):
    """
    Download processed file.
    """
    try:
        return download_file(filename)
    except Exception as e:
        return JsonResponse({"error": f"Download failed: {str(e)}"}, status=404)

# ===============================
# 🔹 Preprocessing API
# ===============================
@csrf_exempt
def preprocess_view(request):
    """
    Handles CSV file upload and runs preprocessing operations.
    """
    if request.method == "POST":
        file = request.FILES.get("file")
        operations = request.POST.getlist("operations")

        if not file:
            return JsonResponse({"error": "No file uploaded."}, status=400)

        if not operations:
            return JsonResponse({"error": "No operations specified."}, status=400)

        try:
            print(f"🔧 Starting preprocessing: {operations}")
            
            # Run preprocessing with auto-download
            processed_df, logs, download_info = run_preprocessing_pipeline(
                file, 
                operations, 
                file.name
            )
            
            preview = processed_df.head(5).to_dict(orient="records") if not processed_df.empty else []
            
            response_data = {
                "status": "success",
                "message": "Preprocessing completed successfully.",
                "processed_info": {
                    "rows": processed_df.shape[0] if not processed_df.empty else 0,
                    "columns": processed_df.shape[1] if not processed_df.empty else 0,
                    "columns_list": processed_df.columns.tolist() if not processed_df.empty else []
                },
                "logs": logs,
                "preview": preview
            }
            
            # Add download info
            if download_info:
                response_data["download"] = {
                    "filename": download_info.get("filename", "processed_file.csv"),
                    "download_url": download_info.get("download_url", ""),
                    "message": "Processed file ready for download"
                }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            print(f"❌ Preprocessing error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                "error": f"Preprocessing failed: {str(e)}"
            }, status=500)

    return JsonResponse({"error": "Only POST method allowed."}, status=405)

# ===============================
# 🔹 Health Check API
# ===============================
@csrf_exempt
def health_check_view(request):
    """
    Health check endpoint for the application.
    """
    try:
        llm = LLMAgent()
        model_status = "connected" if hasattr(llm, 'connected') and llm.connected else "unknown"
        
        return JsonResponse({
            "status": "healthy",
            "model_connection": model_status,
            "service": "Django ML Preprocessing API",
            "mode": "column_wise_operations",
            "description": "Fast column-wise preprocessing operations only"
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "model_connection": "unknown",
            "error": str(e)
        }, status=500)

# ===============================
# 🔹 Analysis Mode Selection API
# ===============================
@csrf_exempt
def analyze_with_mode_view(request):
    """
    Analyze dataset with column-wise mode only
    """
    if request.method == "POST" and request.FILES.get("file"):
        try:
            uploaded_file = request.FILES["file"]
            
            print(f"📥 Received file for analysis: {uploaded_file.name}")
            
            if not uploaded_file.name.lower().endswith('.csv'):
                return JsonResponse({"error": "Only CSV files are supported"}, status=400)
            
            saved_path = handle_uploaded_file(uploaded_file)
            
            # Read CSV for analysis using Django storage
            try:
                with default_storage.open(saved_path, 'rb') as f:
                    df = pd.read_csv(f)
                print(f"📊 CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")
                
                # Perform AI analysis
                llm = LLMAgent()
                ai_result = llm.analyze_dataset(df, "column_wise")
                
                print(f"🤖 AI analysis completed. Status: {ai_result.get('status')}")
                
                operations = ai_result.get("operations", ["validate:datatypes"])
                column_operations = ai_result.get("column_operations", {})
                
                response_data = {
                    "message": "File analyzed successfully!",
                    "file_info": {
                        "filename": uploaded_file.name,
                        "rows": df.shape[0],
                        "columns": df.shape[1],
                        "columns_list": df.columns.tolist()
                    },
                    "ai_analysis": {
                        "status": ai_result.get("status", "unknown"),
                        "suggestions": operations,
                        "column_operations": column_operations,
                        "reasoning": ai_result.get("reasoning", ""),
                        "connection_verified": ai_result.get("connection_verified", False),
                        "analysis_type": ai_result.get("analysis_type", "column_wise"),
                        "is_fallback": ai_result.get("is_fallback", False)
                    }
                }
                
                return JsonResponse(response_data)

            except Exception as e:
                print(f"❌ CSV processing error: {str(e)}")
                return JsonResponse({"error": f"Error processing CSV: {str(e)}"}, status=500)

        except Exception as e:
            print(f"❌ Upload error: {str(e)}")
            return JsonResponse({"error": f"Upload failed: {str(e)}"}, status=500)

    return JsonResponse({"error": "No file uploaded"}, status=400)

# ===============================
# 🔹 Advanced Analysis API
# ===============================
@csrf_exempt
def advanced_analysis_view(request):
    """
    Advanced analysis with full preprocessing
    """
    if request.method == "POST" and request.FILES.get("file"):
        try:
            uploaded_file = request.FILES["file"]
            print(f"📥 Received file for ADVANCED analysis: {uploaded_file.name}")
            
            if not uploaded_file.name.lower().endswith('.csv'):
                return JsonResponse({"error": "Only CSV files are supported"}, status=400)
            
            saved_path = handle_uploaded_file(uploaded_file)
            print(f"💾 File saved at: {saved_path}")

            # Read CSV for analysis using Django storage
            try:
                with default_storage.open(saved_path, 'rb') as f:
                    df = pd.read_csv(f)
                print(f"📊 CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")
                
                # Perform AI analysis
                llm = LLMAgent()
                ai_result = llm.analyze_dataset(df, "column_wise")
                
                print(f"🤖 AI analysis completed. Status: {ai_result.get('status')}")
                
                operations = ai_result.get("operations", ["validate:datatypes"])
                column_operations = ai_result.get("column_operations", {})
                
                # Run preprocessing
                processed_df, logs, download_info = run_preprocessing_pipeline(
                    saved_path, 
                    operations=operations,
                    original_filename=uploaded_file.name,
                    column_operations=None
                )
                
                response_data = {
                    "message": "Advanced analysis completed!",
                    "file_info": {
                        "filename": uploaded_file.name,
                        "rows": df.shape[0],
                        "columns": df.shape[1],
                        "columns_list": df.columns.tolist()
                    },
                    "ai_analysis": {
                        "status": ai_result.get("status", "unknown"),
                        "suggestions": operations,
                        "column_operations": column_operations,
                        "reasoning": ai_result.get("reasoning", ""),
                        "connection_verified": ai_result.get("connection_verified", False),
                        "analysis_type": ai_result.get("analysis_type", "column_wise"),
                        "is_fallback": ai_result.get("is_fallback", False)
                    },
                    "processing": {
                        "status": "success",
                        "executed_operations": operations,
                        "logs": logs,
                        "processed_info": {
                            "rows": processed_df.shape[0] if not processed_df.empty else 0,
                            "columns": processed_df.shape[1] if not processed_df.empty else 0
                        }
                    }
                }
                
                # Add download info
                if download_info:
                    response_data["download"] = {
                        "status": "ready",
                        "filename": download_info.get("filename", "processed_file.csv"),
                        "download_url": download_info.get("download_url", ""),
                        "message": "Processed file ready for download"
                    }
                
                return JsonResponse(response_data)

            except Exception as e:
                print(f"❌ CSV processing error: {str(e)}")
                return JsonResponse({"error": f"Error processing CSV: {str(e)}"}, status=500)

        except Exception as e:
            print(f"❌ Upload error: {str(e)}")
            return JsonResponse({"error": f"Upload failed: {str(e)}"}, status=500)

    return JsonResponse({"error": "No file uploaded"}, status=400)
