import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

def scale_data(df, method='standard', columns=None):
    """
    Scale numerical data
    
    Parameters:
    - df: DataFrame to scale
    - method: 'standard', 'minmax', 'robust'
    - columns: Specific columns to scale (None for all numerical)
    
    Returns:
    - Scaled DataFrame
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns
    
    if len(columns) == 0:
        return df
    
    if method == 'standard':
        scaler = StandardScaler()
    elif method == 'minmax':
        scaler = MinMaxScaler()
    elif method == 'robust':
        scaler = RobustScaler()
    else:
        raise ValueError(f"Unknown scaling method: {method}")
    
    df[columns] = scaler.fit_transform(df[columns])
    return df