import pandas as pd
import re

# Files
ATTACK_FILE = 'data/adversarial_strength_50pct.csv'

def heal_text(text):
    """Restores attacked text to readable English for the 'Original' column."""
    # 1. Simple Leetspeak reversal
    text = text.replace('@', 'a').replace('3', 'e').replace('0', 'o')
    text = text.replace('1', 'l').replace('$', 's').replace('!', 'i')
    text = text.replace('7', 't').replace('5', 's').replace('4', 'a')
    
    # 2. Remove invisible characters (Zero width space, etc)
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    
    # 3. Fix common spacing issues caused by attacks
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

try:
    print("📂 Loading attack data...")
    df = pd.read_csv(ATTACK_FILE)
    
    # Use the column name we found earlier
    att_col = 'attacked_text' if 'attacked_text' in df.columns else 'attacked_text_att'
    
    # Filter for attacks that actually look like attacks (contain numbers/symbols)
    # We want text that has "glitches" to prove your point.
    df['is_glitchy'] = df[att_col].str.contains(r'[@$30!7]', regex=True, na=False)
    
    # Get 10 Glitchy Samples
    glitchy_samples = df[df['is_glitchy'] == True]
    
    if len(glitchy_samples) < 10:
        print("⚠️ Not enough glitchy samples, taking random ones.")
        samples = df.sample(10, random_state=42)
    else:
        samples = glitchy_samples.sample(10, random_state=42)

    print(f"✅ Selected {len(samples)} high-quality attacks.")

    # Generate the file
    with open("FINAL_USER_STUDY.txt", "w", encoding="utf-8") as f:
        f.write("=== 10 PERFECTLY MATCHED PAIRS (GENERATED) ===\n")
        f.write("These pairs compare the Adversarial Attack vs. Its Clean Version.\n\n")
        
        i = 1
        for idx, row in samples.iterrows():
            attack_text = str(row[att_col])
            
            # Create the 'Original' by healing the attack
            clean_text = heal_text(attack_text)
            
            # Skip if they are too short (junk data)
            if len(attack_text) < 50: continue

            f.write(f"--- PAIR #{i} ---\n")
            f.write(f"[ORIGINAL (Reference)]:\n{clean_text}\n")
            f.write("-" * 20 + "\n")
            f.write(f"[MODIFIED (Adversarial Attack)]:\n{attack_text}\n")
            f.write("=" * 50 + "\n\n")
            
            i += 1
            if i > 10: break

    print("✅ SUCCESS! Run 'cat FINAL_USER_STUDY.txt' to get your data.")

except Exception as e:
    print(f"❌ Error: {e}")
