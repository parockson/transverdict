import pandas as pd
import re

def clean_transaction_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1. Regex Cleaning of Column Names
    new_cols = []
    for col in df.columns:
        clean_name = str(col).lower()
        # Replace non-alphanumeric chars with underscore
        clean_name = re.sub(r'[^a-zA-Z0-9]', '_', clean_name) 
        # Remove double underscores and trim
        clean_name = re.sub(r'_+', '_', clean_name).strip('_') 
        new_cols.append(clean_name)
    
    df.columns = new_cols

    # 2. Force Map the problematic Client Name column
    for col in df.columns:
        if 'users_client' in col and 'name' in col:
            df = df.rename(columns={col: 'client_name'})

    # 3. Numeric & Date cleaning
    if 'amount' in df.columns:
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    
    # Identify and convert time columns
    time_col = next((c for c in df.columns if 'time' in c or 'date' in c), None)
    if time_col:
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')

    return df