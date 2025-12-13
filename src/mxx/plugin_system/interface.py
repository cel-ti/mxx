"""Plugin interface for extending MXX functionality."""

from typing import Dict, Any, Optional, TYPE_CHECKING
import inspect

if TYPE_CHECKING:
    from mxx.models.profile import MxxProfile
    import click


class PluginInterface:
    """Base interface for MXX plugins.
    
    All hook methods support an optional 'vars' parameter that will be passed
    if present in the method signature. Use signature inspection to determine
    what parameters your plugin needs.
    """
    
    def init(self, vars: Optional[Dict[str, str]] = None, ctx: Optional["click.Context"] = None) -> None:
        """Initialize the plugin.
        
        Args:
            vars: Optional variables from --var options (if method accepts it)
            ctx: Optional Click context (if method accepts it)
        """
        pass
    
    def register_commands(self, cli_group: "click.Group", vars: Optional[Dict[str, str]] = None) -> None:
        """Register plugin commands with the CLI.
        
        Args:
            cli_group: The main CLI group to add commands to
            vars: Optional variables from --var options (if method accepts it)
        """
        pass
    
    def pre_command(self, command_name: str, ctx: "click.Context") -> None:
        """Hook called before any command executes.
        
        Args:
            command_name: Name of the command being executed
            ctx: Click context object
        """
        pass
    
    def post_command(self, command_name: str, ctx: "click.Context", result: Any) -> None:
        """Hook called after a command executes successfully.
        
        Args:
            command_name: Name of the command that executed
            ctx: Click context object
            result: Return value from the command
        """
        pass
    
    def command_error(self, command_name: str, ctx: "click.Context", error: Exception) -> None:
        """Hook called when a command raises an exception.
        
        Args:
            command_name: Name of the command that failed
            ctx: Click context object
            error: Exception that was raised
        """
        pass

    def pre_profile_start(self, profile: "MxxProfile", ctx: Dict[str, Any], vars: Optional[Dict[str, str]] = None) -> None:
        """Hook called before a profile starts.
        
        Args:
            profile: Profile being started
            ctx: Runtime context dictionary
            vars: Optional variables from --var options (if method accepts it)
        """
        pass
    
    def post_profile_start(self, profile: "MxxProfile", ctx: Dict[str, Any], vars: Optional[Dict[str, str]] = None) -> None:
        """Hook called after a profile starts.
        
        Args:
            profile: Profile that was started
            ctx: Runtime context dictionary
            vars: Optional variables from --var options (if method accepts it)
        """
        pass
    
    def pre_profile_kill(self, profile: "MxxProfile", ctx: Dict[str, Any], vars: Optional[Dict[str, str]] = None) -> None:
        """Hook called before a profile is killed.
        
        Args:
            profile: Profile being killed
            ctx: Runtime context dictionary
            vars: Optional variables from --var options (if method accepts it)
        """
        pass
    
    def post_profile_kill(self, profile: "MxxProfile", ctx: Dict[str, Any], vars: Optional[Dict[str, str]] = None) -> None:
        """Hook called after a profile is killed.
        
        Args:
            profile: Profile that was killed
            ctx: Runtime context dictionary
            vars: Optional variables from --var options (if method accepts it)
        """
        pass
    
    def can_run_profile(self, profile: "MxxProfile", ctx: Dict[str, Any], vars: Optional[Dict[str, str]] = None) -> bool:
        """Check if a profile can run.
        
        Args:
            profile: Profile to check
            ctx: Runtime context dictionary
            vars: Optional variables from --var options (if method accepts it)
            
        Returns:
            True to allow running, False to prevent
        """
        return True
    
    def can_kill_profile(self, profile: "MxxProfile", ctx: Dict[str, Any], vars: Optional[Dict[str, str]] = None) -> bool:
        """Check if a profile can be killed.
        
        Args:
            profile: Profile to check
            ctx: Runtime context dictionary
            vars: Optional variables from --var options (if method accepts it)
            
        Returns:
            True to allow killing, False to prevent
        """
        return True
    
    def get_profiles(self, vars: Optional[Dict[str, str]] = None) -> Dict[str, "MxxProfile"]:
        """Provide profiles contributed by this plugin.
        
        Args:
            vars: Optional variables from --var options (if method accepts it)
            
        Returns:
            Dictionary mapping profile names to MxxProfile instances
        """
        return {}
    
    def hook(self, hook_name: str, *args, **kwargs) -> Any:
        """Generic hook dispatcher with signature inspection.
        
        Calls hook_{hook_name} method if it exists on the plugin.
        Automatically filters kwargs based on the method's signature.
        
        Args:
            hook_name: Name of the hook (e.g., "pre_ld_start")
            *args: Positional arguments
            **kwargs: Keyword arguments (including 'vars' if available)
            
        Returns:
            Return value from the hook method, if any
        """
        func = getattr(self, f"hook_{hook_name}", None)
        if func and callable(func):
            try:
                sig = inspect.signature(func)
                # Filter kwargs to only include parameters the method accepts
                accepted_kwargs = {}
                for key, value in kwargs.items():
                    if key in sig.parameters:
                        accepted_kwargs[key] = value
                return func(*args, **accepted_kwargs)
            except Exception:
                # Fallback: try with all kwargs
                return func(*args, **kwargs)
        return None
