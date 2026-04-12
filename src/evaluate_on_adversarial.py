import pandas as pd
import joblib
import os
import sys
import json
import math
import numpy as np
import fasttext
import tensorflow as tf
from sklearn.metrics import classification_report, accuracy_score
from transformers import TFDistilBertForSequenceClassification, DistilBertTokenizer
from transformers import TFBertForSequenceClassification, BertTokenizer
from transformers import TFMobileBertForSequenceClassification, MobileBertTokenizer
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

BATCH_SIZE = 128

def make_transformer_predict(model, tokenizer):
    original_predict = model.predict
    def new_predict_function(texts_series):
        texts_list = texts_series.tolist()
        all_preds = []
        num_batches = math.ceil(len(texts_list) / BATCH_SIZE)
        print(f"  Predicting with Transformer model in {num_batches} batches...")
        for i in range(num_batches):
            batch_texts = texts_list[i*BATCH_SIZE : (i+1)*BATCH_SIZE]
            encodings = tokenizer(batch_texts, truncation=True, padding=True, max_length=256, return_tensors="tf")
            tf_dataset = tf.data.Dataset.from_tensor_slices(dict(encodings)).batch(BATCH_SIZE)
            preds_output = original_predict(tf_dataset)
            all_preds.append(preds_output.logits.argmax(axis=1))
        print("  Prediction complete.")
        return np.concatenate(all_preds)
    return new_predict_function

def main(dataset_path, model_path, model_type):
    print(f"Starting evaluation on: {dataset_path}")
    print(f"Using model: {model_path} (Type: {model_type})")

    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        print(f"ERROR: Adversarial dataset not found at '{dataset_path}'.")
        return

    X_adversarial = df['attacked_text'].fillna('').astype(str)
    y_true = df['original_label']

    print(f"Loading model: {model_path}...")
    try:
        if model_type == 'sklearn':
            model = joblib.load(model_path)

        elif model_type == 'transformer':
            with open(f"{model_path}/tokenizer_config.json") as f:
                tok_config = json.load(f)
            tokenizer_class = tok_config.get("tokenizer_class", "DistilBertTokenizer")
            print(f"Detected tokenizer: {tokenizer_class}")

            if tokenizer_class == "MobileBertTokenizer":
                tokenizer = MobileBertTokenizer.from_pretrained(model_path)
                model = TFMobileBertForSequenceClassification.from_pretrained(model_path)
            elif tokenizer_class == "BertTokenizer":
                tokenizer = BertTokenizer.from_pretrained(model_path)
                model = TFBertForSequenceClassification.from_pretrained(model_path)
            else:
                tokenizer = DistilBertTokenizer.from_pretrained(model_path)
                model = TFDistilBertForSequenceClassification.from_pretrained(model_path)

            model.predict = make_transformer_predict(model, tokenizer)

        elif model_type == 'char_cnn':
            print(f"Loading Keras model from {model_path}...")
            model = load_model(model_path)
            X_train_text = pd.read_csv('data/splits/X_train.csv').squeeze("columns").astype(str)
            tokenizer = Tokenizer(char_level=True, oov_token='<UNK>')
            tokenizer.fit_on_texts(X_train_text)
            original_keras_predict = model.predict
            def char_cnn_predict(texts_series):
                texts_list = [str(text) for text in texts_series.tolist()]
                all_preds = []
                num_batches = math.ceil(len(texts_list) / BATCH_SIZE)
                print(f"  Predicting with Char-CNN model in {num_batches} batches...")
                for i in range(num_batches):
                    batch_texts = texts_list[i*BATCH_SIZE : (i+1)*BATCH_SIZE]
                    sequences = tokenizer.texts_to_sequences(batch_texts)
                    padded_data = pad_sequences(sequences, maxlen=1024, padding='post', truncating='post')
                    preds_proba = original_keras_predict(padded_data, batch_size=BATCH_SIZE).flatten()
                    all_preds.append((preds_proba > 0.5).astype(int))
                print("  Prediction complete.")
                return np.concatenate(all_preds)
            model.predict = char_cnn_predict

        elif model_type == 'fasttext':
            print(f"Loading FastText model from {model_path}...")
            model = fasttext.load_model(model_path)
            original_fasttext_predict = model.predict
            def new_predict_function(texts_series):
                texts_list = [str(text).replace('\n', ' ') for text in texts_series.tolist()]
                print("  Predicting with FastText model...")
                labels_raw, _ = original_fasttext_predict(texts_list)
                preds = [int(label[0].replace('__label__', '')) for label in labels_raw]
                print("  Prediction complete.")
                return np.array(preds)
            model.predict = new_predict_function

        else:
            print(f"ERROR: Model type '{model_type}' not recognized.")
            return

    except FileNotFoundError:
        print(f"ERROR: Model file not found at '{model_path}'.")
        return
    except Exception as e:
        print(f"ERROR loading model: {e}")
        return

    print("Making predictions on attacked text...")
    try:
        y_pred = model.predict(X_adversarial)
    except Exception as e:
        print(f"ERROR during prediction: {e}")
        return

    print("\n--- Model Performance on Attacked Data ---")
    accuracy = accuracy_score(y_true, y_pred)
    print(f"Accuracy on Adversarial Data: {accuracy:.4f}\n")
    print("Classification Report (on Attacked Data):")
    print(classification_report(y_true, y_pred, target_names=['Safe (0)', 'Phishing (1)']))

    print("\nCalculating Attack Success Rate (ASR) on phishing samples...")
    df_phishing = df[df['original_label'] == 1]
    y_true_phishing = df_phishing['original_label']
    y_pred_phishing = model.predict(df_phishing['attacked_text'].fillna('').astype(str))
    fooled_count = (y_pred_phishing == 0).sum()
    total_phishing_attacks = len(y_true_phishing)

    if total_phishing_attacks > 0:
        asr = fooled_count / total_phishing_attacks
        print("\n--- Attack Success Rate (ASR) ---")
        print(f"Model was fooled on {fooled_count} out of {total_phishing_attacks} phishing attacks.")
        print(f"Attack Success Rate (ASR): {asr:.4f} (Higher is worse for the model)")
    else:
        print("No phishing emails found to calculate ASR.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 evaluate_on_adversarial.py <dataset.csv> <model_path> <model_type>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])