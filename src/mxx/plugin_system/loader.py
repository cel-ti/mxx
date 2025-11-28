
import pkgutil
import importlib
from mxx.plugin_system.i import PluginInterface
from mxx.plugin_system.plugin import MxxPlugin

class MxxPluginLoader(PluginInterface):
    def __init__(self):
        self.plugins : list[MxxPlugin] = []
        self._discover_plugins()
        self.runtime = {}

    def _discover_plugins(self):
        for _, name, _ in pkgutil.iter_modules():
            if name.startswith("mxxp_"):
                try:
                    module = importlib.import_module(f"{name}.__plugin__")
                    if hasattr(module, "plugin") and isinstance(module.plugin, MxxPlugin):
                        self.plugins.append(module.plugin)
                except ImportError:
                    pass
                except Exception as e:
                    print(f"Warning: Failed to load plugin {name}: {e}")

    def emit(self, hook_name: str, *args, **kwargs):
        for plugin in self.plugins:
            plugin.hook(hook_name, *args, **kwargs)
    
    def loadProfiles(self):
        profiles = {}
        for plugin in self.plugins:
            profiles.update(plugin.loadProfiles(self.runtime))
        return profiles

    def loadMaaProfiles(self):
        profiles = {}
        for plugin in self.plugins:
            profiles.update(plugin.loadMaaProfiles(self.runtime))
        return profiles
    
    def preProfileStart(self, profile):
        for plugin in self.plugins:
            plugin.preProfileStart(profile, self.runtime)

    def postProfileStart(self, profile):
        for plugin in self.plugins:
            plugin.postProfileStart(profile, self.runtime)
            
    def preProfileKill(self, profile):
        for plugin in self.plugins:
            plugin.preProfileKill(profile, self.runtime)

    def postProfileKill(self, profile):
        for plugin in self.plugins:
            plugin.postProfileKill(profile, self.runtime)

    def checkPreventScheduleStart(self) -> bool:
        for plugin in self.plugins:
            if plugin.checkPreventScheduleStart(self.runtime):
                return True
        return False

    def canRunProfile(self, profile) -> bool:
        for plugin in self.plugins:
            if not plugin.canRunProfile(profile, self.runtime):
                return False
        return True
    
    def canKillProfile(self, profile) -> bool:
        for plugin in self.plugins:
            if not plugin.canKillProfile(profile, self.runtime):
                return False
        return True

mxx_plugin_loader = MxxPluginLoader()