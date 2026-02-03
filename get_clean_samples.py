import pandas as pd
import os

# Files
ATTACK_FILE = 'data/adversarial_strength_50pct.csv'
MASTER_FILE = 'data/adversarial_benchmark_dataset.csv'

try:
    # 1. Load Data
    df_attacks = pd.read_csv(ATTACK_FILE)
    df_master = pd.read_csv(MASTER_FILE)

    # 2. Merge to get Original Text
    # We try to match ID columns
    merged = pd.merge(df_attacks, df_master, on='original_email_id', how='inner', suffixes=('_att', '_orig'))

    # Find the text columns
    att_col = 'attacked_text'
    # Look for original text column
    orig_col = next((c for c in ['original_text', 'text', 'body', 'text_original', 'clean_text'] if c in df_master.columns), None)
    
    if not orig_col:
        # Fallback: try to find it in the merged columns
        orig_col = next((c for c in merged.columns if c.startswith('text') or c.startswith('original_text')), None)

    if not orig_col: 
        print("❌ Error: Couldn't find original text column. Copying attacks only.")
        orig_col = att_col # Fallback

    # 3. FILTER OUT JUNK (The important part)
    # We remove "tinyurl", "bit.ly", and very short emails
    df_clean = merged[
        (~merged[att_col].str.contains("tinyurl", case=False, na=False)) & 
        (~merged[att_col].str.contains("bit.ly", case=False, na=False)) & 
        (merged[att_col].str.len() > 100)  # Must be longer than 100 chars
    ]

    # 4. Pick 10 Random Samples
    samples = df_clean.sample(10, random_state=42)

    # 5. Save to File
    with open("FINAL_10_PAIRS.txt", "w", encoding="utf-8") as f:
        f.write("=== 10 ADVERSARIAL PAIRS FOR PROFESSOR ===\n\n")
        i = 1
        for idx, row in samples.iterrows():
            f.write(f"PAIR #{i}\n")
            f.write("TYPE: Adversarial Text Manipulation\n")
            f.write("-" * 20 + "\n")
            f.write(f"[ORIGINAL EMAIL]:\n{row[orig_col]}\n")
            f.write("-" * 20 + "\n")
            f.write(f"[MODIFIED EMAIL (ATTACK)]:\n{row[att_col]}\n")
            f.write("=" * 50 + "\n\n")
            i += 1

    print("✅ SUCCESS! 10 Clean Pairs saved to 'FINAL_10_PAIRS.txt'")

except Exception as e:
    print(f"❌ Error: {e}")
