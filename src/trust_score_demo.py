import joblib
import numpy as np
import lime
import lime.lime_text
from sklearn.pipeline import make_pipeline
from attacks.char_attacks import apply_homoglyph_attack 


MODEL_PATH = 'models/random_forest_pipeline.joblib' 

ALPHA = 0.4 
BETA = 0.3  
GAMMA = 0.3 




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
    
    return [x[0] for x in exp.as_list()]

def main():
    print("🚀 Loading Trust-Aware Phishing Detection System...")
    
    
    try:
        model = joblib.load(MODEL_PATH)
    except FileNotFoundError:
        print(f"❌ ERROR: Model not found at {MODEL_PATH}")
        return

    
    explainer = lime.lime_text.LimeTextExplainer(class_names=['Safe', 'Phishing'])
    
    print("Weights: α={:.1f}, β={:.1f}, γ={:.1f}".format(ALPHA, BETA, GAMMA))
    
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

        
        
        probs = model.predict_proba([email_text])[0]
        prediction = np.argmax(probs)
        confidence = probs[prediction] 
        
        label = "PHISHING" if prediction == 1 else "SAFE"
        print(f"1. Model Output: {label} (Confidence C = {confidence:.4f})")

        
        
        
        
        
        clean_explanation_words = get_explanation_features(email_text, explainer, model)
        print(f"   Explanation Features: {clean_explanation_words}")
        
        
        
        intersection = [w for w in clean_explanation_words if w.lower() in PHISHING_INDICATORS]
        fidelity = len(intersection) / len(clean_explanation_words) if clean_explanation_words else 0.0
        print(f"2. Fidelity (F) = {fidelity:.4f} (Overlap with knowledge base)")

        
        
        
        perturbed_text = apply_homoglyph_attack(email_text, attack_strength=0.1)
        perturbed_explanation_words = get_explanation_features(perturbed_text, explainer, model)
        
        
        similarity = calculate_jaccard_similarity(clean_explanation_words, perturbed_explanation_words)
        
        
        instability = 1.0 - similarity
        print(f"3. Instability (I) = {instability:.4f} (Change under perturbation)")

        
        
        trust_score = (ALPHA * confidence) + (BETA * fidelity) - (GAMMA * instability)
        
        
        trust_score = max(0.0, min(1.0, trust_score))

        print("-" * 30)
        print(f"FINAL TRUST SCORE: {trust_score:.4f}")
        
        
        if trust_score > 0.8:
            print("   Decision: ACCEPT AUTOMATICALLY (High Trust)")
        elif trust_score >= 0.5:
            print("   Decision: FLAG FOR SECONDARY CHECK (Medium Trust)")
        else:
            print("   Decision: ESCALATE FOR MANUAL REVIEW (Low Trust)")
        print("="*60)

if __name__ == "__main__":
    main()
