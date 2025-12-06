import json
from pathlib import Path

def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def touch_json(filepath, default={}):
    """Create an empty JSON file if it doesn't exist."""
    filepath = Path(filepath)
    if not filepath.exists():
        save_json(default, filepath)
