import pandas as pd
import os

# 1. Load the Attacks (The 50% intensity ones)
ATTACK_FILE = 'data/adversarial_strength_50pct.csv'
# 2. Load the Master File (To find the original text)
MASTER_FILE = 'data/adversarial_benchmark_dataset.csv'

print(f"📂 Loading attack data from: {ATTACK_FILE}")
print(f"📂 Loading master data from: {MASTER_FILE}")

try:
    df_attacks = pd.read_csv(ATTACK_FILE)
    
    # Try to load master file to find the original text
    if os.path.exists(MASTER_FILE):
        df_master = pd.read_csv(MASTER_FILE)
        
        # Merge them on 'original_email_id' if possible
        if 'original_email_id' in df_attacks.columns and 'original_email_id' in df_master.columns:
            print("🔗 Merging files to find original text...")
            # We look for columns like 'text', 'body', 'original_text' in master
            text_col = next((c for c in ['original_text', 'text_original', 'clean_text', 'text', 'body'] if c in df_master.columns), None)
            
            if text_col:
                # Merge logic
                df_merged = pd.merge(df_attacks, df_master[['original_email_id', text_col]], on='original_email_id', how='left')
                df_merged = df_merged.rename(columns={text_col: 'original_text_found'})
                df_final = df_merged
            else:
                print("⚠️ Master file found, but no text column found in it.")
                df_final = df_attacks
        else:
            print("⚠️ ID columns don't match. Using Master file directly for samples.")
            df_final = df_master
    else:
        print("⚠️ Master file not found. We will just output the attacks.")
        df_final = df_attacks

    # Filter for Phishing (Label 1)
    if 'original_label' in df_final.columns:
        df_final = df_final[df_final['original_label'] == 1]

    # Pick 10 Random Samples
    n = min(10, len(df_final))
    samples = df_final.sample(n, random_state=42)
    
    # Define text columns to use
    orig_col = 'original_text_found' if 'original_text_found' in df_final.columns else 'text'
    if orig_col not in df_final.columns: orig_col = 'attacked_text' # Fallback
    
    attack_col = 'attacked_text'

    print(f"✅ Extracted {n} pairs. Saving to 'user_study_samples.txt'...")
    
    with open("user_study_samples.txt", "w", encoding="utf-8") as f:
        f.write("USER STUDY SAMPLES\n")
        f.write("==================\n\n")
        
        for idx, row in samples.iterrows():
            f.write(f"--- SAMPLE #{idx} ---\n")
            
            # ORIGINAl
            orig_text = row.get(orig_col, "N/A (Could not find original)")
            f.write(f"[ORIGINAL]:\n{orig_text}\n\n")
            
            # ATTACK
            attack_text = row.get(attack_col, "N/A")
            f.write(f"[MODIFIED]:\n{attack_text}\n")
            f.write("-" * 50 + "\n\n")

    print("DONE! Run 'cat user_study_samples.txt' to view them.")

except Exception as e:
    print(f"❌ Error: {e}")
