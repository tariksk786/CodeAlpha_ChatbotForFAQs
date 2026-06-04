from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class FAQVectorizer:
    def __init__(self, preprocessor):
        self.preprocessor = preprocessor
        # Use sublinear TF scaling to damp the effect of high-frequency words
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),  # Use both unigrams and bigrams
            sublinear_tf=True
        )
        self.faq_vectors = None
        self.faq_ids = []
        self.trained = False

    def train(self, faqs):
        """
        Trains/fits the vectorizer on the list of FAQs.
        faqs is a list of dictionaries: [{'id': 1, 'question': '...', 'answer': '...'}]
        """
        if not faqs:
            self.faq_vectors = None
            self.faq_ids = []
            self.trained = False
            return False

        # Preprocess all questions
        corpus = [self.preprocessor.preprocess(faq['question']) for faq in faqs]
        self.faq_ids = [faq['id'] for faq in faqs]

        # Verify if we have valid non-empty tokens in the corpus
        valid_corpus = [doc for doc in corpus if doc.strip()]
        if not valid_corpus:
            self.trained = False
            return False

        # Fit TF-IDF on preprocessed corpus
        try:
            self.faq_vectors = self.vectorizer.fit_transform(corpus)
            self.trained = True
            return True
        except Exception as e:
            print(f"Error training TF-IDF vectorizer: {e}")
            self.trained = False
            return False

    def transform(self, query):
        """Transforms a single query string into its TF-IDF vector representation."""
        if not self.trained or self.faq_vectors is None:
            return None
        preprocessed_query = self.preprocessor.preprocess(query)
        # Check if the vectorizer has terms. If not, return None.
        if not preprocessed_query.strip():
            return None
        try:
            return self.vectorizer.transform([preprocessed_query])
        except Exception:
            return None

    def get_vectors(self):
        return self.faq_vectors

    def get_ids(self):
        return self.faq_ids
