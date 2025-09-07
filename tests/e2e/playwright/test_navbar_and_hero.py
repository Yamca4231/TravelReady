# tests/e2e/playwright/test_fe_layout.py
# --------------------------------------------------------------------------------------
# Testy E2E (UI) – layout/FE: navbar, hero/paralaksa, overlap, motyw
# --------------------------------------------------------------------------------------

import os
import re
import time
from pathlib import Path
import pytest
from contextlib import contextmanager

# Import lokalnego zestawu funkcji pomocniczych (Playwright)
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
from playwright_utils import (
    launch_browser, new_context, save_artifacts, dump_html, wait_ui_ready
)

# ---------------------------------------
# USTAWIENIA / POMOCNICZE (jak w test_e2e_ui.py)
# ---------------------------------------
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
CONFIG_PATH  = pathlib.Path(os.getenv("TR_CONFIG", str(PROJECT_ROOT / "config.env")))
TR_ENV       = os.getenv("TR_ENV", "DEV").upper()
ART_DIR      = "artifacts/e2e"
Path(ART_DIR).mkdir(parents=True, exist_ok=True)

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

# Nazwa artefaktu z timestampem
def _artifact_name(prefix: str) -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    return f"{prefix}_{ts}"    

# Czy base_url jest strona WWW
def _assert_html_or_skip(resp, base_url: str):
    ct = (resp.headers.get("content-type") or "").lower() if resp else ""
    if "html" not in ct:
        pytest.skip(f"Base URL nie jest stroną HTML (Content-Type: {ct}). ")

# Adres startowy UI zczytany z config.env 
@pytest.fixture(scope="session")
def base_url() -> str:
    cfg  = _read_env_file(CONFIG_PATH)
    base = _front_base_url(cfg, TR_ENV)
    if not base:
        pytest.skip(f"Brak FRONT/API BASE URL dla {TR_ENV} w {CONFIG_PATH} – pomijam E2E.")
    return base

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

# --------------------------------------------------------------------------------------
# TESTY
# --------------------------------------------------------------------------------------

# ======================
# TC-E-04 – Navbar: sticky/fixed + top z-index  (DEV/PROD)
# ======================
def test_navbar_sticky_and_top_zindex(base_url):
    with browser_page() as (page, _ctx):
        goto_ready(page, base_url, "TC_FE_navbar")

        nav = page.locator(".navbar.navbar-clear")
        assert nav.is_visible(), "Navbar powinien być widoczny."

        # position: sticky (dopuszczamy też fixed)
        position = nav.evaluate("el => getComputedStyle(el).position")
        assert position in ("sticky", "fixed"), f"Navbar position={position}, oczekiwano sticky/fixed."

        # z-index >= 5 (nad tłem)
        z = nav.evaluate("el => getComputedStyle(el).zIndex")
        try:
            zint = int(z)
        except Exception:
            zint = 0
        assert zint >= 5, f"Navbar z-index={z} – powinno być >= 5."

# ======================
# TC-E-05 – Navbar (mobile): hamburger otwiera menu  (DEV/PROD)
# ======================
def test_hamburger_opens_on_mobile(base_url):
    with browser_page() as (page, _ctx):
        page.set_viewport_size({"width": 390, "height": 844})
        goto_ready(page, base_url, "TC_FE_nav_mobile")

        toggler = page.locator(".navbar-toggler")
        assert toggler.is_visible(), "Toggler (hamburger) powinien być widoczny na mobile."

        toggler.click()

        menu = page.locator("#navbarSupportedContent")
        # Po kliknięciu Bootstrap ustawia aria-expanded="true" na togglerze…
        aria = toggler.get_attribute("aria-expanded")
        assert aria == "true", f"Po kliknięciu aria-expanded={aria}, oczekiwano 'true'."

        # …i dodaje 'show' do klasy elementu collapse
        classes = (menu.get_attribute("class") or "")
        assert re.search(r"\bshow\b", classes), f"Menu powinno mieć klasę 'show', class='{classes}'."
        assert menu.is_visible(), "Menu powinno być widoczne po rozwinięciu."

# ======================
# TC-E-06 – Hero caption: widoczność i czytelność  (DEV/PROD)
# ======================
def test_hero_caption_visible_and_readable(base_url):
    with browser_page() as (page, _ctx):
        goto_ready(page, base_url, "TC_FE_hero_caption")

        caption = page.locator(".parallax-caption")
        assert caption.is_visible(), "Sekcja .parallax-caption powinna być widoczna."

        title = page.locator(".hero-title")
        assert title.is_visible(), "Nagłówek .hero-title powinien być widoczny."
        color = title.evaluate("el => getComputedStyle(el).color")
        assert str(color).startswith("rgb("), f"Nietypowy kolor tytułu: {color!r}"