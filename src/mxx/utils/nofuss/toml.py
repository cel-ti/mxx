
import toml

def load_toml(path: str) -> dict:
    return toml.load(path)
    
def save_toml(data: dict, path: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        toml.dump(data, f)

def touch_toml(path: str, default: dict = {}) -> None:
    """Create an empty TOML file if it doesn't exist."""
    from pathlib import Path
    path_obj = Path(path)
    if not path_obj.exists():
        save_toml(default, path)
