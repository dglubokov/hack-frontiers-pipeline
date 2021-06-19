import re
import unicodedata

import nltk
from nltk.stem import WordNetLemmatizer
from textblob import Word
from bs4 import BeautifulSoup


STOPWORDS = nltk.corpus.stopwords.words('english')

def strip_html_tags(text):
    """Removing html Tags."""
    soup = BeautifulSoup(text, "html.parser")
    [s.extract() for s in soup(['iframe', 'script'])]
    stripped_text = soup.get_text()
    stripped_text = re.sub(r'[\r|\n|\r\n]+', '\n', stripped_text)
    return stripped_text

def remove_accented_chars(text):
    """Expanding Contractions."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return text

def remove_special_characters(text, remove_digits=False):
    """Removing Special Characters."""
    pattern = r'[^a-zA-Z0-9\s]' if not remove_digits else r'[^a-zA-Z\s]'
    text = re.sub(pattern, "", text)
    return text

def correct_spell(text):
    """Spelling Correction."""
    words = nltk.word_tokenize(text)
    corrected_words = [Word(word).correct() for word in words]
    return ' '.join(corrected_words)

def remove_stopwords(text, is_lower_case=False):
    words = nltk.word_tokenize(text)
    words = [word.strip() for word in words]
    if is_lower_case:
        filtered_words = [word for word in words if word not in STOPWORDS]
    else:
        filtered_words = [
            word for word in words if word.lower() not in STOPWORDS
        ]
    return ' '.join(filtered_words)

def lemmatize_text(text):
    """Lemmatizing Text."""
    stemmer = WordNetLemmatizer()
    return [stemmer.lemmatize(word) for word in text]
