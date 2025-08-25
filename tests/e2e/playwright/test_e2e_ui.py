# tests/e2e/test_e2e_ui.py
# --------------------------------------------------------------------------------------
# Testy E2E (UI) dla Travel Ready (DEV/PROD) – dostosowane do TR_ENV/TR_CONFIG
# --------------------------------------------------------------------------------------
# DO REDME:
# Scenariusze:
#   - TC-E-01 (DEV): Persist zaznaczeń (localStorage)
#   - TC-E-02 (PROD): Read-only sanity (status 200, <title>, brak błędów w konsoli/assetach)
#   - TC-E-03 (DEV): Fallback przy awarii API (symulacja błędu sieci na endpointzie checklisty)
#
# Sterowanie środowiskiem i artefaktami:
#   - TR_ENV=DEV|PROD           -> wybór środowiska testów
#   - TR_CONFIG=ścieżka/env     -> (opcjonalnie) niestandardowa lokalizacja pliku config.env
#   - E2E_VIDEO=on|off          -> nagrywanie wideo Playwrighta
#
# Artefakty (zrzuty .png, wideo .webm, zrzuty DOM .html):
#   - artifacts/e2e/
#
# Uruchomienie (DEV, z nagrywaniem) – PowerShell (jedna linia):
#   $env:TR_ENV="DEV"; $env:E2E_VIDEO="on"; pytest tests/e2e -m e2e
# --------------------------------------------------------------------------------------
import os
import time
import pathlib
import pytest
from pathlib import Path
import sys
from contextlib import contextmanager

# Import lokalnego zestawu funkcji pomocniczych (Playwright)
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
from playwright_utils import (
    launch_browser, new_context, capture_console, capture_responses,
    first_n_checkboxes, safe_check, looks_checked, save_artifacts,
    dump_html, wait_ui_ready
)

# USTAWIENIA LOKALNE
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]                              # korzeń repo (.../TravelReady)
CONFIG_PATH  = pathlib.Path(os.getenv("TR_CONFIG", str(PROJECT_ROOT / "config.env")))   # Ścieżka do pliku konfiguracyjnego
TR_ENV       = os.getenv("TR_ENV", "DEV").upper()                                       # Wybór środowiska - DEV domyślnie
ART_DIR      = "artifacts/e2e"
TR_CHECKLIST_PATH = os.getenv("TR_CHECKLIST_PATH", "/api/checklist")
DEV_ONLY  = pytest.mark.skipif(TR_ENV != "DEV",  reason="Test tylko na DEV (TR_ENV=DEV).")
PROD_ONLY = pytest.mark.skipif(TR_ENV != "PROD", reason="Test tylko na PROD (TR_ENV=PROD).")

pytestmark = [pytest.mark.e2e]

# --------------------------------------------------------------------------------------
# Pomocnicze funkcje/fikstury (konfiguracja, przygotowanie strony, asercje wspólne)
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

# Zwraca URL aplikacji frontendowej (DEV/PROD)
def _front_base_url(cfg: dict, env: str) -> str:
    if env == "DEV":
        return (cfg.get("API_BASE_URL_DEVELOPMENT") or "").rstrip("/")
    else:
        return (cfg.get("API_BASE_URL_PRODUCTION") or "").rstrip("/")

# Helper - Interpretacja wartości logicznych (E2E_VIDEO)
def _env_true(v: str) -> bool:
    return str(v).lower() in ("1", "true", "on", "yes")

# Adres startowy UI zczytany z config.env 
@pytest.fixture(scope="session")
def base_url() -> str:
    cfg  = _read_env_file(CONFIG_PATH)
    base = _front_base_url(cfg, TR_ENV)
    if not base:
        pytest.skip(f"Brak FRONT/API BASE URL dla {TR_ENV} w {CONFIG_PATH} – pomijam E2E.")
    return base
# Flaga nagrywania wideo (E2E_VIDEO)
@pytest.fixture(scope="session")
def record_video_flag() -> bool:
    return _env_true(os.getenv("E2E_VIDEO", "off"))

# Nazwa artefaktu z timestampem
def _artifact_name(prefix: str) -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    return f"{prefix}_{ts}"

# Czy base_url jest strona WWW
def _assert_html_or_skip(resp, base_url: str):
    ct = (resp.headers.get("content-type") or "").lower() if resp else ""
    if "html" not in ct:
        pytest.skip(f"Base URL nie jest stroną HTML (Content-Type: {ct}). ")

# Obsługa cyklu życia przeglądarki/kontekstu/strony.
@contextmanager
def browser_page(record_video_flag: bool):
    pw, browser = launch_browser(headless=True)
    ctx = new_context(browser, record_video=record_video_flag, artifacts_dir=ART_DIR)
    try:
        page = ctx.new_page()
        yield page, ctx
    finally:
        try:
            ctx.close()
        finally:
            browser.close(); pw.stop()

# Wejście na UI, krotki timeout, artefakty startowe (PNG/HTML)
def goto_ready(page, url: str, name_prefix: str):
    resp = page.goto(url, wait_until="domcontentloaded")
    _assert_html_or_skip(resp, url)
    wait_ui_ready(page)
    save_artifacts(page, _artifact_name(f"{name_prefix}_after_goto"), ART_DIR)
    dump_html(page, _artifact_name(f"{name_prefix}_after_goto"), ART_DIR)
    return resp

