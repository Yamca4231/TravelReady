# tests/integration/test_post_checked_dev.py
# --------------------------------------------------------------------------------------
# Testy integracyjne dla endpointu: POST /api/checked
# --------------------------------------------------------------------------------------

import os
import json
import pathlib
import pytest
import requests

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]                              # korzeń repo (.../TravelReady)
CONFIG_PATH = pathlib.Path(os.getenv("TR_CONFIG", str(PROJECT_ROOT / "config.env")))    # Ścieżka do pliku konfiguracyjnego
TR_ENV = os.getenv("TR_ENV", "DEV").upper()                                             # Wybór środowiska - DEV domyślnie

# USTAWIENIA LOKALNE
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]  # .../TravelReady
CONFIG_PATH = pathlib.Path(os.getenv("TR_CONFIG", str(PROJECT_ROOT / "config.env")))
TR_ENV = os.getenv("TR_ENV", "DEV").upper()

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

# Przygotowanie zbioru dozwolonych elementów
def _flatten_allowed(items_dict):
    flat = []
    for arr in items_dict.values():
        if isinstance(arr, list):
            flat.extend([x for x in arr if isinstance(x, str)])
    # usuwamy duplikaty, zachowując kolejność
    seen = set()
    out = []
    for x in flat:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

# Pobiera dozwolony zbiór elementów z GET /api/checklist
@pytest.fixture(scope="module")
def allowed_items(join):
    url = join("/api/checklist")
    resp = requests.get(url, timeout=5)
    if resp.status_code != 200:
        pytest.skip(f"Brak checklisty (status {resp.status_code}) – pomijam testy POST.")
    data = resp.json()
    return _flatten_allowed(data)

# TC-I-02: Pusta lista jest akceptowana (reset zaznaczeń)
def test_post_empty_list_is_accepted(join):
    url = join("/api/checked")
    payload = {"checked": []}   # pusta lista
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
    assert resp.status_code in (200, 204), f"POST pustej listy powinien zwrócić 200/204, a zwrócił {resp.status_code}"


# TC-I-02 (wariant pozytywny): Poprawny podzbiór elementów jest akceptowany
def test_post_valid_subset_is_accepted(join, allowed_items):
    url = join("/api/checked")
    subset = allowed_items[:3] if allowed_items else []  # wybierz kilka pierwszych
    payload = {"checked": subset}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
    assert resp.status_code in (200, 204), f"POST poprawnego zestawu powinien zwrócić 200/204, a zwrócił {resp.status_code}"

# TC-I-02 (własność): Powtórny POST z tym samym payloadem
def test_post_is_idempotent_for_same_payload(join, allowed_items):
    url = join("/api/checked")
    subset = allowed_items[:2] if allowed_items else []
    payload = {"checked": subset}
    headers = {"Content-Type": "application/json"}

    r1 = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
    r2 = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
    assert r1.status_code in (200, 204) and r2.status_code in (200, 204), f"Powtarzalny POST powinien być bezbłędny (200/204), r1={r1.status_code}, r2={r2.status_code}"


# TC-I-03: Walidacja – element spoza listy jest odrzucany
def test_post_unknown_item_is_rejected(join, allowed_items):
    url = join("/api/checked")
    invalid = "__INTEGRATION_TEST_INVALID_ITEM__"  # marker testowy: nie ma prawa istnieć
    base = allowed_items[:2] if allowed_items else []  # dorzuć "zły" element do (opcjonalnej) poprawnej podstawy
    payload = {"checked": base + [invalid]}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
    assert 400 <= resp.status_code < 500, f"Oczekiwano kodu 4xx dla niedozwolonego elementu, a zwrócono {resp.status_code}"
