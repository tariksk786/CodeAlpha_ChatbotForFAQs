from flask import Blueprint, request, jsonify, current_app

chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    """
    Receives user query, processes it through NLP, and returns the response.
    Expects JSON: { "message": "user question" }
    """
    data = request.get_json() or {}
    message = data.get('message', '').strip()

    if not message:
        return jsonify({
            "error": "Query message cannot be empty."
        }), 400

    try:
        faq_service = current_app.faq_service
        response_payload = faq_service.get_response(message)
        return jsonify(response_payload)
    except Exception as e:
        print(f"Error in chat route: {e}")
        return jsonify({
            "error": "An error occurred while processing your request.",
            "details": str(e)
        }), 500

@chat_bp.route('/api/chat/feedback', methods=['POST'])
def chat_feedback():
    """
    Receives thumbs up/down feedback for a query.
    Expects JSON: { "query_id": int, "feedback": int } -- feedback is 1 (up) or -1 (down)
    """
    data = request.get_json() or {}
    query_id = data.get('query_id')
    feedback = data.get('feedback')

    if query_id is None or feedback not in [1, -1]:
        return jsonify({
            "error": "Invalid payload. 'query_id' and 'feedback' (1 or -1) are required."
        }), 400

    try:
        db = current_app.db
        success = db.update_query_feedback(query_id, feedback)
        if success:
            return jsonify({"success": True, "message": "Feedback updated successfully."})
        else:
            return jsonify({"error": "Query log entry not found."}), 404
    except Exception as e:
        print(f"Error in feedback route: {e}")
        return jsonify({
            "error": "An error occurred while logging feedback.",
            "details": str(e)
        }), 500
