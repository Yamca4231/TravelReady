# tests/integration/test_favicon.py
# --------------------------------------------------------------------------------------
# Test integracyjny dla favicon
# --------------------------------------------------------------------------------------

import os
import pathlib
import pytest
import requests

# USTAWIENIA LOKALNE
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]                              # korzeń repo (.../TravelReady)
CONFIG_PATH = pathlib.Path(os.getenv("TR_CONFIG", str(PROJECT_ROOT / "config.env")))    # Ścieżka do pliku konfiguracyjnego
TR_ENV = os.getenv("TR_ENV", "DEV").upper()                                             # Wybór środowiska - DEV domyślnie

pytestmark = [pytest.mark.integration, pytest.mark.deploy]

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

# TC-I-04: Sprawdza status, Content-Type i zawartość favicon
def test_favicon_status_content_type_and_size(join):
    url = join("/static/images/favicon.ico")
    resp = requests.get(url, timeout=5)
    # 1) Status
    assert resp.status_code == 200, f"GET {url} zwraca inny status: {resp.status_code}, zamiast 200"

    # 2) Nagłówek Content-Type
    ct = resp.headers.get("Content-Type", "").lower()
    assert any(t in ct for t in ["image/vnd.microsoft.icon", "image/x-icon", "image/ico"]), f"Nieprawidłowy Content-Type: {ct}"

    # 3) Rozmiar treści
    assert len(resp.content) > 0, "Favicon nie może być pusty."
