# # mainapp/file/download.py
# import os
# from django.http import FileResponse, Http404

# DOWNLOAD_DIR = "uploaded_files"  # Or processed_files if you create one

# def download_file(filename):
#     """
#     Returns a file as a downloadable response.
#     """
#     file_path = os.path.join(DOWNLOAD_DIR, filename)

#     if not os.path.exists(file_path):
#         raise Http404("File not found!")

#     response = FileResponse(open(file_path, "rb"), as_attachment=True, filename=filename)
#     return response


import os
import pandas as pd
from django.http import FileResponse, Http404
import uuid

PROCESSED_DIR = "processed_files"

def ensure_processed_dir():
    """Ensure processed files directory exists"""
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)

def download_file(filename):
    """
    Returns a file as a downloadable response.
    """
    file_path = os.path.join(PROCESSED_DIR, filename)

    if not os.path.exists(file_path):
        raise Http404("File not found!")

    response = FileResponse(open(file_path, "rb"), as_attachment=True, filename=filename)
    return response

def save_processed_file(df, original_filename):
    """
    Save processed DataFrame and return download info
    """
    ensure_processed_dir()
    
    # Generate unique filename for processed file
    original_name = os.path.splitext(original_filename)[0]
    unique_id = uuid.uuid4().hex[:8]
    processed_filename = f"processed_{unique_id}_{original_name}.csv"
    
    file_path = os.path.join(PROCESSED_DIR, processed_filename)
    
    # Save processed DataFrame
    df.to_csv(file_path, index=False)
    
    return {
        "filename": processed_filename,
        "file_path": file_path,
        "download_url": f"/download/{processed_filename}"
    }