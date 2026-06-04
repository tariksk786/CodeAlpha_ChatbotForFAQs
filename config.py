import os

class Config:
    # Flask application secret key for session signing
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_super_secret_key_change_me_in_production')
    
    # Base directory of the application
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Path to SQLite database file
    DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'database', 'faq.db'))
    
    # Path to default seed FAQ file
    FAQ_JSON_PATH = os.environ.get('FAQ_JSON_PATH', os.path.join(BASE_DIR, 'faq.json'))
    
    # Minimum similarity confidence threshold (0.0 to 1.0)
    # Queries scoring below this are treated as low-confidence fallback queries.
    SIMILARITY_THRESHOLD = float(os.environ.get('SIMILARITY_THRESHOLD', 0.40))
    
    # Upload folder configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    
    # Default admin credentials (highly recommended to change or set env vars in production)
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
