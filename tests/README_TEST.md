# Travel Ready Tests:
# Wymagania
    - Python 3.12
    - pytest
    - pytest-cov

## Zawartość 
```
py/
  app/
    validation.py             # centralna walidacja (POST /api/checked)
tests/
  conftest.py                 # dodaje 'py' do PYTHONPATH (importy app.*)
  unit/
    test_checklist_repository.py      # testy jednostkowe repozytorium
    test_validation.py                # testy jednostkowe walidacji payloadu "checked"
  integration/
    test_api_contract.py              # testy integracyjne GET /api/checklist
    test_post_checked_dev.py          # testy integracyjne POST /api/checked
    schemas/
      checklist.schema.json           # kontrakt JSON dla GET /api/checklist

pytest.ini                             # markery: unit/integration
```

## Integracja w projekcie (Do uzupełnienia o tetsy INTEGRACYJNE)
1. Skopiuj `py/app/validation.py`
2. Skopiuj folder `tests/unit` i `tests/integration` do katalogu głównego.
3. Upewnij się, że moduł `app.repository` zawiera klasę `ChecklistRepository`
4. Upewnij się, że `tests/conftest.py` dodaje katalog `py` do `sys.path` — dzięki temu importy `from app...` działają z pytest.
5. Upewnij się, masz konfigurację środowisk w pliku `config.env`

## Testy jednostkowe (Unit)
> Testy jednostkowe dla `ChecklistRepository`oraz wydzielony moduł walidacji danych wejściowych dla `POST /api checked`.
> **Nie** wymagają uruchomionej aplikacji ani config.env.
> Jeśli `ChecklistRepository` nie jest dostępny, testy dla repo zostaną **pominięte**.

### Uruchamianie
Z poziomu katalogu głównego repozytorium (tam gdzie jest `tests/`):

```bash
  # Testy jednostkowe
  pytest tests/unit -m unit

  # Testy jednostkowe z pokryciem
  pytest tests/unit -m unit --cov=app --cov-report=term-missing
  pytest -m unit --cov=app --cov-branch --cov-report=html         # Opcionalne - Raport HTML w .\htmlcov\index.html
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

## Testy integracyjne

> Testy integracyjne dla GET /api/checklist oraz POST /api/checked.
> Wymagają uruchomionego backendu na DEV oraz dostępu do konfiguracji.
> Jeśli brakuje API_BASE_URL_DEVELOPMENT lub endpointy nie odpowiadają, odpowiednie przypadki zostaną pominięte; na PROD testy modyfikujące są pomijane (TR_ENV=PROD).

### Uruchamianie
> Krok 1 — uruchom serwer z coverage (okno 1 PowerShell (w katalogu projektu)):
```bash
  pip install coverage
  $env:PYTHONPATH = (Resolve-Path .\py)
  coverage erase
  python -m coverage run --parallel-mode py/run.py
  # Zostaw to okno włączone (serwer działa).
```
> Krok 2 — odpal testy integracyjne (okno 2)
```bash
  pytest tests/integration -m "integration" -ra
```
> Krok 3 — zbuduj raport (wróć do okna 1 po Ctrl+C)
```bash
  coverage combine
  coverage report -m
  coverage html   # Opcionalne - Raport HTML w .\htmlcov\index.html
```

### Co sprawdzamy
`GET /api/checklist`
- Status 200, nagłówek `Content-Type` z `json`.
- Zgodność odpowiedzi z JSON Schema.
- Sanity minimalnej zawartości: ≥ 1 sekcja; każda sekcja to lista `string`.
`POST /api/checked`
- Akceptacja pustej listy `{"checked": []}` `(200/204)`.
- Akceptacja poprawnego podzbioru elementów (pobranych z `GET /api/checklist`).
- Odrzucenie elementu spoza listy (`4xx`).
- Idempotencja: powtórny POST z tym samym payloadem → nadal `200/204`

### Scenariusze & oczekiwane wyniki (integration)
- Contract

TC‑I‑01: GET /api/checklist
Scenariusz: pobierz checklistę; oceń status, nagłówki i kontrakt.
Oczekiwany wynik: 200, Content-Type zawiera json, zgodność z JSON Schema; ≥ 1 sekcja, wartości to list[str].

- Checked

TC‑I‑02: POST /api/checked (pozytywne)
Scenariusz: wyślij (1) pustą listę oraz (2) poprawny podzbiór elementów; następnie (3) powtórz POST z tym samym payloadem.
Oczekiwany wynik: dla (1), (2) i (3) 200/204.

TC‑I‑03: POST /api/checked (negatywne)
Scenariusz: dodaj element spoza dozwolonej listy.
Oczekiwany wynik: kod 4xx (walidacja).