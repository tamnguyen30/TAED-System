import pandas as pd
import joblib
import os
import sys
from sklearn.metrics import classification_report, accuracy_score
import tensorflow as tf
from transformers import TFDistilBertForSequenceClassification, DistilBertTokenizer
from transformers import TFBertForSequenceClassification, BertTokenizer # For TinyBERT
from transformers import TFMobileBertForSequenceClassification, MobileBertTokenizer # For MobileBERT
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import math
import fasttext

# --- Configuration ---
# We will get these from the command line now.
BATCH_SIZE = 128 # Process in smaller batches to save memory
# --- End Configuration ---

def main(dataset_path, model_path, model_type):
    print(f"🚀 Starting evaluation on: {dataset_path}")
    print(f"   Using model: {model_path} (Type: {model_type})")
    
    # 1. Load the adversarial dataset
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        print(f"❌ ERROR: Adversarial dataset not found at '{dataset_path}'.")
        return
            
    X_adversarial = df['attacked_text'].fillna('').astype(str)
    y_true = df['original_label']
    
    # 2. Load the pre-trained model
    print(f"Loading model: {model_path}...")
    try:
        if model_type == 'sklearn':
            model = joblib.load(model_path)
        
        elif model_type == 'transformer':
            print(f"Loading DistilBERT tokenizer and model from {model_path}...")
            tokenizer = DistilBertTokenizer.from_pretrained(model_path)
            model = TFDistilBertForSequenceClassification.from_pretrained(model_path)
            original_tf_predict = model.predict 
            
            def new_predict_function(texts_series):
                texts_list = texts_series.tolist()
                all_preds = []
                num_batches = math.ceil(len(texts_list) / BATCH_SIZE)
                print(f"  Predicting with Transformer model in {num_batches} batches...")
                for i in range(num_batches):
                    batch_texts = texts_list[i*BATCH_SIZE : (i+1)*BATCH_SIZE]
                    encodings = tokenizer(batch_texts, truncation=True, padding=True, max_length=256, return_tensors="tf")
                    tf_dataset = tf.data.Dataset.from_tensor_slices(dict(encodings)).batch(BATCH_SIZE)
                    preds_output = original_tf_predict(tf_dataset) 
                    all_preds.append(preds_output.logits.argmax(axis=1))
                print("  Prediction complete.")
                return np.concatenate(all_preds)
            model.predict = new_predict_function

        elif model_type == 'tinybert':
            print(f"Loading TinyBERT tokenizer and model from {model_path}...")
            tokenizer = BertTokenizer.from_pretrained(model_path) # Use BertTokenizer
            model = TFBertForSequenceClassification.from_pretrained(model_path) # Use TFBert
            original_tf_predict = model.predict 
            
            def new_predict_function(texts_series):
                texts_list = texts_series.tolist()
                all_preds = []
                num_batches = math.ceil(len(texts_list) / BATCH_SIZE)
                print(f"  Predicting with TinyBERT model in {num_batches} batches...")
                for i in range(num_batches):
                    batch_texts = texts_list[i*BATCH_SIZE : (i+1)*BATCH_SIZE]
                    encodings = tokenizer(batch_texts, truncation=True, padding=True, max_length=256, return_tensors="tf")
                    tf_dataset = tf.data.Dataset.from_tensor_slices(dict(encodings)).batch(BATCH_SIZE)
                    preds_output = original_tf_predict(tf_dataset) 
                    all_preds.append(preds_output.logits.argmax(axis=1))
                print("  Prediction complete.")
                return np.concatenate(all_preds)
            model.predict = new_predict_function

        elif model_type == 'mobilebert':
            print(f"Loading MobileBERT tokenizer and model from {model_path}...")
            tokenizer = MobileBertTokenizer.from_pretrained(model_path) # Use MobileBertTokenizer
            model = TFMobileBertForSequenceClassification.from_pretrained(model_path) # Use TFMobileBert
            original_tf_predict = model.predict 
            
            def new_predict_function(texts_series):
                texts_list = texts_series.tolist()
                all_preds = []
                num_batches = math.ceil(len(texts_list) / BATCH_SIZE)
                print(f"  Predicting with MobileBERT model in {num_batches} batches...")
                for i in range(num_batches):
                    batch_texts = texts_list[i*BATCH_SIZE : (i+1)*BATCH_SIZE]
                    encodings = tokenizer(batch_texts, truncation=True, padding=True, max_length=256, return_tensors="tf")
                    tf_dataset = tf.data.Dataset.from_tensor_slices(dict(encodings)).batch(BATCH_SIZE)
                    preds_output = original_tf_predict(tf_dataset) 
                    all_preds.append(preds_output.logits.argmax(axis=1))
                print("  Prediction complete.")
                return np.concatenate(all_preds)
            model.predict = new_predict_function

        elif model_type == 'char_cnn':
            print(f"Loading Keras model from {model_path}...")
            model = load_model(model_path)
            print("  Loading and fitting Char-CNN tokenizer...")
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
            print(f"❌ ERROR: Model type '{model_type}' not recognized for loading.")
            return
    except FileNotFoundError:
        print(f"❌ ERROR: Model file not found at '{model_path}'.")
        return
    except Exception as e:
        print(f"❌ ERROR loading model: {e}")
        return

    # 3. Make predictions on the adversarial text
    print("Making predictions on attacked text...")
    try:
        y_pred = model.predict(X_adversarial)
    # --- THIS IS THE FIX ---
    except Exception as e:
        print(f"❌ ERROR during prediction: {e}")
        return
    # --- END FIX ---
    
    # 4. Evaluate performance
    print("\n--- 📊 Model Performance on Attacked Data ---")
    accuracy = accuracy_score(y_true, y_pred)
    print(f"Accuracy on Adversarial Data: {accuracy:.4f}\n")
    print("Classification Report (on Attacked Data):")
    print(classification_report(y_true, y_pred, target_names=['Safe (0)', 'Phishing (1)']))
    
    # 5. Calculate Attack Success Rate (ASR)
    print("\nCalculating Attack Success Rate (ASR) on phishing samples...")
    df_phishing = df[df['original_label'] == 1]
    y_true_phishing = df_phishing['original_label']
    y_pred_phishing = model.predict(df_phishing['attacked_text'].fillna('').astype(str))
    fooled_count = (y_pred_phishing == 0).sum()
    total_phishing_attacks = len(y_true_phishing)
    
    if total_phishing_attacks > 0:
        asr = fooled_count / total_phishing_attacks
        print("\n--- 🎯 Attack Success Rate (ASR) ---")
        print(f"Model was fooled (predicted 0 for a 1) on {fooled_count} out of {total_phishing_attacks} phishing attacks.")
        print(f"Attack Success Rate (ASR): {asr:.4f} (Higher is worse for the model)")
    else:
        print("\nNo true phishing emails (label 1) found in the dataset to calculate ASR.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("\n❌ ERROR: Incorrect number of arguments.")
        print("Usage: python3 evaluate_on_adversarial.py <path_to_dataset.csv> <path_to_model> <model_type>")
        print("Example: python3 evaluate_on_adversarial.py data/adversarial.csv models/svm.joblib sklearn")
        sys.exit(1)
        
    dataset_path_arg = sys.argv[1]
    model_path_arg = sys.argv[2]
    model_type_arg = sys.argv[3]
    
    main(dataset_path_arg, model_path_arg, model_type_arg)
