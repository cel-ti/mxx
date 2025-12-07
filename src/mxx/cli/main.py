"""Main CLI entry point for mxx."""

import click
from mxx.cli import config, run
from mxx.cli.plugin_aware import PluginAwareGroup
from mxx.core.profile_resolver import profile_resolver


@click.group(cls=PluginAwareGroup)
@click.pass_context
def cli(ctx):
    """Mxx - Unified profile management for LD and MAA."""
    ctx.ensure_object(dict)
    ctx.obj['plugin_loader'] = profile_resolver.plugin_loader


# Register command groups
cli.add_command(config.config)
cli.add_command(run.run)

# Note: Plugin init and register_commands will get vars from context at runtime
# For now, initialize without vars (vars are passed per-command via context)
profile_resolver.plugin_loader.init()
profile_resolver.plugin_loader.register_commands(cli)

if __name__ == "__main__":
    cli()