# Znajdź i zaznacz pierwsze n „checkboxów”:
def tick_first_n(page, n: int, tc_name: str):
    cbs = first_n_checkboxes(page, n)
    if len(cbs) < n:
        save_artifacts(page, _artifact_name(f"{tc_name}_no_checkboxes"), ART_DIR)
        dump_html(page, _artifact_name(f"{tc_name}_no_checkboxes"), ART_DIR)
    assert len(cbs) == n, (f"Na stronie powinny być co najmniej {n} 'checkboxy'. ")
    for cb in cbs:
        safe_check(cb)
    assert all(looks_checked(cb) for cb in cbs), f"{n} pierwszych elementów powinno być zaznaczone."
    return cbs

# Weryfiakcja widocznosci checklisty na stronie
def assert_checklist_visible(page):
    body_text = page.inner_text("body").lower()
    visible = (
        "checklist" in body_text or "lista" in body_text
        or page.query_selector('[data-testid="checklist"]') is not None
        or page.query_selector("#checklist") is not None
    )
    assert visible, "Brak Checklisty."

# Weryfikacja stanu „offline/fallback”
def assert_offline_fallback(page, timeout_ms: int = 6000):
    # 1) Typowe selektory alertów
    try:
        page.wait_for_selector(
            '[data-testid="api-fallback"], [role="alert"], .alert-error, .error, .error-banner, .toast-error',
            timeout=timeout_ms
        )
        return
    except Exception:
        pass
    # 2) Komunikat 'Błąd połączenia z API' z UI
    try:
        page.wait_for_selector('text=/Błąd połączenia z API/i', timeout=timeout_ms)
        return
    except Exception:
        pass
    # 3) Brak komunikatu -> zrzuty i FAIL
    save_artifacts(page, _artifact_name("TC_E_03_no_fallback"), ART_DIR)
    dump_html(page, _artifact_name("TC_E_03_no_fallback"), ART_DIR)
    assert False, "Brak komunikatu: 'Błąd połączenia z API'"

# --------------------------------------------------------------------------------------
# TESTY
# --------------------------------------------------------------------------------------

# ======================
# TC-E-01 – DEV only: Persist zaznaczeń (localStorage)
# ======================
@DEV_ONLY
def test_tc_e_01_persistence_localstorage_dev(base_url, record_video_flag):
    with browser_page(record_video_flag) as (page, _ctx):
        # 1) Wejście na UI, krotki timeout, artefakty startowe (PNG/HTML)
        goto_ready(page, base_url, "TC_E_01")
        # 2) Zeruje localStorage i odświeża (symulacja pierwszego uruchomienia)
        page.evaluate("() => { try { localStorage.clear(); } catch(e) {} }")
        page.reload(wait_until="domcontentloaded"); wait_ui_ready(page)
        # 3) Zaznacz pierwsze 3 „checkboxy”
        tick_first_n(page, 3, "TC_E_01")
        # 4) Odświeża stronę i pobiera pierwsze 3 elementy (czy zachował zaznaczone)
        page.reload(wait_until="domcontentloaded"); wait_ui_ready(page)
        assert all(looks_checked(cb) for cb in first_n_checkboxes(page, 3)), \
            "Brak zaznaczonych elementów."
        
        save_artifacts(page, _artifact_name("TC_E_01_success"), ART_DIR)

# ======================
# TC-E-02 – PROD only: Read-only (200, <title>, brak błędów w konsoli/assetach)
# ======================
@PROD_ONLY
def test_tc_e_02_homepage_readonly_prod(base_url, record_video_flag):
    with browser_page(record_video_flag) as (page, _ctx):
        # 1) Nasłuch błędów
        console_logs, response_errors = [], []
        capture_console(page, console_logs); 
        capture_responses(page, response_errors)
        # 2) Wejście + sanity + artefakty
        resp = goto_ready(page, base_url, "TC_E_02")
        assert resp is not None and resp.ok, f"Strona główna {base_url} nie zwraca 200."
        assert page.title(), "Powinien istnieć <title>."
        assert_checklist_visible(page)
        # 3) Brak błędów krytycznych w konsoli / przy ładowaniu assetów
        errors = [l for l in console_logs if l.startswith("[error]")]
        assert not errors, f"Sprawdź błędy: {errors}"
        assert not response_errors, f"Błąd ładowania assetów: {response_errors}"

        save_artifacts(page, _artifact_name("TC_E_02_success"), ART_DIR)

# ======================
# TC-E-03 – DEV only: Fallback przy awarii API
# ======================
@DEV_ONLY
def test_tc_e_03_fallback_api_unavailable_dev(base_url, record_video_flag):
    with browser_page(record_video_flag) as (page, ctx):
        api_paths = [p.strip() for p in TR_CHECKLIST_PATH.split(",") if p.strip()] or ["/api/checklist"]

        # 1) Przechwytuje żądania do API checklisty i symuluje błąd sieci
        def handler(route):
            url = route.request.url.lower()
            if any(p in url for p in api_paths):
                route.abort("failed")
            else:
                route.continue_()
        ctx.route("**/*", handler)
        # 2) Wejście + sanity + artefakty
        goto_ready(page, base_url, "TC_E_03")
        # 3) Weryfikacja stanu „offline/fallback”
        assert_offline_fallback(page)
        
        save_artifacts(page, _artifact_name("TC_E_03_success"), ART_DIR)
