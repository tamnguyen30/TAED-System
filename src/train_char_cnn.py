import pandas as pd
import os
import time
import numpy as np


import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout

from sklearn.metrics import accuracy_score, f1_score, recall_score, roc_auc_score, classification_report


SPLITS_DIR = 'data/splits'
MODELS_DIR = 'models'
MODEL_NAME = 'char_cnn_model.h5'


MAX_LEN = 1024
EMBEDDING_DIM = 64


print("🚀 Starting Character-CNN model training with COMPLETE evaluation...")


print("Loading data splits...")
try:
    X_train_text = pd.read_csv(os.path.join(SPLITS_DIR, 'X_train.csv')).squeeze("columns").astype(str)
    y_train = pd.read_csv(os.path.join(SPLITS_DIR, 'y_train.csv')).squeeze("columns")
    X_test_text = pd.read_csv(os.path.join(SPLITS_DIR, 'X_test.csv')).squeeze("columns").astype(str)
    y_test = pd.read_csv(os.path.join(SPLITS_DIR, 'y_test.csv')).squeeze("columns")
except FileNotFoundError:
    print(f"❌ ERROR: Data splits not found in '{SPLITS_DIR}'. Please run 'split_data.py' first.")
    exit()


print("Tokenizing text at the character level...")
tokenizer = Tokenizer(char_level=True, oov_token='<UNK>')
tokenizer.fit_on_texts(X_train_text)

X_train_seq = tokenizer.texts_to_sequences(X_train_text)
X_test_seq = tokenizer.texts_to_sequences(X_test_text)


print(f"Padding sequences to a max length of {MAX_LEN} characters...")
X_train = pad_sequences(X_train_seq, maxlen=MAX_LEN, padding='post', truncating='post')
X_test = pad_sequences(X_test_seq, maxlen=MAX_LEN, padding='post', truncating='post')


print("Building the Char-CNN model...")
model = Sequential([
    Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=EMBEDDING_DIM, input_length=MAX_LEN),
    Conv1D(128, 5, activation='relu'),
    GlobalMaxPooling1D(),
    Dense(64, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()


print("\nTraining the model... (This will take several minutes)")
model.fit(X_train, y_train, epochs=3, batch_size=128, validation_split=0.1, verbose=2)
print("✅ Model training complete.")


print("Making predictions on the test set...")
start_time = time.time()
y_pred_proba = model.predict(X_test).flatten()
y_pred = np.round(y_pred_proba)
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
model.save(model_path)
print(f"💾 Model saved to '{model_path}'")


model_size_mb = os.path.getsize(model_path) / (1024 * 1024)
print(f"6. Model Size: {model_size_mb:.2f} MB")
