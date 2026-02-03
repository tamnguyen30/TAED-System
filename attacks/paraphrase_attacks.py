import random
import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# --- Global variables for model and tokenizer ---
try:
    # Use a T5 model fine-tuned for paraphrasing
    _paraphrase_model_name = "humarin/chatgpt_paraphraser_on_T5_base"
    _paraphrase_tokenizer = AutoTokenizer.from_pretrained(_paraphrase_model_name)
    _paraphrase_model = AutoModelForSeq2SeqLM.from_pretrained(_paraphrase_model_name)
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _paraphrase_model.to(_device)
    print(f"Paraphrase model ({_paraphrase_model_name}) loaded successfully on {_device}.")
except Exception as e:
    print(f"Warning: Could not load paraphrase model ({_paraphrase_model_name}). Paraphrase attack will not work. Error: {e}")
    _paraphrase_model = None
    _paraphrase_tokenizer = None
# --- End Global variables ---

def _paraphrase_sentence(sentence: str, max_length: int = 60) -> str:
    """Uses the loaded T5 Paraphrase model to generate paraphrases."""
    if not _paraphrase_model or not _paraphrase_tokenizer:
        return sentence

    # This model expects a specific prompt format
    text = "paraphrase: " + sentence + " </s>"
    encoding = _paraphrase_tokenizer.encode_plus(
        text,
        padding="longest",
        return_tensors="pt",
        max_length=512,
        truncation=True
    )
    input_ids, attention_mask = encoding["input_ids"].to(_device), encoding["attention_mask"].to(_device)

    try:
        _paraphrase_model.eval()
        with torch.no_grad():
            outputs = _paraphrase_model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_length=max_length + 20,
                num_beams=5,
                num_return_sequences=1,
                early_stopping=True,
                temperature=0.7,
                top_p=0.9,
                do_sample=True # Enable sampling
            )
        paraphrased = _paraphrase_tokenizer.decode(outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)

        if len(paraphrased) > 0 and paraphrased.lower() != sentence.lower():
            return paraphrased
        else:
            return sentence
    except Exception as e:
        print(f"Error during paraphrasing sentence '{sentence[:50]}...': {e}")
        return sentence

def apply_paraphrase_attack(email_text: str, attack_strength: float = 0.3, seed: int = 42) -> str:
    """
    Rewrites a percentage of sentences in the email text using the loaded model.
    """
    if not _paraphrase_model:
         print("Warning: Paraphrase model not loaded. Returning original text.")
         return email_text 

    random.seed(seed)

    sentences = re.split(r'([.!?])\s+', email_text.strip())
    reconstructed_sentences = []
    if sentences:
        reconstructed_sentences.append(sentences[0]) # First part
        for i in range(1, len(sentences) -1, 2):
            if i+1 < len(sentences):
                if sentences[i+1]:
                    reconstructed_sentences.append(sentences[i+1] + sentences[i])
            else: 
                 if i < len(sentences) and sentences[i]:
                    reconstructed_sentences.append(sentences[i])

    sentences_to_consider = [(i, s) for i, s in enumerate(reconstructed_sentences) if len(s.split()) > 3]

    if not sentences_to_consider:
        return email_text

    num_to_paraphrase = int(len(sentences_to_consider) * attack_strength)
    if num_to_paraphrase == 0 and attack_strength > 0 and len(sentences_to_consider) > 0:
        num_to_paraphrase = 1

    if num_to_paraphrase > len(sentences_to_consider):
        num_to_paraphrase = len(sentences_to_consider)

    indices_to_paraphrase_info = random.sample(sentences_to_consider, k=num_to_paraphrase)
    original_indices_to_paraphrase = {info[0] for info in indices_to_paraphrase_info}

    paraphrased_sentences = reconstructed_sentences[:] 

    print(f"Attempting to paraphrase {num_to_paraphrase} sentence(s)...")
    for original_index, original_sentence in sentences_to_consider:
         if original_index in original_indices_to_paraphrase:
            paraphrased = _paraphrase_sentence(original_sentence.strip()) 
            if paraphrased != original_sentence.strip(): 
                 print(f"  Original:    '{original_sentence[:80]}...'")
                 print(f"  Paraphrased: '{paraphrased[:80]}...'")
                 
                 original_full_sentence = reconstructed_sentences[original_index]
                 leading_space = original_full_sentence[:len(original_full_sentence) - len(original_full_sentence.lstrip())]
                 
                 trailing_chars = ""
                 match = re.search(r'[\s.!?]*$', original_full_sentence) 
                 if match:
                    trailing_chars = match.group(0)

                 paraphrased_sentences[original_index] = leading_space + paraphrased + trailing_chars

    return " ".join(paraphrased_sentences).strip() 


# --- Test Block ---
if __name__ == "__main__":
    original_email = "Urgent action required! Please log in to your bank account immediately at fake-bank.com to verify your recent transactions. Failure to do so may result in account suspension."

    print("--- Paraphrase Attack Test ---")
    print(f"Original Text:\n{original_email}\n")

    attacked_email_30 = apply_paraphrase_attack(original_email, attack_strength=0.3)
    print(f"\nAttacked Text (30% strength):\n{attacked_email_30}\n")

    attacked_email_100 = apply_paraphrase_attack(original_email, attack_strength=1.0, seed=43) 
    print(f"\nAttacked Text (100% strength):\n{attacked_email_100}\n")
