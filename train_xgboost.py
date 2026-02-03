import pandas as pd
import joblib
import os
import time
import xgboost as xgb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, recall_score, roc_auc_score, classification_report

# --- Configuration ---
SPLITS_DIR = 'data/splits'
MODELS_DIR = 'models'
MODEL_NAME = 'xgboost_pipeline.joblib'
# --- End Configuration ---

print("🚀 Starting XGBoost model training with COMPLETE evaluation...")

# 1. Load the data
print("Loading data splits...")
try:
    X_train = pd.read_csv(os.path.join(SPLITS_DIR, 'X_train.csv')).squeeze("columns")
    y_train = pd.read_csv(os.path.join(SPLITS_DIR, 'y_train.csv')).squeeze("columns")
    X_test = pd.read_csv(os.path.join(SPLITS_DIR, 'X_test.csv')).squeeze("columns")
    y_test = pd.read_csv(os.path.join(SPLITS_DIR, 'y_test.csv')).squeeze("columns")
except FileNotFoundError:
    print(f"❌ ERROR: Data splits not found in '{SPLITS_DIR}'. Please run 'split_data.py' first.")
    exit()

# 2. Create a model pipeline
print("Building model pipeline...")
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', strip_accents='unicode')),
    ('xgb', xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss',
                               use_label_encoder=False, random_state=42, n_jobs=-1))
])

# 3. Train the model
print("Training the model... (This may take a few moments)")
pipeline.fit(X_train, y_train)
print("✅ Model training complete.")

# 4. Make predictions
print("Making predictions on the test set...")
start_time = time.time()
y_pred = pipeline.predict(X_test)
y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
end_time = time.time()

# 5. Evaluate the model's performance
print("\n--- 📊 Model Performance ---")

# METRIC 1: Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"1. Accuracy: {accuracy:.4f}")

# METRIC 2: F1 Score
f1 = f1_score(y_test, y_pred)
print(f"2. F1 Score: {f1:.4f}")

# METRIC 3: Recall
recall = recall_score(y_test, y_pred)
print(f"3. Recall:   {recall:.4f}")

# METRIC 4: ROC-AUC Score
roc_auc = roc_auc_score(y_test, y_pred_proba)
print(f"4. ROC-AUC:  {roc_auc:.4f}")

# METRIC 5: Latency
latency = end_time - start_time
print(f"5. Latency:  {latency:.4f} seconds for {len(X_test)} predictions")

print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred, target_names=['Safe (0)', 'Phishing (1)']))
print("--------------------------")

# 6. Save the pipeline and get model size
model_path = os.path.join(MODELS_DIR, MODEL_NAME)
joblib.dump(pipeline, model_path)
print(f"💾 Model pipeline saved to '{model_path}'")

# METRIC 6: Model Size
model_size_mb = os.path.getsize(model_path) / (1024 * 1024)
print(f"6. Model Size: {model_size_mb:.2f} MB")
