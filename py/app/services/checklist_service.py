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
    
    # Walidacja payload dla POST /api/checked
    def validate(self, data: list) -> list[str]:
        errors: list[str] = []
        if not isinstance(data, list):
            return ["Dane muszą być listą."]
        for idx, el in enumerate(data):
            if not isinstance(el, str):
                errors.append(f"Element na pozycji {idx} nie jest typu string.")
            elif el not in self.allowed_items:
                errors.append(f"'{el}' nie jest poprawnym elementem checklisty.")
        return errors

    #Zapisuje już ZWALIDOWANĄ i ZNORMALIZOWANĄ listę elementów
    def save_checked(self, data: list[str]) -> tuple[bool, list[str]]:
        errors = self.validate(data)
        if errors:
            return False, errors
        self.repo.save_checked(data)
        return True, []