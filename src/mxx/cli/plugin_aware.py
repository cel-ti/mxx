"""Custom Click command and group classes with plugin hook support."""

import click
from typing import Any


def parse_var_from_args(ctx: click.Context) -> dict:
    """Extract --var arguments from context and parse them.
    
    Args:
        ctx: Click context
        
    Returns:
        Dictionary of parsed variables
    """
    vars_dict = {}
    
    # Check if --var is in the arguments
    if hasattr(ctx, 'params') and 'var' in ctx.params:
        var_values = ctx.params.pop('var', [])
        if var_values:
            for var in var_values:
                if '=' in var:
                    key, value = var.split('=', 1)
                    vars_dict[key.strip()] = value.strip()
    
    return vars_dict


class PluginAwareCommand(click.Command):
    """Command class that invokes plugin hooks before and after execution."""
    
    def invoke(self, ctx: click.Context) -> Any:
        """Invoke command with plugin hooks.
        
        Args:
            ctx: Click context
            
        Returns:
            Command result
        """
        # Get plugin loader from context
        plugin_loader = ctx.obj.get('plugin_loader') if ctx.obj else None
        
        # Pre-command hook
        if plugin_loader:
            plugin_loader.pre_command(command_name=self.name, ctx=ctx)
        
        try:
            # Execute the actual command
            result = super().invoke(ctx)
            
            # Post-command hook (success)
            if plugin_loader:
                plugin_loader.post_command(command_name=self.name, ctx=ctx, result=result)
            
            return result
            
        except Exception as e:
            # Command error hook
            if plugin_loader:
                plugin_loader.command_error(command_name=self.name, ctx=ctx, error=e)
            raise


class PluginAwareGroup(click.Group):
    """Group class that ensures all commands and subgroups use plugin-aware classes."""
    
    def command(self, *args, **kwargs):
        """Register a command with plugin awareness.
        
        Automatically uses PluginAwareCommand unless a different cls is specified.
        """
        kwargs.setdefault('cls', PluginAwareCommand)
        return super().command(*args, **kwargs)
    
    def group(self, *args, **kwargs):
        """Register a subgroup with plugin awareness.
        
        Automatically uses PluginAwareGroup unless a different cls is specified.
        """
        kwargs.setdefault('cls', PluginAwareGroup)
        return super().group(*args, **kwargs)
