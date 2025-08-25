# tests/smoke/test_smoke_prod.py
# --------------------------------------------------------------------------------------
# Testy Smoke (PROD, read-only)
# --------------------------------------------------------------------------------------

import os
import pathlib
import pytest
import requests
from pathlib import Path

# USTAWIENIA LOKALNE
PROJECT_ROOT = Path(__file__).resolve().parents[3]                                  # korzeń repo (.../TravelReady)
CONFIG_PATH  = Path(os.getenv("TR_CONFIG", str(PROJECT_ROOT / "config.env")))       # ścieżka do config.env
TR_ENV       = os.getenv("TR_ENV", "PROD").upper()                                  # PROD domyślnie
SMOKE_PATHS  = os.getenv("SMOKE_HEALTH_PATHS", "/api/debug,/api/checklist")
SMOKE_STRICT = (os.getenv("SMOKE_STRICT", "off").lower() in ("1", "true", "on", "yes"))
SMOKE_TIMEOUT = float(os.getenv("SMOKE_TIMEOUT", "5"))
PROD_ONLY  = pytest.mark.skipif(TR_ENV != "PROD", reason="Smoke uruchamiamy na PROD (TR_ENV=PROD).")
pytestmark = [pytest.mark.deploy]

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

# Zwraca URL aplikacji frontendowej (DEV/PROD)
def _front_base_url(cfg: dict, env: str) -> str:
    if env == "PROD":
        return (cfg.get("API_BASE_URL_PRODUCTION") or "").rstrip("/")
    else:
        return (cfg.get("API_BASE_URL_DEVELOPMENT") or "").rstrip("/")

# Łączy bazę URL z endpointem, gwarantując pojedynczy slash pomiędzy
def _join(base: str, endpoint: str) -> str:
    return f"{base.rstrip('/')}/{endpoint.lstrip('/')}"

# Adres startowy UI zczytany z config.env 
@pytest.fixture(scope="session")
def base_url() -> str:
    cfg  = _read_env_file(CONFIG_PATH)
    base = _front_base_url(cfg, TR_ENV)
    if not base:
        pytest.skip(f"Brak FRONT/API BASE URL dla {TR_ENV} w {CONFIG_PATH} – pomijam smoke testy.")
    return base

# --------------------------------------------------------------------------------------
# TESTY
# --------------------------------------------------------------------------------------

# ======================
# TC-S-01 – PROD only: Weryfikacja endpointów
# ======================
@PROD_ONLY
def test_tc_s_01_health_endpoint_returns_json(base_url: str):
    endpoints = [p.strip() for p in SMOKE_PATHS.split(",") if p.strip()]
    errors: list[str] = []
    ok_count = 0

    for ep in endpoints:
        url = _join(base_url, ep)
        # 1) Próba wykonania GET z krótkim timeoutem:
        try:
            resp = requests.get(url, timeout=SMOKE_TIMEOUT)
        except Exception as e:
            errors.append(f"{ep}: exception {e}")
            continue
        # 2) Status HTTP musi być 200:
        if resp.status_code != 200:
            errors.append(f"{ep}: status {resp.status_code}")
            continue
        # 3) Content-Type musi zawierać 'json' (np. 'application/json; charset=utf-8'):
        ct = (resp.headers.get("Content-Type") or "").lower()
        if "json" not in ct:
            errors.append(f"{ep}: Content-Type '{ct}' nie zawiera 'json'")
            continue
        # 4) Ciało odpowiedzi musi być poprawnym JSON-em:
        try:
            data = resp.json()
        except ValueError as e:
            errors.append(f"{ep}: nieprawidłowy JSON ({e})")
            continue
        
        ok_count += 1
        if not SMOKE_STRICT:
            return
    # Weryfikacja progu zaliczenia:
    if SMOKE_STRICT:
        if ok_count == len(endpoints):
            return
        pytest.fail(f"SMOKE_STRICT=on: nie wszystkie endpointy zaliczone ({ok_count}/{len(endpoints)}). "
                    f"Szczegóły: {'; '.join(errors)}")
    else:
        # Wymagaj co najmniej jednego
        if ok_count >= 1:
            return
        pytest.fail("Żaden endpoint nie spełnił warunków: " + "; ".join(errors))
