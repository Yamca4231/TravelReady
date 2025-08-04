# py/services/checklist_service.py

from app.repository import ChecklistRepository

class ChecklistService:
    def __init__(self):
        self.repo = ChecklistRepository()
        self.allowed_items = set(self.repo.get_all_items_flat())

    def get_checklist(self) -> dict:
        """Zwraca pełną checklistę."""
        return self.repo.get_all_items()

    def get_checked(self) -> list:
        """Zwraca zapisane zaznaczone elementy."""
        return self.repo.load_checked()

    def save_checked(self, data: list) -> tuple[bool, list[str]]:
        """
        Waliduje i zapisuje zaznaczone elementy.
        Zwraca krotkę (sukces, lista błędów).
        """
        errors = self.validate(data)
        if errors:
            return False, errors
        self.repo.save_checked(data)
        return True, []

    def validate(self, data: list) -> list[str]:
        """
        Waliduje dane przesyłane do POST /api/checked.
        """
        errors = []

        if not isinstance(data, list):
            return ["Dane muszą być listą."]

        for idx, el in enumerate(data):
            if not isinstance(el, str):
                errors.append(f"Element na pozycji {idx} nie jest typu string.")
            elif el not in self.allowed_items:
                errors.append(f"'{el}' nie jest poprawnym elementem checklisty.")

        return errors
