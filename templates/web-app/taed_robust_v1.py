"""
TAED Robust v1: Intelligent Fidelity Calculation
Fixes: Proper handling of SAFE vs PHISHING predictions
"""
import sys, json, os, numpy as np, warnings
warnings.filterwarnings('ignore')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.getcwd())
from lime.lime_text import LimeTextExplainer
import joblib

class TAEDRobust:
    def __init__(self):
        print(" [TAED Robust v1] Loading...", file=sys.stderr)
        self.rf = joblib.load('models/random_forest_pipeline.joblib')
        self.xgb = joblib.load('models/xgboost_pipeline.joblib')
        self.lime = LimeTextExplainer(class_names=['Safe','Phishing'], bow=True)
        
        self.threat_words = {
            'urgent','immediately','expires','suspended','limited','within',
            'verify','confirm','update','click','download','review','validate',
            'wire','transfer','payment','refund','invoice','transaction','billing',
            'password','account','login','security','credentials','authentication',
            'administrator','support','department','team','blocked','locked','frozen'
        }
        print(f" ✓ Models loaded, {len(self.threat_words)} threat indicators", file=sys.stderr)
    
    def calculate_intelligent_fidelity(self, text, model, prediction, proba):
        """
        Intelligent Fidelity: Measures if model reasoning makes semantic sense
        
        Key insight: Check if LIME weights align with prediction
        - PHISHING prediction + positive weights on threats = HIGH fidelity (good)
        - SAFE prediction + negative weights on threats = model confused = LOW fidelity
        - SAFE prediction + no threats found = HIGH fidelity (good)
        """
        try:
            # Get LIME explanation
            exp = self.lime.explain_instance(text, model.predict_proba, num_features=10, num_samples=5000)
            features = exp.as_list()
            
            # Analyze threat words and their weights
            threat_features = []
            for word, weight in features:
                if word.lower() in self.threat_words:
                    threat_features.append((word, weight))
            
            num_threats = len(threat_features)
            
            # Case 1: Model says PHISHING
            if prediction == 1:
                if num_threats == 0:
                    # PHISHING but no threat words? Suspicious
                    fidelity = 0.3
                    reason = f"Phishing verdict but no threat indicators found"
                else:
                    # Count how many threat words have positive weight (pushing toward phishing)
                    positive_threats = sum(1 for w, wt in threat_features if wt > 0)
                    fidelity = positive_threats / max(num_threats, 1)
                    reason = f"{positive_threats}/{num_threats} threats correctly weighted"
            
            # Case 2: Model says SAFE
            else:
                if num_threats >= 3:
                    # SAFE but has many threat words - check if weights are negative
                    negative_threats = sum(1 for w, wt in threat_features if wt < 0)
                    
                    if negative_threats >= num_threats * 0.5:
                        # Most threats have negative weights = MODEL CONFUSION
                        fidelity = 0.15
                        reason = f"⚠️ MISMATCH: {negative_threats}/{num_threats} threat words push toward SAFE (model confused!)"
                        for word, weight in threat_features:
                            if weight < 0:
                                print(f"   '{word}': {weight:.3f} (should be positive)", file=sys.stderr)
                    else:
                        # Threats exist but model still confident it's safe - might be legitimate urgency
                        fidelity = 0.6
                        reason = f"Threat words present but model confident (check context)"
                
                elif num_threats == 0:
                    # SAFE and no threats = CORRECT reasoning
                    fidelity = 0.95
                    reason = "No threat indicators - correctly classified as safe"
                
                else:
                    # 1-2 threat words, model says safe - probably fine
                    fidelity = 0.8
                    reason = f"Few threats ({num_threats}), likely legitimate"
            
            print(f" Fidelity: {fidelity:.2f} - {reason}", file=sys.stderr)
            return fidelity, reason
            
        except Exception as e:
            print(f" Fidelity error: {e}", file=sys.stderr)
            return 0.5, "Error in calculation"
    
    def analyze(self, text):
        print("\n=== TAED Robust Analysis ===", file=sys.stderr)
        
        # Get predictions from both models
        rf_pred = self.rf.predict([text])[0]
        rf_proba = self.rf.predict_proba([text])[0]
        
        xgb_pred = self.xgb.predict([text])[0]
        xgb_proba = self.xgb.predict_proba([text])[0]
        
        print(f" RF: {'PHISHING' if rf_pred==1 else 'SAFE'} ({rf_proba[1]*100:.1f}%)", file=sys.stderr)
        print(f" XGB: {'PHISHING' if xgb_pred==1 else 'SAFE'} ({xgb_proba[1]*100:.1f}%)", file=sys.stderr)
        
        # Use RF as primary (you can change this)
        primary_pred = rf_pred
        primary_proba = rf_proba
        
        # Calculate fidelity
        C = max(primary_proba)
        F, F_reason = self.calculate_intelligent_fidelity(text, self.rf, primary_pred, primary_proba)
        I = 0.05  # Simplified for now - we'll fix this next
        
        # Trust Score
        TS = 0.3*C + 0.4*F - 0.3*I
        
        print(f" Trust Score: {TS:.2f} (C={C:.2f}, F={F:.2f}, I={I:.2f})", file=sys.stderr)
        
        # Intelligent decision
        if primary_pred == 1:
            # Model says phishing
            if F < 0.4:
                verdict = "PHISHING"
                explanation = f"Phishing detected but low reasoning fidelity ({F:.2f}). {F_reason}"
            else:
                verdict = "PHISHING"
                explanation = f"High confidence phishing. {F_reason}"
        else:
            # Model says safe
            if F < 0.3:
                # LOW FIDELITY + SAFE = MODEL CONFUSED = OVERRIDE TO PHISHING
                verdict = "PHISHING"
                explanation = f"🚨 ADVERSARIAL ATTACK: {F_reason}"
                attack_type = "typosquatting" if any(x in text.lower() for x in ['paypa1','micr0soft','g00gle']) else "social-engineering"
            else:
                # High fidelity + safe = actually safe
                verdict = "SAFE"
                explanation = f"Legitimate email. {F_reason}"
                attack_type = "none"
        
        if verdict == "PHISHING" and 'attack_type' not in locals():
            attack_type = "typosquatting" if any(x in text.lower() for x in ['paypa1','micr0soft']) else "social-engineering"
        
        print(f" Final: {verdict} ({attack_type if verdict=='PHISHING' else 'none'})", file=sys.stderr)
        
        return {
            "trustScore": int(TS*100),
            "confidence": int(C*100),
            "fidelity": int(F*100),
            "stability": 95,
            "verdict": verdict,
            "explanation": explanation,
            "attackType": attack_type if verdict == "PHISHING" else "none"
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error":"No content"}))
        sys.exit(1)
    
    taed = TAEDRobust()
    result = taed.analyze(sys.argv[1])
    print(json.dumps(result))
