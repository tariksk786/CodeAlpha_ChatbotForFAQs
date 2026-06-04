import os
from flask import Flask, render_template

# Import configuration
from config import Config

# Import Models & Services
from models.faq_model import FAQDatabase
from services.faq_service import FAQService
from services.analytics_service import AnalyticsService

# Import blueprints
from routes.chat_routes import chat_bp
from routes.faq_routes import faq_bp
from routes.admin_routes import admin_bp
from routes.analytics_routes import analytics_bp

def create_app(config_class=Config):
    """Application factory method to create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize SQLite Database & Models
    # Generates database tables and seeds them if empty
    db = FAQDatabase(app.config['DATABASE_PATH'], app.config)
    
    # Initialize Core Services
    # Trains TF-IDF Vectorizer on FAQs loaded from database
    faq_service = FAQService(db, app.config)
    analytics_service = AnalyticsService(db)

    # Attach instances to app context for blueprint route accessibility
    app.db = db
    app.faq_service = faq_service
    app.analytics_service = analytics_service

    # Register Blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(faq_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(analytics_bp)

    # Global Template Context Processor (e.g. inject status)
    @app.context_processor
    def inject_global_vars():
        return {
            'threshold': app.config['SIMILARITY_THRESHOLD']
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    # Determine port
    port = int(os.environ.get('PORT', 5000))
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=True)
