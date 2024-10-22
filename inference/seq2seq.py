import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load the tokenizer and model
model_name = "facebook/nllb-200-3.3B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Move the model to GPU if available
device = torch.device("cuda")
model = model.to(device)

# Example source and target languages
source_lang = "ara_Arab"  # Arabic
target_lang = "eng_Latn"  # English

tokenizer.src_lang = source_lang

def get_lang_token_id(tokenizer, lang_code):
    return tokenizer.convert_tokens_to_ids([f'<<{lang_code}>>'])[0]

# Set the source and target language by using the special tokens
# NLLB-200 uses <lang> tokens to denote source and target languages
def translate_text(text):
    target_lang_id = get_lang_token_id(tokenizer, target_lang)

    # Add special tokens for the target language
    inputs = tokenizer(text, return_tensors="pt", padding=True)
    inputs = inputs.to(device)
    
    # Set target language ID in tokenizer
    generated_tokens = model.generate(**inputs, forced_bos_token_id=target_lang_id)
    
    # Decode the generated tokens
    translated_text = tokenizer.decode(generated_tokens[0], skip_special_tokens=True)
    return translated_text

# Example sentence to translate
sentence = "مرحبا بكم"

# Perform translation
translated_sentence = translate_text(sentence)
print(f"Translated sentence: {translated_sentence}")
