# app/routes/checklist_routes.py:
# TODO: Aktywować zapis danych po stronie serwera, gdy będzie potrzebny

from flask import Blueprint, jsonify, request, Response, current_app
from app.services.checklist_service import ChecklistService
import json

# Umożliwia modularne rejestrowanie tras pod wspólną nazwą
checklist_bp = Blueprint('main', __name__)
service = ChecklistService()

# Definiujemy nową trasę API, która zwraca checklistę w formacie JSON
@checklist_bp.route("/api/checklist", methods=["GET"]) 
def checklist_api():
    data = service.get_checklist()
    """
    Zwraca checklistę w formacie JSON z poprawnie zakodowanymi polskimi znakami.
    Używamy json.dumps z ensure_ascii=False, aby znaki jak 'Ł', 'ó', 'ń' itp. były widoczne normalnie.
    Użycie flask.Response pozwala nam ręcznie ustawić Content-Type = application/json.
    """
    return Response(
        json.dumps(data, ensure_ascii=False),  # Konwersja listy na JSON z zachowaniem polskich znaków
        mimetype="application/json"             # Ustawiamy poprawny nagłówek odpowiedzi (JSON)
    )

@checklist_bp.route("/api/checked", methods=["GET", "POST"])
def checklist_checked():
    """
    Obsługuje dwa przypadki:
    - GET: zwraca aktualnie zaznaczone elementy z pliku JSON
    - POST: przyjmuje JSON z listą zaznaczonych elementów i zapisuje je
    """
    if request.method == "POST":
        # Weryfikacja nagłówka Content-Type
        if request.content_type != 'application/json':
            current_app.logger.warning(f"Błędny Content-Type: {request.content_type}")
            return jsonify({
                "status": "error",
                "message": "Nagłówek Content-Type musi być 'application/json'."
            }), 415
        
        data = request.get_json(silent=True)    # Próba pobrania danych
        if data is None:
            current_app.logger.warning("Nieprawidłowy JSON lub brak danych.")
            return jsonify({
                "status": "error",
                "message": "Brak lub błędny JSON w treści żądania."
            }), 400

        # Walidujemy dane wejściowe
        success, errors = validate_checked_items(data)
        if not success:
            current_app.logger.warning(f"Nieprawidłowe dane wejściowe: {data} | Błędy: {errors}")   # Logowanie błędnych danych wejściowych
            return jsonify({
                "status": "error",
                "message": "Nieprawidłowe dane wejściowe.",
                "details": errors
            }), 400
        
        # Jeśli dane są poprawne – zapisujemy
        service.save_checked(data)  # Zapisujemy listę do pliku
        current_app.logger.info(f"Zapisano {len(data)} elementów checklisty: {data}")   # Logowanie poprawnego zapisu danych
        return jsonify({"status": "success"})  # Zwracamy status powodzenia
    return jsonify(service.load_checked())  # Zwracamy wcześniej zapisane elementy (jeśli istnieją)

# ==========================
# Pomocnicza funkcja walidacji
# ==========================

def validate_checked_items(data):
    """
    Sprawdza:
    - Czy dane to lista.
    - Czy liczba elementów nie przekracza limitu.
    - Czy każdy element to string należący do checklisty.
    """
    errors = []

    # Walidacja typu
    if not isinstance(data, list):
        return False, ["Dane muszą być listą."]
    
    # Limit długości (np. max 200 pozycji)
    max_len = current_app.config.get("MAX_CHECKLIST_ITEMS", 200)
    if len(data) > max_len:
        errors.append(f"Lista zawiera zbyt wiele elementów ({len(data)}). Maksymalnie dozwolone: {max_len}.")

    # Walidacja zawartości
    allowed_items = service.allowed_items
    for idx, el in enumerate(data):
        if not isinstance(el, str):
            errors.append(f"Element na pozycji {idx} nie jest typu string.")
        elif el not in allowed_items:
            errors.append(f"'{el}' nie jest poprawnym elementem checklisty.")

    return (len(errors) == 0), errors
