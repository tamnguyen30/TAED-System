import pandas as pd
from difflib import SequenceMatcher

# Files
ATTACK_FILE = 'data/adversarial_strength_50pct.csv'
MASTER_FILE = 'data/adversarial_benchmark_dataset.csv'

def similarity(a, b):
    return SequenceMatcher(None, str(a), str(b)).ratio()

try:
    print("📂 Loading data...")
    df_attacks = pd.read_csv(ATTACK_FILE)
    df_master = pd.read_csv(MASTER_FILE)

    # Merge
    merged = pd.merge(df_attacks, df_master, on='original_email_id', how='inner', suffixes=('_att', '_orig'))

    # Column Setup
    att_col = 'attacked_text_att'
    orig_col = 'original_text'
    label_col = 'original_label_att' 

    print("🔍 Calculating text similarity (this might take 10 seconds)...")
    
    # We filter row by row to find the "Goldilocks" zone
    valid_pairs = []
    
    for idx, row in merged.iterrows():
        # Must be Phishing
        if row[label_col] != 1: continue
        
        t1 = str(row[orig_col])
        t2 = str(row[att_col])
        
        # Skip if too short
        if len(t1) < 100: continue
        
        # Skip tinyurl/bit.ly
        if "tinyurl" in t2 or "bit.ly" in t2: continue

        # --- THE MAGIC METRIC ---
        # Calculate similarity ratio (0.0 = different, 1.0 = identical)
        sim = similarity(t1, t2)
        
        # We want: 
        # > 0.60 (It's the same email)
        # < 0.95 (It has visible changes/glitches)
        if 0.60 < sim < 0.95:
            valid_pairs.append(row)
            
        if len(valid_pairs) >= 10: break

    print(f"✅ Found {len(valid_pairs)} PERFECT MATCH pairs.")

    # Save to File
    with open("PROFESSOR_APPROVED_SAMPLES.txt", "w", encoding="utf-8") as f:
        f.write("=== 10 PERFECTLY MATCHED PAIRS ===\n")
        f.write("These show the EXACT same email, before and after attack.\n\n")
        
        i = 1
        for row in valid_pairs:
            f.write(f"--- PAIR #{i} ---\n")
            f.write(f"[ORIGINAL]:\n{row[orig_col]}\n")
            f.write("-" * 20 + "\n")
            f.write(f"[MODIFIED]:\n{row[att_col]}\n")
            f.write("=" * 50 + "\n\n")
            i += 1

    print("✅ SUCCESS! Run 'cat PROFESSOR_APPROVED_SAMPLES.txt'")

except Exception as e:
    print(f"❌ Error: {e}")
