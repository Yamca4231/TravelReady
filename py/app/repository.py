#app/repository.py
# Klasa pośrednicząca między logiką aplikacji a warstwą danych (plik JSON + lista elementów)

import os, json, logging
from app.data.items import ITEMS
from flask import current_app

logger = logging.getLogger(__name__)

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

#Zwraca absolutną ścieżkę do pliku JSON z zaznaczonymi elementami.
    @staticmethod
    def get_checked_items_path() -> str:
        return os.path.join(current_app.root_path, '..', 'checked_items.json')

# Wczytuje listę zaznaczonych elementów z pliku JSON
    @classmethod
    def load_checked(cls) -> list:
        path = cls.get_checked_items_path()
        if not os.path.exists(path):
            current_app.logger.info(f"🔍 File {path} does not exist - returning an empty list.")
            return []

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            current_app.logger.warning(f"❌ Failed to load JSON file ({path}): {e}")
            return []

# Zapisuje listę zaznaczonych elementów do pliku JSON
    @classmethod
    def save_checked(cls, data: list) -> None:
        path = cls.get_checked_items_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                current_app.logger.info(f"💾 Saved {len(data)} items to {path}")
        except OSError as e:
            current_app.logger.error(f"❌ Error writing to file {path}: {e}")
            logger.error(f"❌ Error writing to file {path}: {e}")
            raise
