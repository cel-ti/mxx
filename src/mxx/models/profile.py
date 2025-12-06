
from dataclasses import dataclass
import typing

from mxx.models.base import BaseModel
from mxx.models.ld import LDModel
from mxx.models.maa import MaaModel

@dataclass
class MxxProfile(BaseModel):
    ld : typing.Optional[LDModel] = None
    maa : typing.Optional[MaaModel] = None
    lifetime : typing.Optional[int] = None  # Total runtime in seconds
    waittime : typing.Optional[int] = None  # Wait time before starting in seconds

