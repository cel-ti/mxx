"""Main CLI entry point for mxx."""

import click
from mxx.cli import config, run
from mxx.core.profile_resolver import profile_resolver


@click.group()
def cli():
    """Mxx - Unified profile management for LD and MAA."""
    pass


# Register command groups
cli.add_command(config.config)
cli.add_command(run.run)
profile_resolver.plugin_loader.init()

if __name__ == "__main__":
    cli()
