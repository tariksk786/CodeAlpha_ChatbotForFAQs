from nlp.preprocess import NLPPreprocessor
from nlp.vectorizer import FAQVectorizer
from nlp.intent import IntentDetector
from nlp.matcher import FAQMatcher

class FAQService:
    def __init__(self, db, config):
        self.db = db
        self.config = config
        
        # Initialize NLP Modules
        self.preprocessor = NLPPreprocessor()
        self.vectorizer = FAQVectorizer(self.preprocessor)
        self.intent_detector = IntentDetector()
        self.matcher = FAQMatcher(self.vectorizer, threshold=config.get('SIMILARITY_THRESHOLD', 0.40))
        
        # Load data and train vectorizer
        self.reload_and_train()

    def reload_and_train(self):
        """Fetches all FAQs from the database and trains the TF-IDF vectorizer."""
        faqs = self.db.get_all_faqs()
        success = self.vectorizer.train(faqs)
        if success:
            print("NLP: Vectorizer retrained successfully.")
        else:
            print("NLP: Vectorizer training skipped or failed (empty database).")
        return success

    def get_response(self, query):
        """
        Processes user query:
        1. Check conversational intents (greet, thanks, exit, identity, help)
        2. Clean and TF-IDF Match against database FAQs
        3. Logs the query in database
        4. Returns standardized response
        """
        query = query.strip() if query else ""
        if not query:
            return {
                "answer": "Please ask a question! I am here to help.",
                "confidence": 0,
                "related_questions": [],
                "query_id": None
            }

        # 1. Intent Detection
        intent_match = self.intent_detector.detect(query)
        if intent_match:
            # We don't log general conversational greets in the query logs to keep analytics pure,
            # or we log them with None matched_faq_id and 100% confidence. Let's log it to capture total queries.
            query_id = self.db.log_query(query, None, 1.0)
            return {
                "answer": intent_match['response'],
                "confidence": 100,
                "related_questions": [],
                "query_id": query_id,
                "intent": intent_match['intent']
            }

        # 2. Database Matching
        faqs = self.db.get_all_faqs()
        
        # Match using combined matcher
        match_result = self.matcher.match(query, faqs)

        # 3. Logging query
        matched_faq_id = None
        # Retrieve matched FAQ ID if confidence is above threshold
        if not match_result['low_confidence']:
            # Find the ID of the matched question
            for faq in faqs:
                if faq['question'] == match_result['matched_question']:
                    matched_faq_id = faq['id']
                    break

        # Log to db
        confidence_fraction = match_result['confidence'] / 100.0
        query_id = self.db.log_query(query, matched_faq_id, confidence_fraction)

        return {
            "answer": match_result['answer'],
            "confidence": match_result['confidence'],
            "related_questions": match_result['related_questions'],
            "query_id": query_id,
            "matched_question": match_result['matched_question'],
            "low_confidence": match_result['low_confidence']
        }

    # Proxy CRUD commands to trigger retraining automatically
    def add_faq(self, question, answer, category):
        faq_id = self.db.add_faq(question, answer, category)
        if faq_id:
            self.reload_and_train()
        return faq_id

    def update_faq(self, faq_id, question, answer, category):
        success = self.db.update_faq(faq_id, question, answer, category)
        if success:
            self.reload_and_train()
        return success

    def delete_faq(self, faq_id):
        success = self.db.delete_faq(faq_id)
        if success:
            self.reload_and_train()
        return success

    def bulk_import_faqs(self, faq_list):
        """Imports list of FAQs and retrains once at the end."""
        imported_count = 0
        for faq in faq_list:
            q = faq.get('question')
            a = faq.get('answer')
            c = faq.get('category', 'General')
            if q and a:
                self.db.add_faq(q, a, c)
                imported_count += 1
        if imported_count > 0:
            self.reload_and_train()
        return imported_count
