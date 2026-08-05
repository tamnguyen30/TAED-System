import pandas as pd
import os

SPLITS_DIR = 'data/splits'
OUTPUT_DIR = 'data'

print("🚀 Starting data preparation for FastText...")


print("Processing training data...")
X_train = pd.read_csv(os.path.join(SPLITS_DIR, 'X_train.csv')).squeeze("columns")
y_train = pd.read_csv(os.path.join(SPLITS_DIR, 'y_train.csv')).squeeze("columns")

with open(os.path.join(OUTPUT_DIR, 'fasttext_train.txt'), 'w') as f:
    for text, label in zip(X_train, y_train):
        
        line = f"__label__{label} {str(text)}\n"
        f.write(line)
print(f"✅ Created '{os.path.join(OUTPUT_DIR, 'fasttext_train.txt')}'")



print("Processing testing data...")
X_test = pd.read_csv(os.path.join(SPLITS_DIR, 'X_test.csv')).squeeze("columns")
y_test = pd.read_csv(os.path.join(SPLITS_DIR, 'y_test.csv')).squeeze("columns")

with open(os.path.join(OUTPUT_DIR, 'fasttext_test.txt'), 'w') as f:
    for text, label in zip(X_test, y_test):
        line = f"__label__{label} {str(text)}\n"
        f.write(line)
print(f"✅ Created '{os.path.join(OUTPUT_DIR, 'fasttext_test.txt')}'")

print("\nData preparation complete.")
