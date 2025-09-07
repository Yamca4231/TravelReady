# app/error_handlers.py
# Obsługa wyjątków globalnych

from flask import jsonify, request
from app.validation import ValidationError
from werkzeug.exceptions import HTTPException

# Rejestruje globalne obsługi błędów dla kodów HTTP i nieoczekiwanych wyjątków
def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(f"400 Bad Request: {error}")
        return jsonify({
            "status": "error",
            "message": "Błędne żądanie (400)"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f"404 Not Found: {error}")
        return jsonify({
            "status": "error",
            "message": "Nie znaleziono (404)"
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        app.logger.warning(
            f"405 Method Not Allowed: {request.method} {request.path}"
        )
        # opcjonalnie: Allow = ",".join(error.valid_methods or [])
        return jsonify({
            "status": "error", 
            "message": "Metoda niedozwolona (405)"
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        # Zaloguj pełny traceback, gdy wystąpi błąd serwera
        app.logger.exception("500 Internal Server Error")
        return jsonify({
            "status": "error",
            "message": "Wewnętrzny błąd serwera (500)"
        }), 500

    # Obsługuje każdy nieprzechwycony wyjątek
    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        if isinstance(error, HTTPException):
            return error
        app.logger.exception(f"Nieoczekiwany wyjątek: {error}")
        return jsonify({
            "status": "error",
            "message": "Wystąpił nieoczekiwany błąd",
            "type": error.__class__.__name__
        }), 500
    
    @app.errorhandler(ValidationError)
    def _validation_err(e):
        return jsonify({"status": "error", "message": str(e)}), 400