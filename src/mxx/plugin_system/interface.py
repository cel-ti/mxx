"""Plugin interface for extending MXX functionality."""

from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mxx.models.profile import MxxProfile


class PluginInterface:
    """Base interface for MXX plugins."""
    
    def pre_profile_start(self, profile: "MxxProfile", ctx: Dict[str, Any]) -> None:
        """Hook called before a profile starts.
        
        Args:
            profile: Profile being started
            ctx: Runtime context dictionary
        """
        pass
    
    def post_profile_start(self, profile: "MxxProfile", ctx: Dict[str, Any]) -> None:
        """Hook called after a profile starts.
        
        Args:
            profile: Profile that was started
            ctx: Runtime context dictionary
        """
        pass
    
    def pre_profile_kill(self, profile: "MxxProfile", ctx: Dict[str, Any]) -> None:
        """Hook called before a profile is killed.
        
        Args:
            profile: Profile being killed
            ctx: Runtime context dictionary
        """
        pass
    
    def post_profile_kill(self, profile: "MxxProfile", ctx: Dict[str, Any]) -> None:
        """Hook called after a profile is killed.
        
        Args:
            profile: Profile that was killed
            ctx: Runtime context dictionary
        """
        pass
    
    def can_run_profile(self, profile: "MxxProfile", ctx: Dict[str, Any]) -> bool:
        """Check if a profile can run.
        
        Args:
            profile: Profile to check
            ctx: Runtime context dictionary
            
        Returns:
            True to allow running, False to prevent
        """
        return True
    
    def can_kill_profile(self, profile: "MxxProfile", ctx: Dict[str, Any]) -> bool:
        """Check if a profile can be killed.
        
        Args:
            profile: Profile to check
            ctx: Runtime context dictionary
            
        Returns:
            True to allow killing, False to prevent
        """
        return True
    
    def get_profiles(self) -> Dict[str, "MxxProfile"]:
        """Provide profiles contributed by this plugin.
        
        Returns:
            Dictionary mapping profile names to MxxProfile instances
        """
        return {}
    
    def hook(self, hook_name: str, *args, **kwargs) -> Any:
        """Generic hook dispatcher.
        
        Calls hook_{hook_name} method if it exists on the plugin.
        
        Args:
            hook_name: Name of the hook (e.g., "pre_ld_start")
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Return value from the hook method, if any
        """
        func = getattr(self, f"hook_{hook_name}", None)
        if func and callable(func):
            return func(*args, **kwargs)
        return None
