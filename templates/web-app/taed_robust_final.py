#!/usr/bin/env python3
"""
TAED Robust Final - FIXED: Trusted domains always override
"""
import sys, json, os, numpy as np, warnings, re, random
warnings.filterwarnings('ignore')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.getcwd())
from lime.lime_text import LimeTextExplainer
import joblib

class TAEDRobustFinal:
    def __init__(self):
        print(" [TAED Robust Final v2] Initializing...", file=sys.stderr)
        
        self.models = {}
        
        try:
            self.rf = joblib.load('models/random_forest_pipeline_v2.joblib')
            self.models['rf'] = self.rf
            print(" ✓ Random Forest v2 (97% acc)", file=sys.stderr)
        except:
            self.rf = joblib.load('models/random_forest_pipeline.joblib')
            self.models['rf'] = self.rf
            print(" ⚠ Random Forest v1", file=sys.stderr)
        
        try:
            self.xgb = joblib.load('models/xgboost_pipeline.joblib')
            self.models['xgb'] = self.xgb
            print(" ✓ XGBoost", file=sys.stderr)
        except:
            self.xgb = None
        
        self.lime = LimeTextExplainer(class_names=['Safe','Phishing'], bow=True, random_state=42)
        
        self.trusted_domains = {
            'amazon.com', 'ebay.com', 'paypal.com', 'google.com', 
            'microsoft.com', 'apple.com', 'facebook.com', 'twitter.com',
            'linkedin.com', 'netflix.com', 'spotify.com', 'github.com',
            'ups.com', 'fedex.com', 'usps.com', 'walmart.com'
        }
        
        self.typosquatting_patterns = {
            'paypa1', 'micr0soft', 'g00gle', 'amaz0n', 'app1e',
            'netf1ix', 'faceb00k', 'twiter', 'gogle', 'amazom'
        }
        
        self.threat_words = {
            'urgent','immediately','expires','suspended','limited','within',
            'verify','confirm','update','click','download','validate',
            'wire','transfer','payment','refund','invoice','transaction',
            'password','account','login','security','credentials',
            'blocked','locked','frozen','terminate'
        }
        
        print(f" ✓ {len(self.models)} models, {len(self.trusted_domains)} trusted domains", file=sys.stderr)
    
    def extract_domains(self, text):
        pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
        return set(re.findall(pattern, text.lower()))
    
    def check_domains(self, text):
        domains = self.extract_domains(text)
        trusted = [d for d in domains if d in self.trusted_domains]
        suspicious = [d for d in domains if any(typo in d for typo in self.typosquatting_patterns)]
        return trusted, suspicious
    
    def generate_perturbations(self, text, num_perturbations=5):
        perturbations = []
        homoglyphs = {
            'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 'c': 'с',
            'l': '1', 'i': '1', 'O': '0', 'S': '$'
        }
        
        for _ in range(num_perturbations):
            chars = list(text)
            num_mods = max(1, int(len(chars) * random.uniform(0.01, 0.03)))
            
            for _ in range(num_mods):
                if chars:
                    idx = random.randint(0, len(chars) - 1)
                    if chars[idx] in homoglyphs:
                        chars[idx] = homoglyphs[chars[idx]]
            
            perturbations.append(''.join(chars))
        
        return perturbations
    
    def calculate_real_instability(self, text, model):
        try:
            original_proba = model.predict_proba([text])[0]
            original_pred = model.predict([text])[0]
            
            perturbations = self.generate_perturbations(text, num_perturbations=5)
            
            prediction_variance = []
            prediction_changes = 0
            
            for pert in perturbations:
                pert_proba = model.predict_proba([pert])[0]
                pert_pred = model.predict([pert])[0]
                
                prob_shift = np.abs(pert_proba[1] - original_proba[1])
                prediction_variance.append(prob_shift)
                
                if pert_pred != original_pred:
                    prediction_changes += 1
            
            avg_variance = np.mean(prediction_variance)
            flip_rate = prediction_changes / len(perturbations)
            instability = (avg_variance + flip_rate) / 2
            
            print(f" Instability: {instability:.3f} (variance={avg_variance:.3f}, flips={prediction_changes}/{len(perturbations)})", file=sys.stderr)
            return instability
            
        except:
            return 0.5
    
    def calculate_ensemble_confidence(self, text):
        predictions = []
        probabilities = []
        
        for name, model in self.models.items():
            try:
                pred = model.predict([text])[0]
                proba = model.predict_proba([text])[0]
                predictions.append(pred)
                probabilities.append(proba[1])
                print(f" {name.upper()}: {'PHISHING' if pred==1 else 'SAFE'} ({proba[1]*100:.1f}%)", file=sys.stderr)
            except:
                pass
        
        if not predictions:
            return 0, 0.5, 0.0
        
        avg_proba = np.mean(probabilities)
        ensemble_pred = 1 if avg_proba >= 0.5 else 0
        agreement = 1.0 - min(np.var(probabilities), 1.0)
        confidences = [max(p, 1-p) for p in probabilities]
        avg_confidence = np.mean(confidences)
        
        print(f" Ensemble: {avg_proba:.2f} avg, {agreement:.2f} agreement", file=sys.stderr)
        return ensemble_pred, avg_confidence, agreement
    
    def calculate_fidelity(self, text, model, prediction):
        try:
            trusted, suspicious = self.check_domains(text)
            
            if suspicious:
                print(f" 🚨 Typosquatting: {suspicious}", file=sys.stderr)
                return 0.10, f"Typosquatting: {', '.join(suspicious)}"
            
            # FIXED: Trusted domain ALWAYS gets high fidelity, regardless of prediction
            if trusted:
                print(f" ✓ Trusted domain found: {trusted}", file=sys.stderr)
                return 0.95, f"Trusted domain: {', '.join(trusted)}"
            
            # LIME analysis for non-domain cases
            exp = self.lime.explain_instance(text, model.predict_proba, num_features=10, num_samples=5000)
            features = exp.as_list()
            
            threat_features = [(w, wt) for w, wt in features if w.lower() in self.threat_words]
            num_threats = len(threat_features)
            
            if prediction == 1:
                if num_threats == 0:
                    return 0.3, "Phishing but no threat indicators"
                positive = sum(1 for w, wt in threat_features if wt > 0)
                fidelity = positive / max(num_threats, 1)
                return fidelity, f"{positive}/{num_threats} threats weighted correctly"
            else:
                if num_threats >= 3:
                    negative = sum(1 for w, wt in threat_features if wt < 0)
                    if negative >= 2:
                        return 0.15, f"Confused: {negative}/{num_threats} threats wrong sign"
                    return 0.6, "Threats present but model confident"
                elif num_threats == 0:
                    return 0.95, "No threats - correctly safe"
                else:
                    return 0.8, "Few threats, likely legitimate"
                    
        except Exception as e:
            return 0.5, f"Error: {e}"
    
    def detect_attack_type(self, text, is_phishing, suspicious_domains):
        if not is_phishing:
            return "none"
        
        text_lower = text.lower()
        
        if suspicious_domains:
            return "typosquatting"
        if any(h in text for h in ['а', 'е', 'о', 'р', 'с']):
            return "homoglyph"
        if any(url in text_lower for url in ['bit.ly', 'tinyurl', 'goo.gl']):
            return "url-obfuscation"
        
        urgency_count = sum(1 for w in ['urgent', 'immediately', 'expires', 'asap'] if w in text_lower)
        if urgency_count >= 2:
            return "urgency"
        if any(t in text_lower for t in ['suspend', 'locked', 'frozen', 'terminate']):
            return "threat"
        
        return "social-engineering"
    
    def analyze(self, text):
        print("\n=== TAED Robust Final v2 ===", file=sys.stderr)
        
        # Critical: Check domains FIRST
        trusted, suspicious = self.check_domains(text)
        
        # Ensemble prediction
        ensemble_pred, C, model_agreement = self.calculate_ensemble_confidence(text)
        
        # Fidelity (now handles trusted domains correctly)
        F, F_reason = self.calculate_fidelity(text, self.rf, ensemble_pred)
        
        # Real instability
        I = self.calculate_real_instability(text, self.rf)
        
        # Trust Score
        alpha, beta, gamma = 0.3, 0.4, 0.3
        TS = (alpha * C) + (beta * F) - (gamma * I)
        TS = max(0.0, min(1.0, TS))
        
        print(f" Trust Score: {TS:.2f} = 0.3×{C:.2f} + 0.4×{F:.2f} - 0.3×{I:.2f}", file=sys.stderr)
        print(f" Fidelity reason: {F_reason}", file=sys.stderr)
        
        # FIXED: Trusted domain override logic
        if suspicious:
            verdict = "PHISHING"
            explanation = f"Typosquatting attack: {', '.join(suspicious)}"
            attack_type = "typosquatting"
        elif trusted and not suspicious:
            # OVERRIDE: Trusted domain = SAFE (unless there's typosquatting)
            verdict = "SAFE"
            explanation = f"Legitimate email from trusted domain: {', '.join(trusted)}"
            attack_type = "none"
            print(f" ✓ OVERRIDE: Trusted domain forces SAFE verdict", file=sys.stderr)
        elif TS < 0.4:
            verdict = "PHISHING"
            explanation = f"Low trust ({TS:.2f}). {F_reason}. Instability: {I:.2f}"
            attack_type = self.detect_attack_type(text, True, suspicious)
        elif TS > 0.7 and model_agreement > 0.8:
            verdict = "PHISHING" if ensemble_pred == 1 else "SAFE"
            explanation = f"High confidence. Models agree ({model_agreement:.2f}). {F_reason}"
            attack_type = self.detect_attack_type(text, verdict=="PHISHING", suspicious)
        else:
            verdict = "PHISHING" if ensemble_pred == 1 else "SAFE"
            explanation = f"Moderate trust ({TS:.2f}). {F_reason}"
            attack_type = self.detect_attack_type(text, verdict=="PHISHING", suspicious)
        
        print(f" Final: {verdict} ({attack_type})", file=sys.stderr)
        
        return {
            "trustScore": int(TS*100),
            "confidence": int(C*100),
            "fidelity": int(F*100),
            "stability": int((1-I)*100),
            "verdict": verdict,
            "explanation": explanation,
            "attackType": attack_type
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error":"No content"}))
        sys.exit(1)
    
    taed = TAEDRobustFinal()
    result = taed.analyze(sys.argv[1])
    print(json.dumps(result))
