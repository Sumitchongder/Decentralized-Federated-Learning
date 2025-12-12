import json
from pathlib import Path

STORAGE_FILE = Path("./storage.json")

def save(data):
    STORAGE_FILE.write_text(json.dumps(data, indent=2))

def load():
    if STORAGE_FILE.exists():
        return json.loads(STORAGE_FILE.read_text())
    return {}
