"""Main CLI entry point for mxx."""

import sys
import click
from mxx.cli import config, run
from mxx.cli.plugin_aware import PluginAwareGroup
from mxx.core.profile_resolver import profile_resolver
from mxx.utils.nofuss.arg_extract import extract_var_args


@click.group(cls=PluginAwareGroup)
@click.pass_context
def cli(ctx):
    """Mxx - Unified profile management for LD and MAA."""
    ctx.ensure_object(dict)
    ctx.obj['plugin_loader'] = profile_resolver.plugin_loader


# Register command groups
cli.add_command(config.config)
cli.add_command(run.run)


def main():
    """Main entry point that extracts --var before Click processes arguments."""
    # Extract --var arguments before Click sees them
    cleaned_argv, vars_dict = extract_var_args(sys.argv)
    
    # Set vars in plugin loader context immediately
    profile_resolver.plugin_loader.set_context({'vars': vars_dict})
    
    # Initialize plugins with vars available
    profile_resolver.plugin_loader.init()
    profile_resolver.plugin_loader.register_commands(cli)
    
    # Run Click with cleaned arguments
    cli(cleaned_argv[1:], standalone_mode=False)


if __name__ == "__main__":
    main()
