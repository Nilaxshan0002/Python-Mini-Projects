# Your Own Python Package (mytool)

A reusable Python library that solves a specific developer problem.

## Features

- 🚀 **Fast**: Optimized for performance.
- 🧹 **Clean**: Removes extra whitespace and punctuation from text.
- 🔢 **Accurate**: Counts words reliably.

## Installation

```bash
pip install your-own-python-package

from mytool import clean_text, count_words

text = "  Hello,   World!  "

# Clean the text
cleaned = clean_text(text)
print(cleaned)  # Output: "Hello World"

# Count words
count = count_words(cleaned)
print(count)    # Output: 2