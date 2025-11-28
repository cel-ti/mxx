

from pathlib import Path
import typing

from mxx.app.config import MxxAppConfig
from mxx.utils.json import load_json, touch_json, save_json


class MxxMgr:
    configPath : typing.ClassVar[Path] = Path("~/.mxx/config.json").expanduser()
    config : MxxAppConfig

    def __init__(self):
        self.config = MxxAppConfig(**load_json(self.configPath))

    def save_config(self):
        save_json(self.config, self.configPath)


touch_json(MxxMgr.configPath, default={})

mxxmgr = MxxMgr()