"""MXX Plugin System.

This module provides a plugin architecture for extending MXX functionality.

Example Plugin:
    # In mxxp_example/__plugin__.py
    from mxx.plugin_system import MxxPlugin
    
    class ExamplePlugin(MxxPlugin):
        def hook_pre_ld_start(self, profile):
            print(f"LD starting for: {profile}")
        
        def can_run_profile(self, profile, ctx):
            if ctx.get('maintenance'):
                print("Maintenance mode - blocking profile")
                return False
            return True
    
    plugin = ExamplePlugin()

Available Hooks:
    - pre_ld_start: Before LD player launches
    - pre_wait_time: Before waiting between LD and MAA
    - pre_maa_launch: Before MAA launches
    - pre_maa_kill: Before MAA is killed
    - pre_ld_kill: Before LD is killed

Plugin Methods:
    - can_run_profile: Return False to prevent profile from running
    - can_kill_profile: Return False to prevent profile from being killed
    - pre_profile_start: Called before profile starts
    - post_profile_start: Called after profile starts
    - pre_profile_kill: Called before profile is killed
    - post_profile_kill: Called after profile is killed
"""

from mxx.plugin_system.interface import PluginInterface
from mxx.plugin_system.plugin import MxxPlugin
from mxx.plugin_system.loader import PluginLoader, plugin_loader

__all__ = [
    "PluginInterface",
    "MxxPlugin",
    "PluginLoader",
    "plugin_loader",
]
