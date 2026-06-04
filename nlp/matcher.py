import difflib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class FAQMatcher:
    def __init__(self, vectorizer, threshold=0.40):
        """
        threshold is a float between 0.0 and 1.0.
        """
        self.vectorizer = vectorizer
        self.threshold = threshold

    def match(self, query, faqs):
        """
        Matches user query against a list of FAQs.
        faqs: list of dicts: [{'id': 1, 'question': '...', 'answer': '...', 'category': '...'}]
        Returns dict:
        {
            "answer": str,
            "matched_question": str,
            "confidence": int (0-100),
            "related_questions": list of strings,
            "low_confidence": bool
        }
        """
        if not faqs:
            return {
                "answer": "I'm sorry, I don't have any FAQs in my database yet.",
                "matched_question": None,
                "confidence": 0,
                "related_questions": [],
                "low_confidence": True
            }

        query_lower = query.lower().strip()

        # 1. Check for exact matching (case-insensitive, ignoring spacing)
        for faq in faqs:
            faq_q_lower = faq['question'].lower().strip()
            if query_lower == faq_q_lower:
                # Compile suggestions (other questions in database)
                related = [f['question'] for f in faqs if f['id'] != faq['id']][:3]
                return {
                    "answer": faq['answer'],
                    "matched_question": faq['question'],
                    "confidence": 100,
                    "related_questions": related,
                    "low_confidence": False
                }

        # 2. Vectorize the query
        query_vector = self.vectorizer.transform(query)
        faq_vectors = self.vectorizer.get_vectors()

        scores = []
        for i, faq in enumerate(faqs):
            # Calculate Cosine Similarity if vectorizer is trained and vector exists
            cosine_score = 0.0
            if self.vectorizer.trained and query_vector is not None and faq_vectors is not None:
                try:
                    # Cosine similarity between query vector and i-th FAQ vector
                    cosine_score = float(cosine_similarity(query_vector, faq_vectors[i])[0][0])
                except Exception:
                    cosine_score = 0.0

            # Calculate Fuzzy String Matching Ratio
            # difflib.SequenceMatcher returns a value between 0.0 and 1.0
            fuzzy_score = difflib.SequenceMatcher(None, query_lower, faq['question'].lower().strip()).ratio()

            # Combine scores (70% weight TF-IDF, 30% weight fuzzy)
            # If TF-IDF didn't produce vector (e.g. all words are stopwords), rely purely on fuzzy matching
            if cosine_score == 0.0:
                combined_score = fuzzy_score * 0.8  # slightly penalize if no word matches TF-IDF
            else:
                combined_score = (cosine_score * 0.70) + (fuzzy_score * 0.30)

            scores.append((combined_score, faq))

        # Sort by combined score descending
        scores.sort(key=lambda x: x[0], reverse=True)

        best_score, best_faq = scores[0]
        confidence = int(round(best_score * 100))

        # Compile suggestions (up to 3 other top scored items)
        related_questions = []
        for score, faq in scores[1:4]:
            if score > 0.1:  # Only suggest items with some minimal relevance
                related_questions.append(faq['question'])

        # If we couldn't get enough relevant suggestions, pad with general database questions
        if len(related_questions) < 3:
            for faq in faqs:
                if faq['id'] != best_faq['id'] and faq['question'] not in related_questions:
                    related_questions.append(faq['question'])
                    if len(related_questions) >= 3:
                        break

        # Check if confidence meets threshold
        low_confidence = best_score < self.threshold

        if low_confidence:
            fallback_answer = (
                "I'm not completely sure about that. Could you please rephrase your question? "
                "Here are some questions that might be relevant:"
            )
            return {
                "answer": fallback_answer,
                "matched_question": best_faq['question'],
                "confidence": confidence,
                "related_questions": related_questions,
                "low_confidence": True
            }
        else:
            return {
                "answer": best_faq['answer'],
                "matched_question": best_faq['question'],
                "confidence": confidence,
                "related_questions": related_questions,
                "low_confidence": False
            }
