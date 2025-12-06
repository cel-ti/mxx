"""Comprehensive example plugin demonstrating all MXX plugin capabilities.

This plugin serves as a reference implementation showing:
- Plugin initialization
- CLI command registration
- Command execution hooks (pre/post/error)
- Profile execution hooks
- Profile validation hooks
- Contributing profiles from plugins
"""

import click
from typing import Dict, Any
from mxx.plugin_system.plugin import MxxPlugin


class ExamplePlugin(MxxPlugin):
    """Example plugin demonstrating all available plugin capabilities."""
    
    def __init__(self):
        """Initialize plugin with state."""
        super().__init__()
        self.command_count = 0
        self.profile_runs = 0
    
    # ==================== Initialization ====================
    
    def init(self) -> None:
        """Initialize the plugin.
        
        Called once when plugin loader initializes.
        Use for:
        - Setup operations
        - Validation checks
        - Early exit conditions (like single-instance check)
        """
        click.echo("[ExamplePlugin] Initialized!")
        # Example: You could check prerequisites here
        # if not check_requirements():
        #     sys.exit(1)
    
    # ==================== CLI Command Registration ====================
    
    def register_commands(self, cli_group) -> None:
        """Register custom CLI commands.
        
        Args:
            cli_group: The main Click CLI group
            
        Plugins can add:
        - New top-level commands
        - Command groups
        - Subcommands
        """
        
        @cli_group.command()
        @click.option("--verbose", "-v", is_flag=True, help="Verbose output")
        def example(verbose):
            """Example command added by plugin."""
            click.echo("Hello from ExamplePlugin command!")
            if verbose:
                click.echo(f"Commands executed: {self.command_count}")
                click.echo(f"Profiles run: {self.profile_runs}")
        
        @cli_group.group()
        def demo():
            """Demo command group from plugin."""
            pass
        
        @demo.command()
        def info():
            """Show plugin info."""
            click.echo("ExamplePlugin v0.1.0")
            click.echo("Demonstrates all plugin capabilities")
        
        @demo.command()
        @click.argument("message")
        def echo(message):
            """Echo a message."""
            click.echo(f"[ExamplePlugin] {message}")
    
    # ==================== Command Execution Hooks ====================
    
    def hook_pre_command(self, command_name: str, ctx: click.Context) -> None:
        """Hook called before any command executes.
        
        Args:
            command_name: Name of the command being executed
            ctx: Click context with params, parent, obj, etc.
            
        Use for:
        - Logging command execution
        - Validating preconditions
        - Modifying context
        - Early exits
        """
        self.command_count += 1
        click.echo(f"[ExamplePlugin] Pre-command: {command_name}")
        
        # Access command parameters
        if ctx.params:
            click.echo(f"[ExamplePlugin] Parameters: {ctx.params}")
        
        # Access plugin loader from context
        plugin_loader = ctx.obj.get('plugin_loader') if ctx.obj else None
        if plugin_loader:
            click.echo(f"[ExamplePlugin] {len(plugin_loader.plugins)} plugins loaded")
    
    def hook_post_command(self, command_name: str, ctx: click.Context, result: Any) -> None:
        """Hook called after successful command execution.
        
        Args:
            command_name: Name of the command that executed
            ctx: Click context
            result: Return value from command (usually None)
            
        Use for:
        - Logging success
        - Cleanup operations
        - Metrics collection
        - Post-processing
        """
        click.echo(f"[ExamplePlugin] Post-command: {command_name} completed successfully")
    
    def hook_command_error(self, command_name: str, ctx: click.Context, error: Exception) -> None:
        """Hook called when command execution fails.
        
        Args:
            command_name: Name of the command that failed
            ctx: Click context
            error: Exception that was raised
            
        Use for:
        - Error logging
        - Custom error handling
        - Cleanup after failures
        - Notifications
        """
        click.echo(f"[ExamplePlugin] Command error in {command_name}: {error}")
    
    # ==================== Profile Execution Hooks ====================
    
    def pre_profile_start(self, profile, ctx: Dict[str, Any]) -> None:
        """Hook called before a profile starts.
        
        Args:
            profile: MxxProfile being started
            ctx: Runtime context dictionary
            
        Use for:
        - Logging profile starts
        - Modifying profile properties
        - Environment setup
        - Precondition checks
        """
        self.profile_runs += 1
        click.echo(f"[ExamplePlugin] Starting profile: {profile.name if hasattr(profile, 'name') else 'unknown'}")
        
        # Access LD configuration
        if profile.ld:
            click.echo(f"[ExamplePlugin] LD index: {profile.ld.index}, name: {profile.ld.name}")
        
        # Access MAA configuration
        if profile.maa:
            click.echo(f"[ExamplePlugin] MAA path: {profile.maa.path}")
    
    def post_profile_start(self, profile, ctx: Dict[str, Any]) -> None:
        """Hook called after a profile starts.
        
        Args:
            profile: MxxProfile that was started
            ctx: Runtime context dictionary
            
        Use for:
        - Logging completion
        - Post-start validation
        - Triggering dependent actions
        """
        click.echo("[ExamplePlugin] Profile started successfully")
    
    def pre_profile_kill(self, profile, ctx: Dict[str, Any]) -> None:
        """Hook called before a profile is killed.
        
        Args:
            profile: MxxProfile being killed
            ctx: Runtime context dictionary
            
        Use for:
        - Cleanup before termination
        - Saving state
        - Notifications
        """
        click.echo("[ExamplePlugin] Killing profile...")
    
    def post_profile_kill(self, profile, ctx: Dict[str, Any]) -> None:
        """Hook called after a profile is killed.
        
        Args:
            profile: MxxProfile that was killed
            ctx: Runtime context dictionary
            
        Use for:
        - Cleanup confirmation
        - Resource release
        - Logging termination
        """
        click.echo("[ExamplePlugin] Profile killed")
    
    # ==================== Profile Validation Hooks ====================
    
    def can_run_profile(self, profile, ctx: Dict[str, Any]) -> bool:
        """Check if a profile can run.
        
        Args:
            profile: MxxProfile to check
            ctx: Runtime context dictionary
            
        Returns:
            True to allow running, False to prevent
            
        Use for:
        - Validating preconditions
        - Checking system state
        - Implementing run policies
        - Resource availability checks
        
        Note: If ANY plugin returns False, profile won't run
        """
        # Example: Check if test mode
        if ctx.get('test_mode'):
            click.echo("[ExamplePlugin] Test mode - allowing run")
            return True
        
        # Example: Validate time windows
        # from datetime import datetime
        # hour = datetime.now().hour
        # if hour < 6 or hour > 23:
        #     click.echo("[ExamplePlugin] Outside allowed hours")
        #     return False
        
        return True
    
    def can_kill_profile(self, profile, ctx: Dict[str, Any]) -> bool:
        """Check if a profile can be killed.
        
        Args:
            profile: MxxProfile to check
            ctx: Runtime context dictionary
            
        Returns:
            True to allow killing, False to prevent
            
        Use for:
        - Protecting critical profiles
        - Enforcing cooldown periods
        - Validating kill conditions
        
        Note: If ANY plugin returns False, profile won't be killed
        """
        return True
    
    # ==================== Profile Contribution ====================
    
    def get_profiles(self) -> Dict[str, Any]:
        """Provide profiles contributed by this plugin.
        
        Returns:
            Dictionary mapping profile names to MxxProfile instances
            
        Use for:
        - Dynamically generated profiles
        - Profiles from external sources
        - Virtual/computed profiles
        
        Note: This is called once during plugin loading
        """
        # Example: Could create profiles programmatically
        # from mxx.models.profile import MxxProfile
        # return {
        #     "plugin-profile": MxxProfile(name="plugin-profile", ...)
        # }
        return {}
    
    # ==================== Generic Hook System ====================
    
    def hook(self, hook_name: str, *args, **kwargs) -> Any:
        """Generic hook dispatcher for custom events.
        
        Args:
            hook_name: Name of the hook (e.g., "pre_ld_start")
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Hook result if hook exists, None otherwise
            
        Use for:
        - Custom plugin-specific events
        - Extending hook system
        - Communication between plugins
        
        Note: Implement hook_{event_name} methods to handle specific events
        """
        # This is already implemented in PluginInterface
        # But you can override for custom behavior
        return super().hook(hook_name, *args, **kwargs)
    
    # Example custom hooks (called via emit())
    def hook_pre_ld_start(self, profile):
        """Example custom hook for LD start."""
        click.echo("[ExamplePlugin] Custom hook: pre_ld_start")
    
    def hook_pre_maa_launch(self, profile):
        """Example custom hook for MAA launch."""
        click.echo("[ExamplePlugin] Custom hook: pre_maa_launch")


# Plugin instance - REQUIRED
# The plugin loader looks for this exact variable name
plugin = ExamplePlugin()
