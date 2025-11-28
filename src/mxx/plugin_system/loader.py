
from mxx.plugin_system.i import PluginInterface
from mxx.plugin_system.plugin import MxxPlugin
from . import CURRENT_PYTHON_ENV_PATH

class MxxPluginLoader(PluginInterface):
    def __init__(self):
        self.plugins : list[MxxPlugin] = []

        # check if site packages is in the __path__, if not, ignore
        if "site-packages" not in CURRENT_PYTHON_ENV_PATH and "dist-packages" not in CURRENT_PYTHON_ENV_PATH[0]:
            return
        

    def emit(self, hook_name: str, *args, **kwargs):
        for plugin in self.plugins:
            plugin.hook(hook_name, *args, **kwargs)
    
    def loadProfiles(self):
        profiles = {}
        for plugin in self.plugins:
            profiles.update(plugin.loadProfiles())
        return profiles

    def loadMaaProfiles(self):
        profiles = {}
        for plugin in self.plugins:
            profiles.update(plugin.loadMaaProfiles())
        return profiles
    
    def preProfileStart(self, profile):
        for plugin in self.plugins:
            plugin.preProfileStart(profile)

    def postProfileStart(self, profile):
        for plugin in self.plugins:
            plugin.postProfileStart(profile)

    def preProfileKill(self, profile):
        for plugin in self.plugins:
            plugin.preProfileKill(profile)

    def postProfileKill(self, profile):
        for plugin in self.plugins:
            plugin.postProfileKill(profile)

    def checkPreventScheduleStart(self) -> bool:
        for plugin in self.plugins:
            if plugin.checkPreventScheduleStart():
                return True
        return False

    def canRunProfile(self, profile) -> bool:
        for plugin in self.plugins:
            if not plugin.canRunProfile(profile):
                return False
        return True
    
    def canKillProfile(self, profile) -> bool:
        for plugin in self.plugins:
            if not plugin.canKillProfile(profile):
                return False
        return True

mxx_plugin_loader = MxxPluginLoader()