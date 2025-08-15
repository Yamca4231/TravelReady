# app/routes/checklist_routes.py:
# TODO: Aktywować zapis danych po stronie serwera, gdy będzie potrzebny

from flask import Blueprint, jsonify, request, Response, current_app
from app.services.checklist_service import ChecklistService
import json
from app.validation import validate_checked_payload, ValidationError

# Umożliwia modularne rejestrowanie tras pod wspólną nazwą
checklist_bp = Blueprint('main', __name__)
service = ChecklistService()

# Definiujemy nową trasę API, która zwraca checklistę w formacie JSON
@checklist_bp.route("/api/checklist", methods=["GET"]) 
def checklist_api():
    data = service.get_checklist()
    return Response(
        json.dumps(data, ensure_ascii=False),  # Konwersja listy na JSON z zachowaniem polskich znaków
        mimetype="application/json"             # Ustawiamy poprawny nagłówek odpowiedzi (JSON)
    )

# GET: zwraca aktualnie zaznaczone elementy z pliku JSON
# POST: przyjmuje JSON z listą zaznaczonych elementów i zapisuje je
@checklist_bp.route("/api/checked", methods=["GET", "POST"])
def checklist_checked():
    if request.method == "POST":
        # Weryfikacja nagłówka Content-Type
        if not request.is_json:
            current_app.logger.warning(f"Błędny Content-Type: {request.content_type}")
            return jsonify({"status": "error", "message": "Nagłówek Content-Type musi być 'application/json'."}), 415
        data = request.get_json(silent=True)    # Próba pobrania danych
        if data is None:
            return jsonify({"status": "error", "message": "Brak lub błędny JSON."}), 400

        # pozwalamy dalej wysyłać gołą listę – opakowujemy w payload:
        payload = {"checked": data} if isinstance(data, list) else data

        max_len = current_app.config.get("MAX_CHECKLIST_ITEMS", 200)

        try:
            normalized = validate_checked_payload(payload, service.allowed_items, max_len=max_len)
        except ValidationError as e:
            current_app.logger.warning(f"Nieprawidłowe dane wejściowe: {data} | Błąd: {e}")
            return jsonify({"status": "error", "message": "Nieprawidłowe dane wejściowe.","details": [str(e)]}), 400

        # Jeśli dane są poprawne – zapisujemy
        service.save_checked(normalized)
        return jsonify({"status": "success"}), 200

    return jsonify(service.load_checked())  # Zwracamy wcześniej zapisane elementy
