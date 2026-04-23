import pandas as pd
import numpy as np

def encode_data(df, method='auto', columns=None):
    """
    Encode categorical data
    
    Parameters:
    - df: DataFrame to encode
    - method: 'auto', 'onehot', 'label', 'frequency'
    - columns: Specific columns to encode (None for all categorical)
    
    Returns:
    - Encoded DataFrame
    """
    if columns is None:
        columns = df.select_dtypes(include=['object', 'category']).columns
    
    if method == 'auto':
        # Auto-select based on cardinality
        for col in columns:
            unique_count = df[col].nunique()
            if unique_count <= 10:
                df = _onehot_encode(df, col)
            else:
                df = _label_encode(df, col)
    
    elif method == 'onehot':
        for col in columns:
            df = _onehot_encode(df, col)
    
    elif method == 'label':
        for col in columns:
            df = _label_encode(df, col)
    
    elif method == 'frequency':
        for col in columns:
            df = _frequency_encode(df, col)
    
    return df

def _onehot_encode(df, col):
    """One-hot encoding for a column"""
    encoded = pd.get_dummies(df[col], prefix=col)
    df = pd.concat([df, encoded], axis=1)
    df.drop(col, axis=1, inplace=True)
    return df

def _label_encode(df, col):
    """Label encoding for a column"""
    df[col] = df[col].astype('category').cat.codes
    return df

def _frequency_encode(df, col):
    """Frequency encoding for a column"""
    freq_map = df[col].value_counts().to_dict()
    df[col] = df[col].map(freq_map)
    return df