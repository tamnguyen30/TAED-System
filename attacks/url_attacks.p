import re
import random
import tldextract

def get_urls(text: str) -> list[str]:
    """Finds all URLs in a given text."""
    # A simple regex to find URLs, can be improved for edge cases
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    return re.findall(url_pattern, text)

def apply_fake_domain_attack(url: str, seed: int = 42) -> str:
    """
    Applies small character edits (insertion, deletion, substitution)
    to the domain part of a URL to simulate typosquatting.

    Args:
        url (str): The original URL.
        seed (int): Random seed for reproducibility.

    Returns:
        str: The URL with a potentially modified domain.
    """
    random.seed(seed)

    try:
        ext = tldextract.extract(url)
        domain = ext.domain

        if not domain or len(domain) < 3: # Don't attack very short domains
            return url

        # Choose a random edit type
        edit_type = random.choice(['insert', 'delete', 'substitute'])
        edit_index = random.randint(0, len(domain) - 1)

        domain_chars = list(domain)

        if edit_type == 'insert':
            # Insert a random nearby character on the keyboard (simplified)
            insert_char = random.choice('qwertyuiopasdfghjklzxcvbnm')
            domain_chars.insert(edit_index, insert_char)
        elif edit_type == 'delete':
            # Delete the character at the index if domain is long enough
            if len(domain_chars) > 1:
                 del domain_chars[edit_index]
            else: # Don't delete if it's the only character
                 return url
        elif edit_type == 'substitute':
            # Substitute with a random nearby character
            substitute_char = random.choice('qwertyuiopasdfghjklzxcvbnm')
            # Ensure substitution is different
            while substitute_char == domain_chars[edit_index] and len(domain_chars) > 1 : # Avoid infinite loop if domain is single char
                 substitute_char = random.choice('qwertyuiopasdfghjklzxcvbnm')
            domain_chars[edit_index] = substitute_char

        modified_domain = "".join(domain_chars)

        # Reconstruct the URL
        modified_url = url.replace(ext.fqdn, f"{ext.subdomain}.{modified_domain}.{ext.suffix}".lstrip('.').rstrip('.'), 1)

        # Handle cases where subdomain might be empty
        if not ext.subdomain:
            modified_url = url.replace(ext.fqdn, f"{modified_domain}.{ext.suffix}".rstrip('.'), 1)


        return modified_url

    except Exception as e:
        # If tldextract fails or any error occurs, return the original URL
        print(f"Error processing URL '{url}': {e}") # Add error logging
        return url

# --- Test Block ---
if __name__ == "__main__":
    original_email = "Please log in to your account at https://paypal.com/login to avoid suspension. Also check www.microsoft.com for updates."

    print("--- Fake Domain Attack Test ---")
    print(f"Original Text:\n{original_email}\n")

    urls = get_urls(original_email)
    print(f"URLs found: {urls}\n")

    attacked_text = original_email
    seed_counter = 42 # Use different seeds for different URLs if needed

    for url in urls:
        attacked_url = apply_fake_domain_attack(url, seed=seed_counter)
