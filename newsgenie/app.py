# Wrapper to launch the real app at repo root (app.py)
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import app  # noqa: F401  # importing runs Streamlit code in root app.py
