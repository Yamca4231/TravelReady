# Importujemy funkcje i klasy z biblioteki Flask:
from flask import render_template, request, redirect, url_for, session, Response, jsonify
# render_template – pozwala załadować szablon HTML z katalogu templates/
# request – obsługuje dane wysyłane przez użytkownika (np. z formularza)
# redirect – umożliwia przekierowanie użytkownika na inną stronę
# url_for – pozwala wygenerować adres URL na podstawie nazwy funkcji
# session – umożliwia zapamiętywanie danych użytkownika między żądaniami (np. zaznaczone elementy)
# Response – służy do tworzenia niestandardowych odpowiedzi HTTP (np. JSON z polskimi znakami)

import json # Importujemy json – standardowy moduł do konwersji obiektów Python ↔ JSON
import os          # Do sprawdzenia, czy plik istnieje

from app import app # Importujemy instancję aplikacji Flask z pliku __init__.py w folderze app/

# Lista elementów do checklisty – statyczna lista z tekstami do wyświetlenia
ITEMS = [
    "Paszport",
    "Bielizna",
    "Koszulki",
    "Ładowarka",
    "Szczoteczka do zębów",
    "Krem z filtrem"
]

# Definiujemy trasę główną aplikacji: "/" – obsługuje metodę GET i POST
@app.route("/", methods=["GET", "POST"])
def index():
    # Sprawdzamy, czy w sesji (czyli "pamięci użytkownika") istnieje klucz "checked"
    # Jeśli nie – tworzymy pustą listę. To pozwala zapamiętać, które elementy user zaznaczył.
    if "checked" not in session:
        session["checked"] = []
    
    # Jeśli użytkownik wysłał formularz (czyli POST):
    if request.method == "POST":
        checked_items = request.form.getlist("item")    # Pobieramy listę zaznaczonych checkboxów o nazwie "item" (z formularza HTML)
        session["checked"] = checked_items              # Zapisujemy zaznaczone elementy do sesji, aby móc je później zaznaczyć ponownie
        return redirect(url_for("index"))               # Przekierowujemy użytkownika z powrotem na stronę główną – zapobiega odświeżeniu POST

    # Gdy użytkownik odwiedza stronę (GET):
    # render_template wczytuje szablon HTML `index.html` z podanymi danymi:
    # - items: lista wszystkich elementów do wyświetlenia
    # - checked: lista elementów wcześniej zaznaczonych przez użytkownika
    return render_template("index.html", items=ITEMS, checked=session["checked"])

# Definiujemy nową trasę API, która zwraca checklistę w formacie JSON
@app.route("/api/checklist", methods=["GET"]) 
def checklist_api():
    """
    Zwraca checklistę w formacie JSON z poprawnie zakodowanymi polskimi znakami.

    Używamy json.dumps z ensure_ascii=False, aby znaki jak 'Ł', 'ó', 'ń' itp. były widoczne normalnie.

    Użycie flask.Response pozwala nam ręcznie ustawić Content-Type = application/json.
    """
    return Response(
        json.dumps(ITEMS, ensure_ascii=False),  # Konwersja listy na JSON z zachowaniem polskich znaków
        mimetype="application/json"             # Ustawiamy poprawny nagłówek odpowiedzi (JSON)
    )

# Plik, w którym będziemy zapisywać zaznaczone przez użytkownika elementy
DATA_FILE = "checked_items.json"

def load_checked():
    """
    Wczytuje zawartość pliku JSON z dysku (zaznaczone elementy checklisty).
    Jeśli plik nie istnieje – zwraca pustą listę (czyli brak zaznaczeń).
    """
    if os.path.exists(DATA_FILE):  # Sprawdzamy, czy plik istnieje fizycznie
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)    # Jeśli tak – odczytujemy dane jako listę (np. ["Paszport"])
    return []  # Domyślnie zwracamy pustą listę

def save_checked(data):
    """
    Zapisuje przekazaną listę do pliku JSON.
    Używa kodowania UTF-8 i formatuje plik (indent=2).
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/api/checked", methods=["GET", "POST"])
def checklist_checked():
    """
    Obsługuje dwa przypadki:
    - GET: zwraca aktualnie zaznaczone elementy z pliku JSON
    - POST: przyjmuje JSON z listą zaznaczonych elementów i zapisuje je
    """
    if request.method == "POST":
        data = request.get_json()  # Pobieramy dane JSON z żądania
        if isinstance(data, list):  # Sprawdzamy, czy przesłana struktura to lista
            save_checked(data)  # Zapisujemy listę do pliku
            return jsonify({"status": "success"})  # Zwracamy status powodzenia
        # Jeśli dane nie są listą – błąd klienta (400 Bad Request)
        return jsonify({"status": "error", "message": "Dane muszą być listą."}), 400
    else:
        return jsonify(load_checked())  # Zwracamy wcześniej zapisane elementy (jeśli istnieją)

