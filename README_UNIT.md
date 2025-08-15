# Travel Ready Tests:
# Wymagania
    - Python 3.12
    - pytest
    - pytest-cov

##   -Testy jednostkowe (Unit)
> Testy jednostkowe dla `ChecklistRepository`oraz wydzielony moduł walidacji danych wejściowych dla `POST /api checked`.
> **Nie** wymagają uruchomionej aplikacji ani config.env.
> Jeśli `ChecklistRepository` nie jest dostępny, testy dla repo zostaną **pominięte**.

### Zawartość
```
py/
  app/
    validation.py             # centralna walidacja (POST /api/checked)
tests/
  conftest.py                 # dodaje 'py' do PYTHONPATH (importy app.*)
  unit/
    test_checklist_repository.py
    test_validation.py
pytest.ini
```

### Integracja w projekcie

1. Skopiuj `py/app/validation.py`
2. Skopiuj folder `tests/unit` do katalogu głównego.
3. Upewnij się, że moduł `app.repository` zawiera klasę `ChecklistRepository`
4. Upewnij się, że `tests/conftest.py` dodaje katalog `py` do `sys.path` — dzięki temu importy `from app...` działają z pytest.



### Uruchamianie testów
Z poziomu katalogu głównego repozytorium (tam gdzie jest `tests/`):

```bash
# Testy jednostkowe
pytest tests/unit -m unit

# Testy jednostkowe z pokryciem
pytest tests/unit -m unit --cov=app --cov-report=term-missing
pytest -m unit --cov=app --cov-branch --cov-report=html         # Raport HTML w htmlcov/index.html
```

### Co sprawdzamy
`ChecklistRepository.get_all_items()`
  - Zwraca `dict` sekcji → listy elementów (≥ 1 sekcja).
  - Każda lista zawiera stringi.

`ChecklistRepository.get_all_items_flat()`
  - Zwraca list[str] (wszystkie elementy to stringi).

Walidacja `POST /api/checked` (`app/validation.py`)
  - payload jest słownikiem z kluczem `"checked"`,
  - `"checked"` to lista stringów,
  - elementy muszą należeć do whitelisty `allowed_items`,
  - duplikaty usuwane z zachowaniem kolejności,
  - limit liczby pozycji (parametr `max_len`) egzekwowany przed deduplikacją,
  - pusta lista dozwolona,
  - przy błędach rzucany jest `ValidationError`,
  - wrapper `validate_checked_list([...])` zachowuje się równoważnie z `validate_checked_payload({"checked":[...]})`
 (deduplikacja + kolejność; limit `max_len`; whitelista).

### Scenariusze & oczekiwane wyniki (Unit)
 - Repository

TC-U-01: get_all_items()
Scenariusz: pobierz pełną checklistę.
Oczekiwany wynik: dict z ≥ 1 sekcją; wartości to list[str].

TC-U-02: get_all_items_flat()
Scenariusz: pobierz spłaszczoną listę pozycji.
Oczekiwany wynik: list[str] (wszystkie elementy są stringami).

- Validation

TC-U-03: Pusta lista
Scenariusz: {"checked": []}.
Oczekiwany wynik: [] (PASS).

TC-U-04: Dedup + kolejność
Scenariusz: duplikaty w checked.
Oczekiwany wynik: zwrócona lista bez duplikatów, kolejność pierwszych wystąpień zachowana.

TC-U-05: checked nie-lista
Scenariusz: checked jest stringiem.
Oczekiwany wynik: ValidationError („musi być listą” / „must be a list”).

TC-U-06: element nie-string
Scenariusz: element int w liście.
Oczekiwany wynik: ValidationError („musi być string”).

TC-U-07: nieznany element
Scenariusz: element nie należy do allowed_items.
Oczekiwany wynik: ValidationError z nazwą winowajcy.

TC-U-08: limit max_len
Scenariusz: lista dłuższa niż max_len (nawet jeśli to duplikaty).
Oczekiwany wynik: ValidationError (limit egzekwowany przed dedupem).

TC-U-09: strażnicy payloadu
Scenariusz: payload nie-dict; brak klucza "checked".
Oczekiwany wynik: ValidationError.

TC-U-10: wrapper
Scenariusz: wywołanie validate_checked_list na „gołej” liście.
Oczekiwany wynik: identyczne jak validate_checked_payload — deduplikacja z zachowaniem kolejności, honorowanie max_len, weryfikacja względem allowed_items.