# tests/integration/test_api_contract.py
# --------------------------------------------------------------------------------------
# Testy integracyjne dla endpointu: GET /api/checklist
# --------------------------------------------------------------------------------------

import os
import json
import pathlib
import pytest
import requests
from jsonschema import validate, ValidationError

# USTAWIENIA LOKALNE
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]                              # korzeń repo (.../TravelReady)
CONFIG_PATH = pathlib.Path(os.getenv("TR_CONFIG", str(PROJECT_ROOT / "config.env")))    # Ścieżka do pliku konfiguracyjnego
TR_ENV = os.getenv("TR_ENV", "DEV").upper()                                             # Wybór środowiska - DEV domyślnie

# Uruchomienie na PROD, pomija całe testy
if TR_ENV == "PROD": pytest.skip("Testy POST są dozwolone wyłącznie na DEV (TR_ENV=DEV).", allow_module_level=True)

pytestmark = [pytest.mark.integration]

#  Prosty parser pliku config.env. Zwraca dict ze zmiennymi konfiguracyjnymi.
def _read_env_file(path: pathlib.Path) -> dict:
    if not path.is_file():
        return {}
    data = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip()
    return data

# Zwraca funkcję sklejającą base_url z endpointem, np. join("/api/checklist").
@pytest.fixture(scope="session")
def join():
    cfg = _read_env_file(CONFIG_PATH)
    base = (cfg.get("API_BASE_URL_DEVELOPMENT", "") or "").rstrip("/")
    if not base:
        pytest.skip(f"Brak API_BASE_URL_DEVELOPMENT w {CONFIG_PATH} – pomijam testy integracyjne POST.")
    def _j(endpoint: str) -> str:
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return f"{base}{endpoint}"
    return _j

# TC-I-01 (Część 1): Endpoint żyje i zwraca JSON (status + nagłówki).
def test_checklist_status_and_headers(join):
    url = join("/api/checklist")
    resp = requests.get(url, timeout=5) # timeout (5 s) chroni przed wiszącym zapytaniem.
    # Sprawdza kod odpowiedzi 200 (usługa działa).
    assert resp.status_code == 200, f"GET {url} powinien zwrócić 200"
    ct = resp.headers.get("Content-Type", "")
    # Sprawdza nagłówek Content-Type, czy wskazuje na JSON.
    assert "json" in ct.lower(), f"Oczekiwano JSON, nagłówek Content-Type={ct}"

# TC-I-01 (część 2): Zgodność ze schematem (kontrakt API)
def test_checklist_contract_schema(join):
    url = join("/api/checklist")
    resp = requests.get(url, timeout=5)
    assert resp.status_code == 200
    data = resp.json()  # Zamiana odpowiedzi HTTP na obiekt Pythona (dict/list).

    # Wczytaj schemat (umowa formatu odpowiedzi)
    schema_path = pathlib.Path(__file__).parent / "schemas" / "checklist.schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    #Walidacja
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        pytest.fail(f"Struktura checklisty narusza schemat JSON: {e.message}")

# TC-I-01 (część 3): Sanity check minimalnej zawartości
def test_checklist_minimal_content(join):
    url = join("/api/checklist")
    resp = requests.get(url, timeout=5)
    assert resp.status_code == 200
    data = resp.json()

    # Minimalna zawartość: co najmniej 1 sekcja
    assert isinstance(data, dict) and len(data) >= 1, "Checklist powinna zawierać >=1 sekcję"
    # Każda sekcja -> lista stringów
    for section, items in data.items():
        assert isinstance(items, list), f"Sekcja '{section}' powinna mieć listę pozycji"
        for it in items:
            assert isinstance(it, str), "Pozycje w sekcji muszą być stringami"