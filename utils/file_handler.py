import os
import pandas as pd
import numpy as np

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def allowed_file(filename):
    """Check if uploaded file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_input_data(file_path):
    """Load dataset from a CSV or XLSX file."""
    try:
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            data = pd.read_excel(file_path)
        else:
            return None
        return data
    except Exception as e:
        print(f"[ERROR] Failed to load data: {e}")
        return None


def validate_numeric_values(data):
    """
    Ensure that all values (except the first column) are numeric.
    Returns True if valid, False otherwise.
    """
    try:
        non_numeric_columns = data.iloc[:, 1:].applymap(lambda x: not np.isreal(x)).any()
        return not non_numeric_columns.any()
    except Exception as e:
        print(f"[ERROR] Numeric validation failed: {e}")
        return False
