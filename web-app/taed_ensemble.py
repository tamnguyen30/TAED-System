import sys
import json
import os
import numpy as np
import warnings
warnings.filterwarnings('ignore')

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.getcwd())

class TAEDEnsemble:
    def __init__(self):
        print(" [TAED] Initializing Multi-Model Ensemble...", file=sys.stderr)
        self.models = {}
        self.load_models()
    
    def load_models(self):
        try:
            import joblib
            self.rf_pipeline = joblib.load('models/random_forest_pipeline.joblib')
            self.models['random_forest'] = True
            print(" ✓ Random Forest loaded", file=sys.stderr)
        except:
            self.models['random_forest'] = False
        
        try:
            import joblib
            self.xgb_pipeline = joblib.load('models/xgboost_pipeline.joblib')
            self.models['xgboost'] = True
            print(" ✓ XGBoost loaded", file=sys.stderr)
        except:
            self.models['xgboost'] = False
    
    def predict_rf(self, text):
        if not self.models.get('random_forest'):
            return None
        try:
            proba = self.rf_pipeline.predict_proba([text])[0]
            return {'prediction': proba[1], 'confidence': max(proba), 'name': 'RandomForest'}
        except:
            return None
    
    def predict_xgb(self, text):
        if not self.models.get('xgboost'):
            return None
        try:
            proba = self.xgb_pipeline.predict_proba([text])[0]
            return {'prediction': proba[1], 'confidence': max(proba), 'name': 'XGBoost'}
        except:
            return None
    
    def rule_based_score(self, text):
        """Enhanced rule-based detection"""
        text_lower = text.lower()
        score = 0.0
        reasons = []
        
        urgency_words = ['urgent', 'immediately', 'asap', 'expires', 'limited time', 'act now', 'within 24']
        urgency_count = sum(1 for w in urgency_words if w in text_lower)
        if urgency_count > 0:
            score += urgency_count * 0.15
            reasons.append(f"urgency tactics")
        
        threats = ['suspend', 'locked', 'frozen', 'terminate', 'close', 'restricted', 'blocked']
        threat_count = sum(1 for w in threats if w in text_lower)
        if threat_count > 0:
            score += threat_count * 0.12
            reasons.append(f"threat language")
        
        verify_words = ['verify', 'confirm', 'validate', 'authenticate', 'update']
        verify_count = sum(1 for w in verify_words if w in text_lower)
        if verify_count > 0:
            score += verify_count * 0.10
            reasons.append(f"verification requests")
        
        creds = ['password', 'username', 'login', 'credential', 'account', 'ssn']
        cred_count = sum(1 for w in creds if w in text_lower)
        if cred_count > 0:
            score += cred_count * 0.10
            reasons.append(f"credential requests")
        
        if 'http' in text_lower or 'www' in text_lower:
            score += 0.05
            reasons.append("contains URLs")
            
            if any(pattern in text_lower for pattern in ['bit.ly', 'tinyurl', 'paypa1', 'micr0soft', 'g00gle']):
                score += 0.25
                reasons.append("typosquatting detected")
        
        if 'click' in text_lower:
            score += 0.08
            reasons.append("click prompts")
        
        return min(score, 1.0), reasons
    
    def detect_attack(self, text, is_phishing):
        """
        Detect attack type regardless of verdict
        Returns the PRIMARY attack type found
        """
        text_lower = text.lower()
        
        # Check all attack types and score them
        attack_scores = {}
        
        # Typosquatting (highest priority for phishing)
        typo_indicators = ['paypa1', 'micr0soft', 'g00gle', 'amazon-', 'app1e', 'netf1ix', 'faceb00k']
        if any(typo in text_lower for typo in typo_indicators):
            attack_scores['typosquatting'] = 10
        
        # Homoglyph
        homoglyphs = ['а', 'е', 'о', 'р', 'с', 'у', 'х']  # Cyrillic
        if any(h in text for h in homoglyphs):
            attack_scores['homoglyph'] = 9
        
        # URL obfuscation
        if 'bit.ly' in text_lower or 'tinyurl' in text_lower or 'goo.gl' in text_lower:
            attack_scores['url-obfuscation'] = 8
        
        # Urgency tactics
        urgency_words = ['urgent', 'immediately', 'expires', 'asap', 'limited time', 'act now', 'within 24 hours']
        urgency_count = sum(1 for w in urgency_words if w in text_lower)
        if urgency_count >= 2:
            attack_scores['urgency'] = 7
        elif urgency_count >= 1:
            attack_scores['urgency'] = 5
        
        # Threat language
        threats = ['suspend', 'locked', 'frozen', 'terminate', 'close', 'restricted', 'blocked', 'disabled']
        if sum(1 for w in threats if w in text_lower) >= 1:
            attack_scores['threat'] = 6
        
        # Credential harvesting
        creds = ['password', 'username', 'login', 'credential', 'ssn', 'social security', 'credit card']
        if sum(1 for w in creds if w in text_lower) >= 2:
            attack_scores['credential-harvesting'] = 6
        
        # Social engineering
        authority = ['irs', 'fbi', 'bank', 'paypal', 'amazon', 'microsoft', 'apple', 'google']
        if any(auth in text_lower for auth in authority):
            attack_scores['social-engineering'] = 4
        
        # Return highest scoring attack type
        if attack_scores:
            primary_attack = max(attack_scores, key=attack_scores.get)
            print(f" Detected attacks: {attack_scores}, primary: {primary_attack}", file=sys.stderr)
            return primary_attack
        
        return "none"
    
    def analyze(self, text):
        predictions = []
        
        rf_result = self.predict_rf(text)
        if rf_result:
            predictions.append(rf_result)
        
        xgb_result = self.predict_xgb(text)
        if xgb_result:
            predictions.append(xgb_result)
        
        rule_score, rule_reasons = self.rule_based_score(text)
        
        ml_avg = np.mean([p['prediction'] for p in predictions]) if predictions else 0.2
        
        if rule_score > 0.7 and ml_avg < 0.3:
            weights = {'RandomForest': 0.15, 'XGBoost': 0.15, 'RuleBased': 0.70}
        elif rule_score > 0.5 and ml_avg < 0.4:
            weights = {'RandomForest': 0.25, 'XGBoost': 0.25, 'RuleBased': 0.50}
        else:
            weights = {'RandomForest': 0.4, 'XGBoost': 0.4, 'RuleBased': 0.2}
        
        predictions.append({'prediction': rule_score, 'confidence': 0.85, 'name': 'RuleBased'})
        
        weighted_pred = sum(
            p['prediction'] * weights.get(p['name'], 0.33) for p in predictions
        ) / sum(weights.get(p['name'], 0.33) for p in predictions)
        
        avg_confidence = np.mean([p['confidence'] for p in predictions])
        
        pred_values = [p['prediction'] for p in predictions]
        variance = np.var(pred_values)
        fidelity = (1.0 - min(variance * 4, 1.0)) * 100
        
        stability = 85
        
        alpha, beta, gamma = 0.4, 0.3, 0.3
        trust_score = int((alpha * avg_confidence * 100) + (beta * fidelity) + (gamma * stability))
        
        if variance > 0.15:
            trust_score = int(trust_score * 0.8)
        
        is_phishing = weighted_pred >= 0.5
        verdict = "PHISHING" if is_phishing else "SAFE"
        
        # Always detect attack type, even for SAFE emails
        attack_type = self.detect_attack(text, is_phishing)
        
        explanation = self.generate_explanation(predictions, is_phishing, fidelity, rule_reasons, weighted_pred)
        
        print(f" Final verdict: {verdict}, attack_type: {attack_type}", file=sys.stderr)
        
        return {
            "trustScore": max(0, min(100, trust_score)),
            "confidence": int(avg_confidence * 100),
            "fidelity": int(fidelity),
            "stability": int(stability),
            "verdict": verdict,
            "explanation": explanation,
            "attackType": attack_type
        }
    
    def generate_explanation(self, predictions, is_phishing, fidelity, rule_reasons, ensemble_score):
        components = []
        
        model_votes = []
        for p in predictions:
            vote = "PHISHING" if p['prediction'] >= 0.5 else "SAFE"
            model_votes.append(f"{p['name']}: {vote} ({p['prediction']*100:.0f}%)")
        
        components.append("Ensemble analysis: " + ", ".join(model_votes))
        
        if rule_reasons:
            components.append("Phishing indicators detected: " + ", ".join(rule_reasons))
        
        if fidelity < 60:
            components.append(f"Models show low agreement ({fidelity:.0f}%) - potential adversarial attack")
        
        if is_phishing:
            if ensemble_score > 0.8:
                components.append("High confidence phishing detection")
            elif ensemble_score > 0.6:
                components.append("Moderate confidence phishing detection")  
            else:
                components.append("Phishing detected - manual review recommended")
        else:
            components.append("No significant phishing indicators found")
        
        return ". ".join(components) + "."

ensemble = None

def get_ensemble():
    global ensemble
    if ensemble is None:
        ensemble = TAEDEnsemble()
    return ensemble

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No content"}))
        sys.exit(1)
    
    text = sys.argv[1]
    system = get_ensemble()
    result = system.analyze(text)
    print(json.dumps(result))
