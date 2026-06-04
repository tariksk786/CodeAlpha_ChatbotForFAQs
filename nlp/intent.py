import re

class IntentDetector:
    def __init__(self):
        # Regular expressions for common conversational intents
        self.rules = {
            'greeting': {
                'patterns': [
                    r'\b(hi|hello|hey|greetings|howdy|hola|yo)\b',
                    r'good\s+(morning|afternoon|evening)',
                    r'is\s+anybody\s+there'
                ],
                'responses': [
                    "Hello! I am your FAQ assistant. How can I help you today?",
                    "Hi there! What can I assist you with?",
                    "Greetings! How may I help you today?"
                ]
            },
            'goodbye': {
                'patterns': [
                    r'\b(bye|goodbye|farewell|see\s+ya|talk\s+to\s+you\s+later)\b',
                    r'exit',
                    r'quit'
                ],
                'responses': [
                    "Goodbye! Have a great day ahead.",
                    "Bye! Feel free to reach out if you have more questions.",
                    "Farewell! Hope I was able to help."
                ]
            },
            'thanks': {
                'patterns': [
                    r'\b(thanks|thank\s+you|appreciate\s+it|thankful|grateful|awesome|perfect)\b',
                    r'thank\s+you\s+so\s+much'
                ],
                'responses': [
                    "You're very welcome! I'm glad I could help.",
                    "Anytime! Let me know if you need anything else.",
                    "Happy to help! Have a wonderful day."
                ]
            },
            'help': {
                'patterns': [
                    r'\b(help|options|menu|commands|what\s+can\s+you\s+do|list\s+capabilities)\b'
                ],
                'responses': [
                    "I can answer your questions by matching them with our FAQs. Try asking about general features, database setup, or deployment processes!",
                    "I'm here to help you browse our FAQs. You can type queries like 'How to deploy?' or 'What is this chatbot?' to get started.",
                    "Need help? Just type in your question, and I'll find the best matching FAQ or suggest similar topics."
                ]
            },
            'bot_identity': {
                'patterns': [
                    r'who\s+are\s+you',
                    r'what\s+is\s+your\s+name',
                    r'your\s+identity',
                    r'are\s+you\s+a\s+bot'
                ],
                'responses': [
                    "I am the AI FAQ Chatbot, an NLP-powered assistant designed to answer questions from our knowledge base.",
                    "I'm the FAQ Whisperer Chatbot, trained to understand questions and match them with database answers.",
                    "I am an intelligent FAQ bot. My goal is to make finding information simple and fast!"
                ]
            }
        }

    def detect(self, query):
        """
        Scans query for predefined patterns.
        Returns a dictionary if intent matched: {'intent': str, 'response': str}
        Otherwise returns None.
        """
        if not query:
            return None

        cleaned_query = query.lower().strip()

        # Check each intent
        for intent_name, data in self.rules.items():
            for pattern in data['patterns']:
                if re.search(pattern, cleaned_query):
                    import random
                    return {
                        'intent': intent_name,
                        'response': random.choice(data['responses'])
                    }

        return None
