
from logging import warning
from pathlib import Path
import typing

from mxx.maaconfig.model import MaaProfile
from mxx.utils.toml import load_toml
from mxx.app.mgr import mxxmgr

class MaaConfigMgr:
    defaultConfigDir : typing.ClassVar[Path] = Path("~/.mxx/maa").expanduser()
    defaultConfigBkup : typing.ClassVar[Path] = Path("~/.mxx/backups").expanduser()

    profiles : dict[str, MaaProfile] = {}

    @property
    def configDir(self) -> Path:
        return Path(str(mxxmgr.config.maaconfig_path or self.defaultConfigDir))
    
    @property
    def bkupDir(self) -> Path:
        return Path(str(mxxmgr.config.maaconfig_bkup_path or self.defaultConfigBkup))

    def __init__(self):
        # loop for toml files in configDir
        for config_file in self.configDir.glob("*.toml"):
            try:
                config_profile_raw = load_toml(config_file.absolute())
                config_profile = MaaProfile(**config_profile_raw)
                self.profiles[config_file.stem] = config_profile
            except Exception as e:
                warning(f"Warning: Failed to load profile from {config_file}: {e}")


mxxmaa = MaaConfigMgr()
mxxmaa.configDir.mkdir(parents=True, exist_ok=True)
mxxmaa.bkupDir.mkdir(parents=True, exist_ok=True)