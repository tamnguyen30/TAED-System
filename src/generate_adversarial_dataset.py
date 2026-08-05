import pandas as pd
import random
import os
import tqdm

from attacks.char_attacks import apply_homoglyph_attack, apply_leetspeak_attack, apply_zero_width_attack
from attacks.url_attacks import get_urls, apply_fake_domain_attack, apply_shortened_link_attack
from attacks.paraphrase_attacks import apply_paraphrase_attack
from attacks.prompt_injection import apply_prompt_injection_attack
from attacks.noise_insertion import apply_noise_insertion_attack


CLEAN_TEST_SET_PATH = 'data/splits/X_test_ccs.csv'
CLEAN_TEST_LABELS_PATH = 'data/splits/y_test_ccs.csv'
OUTPUT_FILE_PATH = 'data/adversarial_benchmark_dataset_ccs.csv'
TARGET_DATASET_SIZE = 20000


def main():
    print(f"Starting adversarial dataset generation...")

    try:
        X_test = pd.read_csv(CLEAN_TEST_SET_PATH).squeeze("columns").astype(str)
        y_test = pd.read_csv(CLEAN_TEST_LABELS_PATH).squeeze("columns")
    except FileNotFoundError:
        print(f"ERROR: Clean test set not found at '{CLEAN_TEST_SET_PATH}'.")
        return

    attack_functions = {
        'homoglyph': apply_homoglyph_attack,
        'leetspeak': apply_leetspeak_attack,
        'zero_width': apply_zero_width_attack,
        'fake_domain': apply_fake_domain_attack,
        'url_shorten': apply_shortened_link_attack,
        'paraphrase': apply_paraphrase_attack,
        'prompt_injection': apply_prompt_injection_attack,
        'noise_insertion': apply_noise_insertion_attack,
    }

    attack_names = list(attack_functions.keys())
    adversarial_examples = []

    num_passes = (TARGET_DATASET_SIZE // len(X_test)) + 1

    print(f"Clean test set size: {len(X_test)}. Target: {TARGET_DATASET_SIZE}.")
    print(f"Running {num_passes} passes...")

    pbar = tqdm.tqdm(total=TARGET_DATASET_SIZE, desc="Generating Examples")
    example_count = 0

    for pass_num in range(num_passes):
        if example_count >= TARGET_DATASET_SIZE:
            break

        for email_id, (original_text, original_label) in enumerate(zip(X_test, y_test)):
            if example_count >= TARGET_DATASET_SIZE:
                break

            seed = (email_id * (pass_num + 1)) + 42
            random.seed(seed)

            attack_name = random.choice(attack_names)
            attack_strength = random.choice([0.1, 0.3, 0.5])

            attacked_text = original_text

            try:
                if attack_name == 'paraphrase':
                    attacked_text = apply_paraphrase_attack(
                        original_text, attack_strength=attack_strength, seed=seed
                    )

                elif attack_name in ['fake_domain', 'url_shorten']:
                    urls = get_urls(original_text)
                    if not urls:
                        continue
                    url_to_attack = random.choice(urls)
                    if attack_name == 'fake_domain':
                        attacked_url = apply_fake_domain_attack(url_to_attack, seed=seed)
                    else:
                        attacked_url = apply_shortened_link_attack(url_to_attack, seed=seed)
                    attacked_text = original_text.replace(url_to_attack, attacked_url, 1)

                elif attack_name in ['prompt_injection', 'noise_insertion']:
                    attacked_text = attack_functions[attack_name](original_text, seed=seed)

                else:
                    attacked_text = attack_functions[attack_name](
                        original_text, attack_strength=attack_strength, seed=seed
                    )

                if attacked_text != original_text:
                    adversarial_examples.append({
                        'original_email_id': email_id,
                        'original_text': original_text,
                        'attacked_text': attacked_text,
                        'attack_type': attack_name,
                        'attack_strength': attack_strength if attack_name not in [
                            'prompt_injection', 'noise_insertion'
                        ] else 'n/a',
                        'random_seed': seed,
                        'original_label': original_label
                    })
                    example_count += 1
                    pbar.update(1)

                    
                    if example_count % 1000 == 0:
                        df_temp = pd.DataFrame(adversarial_examples)
                        df_temp.to_csv(OUTPUT_FILE_PATH, index=False)
                        print(f"\n Checkpoint saved at {example_count} examples")

            except Exception as e:
                print(f"\nERROR applying attack {attack_name} to email {email_id}: {e}")

    pbar.close()

    df_adversarial = pd.DataFrame(adversarial_examples)
    df_adversarial.to_csv(OUTPUT_FILE_PATH, index=False)

    print(f"\n Success! Generated {len(df_adversarial)} adversarial examples.")
    print(f"Saved to: {OUTPUT_FILE_PATH}")

    
    print("\nAttack type distribution:")
    print(df_adversarial['attack_type'].value_counts())


if __name__ == "__main__":
    try:
        import tqdm
    except ImportError:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
        import tqdm

    main()