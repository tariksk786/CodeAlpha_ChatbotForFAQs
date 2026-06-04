from flask import Blueprint, request, jsonify, current_app, Response
from routes.admin_routes import admin_required
from services.export_service import ExportService

faq_bp = Blueprint('faq_bp', __name__)

@faq_bp.route('/api/faqs', methods=['GET'])
def get_faqs():
    """
    Retrieves FAQs with optional query search, category filtering, and pagination.
    """
    search_query = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    limit_str = request.args.get('limit')
    offset_str = request.args.get('offset')

    limit = int(limit_str) if limit_str and limit_str.isdigit() else None
    offset = int(offset_str) if offset_str and offset_str.isdigit() else None

    try:
        db = current_app.db
        faqs = db.get_all_faqs(
            search_query=search_query if search_query else None,
            category=category if category else None,
            limit=limit,
            offset=offset
        )
        total_count = db.count_faqs(
            search_query=search_query if search_query else None,
            category=category if category else None
        )
        categories = db.get_categories()

        return jsonify({
            "faqs": faqs,
            "total": total_count,
            "categories": categories
        })
    except Exception as e:
        return jsonify({"error": "Failed to fetch FAQs.", "details": str(e)}), 500

@faq_bp.route('/api/faqs/add', methods=['POST'])
@admin_required
def add_faq():
    """Adds a new FAQ to the database and triggers NLP retraining."""
    data = request.get_json() or {}
    question = data.get('question', '').strip()
    answer = data.get('answer', '').strip()
    category = data.get('category', 'General').strip()

    if not question or not answer:
        return jsonify({"error": "Question and Answer fields are required."}), 400

    try:
        faq_service = current_app.faq_service
        faq_id = faq_service.add_faq(question, answer, category)
        return jsonify({
            "success": True,
            "message": "FAQ added successfully.",
            "faq_id": faq_id
        }), 201
    except Exception as e:
        return jsonify({"error": "Failed to add FAQ.", "details": str(e)}), 500

@faq_bp.route('/api/faqs/update/<int:faq_id>', methods=['PUT'])
@admin_required
def update_faq(faq_id):
    """Updates an existing FAQ in the database and triggers NLP retraining."""
    data = request.get_json() or {}
    question = data.get('question', '').strip()
    answer = data.get('answer', '').strip()
    category = data.get('category', 'General').strip()

    if not question or not answer:
        return jsonify({"error": "Question and Answer fields are required."}), 400

    try:
        faq_service = current_app.faq_service
        success = faq_service.update_faq(faq_id, question, answer, category)
        if success:
            return jsonify({"success": True, "message": "FAQ updated successfully."})
        else:
            return jsonify({"error": "FAQ not found."}), 404
    except Exception as e:
        return jsonify({"error": "Failed to update FAQ.", "details": str(e)}), 500

@faq_bp.route('/api/faqs/delete/<int:faq_id>', methods=['DELETE'])
@admin_required
def delete_faq(faq_id):
    """Deletes an FAQ and triggers NLP retraining."""
    try:
        faq_service = current_app.faq_service
        success = faq_service.delete_faq(faq_id)
        if success:
            return jsonify({"success": True, "message": "FAQ deleted successfully."})
        else:
            return jsonify({"error": "FAQ not found."}), 404
    except Exception as e:
        return jsonify({"error": "Failed to delete FAQ.", "details": str(e)}), 500

@faq_bp.route('/api/faqs/import', methods=['POST'])
@admin_required
def import_faqs():
    """Bulk imports FAQs from a CSV or JSON file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400

    filename = file.filename.lower()
    
    try:
        file_content = file.read().decode('utf-8')
        
        if filename.endswith('.csv'):
            faq_list = ExportService.parse_csv(file_content)
        elif filename.endswith('.json'):
            faq_list = ExportService.parse_json(file_content)
        else:
            return jsonify({"error": "Unsupported file extension. Only CSV and JSON are supported."}), 400

        if not faq_list:
            return jsonify({"error": "No valid FAQs found in file."}), 400

        faq_service = current_app.faq_service
        imported_count = faq_service.bulk_import_faqs(faq_list)
        
        return jsonify({
            "success": True,
            "message": f"Successfully imported {imported_count} FAQs."
        })
    except Exception as e:
        return jsonify({"error": "Failed to import FAQs.", "details": str(e)}), 500

@faq_bp.route('/api/faqs/export/<string:file_format>', methods=['GET'])
@admin_required
def export_faqs(file_format):
    """Exports all FAQs as a CSV or JSON file download."""
    file_format = file_format.lower().strip()
    if file_format not in ['csv', 'json']:
        return jsonify({"error": "Invalid format. Only 'csv' or 'json' are allowed."}), 400

    try:
        db = current_app.db
        faqs = db.get_all_faqs()
        
        if file_format == 'csv':
            data = ExportService.export_csv(faqs)
            mimetype = 'text/csv'
            filename = 'faqs_export.csv'
        else:
            data = ExportService.export_json(faqs)
            mimetype = 'application/json'
            filename = 'faqs_export.json'

        return Response(
            data,
            mimetype=mimetype,
            headers={"Content-disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return jsonify({"error": "Failed to export FAQs.", "details": str(e)}), 500
