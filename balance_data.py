import pandas as pd
from sklearn.utils import shuffle

# --- Configuration ---
INPUT_FILE = 'data/processed_phishing_dataset.csv'
OUTPUT_FILE = 'data/balanced_phishing_dataset.csv'
SAFE_LABEL = 0
PHISHING_LABEL = 1
# --- End Configuration ---

print(f"⚖️  Loading the processed dataset from '{INPUT_FILE}'...")
try:
    df = pd.read_csv(INPUT_FILE)
except FileNotFoundError:
    print(f" ERROR: Input file not found. Make sure you have run 'process_data.py' first.")
    exit()

# Separate the majority (safe) and minority (phishing) classes
df_safe = df[df['label'] == SAFE_LABEL]
df_phishing = df[df['label'] == PHISHING_LABEL]

phishing_count = len(df_phishing)
print(f"Original distribution: {len(df_safe)} safe emails, {phishing_count} phishing emails.")

print(f"Undersampling safe emails to match the phishing count: {phishing_count}...")
# Undersample the majority class to have the same number of samples as the minority class
df_safe_downsampled = df_safe.sample(n=phishing_count, random_state=42)

# Combine the downsampled safe emails with the original phishing emails
df_balanced = pd.concat([df_safe_downsampled, df_phishing])

# Shuffle the dataset to ensure the data is mixed
df_balanced = shuffle(df_balanced, random_state=42)

print(f"New balanced distribution: {len(df_safe_downsampled)} safe, {len(df_phishing)} phishing.")

# Save the new balanced dataset to a CSV file
df_balanced.to_csv(OUTPUT_FILE, index=False)

print(f"\nSuccess! Balanced dataset with {len(df_balanced)} total emails saved to '{OUTPUT_FILE}'.")
