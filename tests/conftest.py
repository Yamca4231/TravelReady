# tests/conftest.py

import sys
from pathlib import Path

# Dodanie katalogu 'py' do sys.path, aby importy 'from app ...' działały.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PY_DIR = PROJECT_ROOT / "py"

if str(PY_DIR) not in sys.path:
    sys.path.insert(0, str(PY_DIR))
