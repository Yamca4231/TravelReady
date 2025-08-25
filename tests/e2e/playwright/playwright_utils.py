# tests/e2e/playwright_utils.py
# --------------------------------------------------------------------------------------
# Zestaw funkcji pomocniczych dla testów E2E (Playwright)
# --------------------------------------------------------------------------------------
from __future__ import annotations
from pathlib import Path
from typing import List, Tuple, Optional

# Import Playwright (dopiero przy uruchomieniu testów)
try:
    from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Response
except Exception:
    sync_playwright = None  # type: ignore

# USTAWIENIA LOKALNE
ART_DIR_DEFAULT = "artifacts/e2e"       # Domyślny katalog artefaktów (zrzuty, wideo, HTML)
# typowe zasoby, których nie analizujemy pod błędy
_ASSET_EXT_SKIP = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf", ".map")

# Zapewnia istnienie katalogu
def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

# Buduje ścieżkę dla artefaktów (zrzuty z testów).
def _art_path(artifacts_dir: str, name: str, ext: str) -> Path:
    p = Path(artifacts_dir)
    _ensure_dir(p)
    return p / f"{name}.{ext}"

# Start playwright i przeglądarki
def launch_browser(headless: bool = True) -> Tuple[object, "Browser"]:
    if sync_playwright is None:
        raise RuntimeError(
            "Playwright nie jest zainstalowany. Zainstaluj:\n"
            "  pip install playwright\n"
            "  python -m playwright install chromium"
        )
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=headless)
    return pw, browser

# Utwórz nowy kontekst (izolowana sesja przeglądarki) z opcją nagrywania wideo.
def new_context(
    browser: "Browser",
    record_video: bool = False,
    artifacts_dir: str = ART_DIR_DEFAULT
) -> "BrowserContext":
    _ensure_dir(Path(artifacts_dir))
    return browser.new_context(
        ignore_https_errors=True,
        record_video_dir=artifacts_dir if record_video else None
    )

# Nasłuchy (konsola + błędy assetów)
def attach_listeners(
    page: "Page",
    console_sink: Optional[List[str]] = None,
    network_error_sink: Optional[List[str]] = None
) -> None:
    if console_sink is not None:
        page.on("console", lambda msg: console_sink.append(f"[{msg.type()}] {msg.text()}"))
    if network_error_sink is not None:
        def _on_response(resp: "Response"):
            url = resp.url.lower()
             # Pomija typowe assety, których błędy i tak nic nie wnoszą (np. favicon 404)
            if url.endswith(_ASSET_EXT_SKIP) or any(part in url for part in _ASSET_EXT_SKIP):
                return
            ct = (resp.headers.get("content-type") or "").lower()
            if (".css" in url or ".js" in url or "text/css" in ct or "javascript" in ct) and resp.status >= 400:
                network_error_sink.append(f"{resp.status} {resp.url}")
        page.on("response", _on_response)

# Alias kompatybilny z istniejącymi testami
def capture_console(page: "Page", sink: List[str]) -> None:
    attach_listeners(page, console_sink=sink)
def capture_responses(page: "Page", sink: List[str]) -> None:
    attach_listeners(page, network_error_sink=sink)

# Synchronizacja / timeout
def wait_ui_ready(page: "Page", timeout_ms: int = 500) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=timeout_ms)
    except Exception:
        page.wait_for_timeout(500)

CHECKBOX_SELECTORS = [
    # prefer test-id
    'input[type="checkbox"][data-testid="item-checkbox"]',
    '[data-testid="item-checkbox"] input[type="checkbox"]',
    # natywne inputy
    'input[type="checkbox"]',
    # aria/custom
    '[data-testid="item-checkbox"]',
    '[role="checkbox"][data-testid="item-checkbox"]',
    '[role="checkbox"]',
]

# Znajdź i zwróć pierwsze n elementów reprezentujących „checkboxy”
def first_n_checkboxes(page: "Page", n: int = 3):
    for sel in CHECKBOX_SELECTORS:
        els = page.query_selector_all(sel)
        if len(els) >= n:
            return els[:n]
    return []

# Zaznacz element (checkbox)
def safe_check(el) -> None:
    try:
        el.check()
    except Exception:
        el.click(force=True)    #wymuszenie

# Weryfikacja zaznaczenia (checkbox)
def looks_checked(el) -> bool:
    try:
        if el.is_checked():
            return True
    except Exception:
        pass
    aria = (el.get_attribute("aria-checked") or "").lower()
    if aria == "true":
        return True
    cls = (el.get_attribute("class") or "").lower()
    return any(flag in cls for flag in ("checked", "is-checked", "active", "selected"))

# Artefakty (PNG/HTML)
# Zapisz screenshot PNG (full page)
def save_artifacts(page: "Page", name: str, artifacts_dir: str = ART_DIR_DEFAULT) -> None:
    png_path = _art_path(artifacts_dir, name, "png")
    page.screenshot(path=str(png_path), full_page=True)
# Zapisz HTML
def dump_html(page: "Page", name: str, artifacts_dir: str = ART_DIR_DEFAULT) -> None:
    html_path = _art_path(artifacts_dir, name, "html")
    html = page.content()
    html_path.write_text(html, encoding="utf-8")