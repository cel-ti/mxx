

from dataclasses import dataclass, field
from typing import Any

from mxx.models.base import BaseModel

@dataclass
class MaaFileConfigModel(BaseModel):
    exclude : list[str] = field(default_factory=list)
    include : list[str] = field(default_factory=list)

@dataclass
class MaaConfigParseModel(BaseModel):
    overwrite : dict[str, Any] = field(default_factory=dict)
    exclude : list[str] = field(default_factory=list)


@dataclass
class MaaModel(BaseModel):
    path : str = None
    app : str = None
    configDir : str = None
    fileConfig : MaaFileConfigModel = None
    parseConfig : MaaConfigParseModel = None

