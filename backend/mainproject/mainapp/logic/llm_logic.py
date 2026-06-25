# https://console.groq.com/keys

import pandas as pd
import numpy as np
import json
import re
import requests
from typing import Dict, List, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)

class LLMAgent:
    def __init__(self):
        import os
        
        # Groq API Configuration
        self.api_key = "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"
        
        if not self.api_key:
            raise ValueError("❌ GROQ_API_KEY not set")
        
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
        self.connected = True  # Add connected attribute
        
        # Allowed operations
        self.allowed_operations = {
            "validate:datatypes", "remove:duplicates", "flag:missing",
            "impute:mean", "impute:median", "impute:mode",
            "scale:standard", "scale:minmax", "scale:robust",
            "encode:onehot", "encode:label",
            "detect:outliers_iqr", "flag:outliers", "handle:outliers",
            "clean:text", "log_transform"
        }
    
    def analyze_dataset(self, df, analysis_type="basic", context=None):
        """
        Analyze dataset and return preprocessing suggestions from Groq
        Returns both 'operations' and 'column_operations' for compatibility
        """
        print(f"\n🚀 Analyzing dataset with Groq ({analysis_type})")
        
        if df is None or df.empty:
            return self._empty_response()
        
        try:
            # Create dataset summary
            summary = self.generate_enhanced_summary(df)
            
            print("📊 Dataset summary created")
            
            # Call Groq API
            response_text = self._call_groq_api(summary, analysis_type, context)
            
            # Parse and validate response
            parsed_ops = self._parse_groq_response(response_text, analysis_type, df)
            
            # Convert to both formats for compatibility
            operations = parsed_ops.get("operations", ["validate:datatypes"])
            column_operations = self._convert_to_column_operations(operations, df)
            
            return {
                "status": "success",
                "connection_verified": True,
                "operations": operations,  # For string format operations
                "column_operations": column_operations,  # For column-wise format
                "suggestions": operations,  # Backward compatibility
                "analysis_type": analysis_type,
                "generation_time": 0,
                "reasoning": "AI suggested preprocessing steps based on dataset analysis",
                "is_fallback": False,
                "raw_response": response_text[:500]
            }
        
        except Exception as e:
            logger.error(f"Groq analysis error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "reason": str(e),
                "operations": ["validate:datatypes"],
                "column_operations": {},
                "suggestions": ["validate:datatypes"],
                "is_fallback": True
            }
    
    def _convert_to_column_operations(self, operations, df):
        """
        Convert flat operations list to column_operations dict format
        """
        column_ops = {}
        
        for op in operations:
            if isinstance(op, dict):
                # Already in column format
                column = op.get('column')
                operation = op.get('operation')
                if column and operation:
                    if column not in column_ops:
                        column_ops[column] = []
                    column_ops[column].append(operation)
            elif isinstance(op, str):
                # String format - might be dataset-wide or need column inference
                if op in ["validate:datatypes", "remove:duplicates", "flag:missing"]:
                    # Dataset-wide operations
                    if "dataset_wide" not in column_ops:
                        column_ops["dataset_wide"] = []
                    column_ops["dataset_wide"].append(op)
                else:
                    # Try to infer appropriate columns for column-specific operations
                    if op.startswith("impute:") or op.startswith("scale:") or op.startswith("encode:"):
                        # Find numeric/categorical columns
                        if op.startswith("encode:"):
                            cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                        else:
                            cols = df.select_dtypes(include=[np.number]).columns.tolist()
                        
                        # Apply to all relevant columns
                        for col in cols:
                            if col not in column_ops:
                                column_ops[col] = []
                            column_ops[col].append(op)
        
        return column_ops
    
    def generate_enhanced_summary(self, df):
        """
        Create comprehensive dataset summary for Groq
        """
        summary = {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "column_details": []
        }
        
        # Sample rows for context
        sample_rows = min(3, len(df))
        # Ensure we can serialize cleanly
        summary["sample_data"] = json.loads(df.head(sample_rows).to_json(orient='records', date_format='iso'))
        
        # Column-wise analysis
        for col in df.columns:
            series = df[col]
            
            col_info = {
                "name": col,
                "dtype": str(series.dtype),
                "missing": int(series.isnull().sum()),
                "missing_pct": round(series.isnull().mean() * 100, 2),
                "unique": int(series.nunique()),
                "sample": series.dropna().head(3).tolist()
            }
            
            # Add numeric statistics
            if pd.api.types.is_numeric_dtype(series):
                non_null = series.dropna()
                if len(non_null) > 0:
                    col_info.update({
                        "min": float(non_null.min()),
                        "max": float(non_null.max()),
                        "mean": float(non_null.mean()),
                        "std": float(non_null.std()),
                        "skew": float(non_null.skew()) if len(non_null) > 2 else 0.0
                    })
            
            # Add categorical info
            elif pd.api.types.is_object_dtype(series):
                if series.nunique() <= 10:
                    top_values = series.value_counts().head(3).to_dict()
                    col_info["top_values"] = top_values
            
            summary["column_details"].append(col_info)
            
        # Correlation Matrix & Target Leakage Detection
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        high_correlations = []
        if len(numeric_cols) > 1:
            try:
                corr_matrix = df[numeric_cols].corr().abs()
                upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
                # Find index feature pairs with correlation > 0.85
                for col in upper.columns:
                    for row in upper.index:
                        if upper.loc[row, col] > 0.85:
                            high_correlations.append(f"{row} & {col} (Corr: {round(upper.loc[row, col], 2)})")
            except Exception as e:
                pass
        
        summary["high_correlations"] = high_correlations
        
        return json.dumps(summary, default=str)
    
    def _call_groq_api(self, summary, analysis_type, context=None):
        """
        Call Groq API with proper formatting
        """
        try:
            system_prompt = """You are a senior production-grade data scientist powering a full automated ML preprocessing pipeline.

Your job is to suggest a COMPREHENSIVE set of preprocessing operations based on the data statistics.

CRITICAL RULES:
1. Always include "validate:datatypes"
2. NEVER encode ID columns
3. Address ALL columns that have missing values
4. Suggest scaling for ALL numeric columns (if specified by user)
5. Suggest encoding for ALL categorical columns (if specified by user)
6. Respect USER CONTEXT strictly. If user asks for 'auto', perform all standard best practices.
7. Always provide full 'reasoning' for why you chose an action.

STRICT OUTPUT:
Return ONLY a JSON array

FORMAT:
[
  "validate:datatypes",
  {"operation": "impute:median", "column": "age", "reasoning": "Explain exactly why based on stats"},
  {"operation": "drop:column", "column": "tax", "reasoning": "Highly correlated (0.95) with target"}
]

NO explanations outside the JSON array. NO markdown."""
            
            context_text = "None provided"
            if context:
                if isinstance(context, str):
                    try:
                        ctx_dict = json.loads(context)
                        context_text = "\n".join([f"- {k.replace('_', ' ').capitalize()}: {v}" for k, v in ctx_dict.items() if v])
                    except:
                        context_text = context
                elif isinstance(context, dict):
                    context_text = "\n".join([f"- {k.replace('_', ' ').capitalize()}: {v}" for k, v in context.items() if v])
                else:
                    context_text = str(context)

            user_prompt = f"""Dataset Summary:
{summary}

User Configured Context & Guidelines:
{context_text}

Analysis Type: {analysis_type}

IMPORTANT:
- You are a FULL PIPELINE. Suggest operations for ALL columns needing preprocessing.
- Address missing values across all columns based on the strategy in the context.
- Scale all necessary numeric data.
- Encode all necessary categorical data.
- Respect the user's defined context rigorously."""
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 1000
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            print("📡 Sending request to Groq API...")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            print(f"API Status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Groq API error: {response.text}")
                return '["validate:datatypes"]'
            
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            print(f"Raw Groq response: {content[:200]}...")
            
            return content
        
        except requests.exceptions.Timeout:
            logger.error("Groq API timeout")
            return '["validate:datatypes"]'
        except Exception as e:
            logger.error(f"Groq API call error: {str(e)}")
            return '["validate:datatypes"]'
    
    def _parse_groq_response(self, response_text, analysis_type, df=None):
        """
        Parse Groq API response and extract operations
        """
        if not response_text:
            return {
                "status": "error",
                "reason": "Empty response from Groq",
                "operations": ["validate:datatypes"]
            }
        
        operations = []
        
        try:
            # Try to extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                # Clean up any markdown artifacts
                json_str = re.sub(r'```json\s*', '', json_str)
                json_str = re.sub(r'```\s*', '', json_str)
                
                try:
                    parsed = json.loads(json_str)
                    if isinstance(parsed, list):
                        operations = parsed
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parse error: {e}")
                    
                    # Try to extract operations manually
                    for op in self.allowed_operations:
                        if op in response_text.lower():
                            operations.append(op)
            
            # If still empty, try direct parsing
            if not operations:
                try:
                    parsed = json.loads(response_text)
                    if isinstance(parsed, list):
                        operations = parsed
                except:
                    # Fallback: extract known operations
                    for op in self.allowed_operations:
                        if op in response_text.lower():
                            operations.append(op)
            
            # Always include validate:datatypes
            if "validate:datatypes" not in operations and "validate:datatypes" not in str(operations):
                operations.insert(0, "validate:datatypes")
            
            # Validate and filter operations for safety
            validated_ops = self._validate_operations(operations, df)
            
            return {
                "status": "success",
                "connection_verified": True,
                "operations": validated_ops,
                "analysis_type": analysis_type
            }
        
        except Exception as e:
            logger.error(f"Error parsing Groq response: {e}")
            return {
                "status": "error",
                "reason": f"Parse error: {str(e)}",
                "operations": ["validate:datatypes"]
            }
    
    def _validate_operations(self, operations, df=None):
        """
        Validate and clean operations list, filtering out unsafe operations
        """
        if not operations:
            return ["validate:datatypes"]
        
        validated = []
        
        for op in operations:
            try:
                # Dict format
                if isinstance(op, dict):
                    operation = op.get('operation') or op.get('name')
                    column = op.get('column')
                    
                    if operation and operation in self.allowed_operations:
                        if column:
                            # 🛡️ SAFETY CHECK: Skip non-existent columns
                            if df is not None and column not in df.columns:
                                continue
                            
                            # 🛡️ SAFETY CHECK: Do not encode ID columns
                            if "encode" in operation and "id" in column.lower():
                                continue
                            
                            valid_op = {"operation": operation, "column": column}
                            if "reasoning" in op:
                                valid_op["reasoning"] = op["reasoning"]
                            validated.append(valid_op)
                        else:
                            validated.append(operation)
                
                # String format
                elif isinstance(op, str):
                    if op in self.allowed_operations:
                        validated.append(op)
            
            except Exception as e:
                logger.warning(f"Error validating operation {op}: {e}")
                continue
        
        # Ensure validate:datatypes is present
        has_validate = False
        for op in validated:
            if op == "validate:datatypes" or (isinstance(op, dict) and op.get('operation') == "validate:datatypes"):
                has_validate = True
                break
        
        if not has_validate:
            validated.insert(0, "validate:datatypes")
        
        return validated
    
    def _empty_response(self):
        """Return empty response format"""
        return {
            "status": "success",
            "operations": ["validate:datatypes"],
            "column_operations": {},
            "suggestions": ["validate:datatypes"],
            "analysis_type": "basic",
            "is_fallback": True
        }

    def execute_custom_operation(self, df, column, prompt, logs):
        """
        Execute a custom natural language column transformation using LLM-generated lambda code
        """
        try:
            series = df[column]
            sample = series.dropna().head(3).tolist()
            dtype = str(series.dtype)
            
            system_prompt = "You are a Python Pandas Data Scientist. Output ONLY a valid Python code string for the right side of a lambda function. The input variable is 's', which represents a FULL pandas.Series object (the entire column). Use pandas vectorized operations (e.g. s.fillna(s.mode()[0]), s.astype(str), s.str.replace). DO NOT wrap in markdown or quotes. DO NOT output the word lambda."
            user_prompt = f"Data dtype: {dtype}\nSample values: {sample}\nTransformation request: {prompt}\n\nLambda code for s:"
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.0,
                "max_tokens": 100
            }
            
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            
            print(f"🤖 Sending custom prompt for {column}: '{prompt}'")
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            if response.status_code != 200:
                logs.append(f"⚠️ {column}: AI code generation failed ({response.status_code})")
                return df
                
            result = response.json()
            code = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            # Clean up potential markdown formatting
            code = code.replace("```python", "").replace("```", "").strip()
            if code.startswith("lambda s:"):
                code = code.replace("lambda s:", "", 1).strip()
            if code.startswith("'") and code.endswith("'"):
                code = code[1:-1]
            if code.startswith('"') and code.endswith('"'):
                code = code[1:-1]
                
            # Execute the lambda safely within the Series context
            global_env = {
                "__builtins__": {}, 
                "pd": pd, 
                "np": np, 
                "re": __import__('re'), 
                "str": str, "int": int, "float": float, "bool": bool, "len": len,
                "math": __import__('math'), 
                "datetime": __import__('datetime')
            }
            # Give access to the whole dataframe `df` inside global env just in case LLM needs it
            global_env["df"] = df
            
            lambda_func = eval(f"lambda s: {code}", global_env, {})
            
            # Vectorized application
            df[column] = lambda_func(df[column])
            
            logs.append(f"🌟 {column}: Custom AI operation '{prompt}' executed successfully! (lambda s: {code})")
            
        except Exception as e:
            logs.append(f"⚠️ {column}: Custom AI operation '{prompt}' failed - {str(e)}")
            logger.error(f"Custom OP Error on {column}: {str(e)}\nGenerated Code: {locals().get('code', 'None')}", exc_info=True)
            
        return df
