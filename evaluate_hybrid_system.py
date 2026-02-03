import pandas as pd
import joblib
import numpy as np
import lime
import lime.lime_text
import tensorflow as tf
from transformers import TFDistilBertForSequenceClassification, DistilBertTokenizer
from sklearn.metrics import accuracy_score, confusion_matrix
import tqdm
import sys
import argparse

# --- Configuration ---
# Default paths (can be overridden by command line args)
DEFAULT_DATA_PATH = 'data/adversarial_benchmark_dataset.csv'
RF_MODEL_PATH = 'models/random_forest_pipeline.joblib'
BERT_MODEL_PATH = 'models/distilbert_phishing_model'

ALPHA = 0.4 
BETA = 0.3  
GAMMA = 0.3 
TRUST_THRESHOLD = 0.5 

PHISHING_INDICATORS = {
    "urgent", "immediate", "verify", "account", "suspended", "bank", "invoice",
    "click", "link", "password", "update", "security", "unauthorized", "locked",
    "confirm", "action", "required", "pay", "billing", "service", "notice", "alert",
    "winner", "won", "prize", "gift", "reward", "transfer", "wire", "routing"
}

# Logic Engine Keywords
URGENCY_TERMS = ["immediately", "urgent", "24 hours", "suspended", "lockout", "restricted", "unauthorized", "at risk", "terminate", "warning", "asap"]
GREED_TERMS = ["winner", "congratulations", "won", "prize", "gift card", "reward", "lottery", "claim your", "$"]
ACTION_TERMS = ["click here", "login", "sign in", "verify", "update", "confirm", "secure your", "visit our", "portal", "claim", "link"]
SECRECY_TERMS = ["discreet", "confidential", "can't talk", "conference call", "meeting", "personal cell", "personal number", "do not email", "private"]
FINANCIAL_TERMS = ["financial matter", "transfer", "wire", "bank", "expense", "payment", "process", "gift card", "funds", "invoice"]
# --- End Configuration ---

def get_explanation_features(text, explainer, pipeline):
    try:
        # Limit to 3 features to speed up LIME for bulk testing
        exp = explainer.explain_instance(text, pipeline.predict_proba, num_features=3)
        return [x[0] for x in exp.as_list()]
    except:
        return []

def scan_for_semantic_threats(text):
    """The 'Explanation Verifier' logic."""
    if not isinstance(text, str):
        return False
    text_lower = text.lower()
    
    has_urgency = any(t in text_lower for t in URGENCY_TERMS)
    has_greed = any(t in text_lower for t in GREED_TERMS)
    has_action = any(t in text_lower for t in ACTION_TERMS)
    has_secrecy = any(t in text_lower for t in SECRECY_TERMS)
    has_financial = any(t in text_lower for t in FINANCIAL_TERMS)
    
    # Rule 1 & 2: Urgency/Greed + Action
    if has_action and (has_urgency or has_greed): return True
    # Rule 3: CEO Fraud (Secrecy + Financial/Response)
    if has_secrecy and (has_financial or "reply" in text_lower): return True
    
    return False

def main():
    # Parse Command Line Arguments
    parser = argparse.ArgumentParser(description='Evaluate TAED Hybrid System')
    parser.add_argument('--data', type=str, default=DEFAULT_DATA_PATH, help='Path to the CSV dataset')
    args = parser.parse_args()
    
    dataset_path = args.data
    print(f"🚀 Starting Hybrid System Evaluation on: {dataset_path}")
    
    # 1. Load Data
    try:
        df = pd.read_csv(dataset_path)
        
        # --- SAMPLING OPTIMIZATION DISABLED ---
        # The limit is commented out for full evaluation
        # if len(df) > 200:
        #    print("   ⚠️ Sampling 200 emails for rapid evaluation...")
        #    df = df.sample(200, random_state=42)
        # --------------------------------------
        
    except FileNotFoundError:
        print(f"❌ Dataset not found at {dataset_path}")
        return

    X_adversarial = df['attacked_text'].fillna('').astype(str).tolist()
    y_true = df['original_label'].tolist()
    
    # 2. Load Models
    print("   Loading Models (RF + DistilBERT)...")
    try:
        rf_model = joblib.load(RF_MODEL_PATH)
        bert_tokenizer = DistilBertTokenizer.from_pretrained(BERT_MODEL_PATH)
        bert_model = TFDistilBertForSequenceClassification.from_pretrained(BERT_MODEL_PATH)
        explainer = lime.lime_text.LimeTextExplainer(class_names=['Safe', 'Phishing'])
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return

    def bert_predict_single(text):
        encodings = bert_tokenizer([text], truncation=True, padding=True, max_length=256, return_tensors="tf")
        preds = bert_model.predict(dict(encodings), verbose=0)
        prob = tf.nn.softmax(preds.logits, axis=1).numpy()[0][1]
        return 1 if prob > 0.5 else 0

    y_pred_hybrid = []
    escalation_count = 0
    override_count = 0

    print(f"   Processing {len(X_adversarial)} emails... (This may take time)")
    
    for text in tqdm.tqdm(X_adversarial):
        # --- STEP 1: Fast Scan ---
        rf_probs = rf_model.predict_proba([text])[0]
        rf_pred = np.argmax(rf_probs)
        confidence = rf_probs[rf_pred]
        
        # --- STEP 2: Trust Calculation ---
        features = get_explanation_features(text, explainer, rf_model)
        intersection = [w for w in features if w.lower() in PHISHING_INDICATORS]
        fidelity = len(intersection) / len(features) if features else 0.0
        
        # For bulk eval, we assume instability is average (0.5) to save compute time
        trust_score = (ALPHA * confidence) + (BETA * fidelity) - (GAMMA * 0.5)
        trust_score = max(0.0, min(1.0, trust_score))
        
        final_pred = rf_pred
        
        # --- STEP 3: Hybrid Decision Logic ---
        if trust_score < TRUST_THRESHOLD:
            escalation_count += 1
            # Escalate to Deep Scan
            bert_pred = bert_predict_single(text)
            final_pred = bert_pred
            
            # Apply Semantic Logic Override
            if scan_for_semantic_threats(text):
                final_pred = 1 # Force Phishing
                if bert_pred == 0: 
                    override_count += 1
        
        y_pred_hybrid.append(final_pred)

    # --- Results Calculation ---
    accuracy = accuracy_score(y_true, y_pred_hybrid)
    print(f"\n✅ Hybrid System Accuracy: {accuracy:.4f}")
    
    # Calculate ASR (Attack Success Rate)
    df['hybrid_pred'] = y_pred_hybrid
    df_phishing = df[df['original_label'] == 1]
    
    if len(df_phishing) > 0:
        fooled_count = (df_phishing['hybrid_pred'] == 0).sum()
        total_phishing = len(df_phishing)
        asr = fooled_count / total_phishing
        
        print(f"\n--- 🎯 Hybrid Benchmark Results ---\n")
        print(f"Total Emails Tested: {len(df)}")
        print(f"Escalations to AI:   {escalation_count}")
        print(f"Logic Overrides:     {override_count}")
        print("-" * 40)
        print(f"Hybrid ASR: {asr:.4f} ({asr*100:.2f}%)")
        print("-" * 40)
    else:
        print("\nNo phishing samples in this batch.")

    # --- CONFUSION MATRIX FOR PLOTTING ---
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred_hybrid).ravel()
    print(f"\n--- 📊 Confusion Matrix for Plotting ---")
    print(f"TN: {tn}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print(f"TP: {tp}")

if __name__ == "__main__":
    main()
