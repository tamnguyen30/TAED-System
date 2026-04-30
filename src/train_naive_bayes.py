import pandas as pd
import joblib
import os
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, recall_score, roc_auc_score, classification_report


SPLITS_DIR = 'data/splits'
MODELS_DIR = 'models'
MODEL_NAME = 'naive_bayes_pipeline.joblib'


print("🚀 Starting Naive Bayes model training with COMPLETE evaluation...")


print("Loading data splits...")
try:
    X_train = pd.read_csv(os.path.join(SPLITS_DIR, 'X_train.csv')).squeeze("columns")
    y_train = pd.read_csv(os.path.join(SPLITS_DIR, 'y_train.csv')).squeeze("columns")
    X_test = pd.read_csv(os.path.join(SPLITS_DIR, 'X_test.csv')).squeeze("columns")
    y_test = pd.read_csv(os.path.join(SPLITS_DIR, 'y_test.csv')).squeeze("columns")
except FileNotFoundError:
    print(f"❌ ERROR: Data splits not found in '{SPLITS_DIR}'. Please run 'split_data.py' first.")
    exit()


print("Building model pipeline...")
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', strip_accents='unicode')),
    ('nb', MultinomialNB())
])


print("Training the model...")
pipeline.fit(X_train, y_train)
print("✅ Model training complete.")


print("Making predictions on the test set...")
start_time = time.time()
y_pred = pipeline.predict(X_test)
y_pred_proba = pipeline.predict_proba(X_test)[:, 1] 
end_time = time.time()


print("\n--- 📊 Model Performance ---")


accuracy = accuracy_score(y_test, y_pred)
print(f"1. Accuracy: {accuracy:.4f}")


f1 = f1_score(y_test, y_pred)
print(f"2. F1 Score: {f1:.4f}")


recall = recall_score(y_test, y_pred)
print(f"3. Recall:   {recall:.4f}")


roc_auc = roc_auc_score(y_test, y_pred_proba)
print(f"4. ROC-AUC:  {roc_auc:.4f}")


latency = end_time - start_time
print(f"5. Latency:  {latency:.4f} seconds for {len(X_test)} predictions")

print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred, target_names=['Safe (0)', 'Phishing (1)']))
print("--------------------------")


model_path = os.path.join(MODELS_DIR, MODEL_NAME)
joblib.dump(pipeline, model_path)
print(f"💾 Model pipeline saved to '{model_path}'")


model_size_mb = os.path.getsize(model_path) / (1024 * 1024)
print(f"6. Model Size: {model_size_mb:.2f} MB")
