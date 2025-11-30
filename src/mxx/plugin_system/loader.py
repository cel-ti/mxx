"""Plugin loader for discovering and managing MXX plugins."""

import pkgutil
import importlib
from typing import List, Dict, Any, TYPE_CHECKING
from mxx.plugin_system.plugin import MxxPlugin

if TYPE_CHECKING:
    from mxx.models.profile import MxxProfile


class PluginLoader:
    """Discovers and manages MXX plugins."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to avoid re-discovering plugins."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the plugin loader and discover plugins."""
        if not self._initialized:
            self.plugins: List[MxxPlugin] = []
            self._plugin_profiles: Dict[str, "MxxProfile"] = {}
            self._discover_plugins()
            PluginLoader._initialized = True
    
    def _discover_plugins(self) -> None:
        """Discover and load all available plugins.
        
        Searches for installed packages starting with 'mxxp_' and loads
        the plugin instance from their __plugin__ module.
        Also searches in cwd/plugins/ directory.
        """
        import sys
        from pathlib import Path
        
        # Add cwd/plugins to search path
        plugins_dir = Path.cwd() / "plugins"
        if plugins_dir.exists() and str(plugins_dir) not in sys.path:
            sys.path.insert(0, str(plugins_dir))
        
        for _, name, _ in pkgutil.iter_modules():
            if name.startswith("mxxp_"):
                try:
                    module = importlib.import_module(f"{name}.__plugin__")
                    if hasattr(module, "plugin") and isinstance(module.plugin, MxxPlugin):
                        self.plugins.append(module.plugin)
                        print(f"Loaded plugin: {name}")
                except ImportError:
                    pass
                except Exception as e:
                    print(f"Warning: Failed to load plugin {name}: {e}")
    
    def emit(self, hook_name: str, *args, **kwargs) -> None:
        """Emit a hook event to all plugins.
        
        Args:
            hook_name: Name of the hook event (e.g., "pre_ld_start")
            *args: Positional arguments for the hook
            **kwargs: Keyword arguments for the hook
        """
        for plugin in self.plugins:
            try:
                plugin.hook(hook_name, *args, **kwargs)
            except Exception as e:
                print(f"Warning: Plugin hook '{hook_name}' failed: {e}")
    
    def pre_profile_start(self, profile: "MxxProfile", ctx: Dict[str, Any]) -> None:
        """Call pre_profile_start on all plugins.
        
        Args:
            profile: Profile being started
            ctx: Runtime context
        """
        for plugin in self.plugins:
            try:
                plugin.pre_profile_start(profile, ctx)
            except Exception as e:
                print(f"Warning: Plugin pre_profile_start failed: {e}")
    
    def post_profile_start(self, profile: "MxxProfile", ctx: Dict[str, Any]) -> None:
        """Call post_profile_start on all plugins.
        
        Args:
            profile: Profile that was started
            ctx: Runtime context
        """
        for plugin in self.plugins:
            try:
                plugin.post_profile_start(profile, ctx)
            except Exception as e:
                print(f"Warning: Plugin post_profile_start failed: {e}")
    
    def pre_profile_kill(self, profile: "MxxProfile", ctx: Dict[str, Any]) -> None:
        """Call pre_profile_kill on all plugins.
        
        Args:
            profile: Profile being killed
            ctx: Runtime context
        """
        for plugin in self.plugins:
            try:
                plugin.pre_profile_kill(profile, ctx)
            except Exception as e:
                print(f"Warning: Plugin pre_profile_kill failed: {e}")
    
    def post_profile_kill(self, profile: "MxxProfile", ctx: Dict[str, Any]) -> None:
        """Call post_profile_kill on all plugins.
        
        Args:
            profile: Profile that was killed
            ctx: Runtime context
        """
        for plugin in self.plugins:
            try:
                plugin.post_profile_kill(profile, ctx)
            except Exception as e:
                print(f"Warning: Plugin post_profile_kill failed: {e}")
    
    def can_run_profile(self, profile: "MxxProfile", ctx: Dict[str, Any]) -> bool:
        """Check if profile can run via all plugins.
        
        If any plugin returns False, the profile cannot run.
        
        Args:
            profile: Profile to check
            ctx: Runtime context
            
        Returns:
            True if all plugins allow running, False otherwise
        """
        for plugin in self.plugins:
            try:
                if not plugin.can_run_profile(profile, ctx):
                    return False
            except Exception as e:
                print(f"Warning: Plugin can_run_profile check failed: {e}")
        return True
    
    def can_kill_profile(self, profile: "MxxProfile", ctx: Dict[str, Any]) -> bool:
        """Check if profile can be killed via all plugins.
        
        If any plugin returns False, the profile cannot be killed.
        
        Args:
            profile: Profile to check
            ctx: Runtime context
            
        Returns:
            True if all plugins allow killing, False otherwise
        """
        for plugin in self.plugins:
            try:
                if not plugin.can_kill_profile(profile, ctx):
                    return False
            except Exception as e:
                print(f"Warning: Plugin can_kill_profile check failed: {e}")
        return True
    
    def load_plugin_profiles(self) -> Dict[str, "MxxProfile"]:
        """Load profiles contributed by plugins.
        
        Calls get_profiles() on each plugin and aggregates the results.
        
        Returns:
            Dictionary mapping profile names to MxxProfile instances
        """
        if self._plugin_profiles:
            return self._plugin_profiles
        
        for plugin in self.plugins:
            try:
                profiles = plugin.get_profiles()
                if profiles:
                    self._plugin_profiles.update(profiles)
                    print(f"Loaded {len(profiles)} profile(s) from plugin: {plugin.__class__.__name__}")
            except Exception as e:
                print(f"Warning: Failed to load profiles from plugin: {e}")
        
        return self._plugin_profiles
    
    def get_profile(self, name: str) -> "MxxProfile":
        """Get a profile by name from plugin-contributed profiles.
        
        Args:
            name: Profile name
            
        Returns:
            MxxProfile instance
            
        Raises:
            KeyError: If profile not found
        """
        if not self._plugin_profiles:
            self.load_plugin_profiles()
        
        return self._plugin_profiles[name]
    
    def has_profile(self, name: str) -> bool:
        """Check if a plugin provides a profile with the given name.
        
        Args:
            name: Profile name
            
        Returns:
            True if profile exists in plugins, False otherwise
        """
        if not self._plugin_profiles:
            self.load_plugin_profiles()
        
        return name in self._plugin_profiles


# Global plugin loader instance
plugin_loader = PluginLoader()
