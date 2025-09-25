# newsgenie/app.py — robust wrapper that executes the real app at the repo root
import sys, pathlib, os, runpy

ROOT = pathlib.Path(__file__).resolve().parents[1]  # repo root
os.chdir(ROOT)                                      # make root the working dir
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))                   # ensure root is first on sys.path

# Execute the root app.py as if it were the main script
runpy.run_path(str(ROOT / "app.py"), run_name="__main__")
