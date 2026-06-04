import csv
import json
import io

class ExportService:
    @staticmethod
    def parse_csv(file_content_str):
        """
        Parses a CSV string.
        Expected headers: question, answer, category (optional)
        Returns a list of dictionaries.
        """
        faqs = []
        # Use io.StringIO to treat string as a file-like stream
        f = io.StringIO(file_content_str)
        reader = csv.DictReader(f)
        
        # Normalize headers to lowercase to match keys easily
        headers = [h.strip().lower() for h in reader.fieldnames] if reader.fieldnames else []
        
        # Verify required headers
        if 'question' not in headers or 'answer' not in headers:
            raise ValueError("CSV must contain 'question' and 'answer' columns.")

        # Re-read with standard DictReader but mapped headers
        f.seek(0)
        # Skip header row for reading but use manual dict mapping
        next(f)
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if not row or len(row) < 2:
                continue
            
            # Map values based on header indices
            q_idx = headers.index('question')
            a_idx = headers.index('answer')
            c_idx = headers.index('category') if 'category' in headers else -1
            
            question = row[q_idx].strip() if q_idx < len(row) else ""
            answer = row[a_idx].strip() if a_idx < len(row) else ""
            category = row[c_idx].strip() if (c_idx != -1 and c_idx < len(row)) else "General"
            
            if question and answer:
                faqs.append({
                    'question': question,
                    'answer': answer,
                    'category': category or 'General'
                })
        return faqs

    @staticmethod
    def parse_json(file_content_str):
        """
        Parses a JSON array.
        Expected format: [{"question": "...", "answer": "...", "category": "..."}]
        Returns a list of dictionaries.
        """
        try:
            data = json.loads(file_content_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

        if not isinstance(data, list):
            raise ValueError("JSON content must be a list/array of FAQ objects.")

        faqs = []
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Item at index {idx} is not a valid JSON object.")
            
            question = item.get('question', '').strip()
            answer = item.get('answer', '').strip()
            category = item.get('category', 'General').strip()

            if not question or not answer:
                raise ValueError(f"Item at index {idx} must contain both non-empty 'question' and 'answer'.")

            faqs.append({
                'question': question,
                'answer': answer,
                'category': category or 'General'
            })
        return faqs

    @staticmethod
    def export_csv(faqs):
        """
        Exports list of FAQs to a CSV string.
        faqs: list of dicts.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['question', 'answer', 'category'])
        
        # Write rows
        for faq in faqs:
            writer.writerow([faq.get('question'), faq.get('answer'), faq.get('category', 'General')])
            
        return output.getvalue()

    @staticmethod
    def export_json(faqs):
        """
        Exports list of FAQs to a formatted JSON string.
        faqs: list of dicts.
        """
        cleaned_faqs = []
        for faq in faqs:
            cleaned_faqs.append({
                'question': faq.get('question'),
                'answer': faq.get('answer'),
                'category': faq.get('category', 'General')
            })
        return json.dumps(cleaned_faqs, indent=2, ensure_ascii=False)
