# app/routes/debug_routes.py:

from flask import Blueprint, jsonify, current_app

debug_bp = Blueprint("debug", __name__)

@debug_bp.route("/api/debug")
def debug_config():
    config_data = {
        "env": current_app.config.get("LOG_LEVEL"),
        "api": current_app.config.get("API_BASE_URL"),
        "cdn": current_app.config.get("STATIC_CDN"),
    }

    current_app.logger.debug(f"Debug config endpoint wywołany: {config_data}")
    return jsonify(config_data) #Zwraca aktualną konfigurację środowiska