from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from hybrid_defense import TAEDSystem

app = Flask(__name__, template_folder='templates')
CORS(app)

print(" [Server] Loading TAED Engine...")
system = TAEDSystem()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        email_text = data.get('text', '') or data.get('email', '')
        feedback = data.get('feedback')
        if not email_text: return jsonify({'error': 'No text provided'}), 400
        result = system.analyze_email(email_text, user_feedback=feedback)
        print(f"DEBUG: text='{email_text[:50]}' prediction={result['prediction']} confidence={result['metrics']['C (Confidence)']}")
        return jsonify(result)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
