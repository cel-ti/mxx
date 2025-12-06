

from functools import cache
import os
from pathlib import Path

@cache
def get_config_path() -> Path:
    """Get the path to the configuration directory."""
    home = Path.home()
    config_dir = home / ".mxx"

    # check env variable override
    if "MXX_CONFIG_DIR" in os.environ:
        config_dir = Path(os.environ["MXX_CONFIG_DIR"])

    # check keyring override
    try:
        import keyring
        keyring_path = keyring.get_password("mxx", "config_dir")
        if keyring_path:
            config_dir = Path(keyring_path)
    except ImportError:
        pass

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_profile_path() -> Path:
    """Get the path to the profiles directory."""
    profile_dir = get_config_path() / "configs"
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir