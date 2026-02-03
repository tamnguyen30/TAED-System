import re
import random
import tldextract
import string # Added import

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
        # Using extract function which returns a named tuple
        ext = tldextract.extract(url)
        domain = ext.domain
        subdomain = ext.subdomain
        suffix = ext.suffix
        full_domain = ext.fqdn # Fully qualified domain name (e.g., sub.domain.com)


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

        # Reconstruct the domain part
        new_fqdn_parts = []
        if subdomain:
            new_fqdn_parts.append(subdomain)
        if modified_domain:
             new_fqdn_parts.append(modified_domain)
        if suffix:
            new_fqdn_parts.append(suffix)
        new_fqdn = ".".join(new_fqdn_parts)


        # Replace the original fqdn with the new one in the URL
        # We need to be careful not to replace parts of the path if they match
        # Find the start and end of the FQDN within the URL
        url_parts = url.split(full_domain, 1)
        if len(url_parts) == 2:
             modified_url = url_parts[0] + new_fqdn + url_parts[1]
        else: # FQDN not found or at the end
             modified_url = url.replace(full_domain, new_fqdn, 1)


        return modified_url

    except Exception as e:
        # If tldextract fails or any error occurs, return the original URL
        # print(f"Error processing URL '{url}': {e}") # Optional: for debugging
        return url

def apply_shortened_link_attack(url: str, length: int = 6, seed: int = 42) -> str:
    """
    Replaces a URL with a fake shortened link placeholder.

    Args:
        url (str): The original URL (only used to know where to replace).
        length (int): The length of the random path component.
        seed (int): Random seed for reproducibility.

    Returns:
        str: A fake shortened link (e.g., "bit.ly/aBcDeF").
    """
    random.seed(seed)

    shorteners = ["bit.ly", "goo.gl", "tinyurl.com", "is.gd"] # Common shorteners
    chosen_shortener = random.choice(shorteners)

    # Generate a random path component (letters and digits)
    chars = string.ascii_letters + string.digits
    random_path = ''.join(random.choice(chars) for _ in range(length))

    return f"{chosen_shortener}/{random_path}"

# --- Test Block ---
if __name__ == "__main__":
    original_email = "Please log in to your account at https://paypal.com/login to avoid suspension. Also check www.microsoft.com for updates."

    print("--- URL Attack Test (Randomized: Fake Domain or Shortened Link) ---")
    print(f"Original Text:\n{original_email}\n")

    urls = get_urls(original_email)
    print(f"URLs found: {urls}\n")

    attacked_text = original_email
    seed_counter = 42 # Use different seeds for different URLs

    # Set seed for the choice of attack type for reproducibility
    random.seed(seed_counter)

    for url in urls:
        # Randomly choose between fake domain or shortening
        attack_type = random.choice(['fake_domain', 'shorten'])

        if attack_type == 'fake_domain':
            attacked_url = apply_fake_domain_attack(url, seed=seed_counter)
            print(f"Applying Fake Domain: {url} -> {attacked_url}")
        else: # attack_type == 'shorten'
            attacked_url = apply_shortened_link_attack(url, seed=seed_counter)
            print(f"Applying Shortening: {url} -> {attacked_url}")

        attacked_text = attacked_text.replace(url, attacked_url, 1)
        seed_counter += 1 # Increment seed for next URL

    print(f"\nFull Attacked Text:\n{attacked_text}")
