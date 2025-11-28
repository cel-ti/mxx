
from pydantic import BaseModel


class MxxAppConfig(BaseModel):
    profile_path : str = None
    maaconfig_path : str = None
    maaconfig_bkup_path : str = None

