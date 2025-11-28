

from mxx.plugin_system.i import PluginInterface


class MxxPlugin(PluginInterface):
    
    def hook(self, hook_name: str, *args, **kwargs):
        func = getattr(self, f"hook_{hook_name}", None)
        if func:
            return func(*args, **kwargs)
