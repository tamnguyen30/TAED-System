import pandas as pd
import joblib
import numpy as np
from sklearn.metrics import accuracy_score
import tqdm
import re
import random


RF_MODEL_PATH = 'models/random_forest_pipeline.joblib'
DATASET_PATH = 'data/adversarial/adversarial_benchmark_dataset_ccs_clean.csv'
OUTPUT_PATH = 'results/adaptive_adversarial_results.txt'

ALPHA = 0.35
BETA = 0.40
GAMMA = 0.25
TRUST_THRESHOLD = 0.50


THREAT_KEYWORDS = [
    'verify', 'urgent', 'suspend', 'click', 'password', 'account',
    'update', 'confirm', 'security', 'unusual', 'locked', 'expires',
    'immediately', 'action', 'required', 'credential', 'login',
    'authenticate', 'validate', 'restricted', 'unauthorized'
]


TRUSTED_DOMAINS = [
    'amazon.com', 'google.com', 'microsoft.com', 'apple.com',
    'paypal.com', 'netflix.com', 'github.com'
]

HOMOGLYPHS = {
    'a': '@', 'i': '1', 'o': '0', 'e': '3', 's': '$',
    't': '7', 'l': '1', 'g': '9'
}




def attack_keyword_stuffing(text):
    """
    Attacker injects threat keywords at end of email to inflate fidelity.
    Keywords are hidden using zero-width spaces between characters.
    """
    
    stuffed = random.sample(THREAT_KEYWORDS, min(5, len(THREAT_KEYWORDS)))
    injection = ' ' + ' '.join(stuffed) + ' '
    
    hidden = '\u200b'.join(injection)
    return text + hidden


def attack_trusted_domain_injection(text):
    """
    Attacker injects a trusted domain reference to trigger
    TAED's trusted domain override (F=0.95).
    Example: adds 'Secured by google.com' at bottom.
    """
    trusted = random.choice(TRUSTED_DOMAINS)
    injection = f"\n\nSecured by {trusted} | Verified sender"
    return text + injection


def attack_stability_optimization(text):
    """
    Attacker makes email MORE stable by removing unusual characters
    and normalizing text — reduces instability score.
    This makes TAED think the email is trustworthy.
    """
    
    cleaned = re.sub(r'[^\x00-\x7F]+', '', text)  
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    for replacement, original in HOMOGLYPHS.items():
        cleaned = cleaned.replace(original, replacement)
    return cleaned


def attack_combined(text):
    """
    Combined attack: stability optimization + keyword stuffing
    This is the strongest adaptive attack.
    """
    text = attack_stability_optimization(text)
    text = attack_keyword_stuffing(text)
    return text


def attack_domain_plus_stability(text):
    """
    Trusted domain injection + stability optimization.
    Tries to get F=0.95 override while also reducing I.
    """
    text = attack_stability_optimization(text)
    text = attack_trusted_domain_injection(text)
    return text




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


def normalize_text(text):
    text = text.lower()
    for char, replacement in HOMOGLYPHS.items():
        text = text.replace(replacement, char)
    return re.sub(r'\s+', ' ', text).strip()


def extract_urls(text):
    urls = re.findall(r'https?://\S+', text)
    urls.extend(re.findall(r'www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', text))
    return urls


def calculate_fidelity(text, prediction):
    normalized = normalize_text(text)
    urls = extract_urls(text)

    
    for domain in TRUSTED_DOMAINS:
        if domain in normalized and prediction == 0:
            return 0.95

    evidence_tokens = set()
    for category, keywords in PHISHING_EVIDENCE.items():
        for kw in keywords:
            if kw in normalized:
                evidence_tokens.add(category)

    found_ref = sum(1 for t in REFERENCE_FEATURES if t in normalized)
    jaccard = found_ref / len(REFERENCE_FEATURES) if REFERENCE_FEATURES else 0.0
    ver_score = 1.0 if found_ref >= 2 else 0.8
    fidelity = (jaccard * 0.6) + (ver_score * 0.4)

    if prediction == 0:
        fidelity = 1.0 - fidelity

    return fidelity


