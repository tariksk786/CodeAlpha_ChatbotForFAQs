import re
import string
import nltk

# Programmatic downloading of required NLTK resources to ensure zero-config setups
def download_nltk_resources():
    resources = ['punkt', 'stopwords', 'wordnet', 'omw-1.4']
    for resource in resources:
        try:
            if resource == 'punkt':
                nltk.data.find('tokenizers/punkt')
            elif resource == 'stopwords':
                nltk.data.find('corpora/stopwords')
            elif resource == 'wordnet':
                nltk.data.find('corpora/wordnet')
            elif resource == 'omw-1.4':
                nltk.data.find('corpora/omw-1.4')
        except LookupError:
            try:
                nltk.download(resource, quiet=True)
            except Exception as e:
                print(f"Error downloading NLTK resource {resource}: {e}")

# Run downloader on module import
download_nltk_resources()

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer

class NLPPreprocessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = set()

    def clean_text(self, text):
        """Converts text to lowercase and removes punctuation."""
        if not text:
            return ""
        # Lowercase conversion
        text = text.lower().strip()
        # Remove punctuation by replacing with space (prevents merging words)
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        text = text.translate(translator)
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def tokenize(self, text):
        """Splits text into words/tokens."""
        if not text:
            return []
        try:
            return word_tokenize(text)
        except Exception:
            # Fallback simple split if NLTK fails
            return text.split()

    def remove_stopwords(self, tokens):
        """Removes common stopwords from token list."""
        return [token for token in tokens if token not in self.stop_words]

    def lemmatize(self, tokens):
        """Applies lemmatization to tokens (grouping inflections)."""
        return [self.lemmatizer.lemmatize(token) for token in tokens]

    def stem(self, tokens):
        """Applies stemming to tokens (reducing to root word)."""
        return [self.stemmer.stem(token) for token in tokens]

    def preprocess(self, text, use_stemming=False):
        """
        Executes complete text preprocessing pipeline:
        1. Clean text (lowercase & punctuation removal)
        2. Tokenization
        3. Stopword removal
        4. Lemmatization
        5. Stemming (optional)
        Returns preprocessed text joined back as a clean string.
        """
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        filtered_tokens = self.remove_stopwords(tokens)
        processed_tokens = self.lemmatize(filtered_tokens)
        
        if use_stemming:
            processed_tokens = self.stem(processed_tokens)
            
        return " ".join(processed_tokens)
