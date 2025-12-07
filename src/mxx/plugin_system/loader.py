"""Plugin loader for discovering and managing MXX plugins."""

import pkgutil
import importlib
import inspect
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
    
    def _call_with_inspection(self, method, *args, **kwargs) -> Any:
        """Call a method with signature inspection to pass only accepted parameters.
        
        Args:
            method: Method to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Method result
        """
        try:
            sig = inspect.signature(method)
            
            # Filter kwargs to only include parameters the method accepts
            accepted_kwargs = {}
            for key, value in kwargs.items():
                if key in sig.parameters:
                    accepted_kwargs[key] = value
            
            return method(*args, **accepted_kwargs)
        except Exception:
            # Fallback: try with all kwargs
            return method(*args, **kwargs)
    
    def emit(self, hook_name: str, *args, **kwargs) -> None:
        """Emit a hook event to all plugins.
        
        Args:
            hook_name: Name of the hook event (e.g., "pre_ld_start")
            *args: Positional arguments for the hook
            **kwargs: Keyword arguments for the hook (including vars if available)
        """
        for plugin in self.plugins:
            try:
                method = getattr(plugin, f"hook_{hook_name}", None)
                if method and callable(method):
                    self._call_with_inspection(method, *args, **kwargs)
            except Exception as e:
                print(f"Warning: Plugin hook '{hook_name}' failed: {e}")
    
    def init(self, vars: Dict[str, str] = None) -> None:
        """Initialize all plugins.
        
        Args:
            vars: Optional variables from --var options
        """
        for plugin in self.plugins:
            try:
                self._call_with_inspection(plugin.init, vars=vars)
            except Exception as e:
                print(f"Warning: Plugin init failed: {e}")
    
    def register_commands(self, cli_group, vars: Dict[str, str] = None) -> None:
        """Register commands from all plugins.
        
        Args:
            cli_group: Click group to register commands with
            vars: Optional variables from --var options
        """
        for plugin in self.plugins:
            try:
                self._call_with_inspection(plugin.register_commands, cli_group, vars=vars)
            except Exception as e:
                print(f"Warning: Plugin register_commands failed: {e}")

    def pre_profile_start(self, profile: "MxxProfile", ctx: Dict[str, Any], vars: Dict[str, str] = None) -> None:
        """Call pre_profile_start on all plugins.
        
        Args:
            profile: Profile being started
            ctx: Runtime context
            vars: Optional variables from --var options
        """
        for plugin in self.plugins:
            try:
                self._call_with_inspection(plugin.pre_profile_start, profile, ctx, vars=vars)
            except Exception as e:
                print(f"Warning: Plugin pre_profile_start failed: {e}")
    
    def post_profile_start(self, profile: "MxxProfile", ctx: Dict[str, Any], vars: Dict[str, str] = None) -> None:
        """Call post_profile_start on all plugins.
        
        Args:
            profile: Profile that was started
            ctx: Runtime context
            vars: Optional variables from --var options
        """
        for plugin in self.plugins:
            try:
                self._call_with_inspection(plugin.post_profile_start, profile, ctx, vars=vars)
            except Exception as e:
                print(f"Warning: Plugin post_profile_start failed: {e}")
    
    def pre_profile_kill(self, profile: "MxxProfile", ctx: Dict[str, Any], vars: Dict[str, str] = None) -> None:
        """Call pre_profile_kill on all plugins.
        
        Args:
            profile: Profile being killed
            ctx: Runtime context
            vars: Optional variables from --var options
        """
        for plugin in self.plugins:
            try:
                self._call_with_inspection(plugin.pre_profile_kill, profile, ctx, vars=vars)
            except Exception as e:
                print(f"Warning: Plugin pre_profile_kill failed: {e}")
    
    def post_profile_kill(self, profile: "MxxProfile", ctx: Dict[str, Any], vars: Dict[str, str] = None) -> None:
        """Call post_profile_kill on all plugins.
        
        Args:
            profile: Profile that was killed
            ctx: Runtime context
            vars: Optional variables from --var options
        """
        for plugin in self.plugins:
            try:
                self._call_with_inspection(plugin.post_profile_kill, profile, ctx, vars=vars)
            except Exception as e:
                print(f"Warning: Plugin post_profile_kill failed: {e}")
    
    def can_run_profile(self, profile: "MxxProfile", ctx: Dict[str, Any], vars: Dict[str, str] = None) -> bool:
        """Check if profile can run via all plugins.
        
        If any plugin returns False, the profile cannot run.
        
        Args:
            profile: Profile to check
            ctx: Runtime context
            vars: Optional variables from --var options
            
        Returns:
            True if all plugins allow running, False otherwise
        """
        for plugin in self.plugins:
            try:
                result = self._call_with_inspection(plugin.can_run_profile, profile, ctx, vars=vars)
                if not result:
                    return False
            except Exception as e:
                print(f"Warning: Plugin can_run_profile check failed: {e}")
        return True
    
    def can_kill_profile(self, profile: "MxxProfile", ctx: Dict[str, Any], vars: Dict[str, str] = None) -> bool:
        """Check if profile can be killed via all plugins.
        
        If any plugin returns False, the profile cannot be killed.
        
        Args:
            profile: Profile to check
            ctx: Runtime context
            vars: Optional variables from --var options
            
        Returns:
            True if all plugins allow killing, False otherwise
        """
        for plugin in self.plugins:
            try:
                result = self._call_with_inspection(plugin.can_kill_profile, profile, ctx, vars=vars)
                if not result:
                    return False
            except Exception as e:
                print(f"Warning: Plugin can_kill_profile check failed: {e}")
        return True
    
    def load_plugin_profiles(self, vars: Dict[str, str] = None) -> Dict[str, "MxxProfile"]:
        """Load profiles contributed by plugins.
        
        Calls get_profiles() on each plugin and aggregates the results.
        
        Args:
            vars: Optional variables from --var options
        
        Returns:
            Dictionary mapping profile names to MxxProfile instances
        """
        if self._plugin_profiles:
            return self._plugin_profiles
        
        for plugin in self.plugins:
            try:
                profiles = self._call_with_inspection(plugin.get_profiles, vars=vars)
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
