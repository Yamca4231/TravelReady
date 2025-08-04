# app/routes/frontend_routes.py

from flask import Blueprint, current_app, send_from_directory
import os

frontend_bp = Blueprint("frontend", __name__)

@frontend_bp.route("/")
def index():
    return current_app.send_static_file("index.html")

@frontend_bp.route('/css/<path:filename>')
def serve_css_legacy(filename):
    return send_from_directory(os.path.join(current_app.static_folder, 'css'), filename)

@frontend_bp.route('/js/<path:filename>')
def serve_js_legacy(filename):
    return send_from_directory(os.path.join(current_app.static_folder, 'js'), filename)

@frontend_bp.route('/travelready/static/images/<path:filename>')
def serve_images_prefixed(filename):
    return send_from_directory(os.path.join(current_app.static_folder, 'images'), filename)