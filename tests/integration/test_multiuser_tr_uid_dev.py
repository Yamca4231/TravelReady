# tests/integration/test_multiuser_tr_uid_dev.py
# --------------------------------------------------------------------------------------
# Punkt 1: Multi-user v1 (bez logowania) z cookie tr_uid – testy integracyjne (DEV-only)
# --------------------------------------------------------------------------------------

import os
import json
import pathlib
import threading
import pytest
import requests

# USTAWIENIA LOKALNE
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
CONFIG_PATH = pathlib.Path(os.getenv("TR_CONFIG", str(PROJECT_ROOT / "config.env")))
TR_ENV = os.getenv("TR_ENV", "DEV").upper()
TLS_TESTS_ENABLED = os.getenv("TR_TLS_TESTS", "0") == "1"

# Uruchomienie na PROD pomija całe testy (write)
if TR_ENV == "PROD":
    pytest.skip("Testy multi-user (write) są dozwolone wyłącznie na DEV (TR_ENV=DEV).", allow_module_level=True)

pytestmark = [pytest.mark.integration]

# --------------------------------------------------------------------------------------
# Pomocnicze funkcje
# --------------------------------------------------------------------------------------

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
        pytest.skip(f"Brak API_BASE_URL_DEVELOPMENT w {CONFIG_PATH} – pomijam testy integracyjne multi-user.")
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
    r = requests.get(join("/api/checklist"), timeout=5)
    if r.status_code != 200:
        pytest.skip(f"Brak checklisty (status {r.status_code}) – pomijam testy multi-user.")
    return _flatten_allowed(r.json())

# Tworzy NOWĄ sesję HTTP dla jednego "użytkownika" testowego
def _session():
    s = requests.Session()
    s.headers.update({"Accept": "application/json"})    # Oczekiwanie JSON
    return s

# Pobiera bieżący stan zaznaczeń DLA TEJ SESJI (tego usera).
def _get_checked(ses: requests.Session, join):
    r = ses.get(join("/api/checked"), timeout=5)
    assert r.status_code == 200, r.text
    return r.json()

# Zapis stanu zaznaczeń DLA TEJ SESJI (tego usera) przez POST /api/checked.
def _post_checked(ses: requests.Session, join, items):
    url = join("/api/checked")
    payload = {"checked": items}
    r = ses.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=5)
    return r

# --------------------------------------------------------------------------------------
# TESTY
# --------------------------------------------------------------------------------------

# TC-I-05: Nowa sesja (bez tr_uid) robi POST -> backend nadaje unikalne ciasteczko (tr_uid).
def test_cookie_is_issued_on_first_post(join, allowed_items):
    ses = _session()
    resp = _post_checked(ses, join, allowed_items[:2] if allowed_items else [])
    assert resp.status_code in (200, 204), resp.text

    # Walidacja nadania ciasteczka z tr_uid
    set_cookie = resp.headers.get("Set-Cookie", "")
    assert "tr_uid=" in set_cookie or "tr_uid" in [c.name for c in ses.cookies], \
        "Oczekiwał nadania przez backend nadania ciasteczka z tr_uid (Set-Cookie)."
    
    # DEBUG-only
    # print("Set-Cookie:", set_cookie)
    # print("Client cookies:", [(c.name, c.value, c.domain, c.path) for c in ses.cookies])

# TC-I-06: Weryfikacja czy ciasteczko użytkownika ma flagę HttpOnly
def test_cookie_has_httponly_flag(join, allowed_items):
    
    ses = _session()
    resp = _post_checked(ses, join, allowed_items[:1] if allowed_items else [])
    set_cookie = resp.headers.get("Set-Cookie", "")
    assert "HttpOnly" in set_cookie, f"Brak flagi HttpOnly w Set-Cookie: {set_cookie}"

    # DEBUG-only
    # print("Set-Cookie:", set_cookie)

# TC-I-07: Weryfikacja HTTPS (flaga Secure + Path=/)
@pytest.mark.skipif(not TLS_TESTS_ENABLED, reason="Test bezpieczeństwa cookie (Secure/Path=/) – wyłączony domyślnie." \
" Ustaw TR_TLS_TESTS=1, gdy DEV/PROD ma HTTPS i backend ustawia flagi.")
def test_cookie_has_secure_flag_on_dev(join, allowed_items):

    ses = _session()
    resp = _post_checked(ses, join, allowed_items[:1] if allowed_items else [])
    set_cookie = resp.headers.get("Set-Cookie", "")
    assert "Secure" in set_cookie and "Path=/" in set_cookie, f"Brak Secure/Path w Set-Cookie: {set_cookie}"

    # DEBUG-only
    # print("Set-Cookie:", set_cookie)

