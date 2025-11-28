

from mxx.auto_profile.model import MxxAutoProfile
from mxx.maaconfig.model import MaaProfile


class PluginInterface:
    def loadProfiles(self) -> dict[str, MxxAutoProfile]:
        """Loads and returns a dictionary of auto profiles provided by this plugin"""
        return {}
    
    def loadMaaProfiles(self) -> dict[str, MaaProfile]:
        """Loads and returns a dictionary of MAA profiles provided by this plugin"""
        return {}
    
    def preProfileStart(self, profile: MxxAutoProfile) -> None:
        """Hook called before an auto profile starts"""
        pass

    def postProfileStart(self, profile: MxxAutoProfile) -> None:
        """Hook called after an auto profile starts"""
        pass

    def preProfileKill(self, profile: MxxAutoProfile) -> None:
        """Hook called before an auto profile is killed"""
        pass

    def postProfileKill(self, profile: MxxAutoProfile) -> None:
        """Hook called after an auto profile is killed"""
        pass

    def canRunProfile(self, profile: MxxAutoProfile) -> bool:
        """Checks if the profile can run. Return True to allow running, False to prevent."""
        return True
    
    def canKillProfile(self, profile: MxxAutoProfile) -> bool:
        """Checks if the profile can be killed"""
        return True
    
    def checkPreventScheduleStart(self) -> bool:
        """Checks if scheduling should be prevented. Return True to prevent scheduling."""
        return False