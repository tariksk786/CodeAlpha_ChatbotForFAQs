from flask import Blueprint, jsonify, render_template, current_app
from routes.admin_routes import admin_required

analytics_bp = Blueprint('analytics_bp', __name__)

@analytics_bp.route('/analytics')
@admin_required
def analytics_page():
    """Renders the Analytics dashboard interface."""
    return render_template('analytics.html')

@analytics_bp.route('/api/analytics', methods=['GET'])
@admin_required
def get_analytics_data():
    """
    Returns aggregated log metrics for dashboard chart visualizer.
    Includes: summary cards, daily activity line chart, popular FAQs,
    category distribution, and recent activity logs.
    """
    try:
        analytics_service = current_app.analytics_service
        
        summary = analytics_service.get_summary_stats()
        daily_trends = analytics_service.get_daily_trends(days=7)
        top_questions = analytics_service.get_top_questions(limit=5)
        categories = analytics_service.get_category_distribution()
        recent_queries = analytics_service.get_recent_queries(limit=10)

        return jsonify({
            "summary": summary,
            "daily_trends": daily_trends,
            "top_questions": top_questions,
            "categories": categories,
            "recent_queries": recent_queries
        })
    except Exception as e:
        print(f"Error gathering analytics data: {e}")
        return jsonify({
            "error": "Failed to fetch analytics statistics.",
            "details": str(e)
        }), 500
