import pandas as pd

# Files
ATTACK_FILE = 'data/adversarial_strength_50pct.csv'
MASTER_FILE = 'data/adversarial_benchmark_dataset.csv'

try:
    print("📂 Loading data...")
    df_attacks = pd.read_csv(ATTACK_FILE)
    df_master = pd.read_csv(MASTER_FILE)

    # Merge
    merged = pd.merge(df_attacks, df_master, on='original_email_id', how='inner', suffixes=('_att', '_orig'))

    # Column Names
    att_col = 'attacked_text_att'
    orig_col = 'original_text'
    label_col = 'original_label_att' 

    # --- CRITICAL FILTER: LENGTH SIMILARITY ---
    # We want emails where the attack is roughly the same length as the original.
    # This ensures we get "Modified" text, not "Replaced" text.
    
    # Calculate lengths
    merged['len_orig'] = merged[orig_col].str.len()
    merged['len_att'] = merged[att_col].str.len()
    
    # Avoid division by zero
    merged = merged[merged['len_orig'] > 50]

    # Ratio: Attack Length / Original Length
    merged['ratio'] = merged['len_att'] / merged['len_orig']

    # FILTER: 
    # 1. Phishing (Label=1)
    # 2. Ratio between 0.8 and 1.2 (Length is similar)
    # 3. No tinyurl
    
    df_homoglyphs = merged[
        (merged[label_col] == 1) & 
        (merged['ratio'] > 0.8) & 
        (merged['ratio'] < 1.2) &
        (~merged[att_col].str.contains("tinyurl", case=False, na=False))
    ]

    print(f"✅ Found {len(df_homoglyphs)} homoglyph/perturbation pairs.")

    if len(df_homoglyphs) == 0:
        print("⚠️ No perfect matches found. Widening search...")
        df_homoglyphs = merged[(merged[label_col] == 1) & (merged['len_att'] > 100)]

    # Pick 10 Random Samples
    n = min(10, len(df_homoglyphs))
    samples = df_homoglyphs.sample(n, random_state=42)

    # Save to File
    with open("FINAL_PROFESSOR_SAMPLES.txt", "w", encoding="utf-8") as f:
        f.write("=== 10 READABILITY SAMPLES (HOMOGLYPHS) ===\n")
        f.write("These show the SAME email with text distortions.\n\n")
        
        i = 1
        for idx, row in samples.iterrows():
            f.write(f"--- PAIR #{i} ---\n")
            f.write(f"[ORIGINAL]:\n{row[orig_col]}\n")
            f.write("-" * 20 + "\n")
            f.write(f"[MODIFIED]:\n{row[att_col]}\n")
            f.write("=" * 50 + "\n\n")
            i += 1

    print("✅ SUCCESS! Run 'cat FINAL_PROFESSOR_SAMPLES.txt'")

except Exception as e:
    print(f"❌ Error: {e}")
