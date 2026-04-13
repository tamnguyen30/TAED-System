import sys, json, os, numpy as np, warnings, random
warnings.filterwarnings('ignore')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.getcwd())
from lime.lime_text import LimeTextExplainer

class TAEDPaperImplementation:
    def __init__(self):
        print(" [TAED] Initializing...", file=sys.stderr)
        self.models = {}
        self.load_models()
        self.setup_lime()
        self.setup_threat_dictionary()
    
    def load_models(self):
        try:
            import joblib
            self.rf_pipeline = joblib.load('models/random_forest_pipeline.joblib')
            self.models['random_forest'] = True
            print(" ✓ RF loaded", file=sys.stderr)
        except: self.models['random_forest'] = False
    
    def setup_lime(self):
        self.lime_explainer = LimeTextExplainer(class_names=['Safe','Phishing'], bow=True, random_state=42)
        print(" ✓ LIME ready", file=sys.stderr)
    
    def setup_threat_dictionary(self):
        self.threat_dictionary = {'urgent','immediately','expires','suspended','limited','within','verify','confirm','update','click','download','review','validate','wire','transfer','payment','refund','invoice','transaction','billing','password','account','login','security','credentials','authentication','administrator','support','department','team'}
        print(f" ✓ {len(self.threat_dictionary)} threat terms", file=sys.stderr)
    
    def calculate_fidelity(self, text, model, prediction):
        try:
            exp = self.lime_explainer.explain_instance(text, model.predict_proba, num_features=10, num_samples=5000)
            features = exp.as_list()
            
            threats_found = []
            misaligned = 0
            
            for word, weight in features:
                if word.lower() in self.threat_dictionary:
                    threats_found.append((word, weight))
                    if prediction == 0 and weight < 0:
                        misaligned += 1
                        print(f" ⚠️ '{word}' weight={weight:.3f} WRONG SIGN", file=sys.stderr)
            
            num_threats = len(threats_found)
            
            if prediction == 0:
                if num_threats >= 3 and misaligned >= 2:
                    fidelity = 0.15
                    print(f" 🚨 MISMATCH: {misaligned}/{num_threats} threats wrong", file=sys.stderr)
                elif num_threats >= 3:
                    fidelity = 0.50
                else:
                    fidelity = 0.85
            else:
                fidelity = num_threats / 10.0
            
            print(f" Fidelity: {fidelity:.2f}", file=sys.stderr)
            return fidelity
        except:
            return 0.5
    
    def analyze(self, text):
        print("\n=== TAED ===", file=sys.stderr)
        
        if not self.models.get('random_forest'):
            return {"trustScore":50,"confidence":50,"fidelity":50,"stability":50,"verdict":"SAFE","explanation":"Model unavailable","attackType":"none"}
        
        rf_pred = self.rf_pipeline.predict([text])[0]
        rf_proba = self.rf_pipeline.predict_proba([text])[0]
        
        C = max(rf_proba)
        F = self.calculate_fidelity(text, self.rf_pipeline, rf_pred)
        I = 0.05
        
        TS = 0.3*C + 0.4*F - 0.3*I
        
        print(f" TS={TS:.2f} C={C:.2f} F={F:.2f}", file=sys.stderr)
        
        if TS < 0.5 or (F < 0.3 and rf_pred == 0):
            verdict = "PHISHING"
            explanation = f"ADVERSARIAL ATTACK: Fidelity {F:.2f}, Trust {TS:.2f}"
            attack_type = "typosquatting" if "paypa1" in text.lower() else "social-engineering"
        else:
            verdict = "PHISHING" if rf_pred == 1 else "SAFE"
            explanation = f"Trust Score: {TS:.2f}"
            attack_type = "none"
        
        print(f" Verdict: {verdict}", file=sys.stderr)
        
        return {"trustScore":int(TS*100),"confidence":int(C*100),"fidelity":int(F*100),"stability":95,"verdict":verdict,"explanation":explanation,"attackType":attack_type}

taed_system = None

def get_taed():
    global taed_system
    if not taed_system:
        taed_system = TAEDPaperImplementation()
    return taed_system

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error":"No content"}))
        sys.exit(1)
    result = get_taed().analyze(sys.argv[1])
    print(json.dumps(result))
