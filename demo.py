import joblib
import os

# --- Configuration ---
MODEL_PATH = 'models/random_forest_pipeline.joblib'
# --- End Configuration ---

def main():
    print("🚀 Loading phishing detection model...")

    # 1. Load the trained model pipeline
    try:
        model = joblib.load(MODEL_PATH)
    except FileNotFoundError:
        print(f"❌ ERROR: Model file not found at '{MODEL_PATH}'")
        print("Please run 'python3 train_random_forest.py' to create the model file first.")
        return
    except Exception as e:
        print(f"❌ ERROR loading model: {e}")
        return

    print(f"✅ Model '{MODEL_PATH}' loaded successfully.")
    print("--- Phishing Detection Demo ---")
    print("Type or paste an email and press Enter. Type 'exit' to quit.")

    # 2. Start the prediction loop
    while True:
        print("\n" + "="*40)
        # Use a more robust way to get multi-line input
        print("Enter email text (press Ctrl+D or Ctrl+Z on Windows then Enter when done):")
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            pass

        email_text = "\n".join(lines)

        if not email_text:
            continue

        # 3. Check for exit command
        if email_text.strip().lower() == 'exit':
            print("👋 Exiting demo. Goodbye!")
            break

        # 4. Make a prediction
        # The model expects a list of items, so we put our text in a list
        prediction = model.predict([email_text])

        # 5. Show the result
        if prediction[0] == 1:
            print("\n🚨 R E S U L T :  This email is PHISHING 🚨")
        else:
            print("\n✅ R E S U L T :  This email is SAFE ✅")

if __name__ == "__main__":
    main()
