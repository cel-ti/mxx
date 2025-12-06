

from dataclasses import dataclass
from typing import Optional

from mxx.models.base import BaseModel


@dataclass
class LDModel(BaseModel):
    index : Optional[int] = None
    name : Optional[str] = None

    def __post_init__(self):
        if not self.name and self.index is None:
            raise ValueError("Either 'name' or 'index' must be provided for LDModel.")
        
        if self.name and self.index is not None:
            raise ValueError("Only one of 'name' or 'index' should be provided for LDModel.")
        
