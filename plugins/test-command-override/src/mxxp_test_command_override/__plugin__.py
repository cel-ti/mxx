"""Plugin that overrides/extends test command behavior through hooks."""

import click
from mxx.plugin_system.plugin import MxxPlugin


class TestCommandOverridePlugin(MxxPlugin):
    """Extends the test command behavior using hooks."""
    
    def hook_pre_command(self, command_name, ctx):
        """Hook that runs before any command.
        
        This demonstrates how a plugin can extend command behavior
        without replacing the original command.
        """
        if command_name == "test":
            click.echo("=" * 60)
            click.echo("[TestCommandOverridePlugin] ⚡ Enhanced test mode activated!")
            click.echo("=" * 60)
            
            # Access command parameters from context
            params = ctx.params
            if "name" in params:
                click.echo(f"[TestCommandOverridePlugin] Processing for user: {params['name']}")
    
    def hook_post_command(self, command_name, ctx, result):
        """Hook that runs after successful command execution."""
        if command_name == "test":
            click.echo("=" * 60)
            click.echo("[TestCommandOverridePlugin] ✨ Additional features activated:")
            click.echo("  - Logging enabled")
            click.echo("  - Metrics collected")
            click.echo("  - Enhancement layer applied")
            click.echo("=" * 60)
    
    def hook_command_error(self, command_name, ctx, error):
        """Hook that runs when a command fails."""
        if command_name == "test":
            click.echo(f"[TestCommandOverridePlugin] ❌ Error detected: {error}")
            click.echo("[TestCommandOverridePlugin] Attempting recovery...")
    

plugin = TestCommandOverridePlugin()
