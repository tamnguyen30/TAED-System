import pandas as pd
import joblib
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix
import tqdm
import re

# Configuration - matching hybrid_defense.py exactly
RF_MODEL_PATH = 'models/random_forest_pipeline.joblib'
ALPHA = 0.35
BETA = 0.40
GAMMA = 0.25
TRUST_THRESHOLD = 0.50

PHISHING_EVIDENCE = {
    'urgency': ['urgent', 'immediately', 'asap', 'limited time', 'expires', 'act now'],
    'threats': ['suspend', 'lock', 'frozen', 'terminate', 'close', 'restricted'],
    'verification': ['verify', 'confirm', 'validate', 'authenticate', 'update'],
    'financial': ['payment', 'refund', 'wire', 'bitcoin', 'gift card', 'transfer'],
    'credentials': ['password', 'username', 'login', 'credential', 'ssn'],
    'rewards': ['winner', 'prize', 'reward', 'claim', 'congratulations'],
    'authority': ['irs', 'fbi', 'bank', 'paypal', 'amazon', 'microsoft']
}

REFERENCE_FEATURES = [
    'verify', 'urgent', 'suspend', 'click', 'password', 'account',
    'update', 'confirm', 'security', 'unusual', 'locked', 'expires'
]

HOMOGLYPHS = {
    '@': 'a', '1': 'i', '0': 'o', '3': 'e', '$': 's', '!': 'i',
    '5': 's', '7': 't', '4': 'a'
}

TRUSTED_DOMAINS = ['google.com', 'microsoft.com', 'apple.com', 'amazon.com', 
                   'github.com', 'linkedin.com', 'paypal.com']

BRAND_TARGETS = ['paypal', 'amazon', 'netflix', 'microsoft', 'apple', 
                 'google', 'facebook', 'chase']

def normalize_text(text):
    text = text.lower()
    for char, replacement in HOMOGLYPHS.items():
        text = text.replace(char, replacement)
    return re.sub(r'\s+', ' ', text).strip()

def extract_urls(text):
    urls = re.findall(r'https?://\S+', text)
    urls.extend(re.findall(r'www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', text))
    return urls

def check_typosquatting(domain):
    domain_lower = domain.lower()
    for brand in BRAND_TARGETS:
        if brand in domain_lower:
            if not any(trusted in domain_lower for trusted in TRUSTED_DOMAINS):
                return True
    return False

def calculate_fidelity(text, prediction):
    normalized = normalize_text(text)
    
    # Check URLs
    urls = extract_urls(text)
    typosquat = False
    shortened = False
    for url in urls:
        if any(s in url.lower() for s in ['bit.ly', 'tinyurl', 'goo.gl']):
            shortened = True
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url if url.startswith('http') else f'http://{url}')
            domain = parsed.netloc or parsed.path.split('/')[0]
            if check_typosquatting(domain):
                typosquat = True
        except:
            pass
    
    if typosquat:
        return 0.10
    
    # Check trusted domain override
    for domain in TRUSTED_DOMAINS:
        if domain in normalized and prediction == 0:
            return 0.95
    
    # Calculate evidence tokens
    evidence_tokens = set()
    for category, keywords in PHISHING_EVIDENCE.items():
        for kw in keywords:
            if kw in normalized:
                evidence_tokens.add(category)
    
    ref_tokens = set(REFERENCE_FEATURES)
    found_ref = sum(1 for t in ref_tokens if t in normalized)
    
    if not evidence_tokens and found_ref == 0:
        jaccard = 0.0
    else:
        all_tokens = evidence_tokens | ref_tokens
        common = sum(1 for t in ref_tokens if t in normalized)
        jaccard = common / len(ref_tokens) if ref_tokens else 0.0
    
    # Verification score
    ver_score = 1.0
    if found_ref < 2:
        ver_score -= 0.2
    
    fidelity = (jaccard * 0.6) + (ver_score * 0.4)
    
    if prediction == 0:
        fidelity = 1.0 - fidelity
    
    return fidelity

def generate_perturbations(text):
    variants = []
    v1 = text
    for char, replacement in HOMOGLYPHS.items():
        if replacement in v1:
            v1 = v1.replace(replacement, char)
    variants.append(v1)
    words = text.split()
    if len(words) > 2:
        v2 = words.copy()
        v2[0], v2[1] = v2[1], v2[0]
        variants.append(' '.join(v2))
    chars = list(text)
    if len(chars) > 5:
        chars[2], chars[3] = chars[3], chars[2]
    variants.append(''.join(chars))
    return variants

def calculate_instability(text, rf_model):
    try:
        base_conf = rf_model.predict_proba([text])[0][1]
        perturbations = generate_perturbations(text)
        var_scores = []
        for p in perturbations:
            p_conf = rf_model.predict_proba([p])[0][1]
            var_scores.append(abs(base_conf - p_conf))
        return float(np.mean(var_scores)) if var_scores else 0.0
    except:
        return 0.05

def main():
    print("Loading dataset...")
    import sys
    data_path = sys.argv[1] if len(sys.argv) > 1 else 'data/adversarial/adversarial_benchmark_dataset_ccs_clean.csv'
    df = pd.read_csv(data_path)
    X = df['attacked_text'].fillna('').astype(str).tolist()
    y_true = df['original_label'].tolist()
    
    print("Loading RF model...")
    rf_model = joblib.load(RF_MODEL_PATH)
    
    y_pred = []
    escalation_count = 0
    
    print(f"Evaluating {len(X)} emails...")
    for text in tqdm.tqdm(X):
        # Stage 1: RF prediction
        rf_probs = rf_model.predict_proba([text])[0]
        rf_pred = int(np.argmax(rf_probs))
        confidence = float(rf_probs[rf_pred])
        C = confidence if rf_pred == 1 else (1.0 - confidence)
        
        # Stage 2: Trust score
        F = calculate_fidelity(text, rf_pred)
        I = calculate_instability(text, rf_model)
        
        ts = (ALPHA * C) + (BETA * F) - (GAMMA * I)
        ts = max(0.0, min(1.0, ts))
        
        if ts < TRUST_THRESHOLD:
            escalation_count += 1
            # For bulk eval use RF pred with logic override
            from urllib.parse import urlparse
            urls = extract_urls(text)
            normalized = normalize_text(text)
            has_threat = any(kw in normalized for kw in 
                           ['verify', 'suspend', 'password', 'urgent', 'click', 'confirm'])
            if has_threat:
                final_pred = 1
            else:
                final_pred = rf_pred
        else:
            final_pred = rf_pred
        
        y_pred.append(final_pred)
    
    accuracy = accuracy_score(y_true, y_pred)
    
    df['hybrid_pred'] = y_pred
    df_phishing = df[df['original_label'] == 1]
    fooled_count = (df_phishing['hybrid_pred'] == 0).sum()
    total_phishing = len(df_phishing)
    asr = fooled_count / total_phishing
    
    print(f"\n=== TAED Hybrid Results ===")
    print(f"Total emails: {len(df)}")
    print(f"Escalations: {escalation_count}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"ASR: {asr:.4f} ({asr*100:.2f}%)")
    
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    print(f"\nConfusion Matrix:")
    print(f"TN: {tn}, FP: {fp}, FN: {fn}, TP: {tp}")

if __name__ == "__main__":
    main()