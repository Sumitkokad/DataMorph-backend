import pandas as pd
import numpy as np

def impute_data(df, method='auto', columns=None):
    """
    Impute missing values
    
    Parameters:
    - df: DataFrame to impute
    - method: 'auto', 'mean', 'median', 'mode', 'constant'
    - columns: Specific columns to impute (None for all with missing values)
    
    Returns:
    - DataFrame with imputed values
    """
    if columns is None:
        # Get columns with missing values
        columns = df.columns[df.isnull().any()].tolist()
    
    if method == 'auto':
        for col in columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(df[col].median(), inplace=True)
            else:
                mode_val = df[col].mode()
                df[col].fillna(mode_val[0] if not mode_val.empty else "Unknown", inplace=True)
    
    elif method == 'mean':
        for col in columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(df[col].mean(), inplace=True)
    
    elif method == 'median':
        for col in columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(df[col].median(), inplace=True)
    
    elif method == 'mode':
        for col in columns:
            mode_val = df[col].mode()
            df[col].fillna(mode_val[0] if not mode_val.empty else "Unknown", inplace=True)
    
    elif method == 'constant':
        for col in columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(0, inplace=True)
            else:
                df[col].fillna("Unknown", inplace=True)
    
    return df