#app/repository.py
# Klasa pośrednicząca między logiką aplikacji a warstwą danych (plik JSON + lista elementów)

import os, json, logging
from app.data.items import ITEMS
from flask import current_app, request

logger = logging.getLogger(__name__)
DATA_SUBDIR = ("data", "checked")  # app/data/checked

# Repozytorium danych – zarządza checklistą i zaznaczonymi elementami.
# Ułatwia przyszłe przejście na bazę danych lub zewnętrzne źródła danych
class ChecklistRepository:
    
    #Zwraca pełną strukturę checklisty pogrupowaną według kategorii
    @staticmethod
    def get_all_items() -> dict:
        return ITEMS

    # Zwraca listę wszystkich dostępnych elementów checklisty (flatten)
    @staticmethod
    def get_all_items_flat() -> list:
        return [item for sublist in ITEMS.values() for item in sublist]

    #Ścieżka do pliku z zaznaczeniami dla bieżącego użytkownika.
    @staticmethod
    def _user_file() -> str:
        uid = request.cookies.get("tr_uid") or "anonymous"
        base = os.path.join(current_app.root_path, *DATA_SUBDIR)
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, f"{uid}.json")

    # Wczytuje listę zaznaczonych elementów z pliku JSON (per-user).
    @classmethod
    def load_checked(cls) -> list:
        path = cls._user_file()
        if not os.path.exists(path):
            current_app.logger.info(f"🔍 File {path} does not exist - returning an empty list.")
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            current_app.logger.warning(f"❌ Failed to load JSON file ({path}): {e}")
            return []

    # Zapisuje listę zaznaczonych elementów per-user (atomowo) do pliku JSON
    @classmethod
    def save_checked(cls, data: list) -> None:
        path = cls._user_file()
        tmp = path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, path)
            current_app.logger.info(f"💾 Saved {len(data)} items to {path}")
        except OSError as e:
            current_app.logger.error(f"❌ Error writing to file {path}: {e}")
            logger.error(f"❌ Error writing to file {path}: {e}")
            raise
