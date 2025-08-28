# app/routes/checklist_routes.py

from flask import Blueprint, jsonify, request, current_app, abort
from app.services.checklist_service import ChecklistService
import os, pathlib

# Umożliwia modularne rejestrowanie tras pod wspólną nazwą
checklist_bp = Blueprint("checklist", __name__)

# USTAWIENIA LOKALNE
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]                              # korzeń repo (.../TravelReady)
CONFIG_PATH = pathlib.Path(os.getenv("TR_CONFIG", str(PROJECT_ROOT / "config.env")))    # Ścieżka do pliku konfiguracyjnego
TR_ENV = os.getenv("TR_ENV", "DEV").upper()                                             # Wybór środowiska - DEV domyślnie

def _read_env_file(path: pathlib.Path) -> dict:
    if not path.is_file():
        return {}
    data = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip()
    return data

_cfg = _read_env_file(CONFIG_PATH)
_key = "MAX_CHECKLIST_ITEMS_PRODUCTION" if TR_ENV == "PROD" else "MAX_CHECKLIST_ITEMS_DEVELOPMENT"
_MAX = int(_cfg.get(_key, _cfg.get("MAX_CHECKLIST_ITEMS", "200")))

service = ChecklistService(max_items=_MAX)

# Definiujemy nową trasę API, która zwraca checklistę w formacie JSON
@checklist_bp.get("/api/checklist")
def get_checklist():
    return jsonify(service.get_checklist())

# GET: zwraca aktualnie zaznaczone elementy
@checklist_bp.get("/api/checked")
def get_checked():
    return jsonify(service.get_checked())

# POST: zapisuje liste zaznaczonych elementów
@checklist_bp.post("/api/checked")
def post_checked():
    # 1) Wymuś JSON
    if not request.is_json:
        return jsonify({"status": "error", "message": "Content-Type musi być application/json"}), 415
    data = request.get_json(silent=True)	# Próba pobrania danych
    if data is None:
        return jsonify({"status": "error", "message": "Brak lub błędny JSON"}), 400

    # 2) Akceptuj „gołą” listę lub {"checked": [...]}
    if isinstance(data, dict) and "checked" in data:
        data = data["checked"]

    # Limit liczby elementów z configu (fallback = 200)
    raw_limit = current_app.config.get("MAX_CHECKLIST_ITEMS", 200)
    try:
        max_len = int(raw_limit)
    except (TypeError, ValueError):
        max_len = 200
    if not isinstance(data, list):
        return jsonify({"status": "error", "message": "Nieprawidłowe dane wejściowe.","details": errors}), 400
    if len(data) > max_len:
        return jsonify({
            "status": "error",
            "message": f"Przekroczono limit elementów ({len(data)}/{max_len})."
        }), 400

    # 3) Walidacja  zapis przez serwis
    ok, errors = service.save_checked(data)
    if not ok:
        return jsonify({"status": "error", "message": "Brak lub błędny JSON."}), 400
    return jsonify({"status": "success"}), 200

@checklist_bp.route("/api/checked", methods=["GET", "POST"])
def checked():
    if request.method == "GET":
        return jsonify(service.get_checked()), 200