import re

def clean_text(text: str) -> str:
    """Remove extra whitespace and punctuation from text."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove punctuation (keep basic characters)
    text = re.sub(r'[^\w\s]', '', text)
    return text

def count_words(text: str) -> int:
    """Count the number of words in the text."""
    if not text:
        return 0
    return len(text.split())