import pandas as pd


ATTACK_FILE = 'data/adversarial_strength_50pct.csv'
MASTER_FILE = 'data/adversarial_benchmark_dataset.csv'

try:
    print("📂 Loading data...")
    df_attacks = pd.read_csv(ATTACK_FILE)
    df_master = pd.read_csv(MASTER_FILE)

    
    merged = pd.merge(df_attacks, df_master, on='original_email_id', how='inner', suffixes=('_att', '_orig'))

    
    att_col = 'attacked_text_att'
    orig_col = 'original_text'
    label_col = 'original_label_att' 

    
    df_clean = merged[
        (merged[label_col] == 1) & 
        (~merged[att_col].str.contains("tinyurl", case=False, na=False)) & 
        (~merged[att_col].str.contains("bit.ly", case=False, na=False)) & 
        (merged[att_col].str.len() > 100)
    ]

    print(f"✅ Found {len(df_clean)} valid phishing pairs.")

    
    n = min(10, len(df_clean))
    samples = df_clean.sample(n, random_state=42)

    
    with open("REAL_USER_STUDY_PAIRS.txt", "w", encoding="utf-8") as f:
        f.write("=== 10 VALID ADVERSARIAL PAIRS (PHISHING ONLY) ===\n")
        f.write("These compare the ORIGINAL Phishing email vs. the ATTACKED version.\n\n")
        
        i = 1
        for idx, row in samples.iterrows():
            f.write(f"--- PAIR 
            f.write(f"[ORIGINAL PHISHING]:\n{row[orig_col]}\n")
            f.write("-" * 20 + "\n")
            f.write(f"[MODIFIED (ATTACK)]:\n{row[att_col]}\n")
            f.write("=" * 50 + "\n\n")
            i += 1

    print("✅ SUCCESS! Run 'cat REAL_USER_STUDY_PAIRS.txt' to view them.")

except Exception as e:
    print(f"❌ Error: {e}")
