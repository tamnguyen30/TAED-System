import pandas as pd

# Files
ATTACK_FILE = 'data/adversarial_strength_50pct.csv'
MASTER_FILE = 'data/adversarial_benchmark_dataset.csv'

try:
    print("📂 Loading data...")
    df_attacks = pd.read_csv(ATTACK_FILE)
    df_master = pd.read_csv(MASTER_FILE)

    # Merge
    print("🔗 Merging files...")
    merged = pd.merge(df_attacks, df_master, on='original_email_id', how='inner', suffixes=('_att', '_orig'))

    # DYNAMIC COLUMN FINDER (The Fix)
    # 1. Find the Attack Text Column
    att_col = None
    for col in ['attacked_text', 'attacked_text_att', 'attacked_text_x', 'text_att']:
        if col in merged.columns:
            att_col = col
            break
            
    # 2. Find the Original Text Column
    orig_col = None
    for col in ['original_text', 'text', 'body', 'text_original', 'clean_text', 'original_text_orig', 'text_orig']:
        if col in merged.columns:
            orig_col = col
            break

    if not att_col or not orig_col:
        print(f"❌ Error: Could not find columns. Available: {list(merged.columns)}")
        exit()

    print(f"✅ Found Attack Column: {att_col}")
    print(f"✅ Found Original Column: {orig_col}")

    # FILTER OUT JUNK (Remove tinyurl, bit.ly, and short texts)
    df_clean = merged[
        (~merged[att_col].str.contains("tinyurl", case=False, na=False)) & 
        (~merged[att_col].str.contains("bit.ly", case=False, na=False)) & 
        (merged[att_col].str.len() > 150)  # Min length 150 chars
    ]

    # Pick 10 Random Samples
    n = min(10, len(df_clean))
    if n == 0:
        print("⚠️ No samples passed the filter! Creating file with unfiltered samples instead.")
        samples = merged.sample(10, random_state=42)
    else:
        samples = df_clean.sample(n, random_state=42)

    # Save to File
    with open("FINAL_10_PAIRS.txt", "w", encoding="utf-8") as f:
        f.write("=== 10 ADVERSARIAL PAIRS FOR USER STUDY ===\n")
        f.write("Use these to show that attacks are readable.\n\n")
        
        i = 1
        for idx, row in samples.iterrows():
            f.write(f"--- PAIR #{i} ---\n")
            f.write(f"[ORIGINAL]:\n{row[orig_col]}\n")
            f.write("-" * 20 + "\n")
            f.write(f"[MODIFIED]:\n{row[att_col]}\n")
            f.write("=" * 50 + "\n\n")
            i += 1

    print("✅ SUCCESS! Run 'cat FINAL_10_PAIRS.txt' to see the emails.")

except Exception as e:
    print(f"❌ Error: {e}")
