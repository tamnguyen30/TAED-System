import random


def apply_homoglyph_attack(email_text: str, attack_strength: float = 0.1, seed: int = 42) -> str:
    """
    Replaces a percentage of characters with visually similar characters (homoglyphs)
    using a predefined map.

    Args:
        email_text (str): The original email text.
        attack_strength (float): The percentage of eligible characters to replace (0.0 to 1.0).
        seed (int): Random seed for reproducibility.

    Returns:
        str: The email text with homoglyphs substituted.
    """
    random.seed(seed)

    # Simple predefined homoglyph map (add more if needed)
    homoglyph_map = {
        'o': ['0'], 'O': ['0'],
        'l': ['1'], 'I': ['1'], # Lowercase L, Uppercase I
        'a': ['@'], 'A': ['@'],
        'e': ['3'], 'E': ['3'],
        's': ['$'], 'S': ['$'],
        'i': ['!'],
        'g': ['9'], 'G': ['9']
    }

    eligible_chars = list(homoglyph_map.keys())

    # Find all character indices in the string that can be replaced
    possible_indices = [i for i, char in enumerate(email_text) if char in eligible_chars]

    # Determine how many characters to replace
    num_to_replace = int(len(possible_indices) * attack_strength)
    if num_to_replace == 0 and attack_strength > 0 and len(possible_indices) > 0:
        num_to_replace = 1 # Ensure at least one char is replaced if possible

    if num_to_replace > len(possible_indices):
        num_to_replace = len(possible_indices)

    indices_to_attack = random.sample(possible_indices, k=num_to_replace)

    attacked_chars = list(email_text)

    for i in indices_to_attack:
        original_char = attacked_chars[i]
        # Choose a random replacement from our predefined map
        if original_char in homoglyph_map:
             attacked_chars[i] = random.choice(homoglyph_map[original_char])

    return "".join(attacked_chars)

def apply_leetspeak_attack(email_text: str, attack_strength: float = 0.1, seed: int = 42) -> str:
    """
    Replaces a percentage of characters with common leetspeak substitutions.

    Args:
        email_text (str): The original email text.
        attack_strength (float): The percentage of eligible characters to replace (0.0 to 1.0).
        seed (int): Random seed for reproducibility.

    Returns:
        str: The email text with leetspeak substitutions.
    """
    random.seed(seed)

    # Define common leetspeak substitutions
    leetspeak_map = {
        'a': ['4', '@'], 'A': ['4', '@'],
        'e': ['3'], 'E': ['3'],
        'i': ['1', '!'], 'I': ['1', '!'],
        'o': ['0'], 'O': ['0'],
        's': ['5', '$'], 'S': ['5', '$'],
        't': ['7'], 'T': ['7'],
        'z': ['2'], 'Z': ['2'],
        'g': ['9', '6'], 'G': ['9', '6'],
        'b': ['8'], 'B': ['8']
    }

    eligible_chars = list(leetspeak_map.keys())

    # Find all character indices in the string that can be replaced
    possible_indices = [i for i, char in enumerate(email_text) if char in eligible_chars]

    # Determine how many characters to replace
    num_to_replace = int(len(possible_indices) * attack_strength)
    if num_to_replace == 0 and attack_strength > 0 and len(possible_indices) > 0:
        num_to_replace = 1 # Ensure at least one char is replaced if possible

    if num_to_replace > len(possible_indices):
        num_to_replace = len(possible_indices)

    indices_to_attack = random.sample(possible_indices, k=num_to_replace)

    attacked_chars = list(email_text)

    for i in indices_to_attack:
        original_char = attacked_chars[i]
        # Choose a random leetspeak replacement
        attacked_chars[i] = random.choice(leetspeak_map[original_char])

    return "".join(attacked_chars)

def apply_zero_width_attack(email_text: str, attack_strength: float = 0.05, seed: int = 42) -> str:
    """
    Inserts zero-width characters at random locations within the text.

    Args:
        email_text (str): The original email text.
        attack_strength (float): Probability of inserting a zero-width char between any two chars.
                                 (Note: Lower strength is recommended for this attack).
        seed (int): Random seed for reproducibility.

    Returns:
        str: The email text with zero-width characters inserted.
    """
    random.seed(seed)

    # Common zero-width characters
    zero_width_chars = [
        '\u200b',  # Zero Width Space
        '\u200c',  # Zero Width Non-Joiner
        '\u200d',  # Zero Width Joiner
        '\ufeff'   # Zero Width No-Break Space (also BOM)
    ]

    attacked_chars = []
    for char in email_text:
        attacked_chars.append(char)
        # Randomly decide whether to insert a zero-width char after the current char
        if random.random() < attack_strength:
            attacked_chars.append(random.choice(zero_width_chars))

    return "".join(attacked_chars)

# --- Test Block ---
if __name__ == "__main__":
    original_email = "paypal account security update: Please log in to your account at paypal.com to avoid suspension. Your password is secure."

    print("--- Homoglyph Attack Test ---")
    print(f"Original Text:\n{original_email}\n")

    # Apply the attack with 10% strength
    attacked_email_10 = apply_homoglyph_attack(original_email, attack_strength=0.1)
    print(f"Attacked Text (10% strength):\n{attacked_email_10}\n")

    # Apply the attack with 50% strength
    attacked_email_50 = apply_homoglyph_attack(original_email, attack_strength=0.5)
    print(f"Attacked Text (50% strength):\n{attacked_email_50}\n")

    print("\n--- Leetspeak Attack Test ---")
    # Apply the attack with 10% strength
    attacked_email_leet_10 = apply_leetspeak_attack(original_email, attack_strength=0.1)
    print(f"Attacked Text (10% strength):\n{attacked_email_leet_10}\n")

    # Apply the attack with 50% strength
    attacked_email_leet_50 = apply_leetspeak_attack(original_email, attack_strength=0.5)
    print(f"Attacked Text (50% strength):\n{attacked_email_leet_50}\n")

    print("\n--- Zero-Width Attack Test ---")
    # Apply the attack with a low strength (e.g., 5% probability between chars)
    # Note: These changes are invisible in most text editors!
    attacked_email_zw_5 = apply_zero_width_attack(original_email, attack_strength=0.05)
    print(f"Attacked Text (5% strength - invisible changes):\n{attacked_email_zw_5}\n")
    print(f"(Original length: {len(original_email)}, Attacked length: {len(attacked_email_zw_5)})")

    # You can try a higher strength, but it might become very noticeable in length
    attacked_email_zw_20 = apply_zero_width_attack(original_email, attack_strength=0.20)
    print(f"Attacked Text (20% strength - invisible changes):\n{attacked_email_zw_20}\n")
    print(f"(Original length: {len(original_email)}, Attacked length: {len(attacked_email_zw_20)})")
