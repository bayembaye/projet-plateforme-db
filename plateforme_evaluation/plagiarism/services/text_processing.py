import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging
logger = logging.getLogger(__name__)

def preprocess_text(text):
    if not text or not isinstance(text, str):
        return ""
    
    try:
        text = text.lower()
        text = re.sub(r'\d+', '', text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        tokens = word_tokenize(text)
        return ' '.join(tokens)
    except Exception as e:
        logger.error(f"Erreur prétraitement: {str(e)}")
        return ""