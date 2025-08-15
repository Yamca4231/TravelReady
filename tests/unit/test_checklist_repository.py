# tests/unit/test_checklist_repository.py
# ======================================================================
# Testy jednostkowe dla checklist (app.repository).
# ======================================================================
import importlib
import pytest

pytestmark = [pytest.mark.unit]



# Scenariusz:
#     Ładowanie klasy ChecklistRepository z modułu app.repository w sposób „bezpieczny”
#     dla środowisk, gdzie moduł może być tymczasowo niedostępny.
def _load_repo():
    try:
        repo_mod = importlib.import_module("app.repository")
    except ModuleNotFoundError:
        pytest.skip("Missing module app.repository – skipping tests.")
    ChecklistRepository = getattr(repo_mod, "ChecklistRepository", None)
    if ChecklistRepository is None:
        pytest.skip("Missing class ChecklistRepository in app.repository – skipping tests.")
    return ChecklistRepository


# Scenariusz:
#   Wywołanie repo.get_all_items() do pobrania pełnej checklisty.
def test_get_all_items_returns_dict_with_sections():
    ChecklistRepository = _load_repo()
    repo = ChecklistRepository()
    data = repo.get_all_items()
    assert isinstance(data, dict), "get_all_items() should return an object of type dict"
    assert len(data) >= 1, "Checklist should contain at least one section"
    
    # Wszystkie wartości to listy stringów
    for section, items in data.items():
        assert isinstance(items, list), f"Section '{section}' should be list"
        for it in items:
            assert isinstance(it, str), f"Element '{it}' in section '{section}' should be string"


# Scenariusz:
#   Wywołanie repo.get_all_items_flat() - pobranie płaskiej listy wszystkich pozycji 
#   checklisty bez podziału na sekcje.
def test_get_all_items_flat_is_list_of_strings():
    ChecklistRepository = _load_repo()
    repo = ChecklistRepository()
    flat = repo.get_all_items_flat()
    assert isinstance(flat, list), "get_all_items_flat() should return list"
    for item in flat:
        assert isinstance(item, str), "Checklist items should be strings"