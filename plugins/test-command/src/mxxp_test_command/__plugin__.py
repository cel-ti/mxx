"""Plugin that adds a test command."""

import click
from mxx.plugin_system.plugin import MxxPlugin


class TestCommandPlugin(MxxPlugin):
    """Adds a test command to the CLI."""
    
    def register_commands(self, cli_group) -> None:
        """Register the test command.
        
        Args:
            cli_group: The main CLI group
        """
        @cli_group.command()
        @click.option("--name", default="World", help="Name to greet")
        def test(name):
            """Test command added by plugin."""
            click.echo(f"Hello {name} from TestCommandPlugin!")
            click.echo("This is the base test command.")
    
    def hook_pre_command(self, command_name, ctx):
        """Hook that runs before any command."""
        if command_name == "test":
            click.echo("[TestCommandPlugin] Pre-command hook: test command starting...")
    
    def hook_post_command(self, command_name, ctx, result):
        """Hook that runs after successful command execution."""
        if command_name == "test":
            click.echo("[TestCommandPlugin] Post-command hook: test command completed!")


plugin = TestCommandPlugin()