# TC-I-08: Izolacja - Dwie niezależne sesje (A i B) mają odseparowane listy
def test_isolation_between_two_users(join, allowed_items):
    
    ses_a = _session()
    ses_b = _session()

    items_a = allowed_items[:2] if allowed_items else []
    items_b = allowed_items[2:5] if len(allowed_items) >= 5 else []

    # A – pierwszy POST (ustawi tr_uid), ale zapis może pójść 'bez UID'
    ra1 = _post_checked(ses_a, join, items_a);  assert ra1.status_code in (200, 204)
    # A – drugi POST (już z tr_uid) → zapis na 'konto' A
    ra2 = _post_checked(ses_a, join, items_a);  assert ra2.status_code in (200, 204)

    # B – analogicznie
    rb1 = _post_checked(ses_b, join, items_b);  assert rb1.status_code in (200, 204)
    rb2 = _post_checked(ses_b, join, items_b);  assert rb2.status_code in (200, 204)

    # Odczyty per user
    after_a = _get_checked(ses_a, join)
    after_b = _get_checked(ses_b, join)

    assert set(after_a) == set(items_a), f"A powinien widzieć tylko swoje zaznaczenia, dostał: {after_a}"
    assert set(after_b) == set(items_b), f"B powinien widzieć tylko swoje zaznaczenia, dostał: {after_b}"
    assert set(after_a) != set(after_b) or (items_a == items_b == []), "Stany A i B nie powinny się mieszać."

    # DEBUG-only
    # print("A:", after_a, "B:", after_b)

# TC-I-09: Nowy użytkownik (nowa sesja bez tr_uid) – stan bazowy i możliwość wyzerowania
def test_new_user_sees_empty_until_posts(join):
    fresh = _session()

     # 1) Stan bazowy – dopuszczamy [], ale tolerujemy też preseedowany fallback
    current = _get_checked(fresh, join)
    assert isinstance(current, list), f"Kontrakt: GET /api/checked powinien zwracać listę, a nie {type(current).__name__}"

    # 2) Resetujemy stan dla tej świeżej sesji
    r = _post_checked(fresh, join, [])
    assert r.status_code in (200, 204), f"POST [] powinien zwrócić 200/204, a zwrócił {r.status_code}: {r.text}"

    # 3) Po resecie stan MUSI być pusty
    after = _get_checked(fresh, join)
    assert after == [], f"Po resecie nowa sesja powinna mieć pusty stan, a zwrócono: {after}"

    # DEBUG-only
    # print("Baseline:", current, "After reset:", after)

# TC-I-10: Współbieżność – jednoczesne zapisy A i B nie krzyżują stanów
def test_concurrent_posts_two_users(join, allowed_items):  
    ses_a = _session()
    ses_b = _session()

     # WARM-UP: nadaje tr_uid i czyści stan w obu sesjach
    r_aw = _post_checked(ses_a, join, [])  # pusty POST tylko po to, by ustawić cookie tr_uid
    r_bw = _post_checked(ses_b, join, [])
    assert r_aw.status_code in (200, 204) and r_bw.status_code in (200, 204), \
        f"Warm-up POST powinien wskazać 200/204, otrzymano: A={r_aw.status_code}, B={r_bw.status_code}"

    # Payloady do równoległego zapisu
    items_a = allowed_items[:3] if allowed_items else []
    items_b = allowed_items[3:6] if len(allowed_items) >= 6 else ["Telefon"]

    res = {}

    # Każdy wątek robi swój POST; wynik statusu zapisujemy do 'res'
    def do_post(name, ses, items):
        res[name] = _post_checked(ses, join, items).status_code

    # Równoległe POST-y A i B
    t1 = threading.Thread(target=do_post, args=("A", ses_a, items_a))
    t2 = threading.Thread(target=do_post, args=("B", ses_b, items_b))
    t1.start(); t2.start(); t1.join(); t2.join()

    # Operacja zapisu dla A jak i B musi sie powieść
    assert res.get("A") in (200, 204) and res.get("B") in (200, 204)

    # Stany A i B
    after_a = _get_checked(ses_a, join)
    after_b = _get_checked(ses_b, join)

    assert set(after_a) == set(items_a)
    assert set(after_b) == set(items_b)

    # DEBUG-only
    # print("A:", after_a, "B:", after_b)

# TC-I-11: Ten sam user – dwa szybkie POST-y -> last-write-wins
def test_same_user_last_write_wins(join, allowed_items):
    ses = _session()
    first = allowed_items[:1] if allowed_items else []
    second = allowed_items[1:3] if len(allowed_items) >= 3 else ["Paszport"]

    r1 = _post_checked(ses, join, first)
    assert r1.status_code in (200, 204)
    r2 = _post_checked(ses, join, second)
    assert r2.status_code in (200, 204)

    after = _get_checked(ses, join)
    assert set(after) == set(second), f"Oczekiwałem last-write-wins. Otrzymałem: {after}"

    # DEBUG-only
    # print("first:", first, "second:", second, "after:", after)