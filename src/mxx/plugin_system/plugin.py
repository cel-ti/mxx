"""MXX Plugin base class."""

from mxx.plugin_system.interface import PluginInterface


class MxxPlugin(PluginInterface):
    """Base class for MXX plugins.
    
    Inherit from this class to create a plugin. Implement any hook methods
    you need, following the naming convention hook_{event_name}.
    
    Example:
        class MyPlugin(MxxPlugin):
            def hook_pre_ld_start(self, profile):
                print(f"LD starting for profile: {profile}")
            
            def can_run_profile(self, profile, ctx):
                # Prevent running during maintenance window
                if ctx.get('maintenance_mode'):
                    return False
                return True
    """
    pass
