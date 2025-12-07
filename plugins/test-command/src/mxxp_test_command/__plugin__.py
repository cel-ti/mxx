"""Plugin that adds a test command."""

import click
from typing import Dict
from mxx.plugin_system.plugin import MxxPlugin


class TestCommandPlugin(MxxPlugin):
    """Adds a test command to the CLI."""
    
    def register_commands(self, cli_group, vars: Dict[str, str] = None) -> None:
        """Register the test command.
        
        Args:
            cli_group: The main CLI group
            vars: Optional variables from --var options
        """
        @cli_group.command()
        @click.option("--name", default="World", help="Name to greet")
        def test(name):
            """Test command added by plugin."""
            click.echo(f"Hello {name} from TestCommandPlugin!")
            click.echo("This is the base test command.")
    
    def hook_pre_command(self, command_name, ctx, vars: Dict[str, str] = None):
        """Hook that runs before any command.
        
        Args:
            command_name: Name of command
            ctx: Click context
            vars: Optional variables from --var options
        """
        if command_name == "test":
            click.echo("[TestCommandPlugin] Pre-command hook: test command starting...")
            if vars:
                click.echo(f"[TestCommandPlugin] Variables passed: {vars}")
    
    def hook_post_command(self, command_name, ctx, result, vars: Dict[str, str] = None):
        """Hook that runs after successful command execution.
        
        Args:
            command_name: Name of command
            ctx: Click context
            result: Command result
            vars: Optional variables from --var options
        """
        if command_name == "test":
            click.echo("[TestCommandPlugin] Post-command hook: test command completed!")


plugin = TestCommandPlugin()
