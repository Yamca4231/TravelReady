# app/storage.py
import json, os

# Plik, w którym będziemy zapisywać zaznaczone przez użytkownika elementy
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "checked_items.json")

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