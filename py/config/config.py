# config/config.py

import os
from dotenv import load_dotenv

# Wczytanie pliku .env tylko raz
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config.env'))
load_dotenv(dotenv_path)

class BaseConfig:
    ENV = os.getenv("TRAVELREADY_ENV", "development").lower()
    SECRET_KEY = os.getenv(f"SECRET_KEY_{ENV.upper()}")
    if ENV == "production" and not SECRET_KEY:
        raise RuntimeError("SECRET_KEY_PRODUCTION musi być ustawiony w pliku config.env")
    API_BASE_URL = os.getenv(f"API_BASE_URL_{ENV.upper()}")
    STATIC_CDN = os.getenv(f"STATIC_CDN_{ENV.upper()}")
    LOG_LEVEL = os.getenv(f"LOG_LEVEL_{ENV.upper()}", "DEBUG")
    SENTRY_DSN = os.getenv(f"SENTRY_DSN_{ENV.upper()}", "")
    DATABASE_URL = os.getenv(f"DATABASE_URL_{ENV.upper()}", "")
    FLASK_HOST = os.getenv(f"FLASK_HOST_{ENV.upper()}", "0.0.0.0")
    FLASK_PORT = int(os.getenv(f"FLASK_PORT_{ENV.upper()}", "5000"))
    FLASK_DEBUG = os.getenv(f"FLASK_DEBUG_{ENV.upper()}", "true").lower() == "true"

       # ✅ Limit liczby elementów w checklist – z .env
    MAX_CHECKLIST_ITEMS = int(os.getenv(f"MAX_CHECKLIST_ITEMS_{ENV.upper()}", 200))
    os.environ["MAX_CHECKLIST_ITEMS"] = str(MAX_CHECKLIST_ITEMS)

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class ProductionConfig(BaseConfig):
    DEBUG = False

def get_config_class():
    env = os.getenv("TRAVELREADY_ENV", "development").lower()
    return {
        "development": DevelopmentConfig,
        "production": ProductionConfig
    }.get(env, DevelopmentConfig)