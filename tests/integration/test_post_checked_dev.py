# tests/integration/test_post_checked_dev.py
# --------------------------------------------------------------------------------------
# Testy integracyjne dla endpointu: POST /api/checked
# --------------------------------------------------------------------------------------

import os
import json
import pathlib
import pytest
import requests

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

# TC-I-02 (część 1): Pusta lista jest akceptowana (reset zaznaczeń)
def test_post_empty_list_is_accepted(join):
    url = join("/api/checked")
    payload = {"checked": []}   # pusta lista
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
    assert resp.status_code in (200, 204), f"POST pustej listy powinien zwrócić 200/204, a zwrócił {resp.status_code}"


# TC-I-02 (część 2): Poprawny podzbiór elementów jest akceptowany (Wariant pozytywny)
def test_post_valid_subset_is_accepted(join, allowed_items):
    url = join("/api/checked")
    subset = allowed_items[:3] if allowed_items else []  # wybierz kilka pierwszych
    payload = {"checked": subset}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
    assert resp.status_code in (200, 204), f"POST poprawnego zestawu powinien zwrócić 200/204, a zwrócił {resp.status_code}"

# TC-I-02 (część 3): Własność - Powtórny POST z tym samym payloadem
def test_post_is_idempotent_for_same_payload(join, allowed_items):
    url = join("/api/checked")
    subset = allowed_items[:2] if allowed_items else []
    payload = {"checked": subset}
    headers = {"Content-Type": "application/json"}

    r1 = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
    r2 = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
    assert r1.status_code in (200, 204) and r2.status_code in (200, 204), f"Powtarzalny POST powinien być bezbłędny (200/204), r1={r1.status_code}, r2={r2.status_code}"

# TC-I-02 (część 4): Content-Type != application/json (oczekiwane 4xx)
def test_variant_content_type_non_json_rejected(join, allowed_items):
    url = join("/api/checked")
    subset = allowed_items[:1] if allowed_items else []
    # Wysyłamy poprawny JSON, ale z niewłaściwym Content-Type
    resp = requests.post(
        url,
        data=json.dumps({"checked": subset}),
        headers={"Content-Type": "text/plain"},
        timeout=5
    )
    # DEBUG-only
    """
    print("\n[DEBUG malformed-json]")
    print("URL:      ", url)
    print("Status:   ", resp.status_code)
    print("Req-CT:  ", (resp.request.headers.get("Content-Type") or ""))
    print("Resp-CT:  ", (resp.headers.get("Content-Type") or ""))
    print("Resp-Hdr: ", dict(resp.headers))
    print("Resp-Body:", resp.text[:500])
    """

    assert 400 <= resp.status_code < 500, f"Oczekiwał 4xx dla niewłaściwego Content-Type, a zwrócił {resp.status_code}"

# TC-I-02 (część 5): Uszkodzony JSON (oczekiwane 4xx)
def test_variant_malformed_json_rejected(join):
    url = join("/api/checked")
    bad_body = '{"checked": [}' # celowo uszkodzony JSON
    
    resp = requests.post(
        url,
        data=bad_body,
        headers={"Content-Type": "application/json"},
        timeout=5
    )

    # DEBUG-only
    """
    print("\n[DEBUG malformed-json]")
    print("URL:      ", url)
    print("Status:   ", resp.status_code)
    print("Req-CT:   ", "application/json")
    print("Resp-CT:  ", (resp.headers.get("Content-Type") or ""))
    print("Resp-Hdr: ", dict(resp.headers))
    print("Resp-Body:", resp.text[:500])
    """

    assert 400 <= resp.status_code < 500, f"Oczekiwał kod błędu 4xx dla nieparsowalnego JSON, a zwrócił {resp.status_code}"

# TC-I-02 (część 6): Duplikaty.
def test_variant_duplicates_policy_documented(join, allowed_items):
    url = join("/api/checked")
    if not allowed_items:
        pytest.skip("Brak listy dozwolonych elementów.")
    item = allowed_items[0]
    payload = {"checked": [item, item]}
    r = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=5)

    assert r.status_code in (200, 204), r.text
    get_r = requests.get(join("/api/checked"), timeout=5)
    got = get_r.json()
    # Oczekiwanie jednego wystąpienia elementu
    assert got.count(item) == 1, f"Deduplikacja: Oczekiwał 1 wystąpienia '{item}', otrzymano {got.count(item)}; got={got}"
    # DEBUG-only
    #print(f"[PASS] TC-I-02(6) dedup — input=[{item},{item}] -> stored={got}")

# TC-I-02 (część 7) - Over-limit - Długość listy > limit z config.env
def test_variant_over_limit_rejected(join, allowed_items):
    cfg = _read_env_file(CONFIG_PATH)
    limit = int(cfg.get("MAX_CHECKLIST_ITEMS_DEVELOPMENT", "200"))

    # Fallback, gdyby allowed_items było puste:
    base = list(allowed_items) if allowed_items else ["Paszport"]

    # Zbuduj listę o długości (limit + 1) przez powielenie elementów bazowych
    factor = max(1, (limit // len(base)) + 2)
    too_long = (base * factor)[:limit + 1]
    assert len(too_long) == limit + 1  # sanity check testu

    resp = requests.post(
        join("/api/checked"),
        json={"checked": too_long}, 
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    assert 400 <= resp.status_code < 500, f"Oczekiwał kodu błędu 4xx dla payloadu > {limit}, a zwrócił {resp.status_code}"

# TC-I-02 (część 8): Method safety (niedozwolone metody -> 405)
def test_variant_method_safety_put_delete(join):
    url = join("/api/checked")
    r_put = requests.put(url, data="{}", headers={"Content-Type": "application/json"}, timeout=5)
    r_del = requests.delete(url, timeout=5)
    assert r_put.status_code == 405 or r_put.status_code == 404, f"PUT jest zabroniony (405/404), a jest {r_put.status_code}"
    assert r_del.status_code == 405 or r_del.status_code == 404, f"DELETE jest zabroniony (405/404), a jest {r_del.status_code}"

# TC-I-03: Walidacja – element spoza listy jest odrzucany
def test_post_unknown_item_is_rejected(join, allowed_items):
    url = join("/api/checked")
    invalid = "__INTEGRATION_TEST_INVALID_ITEM__"  # marker testowy: nie ma prawa istnieć
    base = allowed_items[:2] if allowed_items else []  # dorzuć "zły" element do (opcjonalnej) poprawnej podstawy
    payload = {"checked": base + [invalid]}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
    assert 400 <= resp.status_code < 500, f"Oczekiwał kodu błędu 4xx dla niedozwolonego elementu, a zwrócił {resp.status_code}"