def generate_perturbations(text):
    variants = []
    v1 = text
    for char, replacement in HOMOGLYPHS.items():
        if char in v1:
            v1 = v1.replace(char, replacement)
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


def compute_trust_score(text, rf_model):
    rf_probs = rf_model.predict_proba([text])[0]
    rf_pred = int(np.argmax(rf_probs))
    confidence = float(rf_probs[rf_pred])
    C = confidence if rf_pred == 1 else (1.0 - confidence)
    F = calculate_fidelity(text, rf_pred)
    I = calculate_instability(text, rf_model)
    ts = (ALPHA * C) + (BETA * F) - (GAMMA * I)
    ts = max(0.0, min(1.0, ts))
    return rf_pred, ts, C, F, I


def taed_predict(text, rf_model):
    rf_pred, ts, C, F, I = compute_trust_score(text, rf_model)
    if ts >= TRUST_THRESHOLD:
        return rf_pred, ts
    
    normalized = normalize_text(text)
    has_threat = any(kw in normalized for kw in
                     ['verify', 'suspend', 'password', 'urgent', 'click', 'confirm'])
    return (1 if has_threat else rf_pred), ts




def evaluate_attack(df, rf_model, attack_fn, attack_name):
    y_true = df['original_label'].tolist()
    texts = df['attacked_text'].fillna('').astype(str).tolist()

    y_pred = []
    trust_scores = []

    for text in texts:
        
        adapted_text = attack_fn(text)
        pred, ts = taed_predict(adapted_text, rf_model)
        y_pred.append(pred)
        trust_scores.append(ts)

    
    phishing_idx = [i for i, y in enumerate(y_true) if y == 1]
    fooled = sum(1 for i in phishing_idx if y_pred[i] == 0)
    asr = fooled / len(phishing_idx) if phishing_idx else 0

    acc = accuracy_score(y_true, y_pred)
    mean_ts = np.mean(trust_scores)

    return {
        'attack': attack_name,
        'accuracy': acc,
        'asr': asr,
        'mean_trust_score': mean_ts,
        'fooled': fooled,
        'total_phishing': len(phishing_idx)
    }


def main():
    print("Loading dataset and model...")
    df = pd.read_csv(DATASET_PATH)
    rf_model = joblib.load(RF_MODEL_PATH)

    
    df_sample = df.sample(n=min(2000, len(df)), random_state=42)
    print(f"Evaluating on {len(df_sample)} samples...")

    attacks = [
        (lambda x: x, "Baseline (no adaptive attack)"),
        (attack_keyword_stuffing, "Keyword Stuffing"),
        (attack_trusted_domain_injection, "Trusted Domain Injection"),
        (attack_stability_optimization, "Stability Optimization"),
        (attack_combined, "Combined (Stability + Keyword Stuffing)"),
        (attack_domain_plus_stability, "Domain + Stability"),
    ]

    results = []
    for attack_fn, attack_name in attacks:
        print(f"Running: {attack_name}...")
        result = evaluate_attack(df_sample, rf_model, attack_fn, attack_name)
        results.append(result)
        print(f"  ASR: {result['asr']:.4f} | Acc: {result['accuracy']:.4f} | Mean TS: {result['mean_trust_score']:.4f}")

    
    output = []
    output.append("=" * 60)
    output.append("ADAPTIVE ADVERSARIAL EVALUATION — TAED WHITE-BOX ATTACK")
    output.append("=" * 60)
    output.append(f"Dataset: {DATASET_PATH}")
    output.append(f"Sample size: {len(df_sample)}")
    output.append("")
    output.append(f"{'Attack':<40} {'ASR':>8} {'Accuracy':>10} {'Mean TS':>10}")
    output.append("-" * 72)
    for r in results:
        output.append(
            f"{r['attack']:<40} {r['asr']:>8.4f} {r['accuracy']:>10.4f} {r['mean_trust_score']:>10.4f}"
        )
    output.append("-" * 72)
    output.append("")
    output.append("ASR = Attack Success Rate (higher = worse for TAED)")
    output.append("Mean TS = Average Trust Score assigned to samples")

    report = "\n".join(output)
    print("\n" + report)

    with open(OUTPUT_PATH, 'w') as f:
        f.write(report)
    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()