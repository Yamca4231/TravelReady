# app/__init__.py
# inicjalizacja aplikacji Flask

from flask import Flask
from flask_cors import CORS
from config.config import get_config_class
from app.log_config import setup_logging  # Import konfiguracji logowania
from app.routes.frontend_routes import frontend_bp

import os

def create_app():

    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    STATIC_DIR = os.path.join(BASE_DIR, "static")

    app = Flask(
        __name__,
        static_folder=STATIC_DIR,
        static_url_path="/static"
    )

    # Załaduj klasę konfiguracyjną zależną od środowiska
    app.config.from_object(get_config_class())

    # Skonfiguruj logowanie po załadowaniu konfiguracji
    log_level = app.config.get("LOG_LEVEL", "DEBUG")  # <--- [2] Poziom z config.env
    setup_logging(log_level)                          # <--- [3] Aktywacja loggera

    CORS(app)  # Pozwala JS w PHP łączyć się z API (np. przez fetch)

    # Rejestrujemy blueprint z trasami API
    from app.routes.checklist_routes import checklist_bp
    from app.routes.debug_routes import debug_bp

    app.register_blueprint(frontend_bp)
    app.register_blueprint(checklist_bp)
    app.register_blueprint(debug_bp)
    
    # Rejestrujemy globalną obsługę błędów
    from app.error_handlers import register_error_handlers
    register_error_handlers(app)

    return app

