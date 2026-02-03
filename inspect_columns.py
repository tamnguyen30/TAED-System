import pandas as pd
import os

# Path to your data file
file_path = os.path.join('data', 'phishing_email.csv')

print(f" Inspecting columns for '{file_path}'...\n")

try:
    # Load just the first 5 rows to be quick
    df = pd.read_csv(file_path, on_bad_lines='skip', nrows=5)

    
    # Print the list of column names
    print(list(df.columns))
    print("\n" + "="*40)
    print("ACTION: Use these names to fix the `rename` line in `process_data.py`.")

except FileNotFoundError:
    print(f"ERROR: File not found at '{file_path}'.")
