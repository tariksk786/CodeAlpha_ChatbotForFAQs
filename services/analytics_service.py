import sqlite3
from datetime import datetime, timedelta

class AnalyticsService:
    def __init__(self, db):
        self.db = db

    def get_summary_stats(self):
        """Returns high-level analytics summary counts."""
        with self.db._connection() as conn:
            cursor = conn.cursor()
            
            # Total queries
            cursor.execute("SELECT COUNT(*) FROM queries_log")
            total_queries = cursor.fetchone()[0]

            # Feedback positive (1) and negative (-1)
            cursor.execute("SELECT COUNT(*) FROM queries_log WHERE feedback = 1")
            positive_feedback = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM queries_log WHERE feedback = -1")
            negative_feedback = cursor.fetchone()[0]

            # Average confidence score (excluding conversational intents where matched_faq_id is null but confidence is 1.0)
            cursor.execute("SELECT AVG(confidence) FROM queries_log WHERE matched_faq_id IS NOT NULL")
            avg_confidence = cursor.fetchone()[0]
            avg_confidence = round(avg_confidence * 100, 1) if avg_confidence is not None else 0.0

            # Low confidence count (defined as confidence < threshold, threshold is typically 0.40)
            # In our db logs, we store the actual confidence score
            cursor.execute("SELECT COUNT(*) FROM queries_log WHERE confidence < 0.40 AND matched_faq_id IS NULL")
            low_confidence_queries = cursor.fetchone()[0]
            
            # Total FAQs in db
            cursor.execute("SELECT COUNT(*) FROM faqs")
            total_faqs = cursor.fetchone()[0]

            return {
                "total_queries": total_queries,
                "positive_feedback": positive_feedback,
                "negative_feedback": negative_feedback,
                "avg_confidence": avg_confidence,
                "low_confidence_queries": low_confidence_queries,
                "total_faqs": total_faqs
            }

    def get_daily_trends(self, days=7):
        """Returns the daily query volume and average confidence for the past N days."""
        trends = []
        with self.db._connection() as conn:
            cursor = conn.cursor()
            
            # Query log grouping by date
            # We construct a series of dates for the last N days to make sure we don't have gaps
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days-1)
            
            date_list = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
            
            cursor.execute("""
                SELECT DATE(timestamp) as log_date, COUNT(*) as query_count, AVG(confidence) as avg_conf
                FROM queries_log
                WHERE timestamp >= DATE('now', ?)
                GROUP BY log_date
            """, (f"-{days} days",))
            
            db_results = {row['log_date']: (row['query_count'], row['avg_conf']) for row in cursor.fetchall()}
            
            for date_str in date_list:
                count, avg_conf = db_results.get(date_str, (0, 0.0))
                trends.append({
                    "date": date_str,
                    "count": count,
                    "avg_confidence": round(avg_conf * 100, 1)
                })
                
        return trends

    def get_top_questions(self, limit=5):
        """Returns the most frequently matched FAQs."""
        with self.db._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT faqs.id, faqs.question, faqs.category, COUNT(queries_log.id) as match_count
                FROM queries_log
                INNER JOIN faqs ON queries_log.matched_faq_id = faqs.id
                GROUP BY faqs.id
                ORDER BY match_count DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_category_distribution(self):
        """Returns query counts and total FAQs by category."""
        with self.db._connection() as conn:
            cursor = conn.cursor()
            
            # Query count by category
            cursor.execute("""
                SELECT faqs.category, COUNT(queries_log.id) as query_count
                FROM queries_log
                INNER JOIN faqs ON queries_log.matched_faq_id = faqs.id
                GROUP BY faqs.category
                ORDER BY query_count DESC
            """)
            query_dist = [dict(row) for row in cursor.fetchall()]

            # FAQ count by category
            cursor.execute("""
                SELECT category, COUNT(*) as faq_count
                FROM faqs
                GROUP BY category
                ORDER BY faq_count DESC
            """)
            faq_dist = {row['category']: row['faq_count'] for row in cursor.fetchall()}

            # Combine
            result = []
            for item in query_dist:
                cat = item['category']
                result.append({
                    "category": cat,
                    "query_count": item['query_count'],
                    "faq_count": faq_dist.get(cat, 0)
                })
                
            # Add categories that have FAQs but 0 queries
            for cat, count in faq_dist.items():
                if not any(item['category'] == cat for item in result):
                    result.append({
                        "category": cat,
                        "query_count": 0,
                        "faq_count": count
                    })

            return result

    def get_recent_queries(self, limit=10):
        """Returns the most recent user queries and their outcomes."""
        with self.db._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT q.id, q.query_text, q.confidence, q.timestamp, q.feedback, f.question as matched_question
                FROM queries_log q
                LEFT JOIN faqs f ON q.matched_faq_id = f.id
                ORDER BY q.timestamp DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                item = dict(row)
                item['confidence'] = int(round(item['confidence'] * 100))
                results.append(item)
            return results
