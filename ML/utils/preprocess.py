import joblib
import pandas as pd

# Load the permission columns you saved
PERMISSION_COLUMNS_PATH = "ml/models/permission_columns.pkl"
permission_columns = joblib.load(PERMISSION_COLUMNS_PATH)

def permissions_to_vector(permissions_list):
    """
    Convert extracted permissions into a 0/1 one-hot encoded row.
    """
    df = pd.DataFrame([0] * len(permission_columns), index=permission_columns).T

    for perm in permissions_list:
        if perm in df.columns:
            df[perm] = 1    

    return df  # DataFrame with 1 row
