import pandas as pd
import os
import time
import numpy as np
import tensorflow as tf
from transformers import MobileBertTokenizer, TFMobileBertForSequenceClassification
from sklearn.metrics import accuracy_score, f1_score, recall_score, roc_auc_score, classification_report

# --- Configuration ---
SPLITS_DIR = 'data/splits'
MODELS_DIR = 'models' # Note: We deleted this folder, a new one will be created.
MODEL_NAME = 'mobilebert_phishing_model'

# Model Hyperparameters
MODEL_CHECKPOINT = 'google/mobilebert-uncased'
MAX_LEN = 256
BATCH_SIZE = 16
EPOCHS = 1
# --- End Configuration ---

print(f"🚀 Fine-tuning MobileBERT model...")

# Create models directory if it doesn't exist
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

# 1. Load the data
print("Loading data splits...")
X_train_text = pd.read_csv(os.path.join(SPLITS_DIR, 'X_train.csv')).squeeze("columns").astype(str).tolist()
y_train = pd.read_csv(os.path.join(SPLITS_DIR, 'y_train.csv')).squeeze("columns").tolist()
X_test_text = pd.read_csv(os.path.join(SPLITS_DIR, 'X_test.csv')).squeeze("columns").astype(str).tolist()
y_test = pd.read_csv(os.path.join(SPLITS_DIR, 'y_test.csv')).squeeze("columns").tolist()

# 2. Tokenize the text
print(f"Tokenizing text for '{MODEL_CHECKPOINT}'...")
tokenizer = MobileBertTokenizer.from_pretrained(MODEL_CHECKPOINT)
train_encodings = tokenizer(X_train_text, truncation=True, padding=True, max_length=MAX_LEN)
test_encodings = tokenizer(X_test_text, truncation=True, padding=True, max_length=MAX_LEN)

# 3. Create TensorFlow datasets
print("Creating TensorFlow datasets...")
train_dataset = tf.data.Dataset.from_tensor_slices((dict(train_encodings), y_train)).shuffle(len(y_train)).batch(BATCH_SIZE)
test_dataset = tf.data.Dataset.from_tensor_slices((dict(test_encodings), y_test)).batch(BATCH_SIZE)

# 4. Load pre-trained model and compile
print("Loading pre-trained MobileBERT model...")
# This should now work because you upgraded the 'torch' library
model = TFMobileBertForSequenceClassification.from_pretrained(MODEL_CHECKPOINT, num_labels=2, from_pt=True)
optimizer = tf.keras.optimizers.Adam(learning_rate=5e-5)
model.compile(optimizer=optimizer, loss=model.hf_compute_loss, metrics=['accuracy'])

# 5. Fine-tune the model
print(f"\nFine-tuning the model for {EPOCHS} epoch(s)...")
model.fit(train_dataset, epochs=EPOCHS, validation_data=test_dataset)
print("✅ Model fine-tuning complete.")

# 6. Make predictions
print("Making predictions on the test set...")
start_time = time.time()
preds_output = model.predict(test_dataset)
y_pred_logits = preds_output.logits
y_pred_proba = tf.nn.softmax(y_pred_logits, axis=1).numpy()[:, 1]
y_pred = np.argmax(y_pred_logits, axis=1)
end_time = time.time()

# 7. Evaluate the model's performance
print("\n--- 📊 Model Performance ---")
accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)
latency = end_time - start_time
model_path = os.path.join(MODELS_DIR, MODEL_NAME)
model.save_pretrained(model_path)
tokenizer.save_pretrained(model_path)
total_size = sum(os.path.getsize(os.path.join(dirpath, f)) for dirpath, _, filenames in os.walk(model_path) for f in filenames)
model_size_mb = total_size / (1024 * 1024)

print(f"1. Accuracy: {accuracy:.4f}")
print(f"2. F1 Score: {f1:.4f}")
print(f"3. Recall:   {recall:.4f}")
print(f"4. ROC-AUC:  {roc_auc:.4f}")
print(f"5. Latency:  {latency:.4f} seconds for {len(X_test_text)} predictions")
print(f"6. Model Size: {model_size_mb:.2f} MB")

print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred, target_names=['Safe (0)', 'Phishing (1)']))
print(f"💾 Model saved to directory '{model_path}'")
