import pandas as pd
import random
import os
import tqdm 
import sys
import subprocess

# --- Import all our attack functions ---
# We wrap imports in try/except in case a file is missing
try:
    from attacks.char_attacks import apply_homoglyph_attack, apply_leetspeak_attack, apply_zero_width_attack
    from attacks.url_attacks import get_urls, apply_fake_domain_attack, apply_shortened_link_attack
    from attacks.paraphrase_attacks import apply_paraphrase_attack
    from attacks.prompt_injection import apply_prompt_injection_attack
    from attacks.noise_insertion import apply_noise_insertion_attack
except ImportError as e:
    print(f"❌ ERROR: Could not import attack functions from 'attacks/' folder.")
    print(f"Details: {e}")
    print("Please ensure all attack scripts (char_attacks.py, etc.) exist.")
    sys.exit(1)


# --- Configuration ---
CLEAN_TEST_SET_PATH = 'data/splits/X_test.csv'
CLEAN_TEST_LABELS_PATH = 'data/splits/y_test.csv'
STRENGTH_LEVELS = [0.1, 0.3, 0.5] # 10%, 30%, 50%
# --- End Configuration ---

def main():
    print(f"🚀 Starting Attack Strength Dataset Generation...")
    
    # Load the clean test data
    try:
        X_test = pd.read_csv(CLEAN_TEST_SET_PATH).squeeze("columns").astype(str)
        y_test = pd.read_csv(CLEAN_TEST_LABELS_PATH).squeeze("columns")
    except FileNotFoundError:
        print(f"❌ ERROR: Clean test set not found at '{CLEAN_TEST_SET_PATH}'.")
        return

    # Filter for phishing emails only, as per your goal
    phishing_mask = (y_test == 1)
    X_test_phishing = X_test[phishing_mask].reset_index(drop=True)
    y_test_phishing = y_test[phishing_mask].reset_index(drop=True)
    print(f"Loaded {len(X_test_phishing)} clean phishing emails to be attacked.")


    attack_functions = {
        'homoglyph': apply_homoglyph_attack, 'leetspeak': apply_leetspeak_attack,
        'zero_width': apply_zero_width_attack, 'fake_domain': apply_fake_domain_attack, 
        'url_shorten': apply_shortened_link_attack, 'paraphrase': apply_paraphrase_attack,
        'prompt_injection': apply_prompt_injection_attack, 'noise_insertion': apply_noise_insertion_attack,
    }
    # These attacks don't use a % strength, so we'll apply them differently
    strengthless_attacks = ['prompt_injection', 'noise_insertion', 'url_shorten']
    
    
    for strength in STRENGTH_LEVELS:
        strength_percent = int(strength * 100)
        OUTPUT_FILE_PATH = f'data/adversarial_strength_{strength_percent}pct.csv'
        adversarial_examples = []
        
        print(f"\n--- Generating dataset for {strength_percent}% strength ---")
        
        # Create a progress bar
        pbar = tqdm.tqdm(total=len(X_test_phishing), desc=f"{strength_percent}% Strength")

        for email_id, original_text in enumerate(X_test_phishing):
            
            seed = (email_id * strength_percent) + 42
            random.seed(seed)
            
            # Randomly select an attack
            # We'll apply *one* attack per email for a clean comparison
            attack_name = random.choice(list(attack_functions.keys()))
            attack_func = attack_functions[attack_name]
            attacked_text = original_text
            
            # --- Apply the chosen attack ---
            try:
                if attack_name in strengthless_attacks:
                    # These attacks don't use 'strength'
                    attacked_text = attack_func(original_text, seed=seed)
                elif attack_name in ['fake_domain']:
                    # Special handling for URL attacks
                    urls = get_urls(original_text)
                    if not urls: 
                        pbar.update(1)
                        continue # Skip if no URLs to attack
                    url_to_attack = random.choice(urls)
                    attacked_url = apply_fake_domain_attack(url_to_attack, seed=seed)
                    attacked_text = original_text.replace(url_to_attack, attacked_url, 1)
                else: 
                    # For char_attacks and paraphrase, 'strength' is used
                    attacked_text = attack_func(original_text, attack_strength=strength, seed=seed)
                
                # Store it
                adversarial_examples.append({
                    'original_email_id': email_id,
                    'attacked_text': attacked_text,
                    'original_label': 1, # We only attack phishing emails
                    'attack_type': attack_name,
                    'attack_strength_pct': strength_percent,
                    'random_seed': seed,
                })
                pbar.update(1)
            
            except Exception as e:
                print(f"\nError applying attack {attack_name}: {e}") # Optional: for debugging
                pbar.update(1) # Still update progress bar on failure

        pbar.close()
        
        df_results = pd.DataFrame(adversarial_examples)
        df_results.to_csv(OUTPUT_FILE_PATH, index=False)
        print(f"  ✅ Saved {len(df_results)} examples to: {OUTPUT_FILE_PATH}")

if __name__ == "__main__":
    try:
        import tqdm # Ensure tqdm is available
    except ImportError:
        print("Installing 'tqdm'...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
    main()
