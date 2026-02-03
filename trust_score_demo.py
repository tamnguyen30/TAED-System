import joblib
import numpy as np
import lime
import lime.lime_text
from sklearn.pipeline import make_pipeline
from attacks.char_attacks import apply_homoglyph_attack # We need an attack for Instability

# --- Configuration ---
MODEL_PATH = 'models/random_forest_pipeline.joblib' # Using your robust model
# Tunable weights (alpha, beta, gamma) must sum to 1 roughly, or be balanced
ALPHA = 0.4 # Weight for Confidence
BETA = 0.3  # Weight for Fidelity
GAMMA = 0.3 # Weight for Instability
# --- End Configuration ---

# A simple "Knowledge Base" of phishing indicators for Fidelity check
# In a real system, this would be a large database or ontology
PHISHING_INDICATORS = {
    "urgent", "immediate", "verify", "account", "suspended", "bank", "invoice",
    "click", "link", "password", "update", "security", "unauthorized", "locked"
}

def calculate_jaccard_similarity(list1, list2):
    """Calculates intersection over union for two lists of words."""
    s1 = set(list1)
    s2 = set(list2)
    if not s1 and not s2: return 1.0
    return len(s1.intersection(s2)) / len(s1.union(s2))

def get_explanation_features(text, explainer, pipeline):
    """Generates LIME explanation and returns top words."""
    exp = explainer.explain_instance(
        text, 
        pipeline.predict_proba, 
        num_features=5
    )
    # Extract just the words from the explanation (list of tuples)
    return [x[0] for x in exp.as_list()]

def main():
    print("🚀 Loading Trust-Aware Phishing Detection System...")
    
    # 1. Load Model
    try:
        model = joblib.load(MODEL_PATH)
    except FileNotFoundError:
        print(f"❌ ERROR: Model not found at {MODEL_PATH}")
        return

    # Initialize LIME Explainer
    explainer = lime.lime_text.LimeTextExplainer(class_names=['Safe', 'Phishing'])
    
    print("✅ System Ready. Weights: α={:.1f}, β={:.1f}, γ={:.1f}".format(ALPHA, BETA, GAMMA))
    
    while True:
        print("\n" + "="*60)
        print("Enter email text (Ctrl+D to finish, or type 'exit'):")
        try:
            lines = []
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        email_text = "\n".join(lines).strip()
        if not email_text: continue
        if email_text.lower() == 'exit': break

        print("\n🔍 Analyzing Risk and Trustworthiness...")

        # --- COMPONENT 1: CONFIDENCE (C) ---
        # "Use model’s predicted probability" 
        probs = model.predict_proba([email_text])[0]
        prediction = np.argmax(probs)
        confidence = probs[prediction] # C
        
        label = "PHISHING" if prediction == 1 else "SAFE"
        print(f"1. Model Output: {label} (Confidence C = {confidence:.4f})")

        # Only calculate Trust Score if predicted as Phishing (usually)
        # But we can do it for both. Let's focus on the explanation.
        
        # --- COMPONENT 2: FIDELITY (F) ---
        # "Compare explanation tokens to key phishing indicators" 
        clean_explanation_words = get_explanation_features(email_text, explainer, model)
        print(f"   Explanation Features: {clean_explanation_words}")
        
        # Calculate F: How many explanation words are in our known Phishing Dictionary?
        # This is a simplified "Jaccard overlap" [cite: 44]
        intersection = [w for w in clean_explanation_words if w.lower() in PHISHING_INDICATORS]
        fidelity = len(intersection) / len(clean_explanation_words) if clean_explanation_words else 0.0
        print(f"2. Fidelity (F) = {fidelity:.4f} (Overlap with knowledge base)")

        # --- COMPONENT 3: INSTABILITY (I) ---
        # "Generate a perturbed version... Produce explanation for both... Compute similarity" [cite: 51-53]
        # We use a light homoglyph attack to perturb the input
        perturbed_text = apply_homoglyph_attack(email_text, attack_strength=0.1)
        perturbed_explanation_words = get_explanation_features(perturbed_text, explainer, model)
        
        # Calculate Similarity between clean and perturbed explanations
        similarity = calculate_jaccard_similarity(clean_explanation_words, perturbed_explanation_words)
        
        # "I = 1 - similarity" [cite: 54]
        instability = 1.0 - similarity
        print(f"3. Instability (I) = {instability:.4f} (Change under perturbation)")

        # --- FINAL TRUST SCORE (TS) ---
        # "TS = α⋅C + β⋅F - γ⋅I" 
        trust_score = (ALPHA * confidence) + (BETA * fidelity) - (GAMMA * instability)
        
        # Clamp score between 0 and 1
        trust_score = max(0.0, min(1.0, trust_score))

        print("-" * 30)
        print(f"🛡️  FINAL TRUST SCORE: {trust_score:.4f}")
        
        # Interpret the score [cite: 57]
        if trust_score > 0.8:
            print("   Decision: ACCEPT AUTOMATICALLY (High Trust)")
        elif trust_score >= 0.5:
            print("   Decision: FLAG FOR SECONDARY CHECK (Medium Trust)")
        else:
            print("   Decision: ESCALATE FOR MANUAL REVIEW (Low Trust)")
        print("="*60)

if __name__ == "__main__":
    main()
