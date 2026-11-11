import os
import sys
sys.path.insert(0, os.path.abspath("."))
import glob

print("Importing backend.app.main...", flush=True)
from backend.app.main import app
print("FastAPI imported successfully.", flush=True)

from backend.app.database import engine
from sqlalchemy import text, inspect

print("=== FASTAPI ROUTES ===", flush=True)
for route in app.routes:
    methods = getattr(route, "methods", None)
    path = getattr(route, "path", None)
    name = getattr(route, "name", None)
    if path:
        print(f"{list(methods) if methods else ''} -> {path} ({name})", flush=True)

print("\n=== DB TABLES AND COUNTS ===", flush=True)
insp = inspect(engine)
tables = insp.get_table_names()
with engine.connect() as conn:
    for t in tables:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        print(f"Table: {t} | Rows: {count}", flush=True)

print("\n=== ML MODELS ===", flush=True)
for p in glob.glob("ml/**/*.pkl", recursive=True):
    print(f"Model file: {p} ({os.path.getsize(p)} bytes)", flush=True)
for p in glob.glob("ml/**/*.joblib", recursive=True):
    print(f"Model file: {p} ({os.path.getsize(p)} bytes)", flush=True)

