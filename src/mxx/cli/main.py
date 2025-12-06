"""Main CLI entry point for mxx."""

import click
from mxx.cli import config, run


@click.group()
def cli():
    """Mxx - Unified profile management for LD and MAA."""
    pass


# Register command groups
cli.add_command(config.config)
cli.add_command(run.run)


if __name__ == "__main__":
    cli()
