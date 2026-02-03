import pandas as pd
import fasttext
import os
import time
from sklearn.metrics import accuracy_score, f1_score, recall_score, roc_auc_score, classification_report

# --- Configuration ---
DATA_DIR = 'data'
MODELS_DIR = 'models'
MODEL_NAME = 'fasttext_model.bin'
# --- End Configuration ---

print("🚀 Starting FastText model training with COMPLETE evaluation...")

# 1. Train the FastText model
print("Training the model...")
try:
    # Train the classifier using the prepared training data
    model = fasttext.train_supervised(input=os.path.join(DATA_DIR, 'fasttext_train.txt'), epoch=25, lr=1.0, wordNgrams=2)
    print("✅ Model training complete.")
except Exception as e:
    print(f"❌ ERROR during training: {e}")
    print("Please make sure you have run 'prepare_fasttext_data.py' first.")
    exit()

# 2. Load test data for evaluation
print("Loading test data for detailed evaluation...")
X_test = pd.read_csv(os.path.join(DATA_DIR, 'splits', 'X_test.csv')).squeeze("columns").astype(str)
y_test = pd.read_csv(os.path.join(DATA_DIR, 'splits', 'y_test.csv')).squeeze("columns")


# 3. Make predictions
print("Making predictions on the test set...")
start_time = time.time()
# The predict method needs a list of texts
# NEW, corrected lines
# Clean the text to remove newlines and carriage returns that FastText can't handle
texts_to_predict = [text.replace('\n', ' ').replace('\r', ' ') for text in X_test.tolist()]
labels_raw, probas_raw = model.predict(texts_to_predict)
end_time = time.time()

# Process predictions to get them into a usable format
y_pred = [int(label[0].replace('__label__', '')) for label in labels_raw]
y_pred_proba = [proba[0] for proba in probas_raw]


# 4. Evaluate the model's performance
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


# 5. Save the pipeline and get model size
model_path = os.path.join(MODELS_DIR, MODEL_NAME)
model.save_model(model_path)
print(f"💾 Model saved to '{model_path}'")

# METRIC 6: Model Size
model_size_mb = os.path.getsize(model_path) / (1024 * 1024)
print(f"6. Model Size: {model_size_mb:.2f} MB")
