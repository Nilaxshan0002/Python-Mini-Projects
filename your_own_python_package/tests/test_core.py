import pytest
from mytool.core import clean_text, count_words

def test_clean_text_basic():
    assert clean_text("  Hello,   World!  ") == "Hello World"

def test_clean_text_empty():
    assert clean_text("") == ""

def test_clean_text_type_error():
    with pytest.raises(TypeError):
        clean_text(123)

def test_count_words():
    assert count_words("Hello World") == 2
    assert count_words("") == 0
    assert count_words("One") == 1