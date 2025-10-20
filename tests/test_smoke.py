import sys, os
from pathlib import Path

# Add repo root to import path so `import run` works when pytest's rootdir is tests/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# tests/test_smoke.py
import os
import importlib

# Use an in-memory DB so CI doesn't need Postgres
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

# Import your app from run.py
mod = importlib.import_module("run")

# Support either a global `app` or an app-factory `create_app()`
app = getattr(mod, "app", None)
if app is None:
    create_app = getattr(mod, "create_app", None)
    if create_app is None:
        raise RuntimeError("Neither `app` nor `create_app()` found in run.py")
    app = create_app()

def test_root_responds_or_redirects():
    client = app.test_client()
    r = client.get("/", follow_redirects=False)
    # some apps serve a page on '/', others redirect to /login or /dashboard
    assert r.status_code in (200, 301, 302)