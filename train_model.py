import pandas as pd
import joblib
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

# CONFIGURATION
DATA_PATH = 'data/balanced_phishing_dataset.csv'
MODEL_PATH = 'models/random_forest_pipeline.joblib'

print("\n" + "="*60)
print("  TRAINING ROBUST PHISHING MODEL (Random Forest + TF-IDF)")
print("="*60)

# 1. Load Data
try:
    print(f"[1] Loading dataset: {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # Auto-detect target column
    target_col = 'label' if 'label' in df.columns else 'phishing'
    if target_col not in df.columns:
        # Fallback for some dataset versions
        target_col = df.columns[-1]
    
    # Handle missing text
    df['text'] = df['text'].fillna('')
    print(f"    > Loaded {len(df)} samples.")
    
except Exception as e:
    print(f"[!] Critical Error: {e}")
    exit(1)

# 2. Split Data
X_train, X_test, y_train, y_test = train_test_split(
    df['text'], df[target_col], test_size=0.2, random_state=42
)

# 3. Build Pipeline
print("[2] Building Pipeline...")
pipeline = Pipeline([
    # TfidfVectorizer converts text to math (words -> numbers)
    ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1,2))),
    # RandomForest is robust against overfitting
    ('clf', RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42))
])

# 4. Cross-Validation (The "Research Grade" Verification)
print("[3] Running 5-Fold Cross-Validation (Checking for Overfitting)...")
cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5)
print(f"    > CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# 5. Train Final Model
print("[4] Training Final Model on full training set...")
pipeline.fit(X_train, y_train)

# 6. Evaluation
print("[5] Evaluating on Test Set...")
preds = pipeline.predict(X_test)
acc = accuracy_score(y_test, preds)
print(f"    > Test Set Accuracy: {acc:.4f}")
print("\nDetailed Report:")
print(classification_report(y_test, preds))

# 7. Save
print(f"[6] Saving model to {MODEL_PATH}...")
joblib.dump(pipeline, MODEL_PATH)
print("✅ MODEL SAVED. System is ready for hybrid_defense.py")
