import pandas as pd
import numpy as np

def remove_outliers(df, method='iqr', columns=None):
    """
    Handle outliers in data
    
    Parameters:
    - df: DataFrame to process
    - method: 'iqr', 'zscore', 'isolation'
    - columns: Specific columns to process (None for all numerical)
    
    Returns:
    - DataFrame with outliers handled
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns
    
    if method == 'iqr':
        return _handle_outliers_iqr(df, columns)
    elif method == 'zscore':
        return _handle_outliers_zscore(df, columns)
    elif method == 'isolation':
        return _handle_outliers_isolation(df, columns)
    else:
        raise ValueError(f"Unknown outlier method: {method}")

def _handle_outliers_iqr(df, columns):
    """Handle outliers using IQR method"""
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Cap outliers instead of removing
        df[col] = np.where(df[col] < lower_bound, lower_bound, df[col])
        df[col] = np.where(df[col] > upper_bound, upper_bound, df[col])
    
    return df

def _handle_outliers_zscore(df, columns):
    """Handle outliers using Z-score method"""
    for col in columns:
        z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
        # Cap values beyond 3 standard deviations
        upper_bound = df[col].mean() + 3 * df[col].std()
        lower_bound = df[col].mean() - 3 * df[col].std()
        
        df[col] = np.where(df[col] > upper_bound, upper_bound, df[col])
        df[col] = np.where(df[col] < lower_bound, lower_bound, df[col])
    
    return df

def _handle_outliers_isolation(df, columns):
    """Handle outliers using isolation (placeholder)"""
    # Simple version - use IQR as fallback
    return _handle_outliers_iqr(df, columns)