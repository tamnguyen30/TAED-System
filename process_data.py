import pandas as pd
import os

print("🚀 Starting the COMPREHENSIVE data processing script for ALL NINE files...")

# --- Configuration ---
FINAL_COLUMNS = ['text', 'label']
PHISHING = 1
SAFE = 0
DATA_PATH = 'data/'

# --- Helper function ---
def get_email_body(raw_text):
    if not isinstance(raw_text, str): return ""
    header_end = raw_text.find('\n\n')
    return raw_text[header_end + 2:].strip() if header_end != -1 else raw_text.strip()

# --- Processing Functions ---

def process_main_files(path):
    """Processes the three main, well-structured CSVs."""
    all_dfs = []
    
    # 1. Main Phishing File (with its own labels)
    try:
        df_phish = pd.read_csv(os.path.join(path, 'phishing_email.csv'), on_bad_lines='skip')
        df_phish = df_phish.rename(columns={'Email Text': 'text', 'Email Type': 'label'})
        df_phish['label'] = df_phish['label'].apply(lambda x: PHISHING if 'Phishing' in str(x) else SAFE)
        print(f"📊 Loaded 'phishing_email.csv': {len(df_phish)} rows")
        all_dfs.append(df_phish[FINAL_COLUMNS])
    except FileNotFoundError:
        print("⚠️ 'phishing_email.csv' not found. Skipping.")

    # 2. Both Enron Files (labeled as SAFE)
    try:
        df_raw = pd.read_csv(os.path.join(path, 'emails.csv'))
        df_raw = df_raw.rename(columns={'message': 'text'})
        df_raw['text'] = df_raw['text'].apply(get_email_body)
        
        df_parsed = pd.read_csv(os.path.join(path, 'enron_mails.csv'))
        df_parsed = df_parsed.rename(columns={'body': 'text'})
        
        df_enron = pd.concat([df_raw[['text']], df_parsed[['text']]], ignore_index=True)
        df_enron['label'] = SAFE
        print(f"📊 Loaded and combined both main Enron files: {len(df_enron)} rows")
        all_dfs.append(df_enron[FINAL_COLUMNS])
    except FileNotFoundError:
        print("⚠️ Main Enron CSVs not found. Skipping.")
        
    return pd.concat(all_dfs, ignore_index=True)

def process_subset_files(path):
    """Processes the six other individual CSV files by assigning labels based on filename."""
    
    # Define which files are phishing and which are safe
    file_map = {
        'CEAS_08.csv': PHISHING,
        'Ling.csv': PHISHING,
        'Nazario.csv': PHISHING,
        'Nigerian_Fraud.csv': PHISHING,
        'Enron.csv': SAFE,
        'SpamAssasin.csv': SAFE
    }
    
    all_dfs = []
    for filename, label in file_map.items():
        try:
            df = pd.read_csv(os.path.join(path, filename), encoding='latin1', on_bad_lines='skip')
            # Assume the first column is the email text
            df = df.rename(columns={df.columns[0]: 'text'})
            df['label'] = label
            print(f"📊 Loaded subset file '{filename}': {len(df)} rows")
            all_dfs.append(df[FINAL_COLUMNS])
        except FileNotFoundError:
            print(f"⚠️ Subset file '{filename}' not found. Skipping.")
            continue
            
    return pd.concat(all_dfs, ignore_index=True)

# --- Main Execution ---
main_df = process_main_files(DATA_PATH)
subset_df = process_subset_files(DATA_PATH)

print("\n⚙️ Combining all datasets...")
final_df = pd.concat([main_df, subset_df], ignore_index=True)
print(f"Total rows before cleaning: {len(final_df)}")

# --- Final Cleaning ---
print("🧹 Cleaning the dataset (dropping duplicates and missing values)...")
final_df.dropna(subset=['text'], inplace=True)
final_df['text'] = final_df['text'].astype(str)
# This de-duplication step is now very important
final_df.drop_duplicates(subset=['text'], inplace=True, keep='first')
final_df = final_df[final_df['text'].str.len() > 50].copy()

# Shuffle the dataset
final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\nTotal rows after cleaning and de-duplication: {len(final_df)}")
print("\nFinal label distribution:")
print(final_df['label'].value_counts())

# --- Save the Final Dataset ---
output_path = os.path.join(DATA_PATH, 'unified_phishing_dataset.csv')
final_df.to_csv(output_path, index=False)
print(f"\n✅ Success! Your final, comprehensive dataset is saved at: {output_path}")
