import sys
import json
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hybrid_defense import TAEDSystem

taed = None

def get_taed():
    global taed
    if taed is None:
        taed = TAEDSystem()
    return taed

def analyze_email(content, sender="", subject=""):
    try:
        system = get_taed()
        result = system.analyze_email(content)
        
        trust_score = int(result['trust_score'] * 100)
        metrics = result.get('metrics', {})
        confidence = int(metrics.get('C (Confidence)', 0.5) * 100)
        fidelity = int(metrics.get('F (Fidelity)', 0.5) * 100)
        instability = metrics.get('I (Instability)', 0.0)
        stability = int((1.0 - instability) * 100)
        
        explanation = result.get('natural_language', '')
        attack_type = 'none'
        if 'typosquat' in explanation.lower() or 'domain' in explanation.lower():
            attack_type = 'homoglyph'
        elif 'url' in explanation.lower() or 'link' in explanation.lower():
            attack_type = 'url'
        elif 'urgency' in explanation.lower():
            attack_type = 'urgency'
        
        return {
            "trustScore": trust_score,
            "confidence": confidence,
            "fidelity": fidelity,
            "stability": stability,
            "verdict": result['prediction'],
            "explanation": explanation,
            "attackType": attack_type
        }
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return {"trustScore": 50, "confidence": 50, "fidelity": 50, "stability": 50, "verdict": "SAFE", "explanation": f"Error: {str(e)}", "attackType": "none"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No content"}))
        sys.exit(1)
    
    content = sys.argv[1]
    result = analyze_email(content)
    print(json.dumps(result))
