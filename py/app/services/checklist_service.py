# py/services/checklist_service.py

from app.repository import ChecklistRepository

class ChecklistService:
    def __init__(self, repo: ChecklistRepository | None = None):
        self.repo = repo or ChecklistRepository()
        
        # źródło prawdy o dozwolonych pozycjach – używane w routach z validation.py
        self.allowed_items = set(self.repo.get_all_items_flat())

# Zwraca pełną checklistę
    def get_checklist(self) -> dict:
        return self.repo.get_all_items()
# Zwraca zapisane zaznaczone elementy
    def get_checked(self) -> list:
        return self.repo.load_checked()

#Zapisuje już ZWALIDOWANĄ i ZNORMALIZOWANĄ listę elementów
    def save_checked(self, items: list[str]) -> None:
        self.repo.save_checked(items)