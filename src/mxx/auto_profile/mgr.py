
from logging import warning
from pathlib import Path
import typing

from mxx.app.mgr import mxxmgr
from mxx.auto_profile.model import MxxAutoProfile
from mxx.utils.toml import load_toml


class AutoProfileMgr:
    defaultConfigDir : typing.ClassVar[Path] = Path("~/.mxx/profiles").expanduser()

    profiles : dict[str, MxxAutoProfile] = {}

    @property
    def configDir(self) -> Path:
        return Path(str(mxxmgr.config.profile_path or self.defaultConfigDir))

    def __init__(self):
        # loop for toml files in configDir
        for config_file in self.configDir.glob("*.toml"):
            try:
                config_profile_raw = load_toml(str(config_file.absolute()))
                config_profile = MxxAutoProfile(**config_profile_raw)
                self.profiles[config_file.stem] = config_profile
            except Exception as e:
                warning(f"Warning: Failed to load auto profile from {config_file}: {e}")

AutoProfileMgr.defaultConfigDir.mkdir(parents=True, exist_ok=True)

auto_profiles = AutoProfileMgr()
