import os
import sqlite3
import json
from contextlib import contextmanager
from werkzeug.security import generate_password_hash, check_password_hash

class FAQDatabase:
    def __init__(self, db_path, config_obj):
        self.db_path = db_path
        self.config = config_obj
        self.init_db()

    @contextmanager
    def _connection(self):
        """Context manager for SQLite connections, ensuring connections are closed properly."""
        # Ensure database directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name like a dictionary
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Initializes database tables and seeds them if they are empty."""
        with self._connection() as conn:
            cursor = conn.cursor()
            
            # 1. Create FAQs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS faqs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    category TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 2. Create queries_log table for analytics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS queries_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_text TEXT NOT NULL,
                    matched_faq_id INTEGER,
                    confidence REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    feedback INTEGER, -- 1 for Thumbs Up, -1 for Thumbs Down
                    FOREIGN KEY (matched_faq_id) REFERENCES faqs(id) ON DELETE SET NULL
                )
            ''')

            # 3. Create admin table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            ''')
            
            conn.commit()

        # Seed data
        self.seed_admin()
        self.seed_faqs()

    def seed_admin(self):
        """Seeds default administrator account if none exists."""
        username = self.config.get('ADMIN_USERNAME')
        password = self.config.get('ADMIN_PASSWORD')
        
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM admins WHERE username = ?", (username,))
            if not cursor.fetchone():
                hashed_pw = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                    (username, hashed_pw)
                )
                conn.commit()
                print(f"Database: Created default administrator account '{username}'.")

    def seed_faqs(self):
        """Seeds default FAQs from the json file if the FAQ table is empty."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM faqs")
            if cursor.fetchone()[0] == 0:
                json_path = self.config.get('FAQ_JSON_PATH')
                if os.path.exists(json_path):
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            faqs = json.load(f)
                        for faq in faqs:
                            cursor.execute(
                                "INSERT INTO faqs (question, answer, category) VALUES (?, ?, ?)",
                                (faq['question'], faq['answer'], faq['category'])
                            )
                        conn.commit()
                        print(f"Database: Seeded {len(faqs)} FAQs from {json_path}.")
                    except Exception as e:
                        print(f"Database seeding error: {e}")

    # FAQ CRUD Methods
    def add_faq(self, question, answer, category):
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO faqs (question, answer, category) VALUES (?, ?, ?)",
                (question.strip(), answer.strip(), category.strip())
            )
            conn.commit()
            return cursor.lastrowid

    def get_faq(self, faq_id):
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM faqs WHERE id = ?", (faq_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_faqs(self, search_query=None, limit=None, offset=None, category=None):
        with self._connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM faqs"
            params = []
            conditions = []

            if search_query:
                conditions.append("(question LIKE ? OR answer LIKE ?)")
                params.extend([f"%{search_query}%", f"%{search_query}%"])
            if category:
                conditions.append("category = ?")
                params.append(category)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY id DESC"

            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
                if offset is not None:
                    query += " OFFSET ?"
                    params.append(offset)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def count_faqs(self, search_query=None, category=None):
        with self._connection() as conn:
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM faqs"
            params = []
            conditions = []

            if search_query:
                conditions.append("(question LIKE ? OR answer LIKE ?)")
                params.extend([f"%{search_query}%", f"%{search_query}%"])
            if category:
                conditions.append("category = ?")
                params.append(category)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            cursor.execute(query, params)
            return cursor.fetchone()[0]

    def get_categories(self):
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM faqs ORDER BY category ASC")
            return [row['category'] for row in cursor.fetchall()]

    def update_faq(self, faq_id, question, answer, category):
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE faqs SET question = ?, answer = ?, category = ? WHERE id = ?",
                (question.strip(), answer.strip(), category.strip(), faq_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_faq(self, faq_id):
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM faqs WHERE id = ?", (faq_id,))
            conn.commit()
            return cursor.rowcount > 0

    # Analytics Logging Methods
    def log_query(self, query_text, matched_faq_id, confidence, feedback=None):
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO queries_log (query_text, matched_faq_id, confidence, feedback) VALUES (?, ?, ?, ?)",
                (query_text, matched_faq_id, confidence, feedback)
            )
            conn.commit()
            return cursor.lastrowid

    def update_query_feedback(self, query_id, feedback):
        """Updates query feedback with 1 (thumbs up) or -1 (thumbs down)."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE queries_log SET feedback = ? WHERE id = ?",
                (feedback, query_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    # Admin Auth Methods
    def verify_admin(self, username, password):
        """Verifies admin credentials. Returns True if valid."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM admins WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row and check_password_hash(row['password_hash'], password):
                return True
            return False

    def change_admin_password(self, username, new_password):
        with self._connection() as conn:
            cursor = conn.cursor()
            hashed_pw = generate_password_hash(new_password)
            cursor.execute(
                "UPDATE admins SET password_hash = ? WHERE username = ?",
                (hashed_pw, username)
            )
            conn.commit()
            return cursor.rowcount > 0
