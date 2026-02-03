import pandas as pd
from sklearn.model_selection import train_test_split
import os

# --- Configuration ---
INPUT_FILE = 'data/balanced_phishing_dataset.csv'
OUTPUT_DIR = 'data/splits'
TEST_SIZE = 0.2  # 20% of the data will be for testing
RANDOM_STATE = 42
# --- End Configuration ---

print(f"🚀 Starting data splitting process...")

# 1. Load the balanced dataset
print(f"Loading balanced data from '{INPUT_FILE}'...")
try:
    df = pd.read_csv(INPUT_FILE)
except FileNotFoundError:
    print(f"❌ ERROR: Balanced dataset not found at '{INPUT_FILE}'.")
    exit()

# Create the output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"Output directory '{OUTPUT_DIR}' is ready.")

# 2. Separate features (X = email text) and target (y = label)
X = df['text']
y = df['label']

# 3. Split the data
print(f"Splitting data: {1-TEST_SIZE:.0%} for training, {TEST_SIZE:.0%} for testing...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
)
# 'stratify=y' ensures the ratio of safe/phishing emails is the same in both the train and test sets.

print("\n--- Split Sizes ---")
print(f"Training samples: {len(X_train)}")
print(f"Testing samples:  {len(X_test)}")
print("--------------------")

# 4. Save the splits to separate files
print(f"💾 Saving splits to the '{OUTPUT_DIR}' directory...")
X_train.to_csv(os.path.join(OUTPUT_DIR, 'X_train.csv'), index=False)
X_test.to_csv(os.path.join(OUTPUT_DIR, 'X_test.csv'), index=False)
y_train.to_csv(os.path.join(OUTPUT_DIR, 'y_train.csv'), index=False)
y_test.to_csv(os.path.join(OUTPUT_DIR, 'y_test.csv'), index=False)

print(f"\n✅ Success! Data has been split and saved.")
