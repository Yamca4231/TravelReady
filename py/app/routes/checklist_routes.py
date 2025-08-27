# app/routes/checklist_routes.py

from flask import Blueprint, jsonify, request, current_app
from app.services.checklist_service import ChecklistService

# Umożliwia modularne rejestrowanie tras pod wspólną nazwą
checklist_bp = Blueprint("checklist", __name__)
service = ChecklistService()

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