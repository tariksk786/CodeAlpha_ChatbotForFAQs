from functools import wraps
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, current_app

admin_bp = Blueprint('admin_bp', __name__)

def admin_required(f):
    """Decorator to restrict routes to logged-in administrator sessions."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            # If API endpoint, return unauthorized JSON
            if request.path.startswith('/api/'):
                return jsonify({"error": "Unauthorized. Administrative session required."}), 401
            # Otherwise redirect to login page
            return redirect(url_for('admin_bp.login_page'))
        return f(*args, **kwargs)
    return decorated_function

# Page Rendering Routes

@admin_bp.route('/')
def landing_page():
    """Renders the landing page."""
    return render_template('index.html')

@admin_bp.route('/chatbot')
def chatbot_page():
    """Renders the main chatbot interface."""
    return render_template('chatbot.html')

@admin_bp.route('/about')
def about_page():
    """Renders the about and tech stack page."""
    return render_template('about.html')

@admin_bp.route('/login')
def login_page():
    """Renders the administrator login page."""
    if session.get('logged_in'):
        return redirect(url_for('admin_bp.admin_dashboard'))
    return render_template('login.html')

@admin_bp.route('/admin')
@admin_required
def admin_dashboard():
    """Renders the administrator CRUD management panel."""
    return render_template('admin.html')

# Authentication API Routes

@admin_bp.route('/api/login', methods=['POST'])
def login_api():
    """Handles admin authentication requests."""
    # Support both JSON and standard Form posts
    if request.is_json:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
    else:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

    if not username or not password:
        return jsonify({"error": "Both username and password fields are required."}), 400

    try:
        db = current_app.db
        if db.verify_admin(username, password):
            session.clear()
            session['logged_in'] = True
            session['username'] = username
            return jsonify({
                "success": True,
                "message": "Login successful.",
                "redirect_url": url_for('admin_bp.admin_dashboard')
            })
        else:
            return jsonify({"error": "Invalid username or password credentials."}), 401
    except Exception as e:
        return jsonify({"error": "An authentication error occurred.", "details": str(e)}), 500

@admin_bp.route('/api/logout', methods=['POST', 'GET'])
def logout_api():
    """Clears the administrator session."""
    session.clear()
    if request.method == 'GET':
        return redirect(url_for('admin_bp.landing_page'))
    return jsonify({
        "success": True,
        "message": "Logged out successfully.",
        "redirect_url": url_for('admin_bp.landing_page')
    })
