#app/repository.py
# Klasa pośrednicząca między logiką aplikacji a warstwą danych (plik JSON + lista elementów)

import os, json, logging
from app.data.items import ITEMS
from flask import current_app

logger = logging.getLogger(__name__)

class ChecklistRepository:
    """
    Repozytorium danych – zarządza checklistą i zaznaczonymi elementami.
    Ułatwia przyszłe przejście na bazę danych lub zewnętrzne źródła danych.
    """

    @staticmethod
    def get_all_items() -> dict:
        """Zwraca pełną strukturę checklisty pogrupowaną według kategorii."""
        return ITEMS

    @staticmethod
    def get_all_items_flat() -> list:
        """Zwraca listę wszystkich dostępnych elementów checklisty (flatten)."""
        return [item for sublist in ITEMS.values() for item in sublist]

    @staticmethod
    def get_checked_items_path() -> str:
        """
        Zwraca absolutną ścieżkę do pliku JSON z zaznaczonymi elementami.
        Plik może być zdefiniowany dynamicznie z config, domyślnie 'checked_items.json'.
        """
        return os.path.join(current_app.root_path, '..', 'checked_items.json')

    @classmethod
    def load_checked(cls) -> list:
        """Wczytuje listę zaznaczonych elementów z pliku JSON."""
        path = cls.get_checked_items_path()
        if not os.path.exists(path):
            current_app.logger.info(f"🔍 Plik {path} nie istnieje – zwracam pustą listę.")
            return []

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            current_app.logger.warning(f"❌ Nie udało się wczytać pliku JSON ({path}): {e}")
            return []

    @classmethod
    def save_checked(cls, data: list) -> None:
        """Zapisuje listę zaznaczonych elementów do pliku JSON."""
        path = cls.get_checked_items_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                current_app.logger.info(f"💾 Zapisano {len(data)} elementów do {path}")
        except OSError as e:
            current_app.logger.error(f"❌ Błąd zapisu do pliku {path}: {e}")
            logger.error(f"❌ Błąd zapisu do pliku {path}: {e}")
            raise
