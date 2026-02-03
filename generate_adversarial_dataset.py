import pandas as pd
import random
import os
import tqdm # For a nice progress bar

# Import all our attack functions from the 'attacks' folder
from attacks.char_attacks import apply_homoglyph_attack, apply_leetspeak_attack, apply_zero_width_attack
from attacks.url_attacks import get_urls, apply_fake_domain_attack, apply_shortened_link_attack
from attacks.paraphrase_attacks import apply_paraphrase_attack
from attacks.prompt_injection import apply_prompt_injection_attack
from attacks.noise_insertion import apply_noise_insertion_attack

# --- Configuration ---
CLEAN_TEST_SET_PATH = 'data/splits/X_test.csv'
CLEAN_TEST_LABELS_PATH = 'data/splits/y_test.csv'
OUTPUT_FILE_PATH = 'data/adversarial_benchmark_dataset.csv'
TARGET_DATASET_SIZE = 5000 # As per your plan
# --- End Configuration ---

def main():
    print(f"🚀 Starting adversarial dataset generation...")

    # Load the clean test data
    try:
        X_test = pd.read_csv(CLEAN_TEST_SET_PATH).squeeze("columns").astype(str)
        y_test = pd.read_csv(CLEAN_TEST_LABELS_PATH).squeeze("columns")
    except FileNotFoundError:
        print(f"❌ ERROR: Clean test set not found at '{CLEAN_TEST_SET_PATH}'.")
        return

    # List of all available attack functions
    # We balance the list to control how often each attack is used
    # Paraphrase is slow, so we might include it less, but for now, let's keep it simple
    attack_functions = {
        'homoglyph': apply_homoglyph_attack,
        'leetspeak': apply_leetspeak_attack,
        'zero_width': apply_zero_width_attack,
        'fake_domain': apply_fake_domain_attack, # This one needs a helper
        'url_shorten': apply_shortened_link_attack, # This one needs a helper
        'paraphrase': apply_paraphrase_attack,
        'prompt_injection': apply_prompt_injection_attack,
        'noise_insertion': apply_noise_insertion_attack,
    }
    
    attack_names = list(attack_functions.keys())
    adversarial_examples = []
    
    # Calculate how many passes we need to get close to our target size
    # (e.g., 5000 target / 1600 emails = 3.125 -> 4 passes)
    num_passes = (TARGET_DATASET_SIZE // len(X_test)) + 1
    
    print(f"Clean test set size: {len(X_test)}. Target adversarial size: {TARGET_DATASET_SIZE}.")
    print(f"Running {num_passes} passes over the data...")
    
    pbar = tqdm.tqdm(total=TARGET_DATASET_SIZE, desc="Generating Examples")
    example_count = 0
    
    for pass_num in range(num_passes):
        if example_count >= TARGET_DATASET_SIZE:
            break
            
        # We use the index as a reproducible original_email_id
        for email_id, (original_text, original_label) in enumerate(zip(X_test, y_test)):
            if example_count >= TARGET_DATASET_SIZE:
                break
            
            # Use a reproducible seed for each unique example
            seed = (email_id * (pass_num + 1)) + 42
            random.seed(seed)
            
            # Randomly select an attack and strength
            attack_name = random.choice(attack_names)
            attack_strength = random.choice([0.1, 0.3, 0.5]) # 10%, 30%, 50%
            
            attacked_text = original_text
            
            # --- Apply the chosen attack ---
            try:
                if attack_name == 'paraphrase':
                    # Paraphrase is very slow, log it
                    # print(f"\nApplying paraphrase to email {email_id}...")
                    attacked_text = apply_paraphrase_attack(original_text, attack_strength=attack_strength, seed=seed)
                
                elif attack_name in ['fake_domain', 'url_shorten']:
                    # These attacks need to find URLs first
                    urls = get_urls(original_text)
                    if not urls: 
                        continue # Skip if no URLs to attack
                    
                    # Attack one random URL in the email
                    url_to_attack = random.choice(urls)
                    
                    if attack_name == 'fake_domain':
                        attacked_url = apply_fake_domain_attack(url_to_attack, seed=seed)
                    else: # url_shorten
                        attacked_url = apply_shortened_link_attack(url_to_attack, seed=seed)
                    
                    attacked_text = original_text.replace(url_to_attack, attacked_url, 1)
                
                elif attack_name in ['prompt_injection', 'noise_insertion']:
                    # These don't use 'strength'
                    attacked_text = attack_functions[attack_name](original_text, seed=seed)
                
                else: # char_attacks
                    attacked_text = attack_functions[attack_name](original_text, attack_strength=attack_strength, seed=seed)
                
                # If the attack did something, store it
                if attacked_text != original_text:
                    adversarial_examples.append({
                        'original_email_id': email_id,
                        'original_text': original_text,
                        'attacked_text': attacked_text,
                        'attack_type': attack_name,
                        'attack_strength': attack_strength if attack_name not in ['prompt_injection', 'noise_insertion'] else 'n/a',
                        'random_seed': seed,
                        'original_label': original_label
                    })
                    example_count += 1
                    pbar.update(1)
            
            except Exception as e:
                print(f"\nERROR applying attack {attack_name} to email {email_id}: {e}")

    pbar.close()
    
    # Convert list of dicts to a DataFrame
    df_adversarial = pd.DataFrame(adversarial_examples)
    
    # Save to CSV
    df_adversarial.to_csv(OUTPUT_FILE_PATH, index=False)
    
    print(f"\n✅ Success! Generated {len(df_adversarial)} adversarial examples.")
    print(f"Benchmark dataset saved to: {OUTPUT_FILE_PATH}")


if __name__ == "__main__":
    # Install tqdm if it's not already
    try:
        import tqdm
    except ImportError:
        print("Installing 'tqdm' for progress bars...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
        import tqdm
        
    main()
