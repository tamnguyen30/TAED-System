import random

def apply_noise_insertion_attack(email_text: str, seed: int = 42) -> str:
    """
    Appends a block of benign, "noisy" text to the email.
    This could be a fake signature, a privacy disclaimer, or part of a forwarded email.

    Args:
        email_text (str): The original email text.
        seed (int): Random seed for reproducibility.

    Returns:
        str: The email text with a noisy block appended.
    """
    random.seed(seed)

    # A list of benign text blocks
    noise_blocks = [
        """
--
CONFIDENTIALITY NOTICE: This email and any attachments are for the
exclusive and confidential use of the intended recipient. If you are not
the intended recipient, please do not read, distribute, or take any
action in reliance on this message.
        """,
        """
--
John Smith
Senior Account Manager
MegaCorp Inc.
(123) 456-7890
        """,
        """
--- Forwarded Message ---
From: IT Support <support@company.com>
Date: Tue, 28 Oct 2025 10:00:00 -0500
Subject: System Maintenance

Please be advised of upcoming system maintenance...
        """
    ]

    chosen_noise = random.choice(noise_blocks)

    # Append the noise to the end of the email
    attacked_text = f"{email_text}\n\n{chosen_noise}"

    return attacked_text

# --- Test Block ---
if __name__ == "__main__":
    original_email = "Urgent: Your account is locked. Click here: www.fake-paypal.com to unlock it."

    print("--- Noise Insertion Attack Test ---")
    print(f"Original Text:\n{original_email}\n")

    # Apply the attack
    attacked_email = apply_noise_insertion_attack(original_email, seed=42)
    print(f"Attacked Text (with noise):\n{attacked_email}\n")
