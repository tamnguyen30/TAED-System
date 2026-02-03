import pandas as pd

# Files
ATTACK_FILE = 'data/adversarial_strength_50pct.csv'
MASTER_FILE = 'data/adversarial_benchmark_dataset.csv'

try:
    print("📂 Loading data...")
    df_attacks = pd.read_csv(ATTACK_FILE)
    df_master = pd.read_csv(MASTER_FILE)

    # Merge to match Attacks with Originals
    print("🔗 Merging files...")
    merged = pd.merge(df_attacks, df_master, on='original_email_id', how='inner', suffixes=('_att', '_orig'))

    # Identify Label Column (to filter for Phishing only)
    label_col = next((c for c in ['label', 'original_label', 'label_orig'] if c in merged.columns), None)
    
    # Identify Text Columns
    att_col = next((c for c in ['attacked_text', 'attacked_text_att', 'text_att'] if c in merged.columns), None)
    orig_col = next((c for c in ['original_text', 'text', 'body', 'text_original', 'clean_text'] if c in merged.columns), None)

    if not label_col or not att_col or not orig_col:
        print(f"❌ Error: Missing columns. Found: {list(merged.columns)}")
        exit()

    # --- CRITICAL FILTERS ---
    # 1. Must be PHISHING (Label=1)
    # 2. Must NOT be a tinyurl/bit.ly link (Too simple)
    # 3. Must be decent length (>100 chars)
    
    df_clean = merged[
        (merged[label_col] == 1) & 
        (~merged[att_col].str.contains("tinyurl", case=False, na=False)) & 
        (~merged[att_col].str.contains("bit.ly", case=False, na=False)) & 
        (merged[att_col].str.len() > 100)
    ]

    print(f"✅ Found {len(df_clean)} valid phishing pairs.")

    # Pick 10 Random Samples
    n = min(10, len(df_clean))
    samples = df_clean.sample(n, random_state=42)

    # Save to File
    with open("REAL_USER_STUDY_PAIRS.txt", "w", encoding="utf-8") as f:
        f.write("=== 10 VALID ADVERSARIAL PAIRS (PHISHING ONLY) ===\n")
        f.write("Note: These show the Phishing email BEFORE and AFTER perturbation.\n\n")
        
        i = 1
        for idx, row in samples.iterrows():
            f.write(f"--- PAIR #{i} ---\n")
            f.write(f"[ORIGINAL PHISHING]:\n{row[orig_col]}\n")
            f.write("-" * 20 + "\n")
            f.write(f"[MODIFIED (ATTACK)]:\n{row[att_col]}\n")
            f.write("=" * 50 + "\n\n")
            i += 1

    print("✅ SUCCESS! Run 'cat REAL_USER_STUDY_PAIRS.txt'")

except Exception as e:
    print(f"❌ Error: {e}")
