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
    
    def __init__(self, *args, **kwargs):
        """Initialize command with --var option."""
        super().__init__(*args, **kwargs)
        # Add --var option to all plugin-aware commands
        self.params.insert(0, click.Option(
            ['--var'],
            multiple=True,
            help='Pass variables in x=y format (can be used multiple times)'
        ))
    
    def invoke(self, ctx: click.Context) -> Any:
        """Invoke command with plugin hooks.
        
        Args:
            ctx: Click context
            
        Returns:
            Command result
        """
        # Extract --var from params before command execution
        vars_dict = parse_var_from_args(ctx)
        
        # Store in context for plugin access
        if ctx.obj is None:
            ctx.obj = {}
        ctx.obj['vars'] = vars_dict
        
        # Get plugin loader from context
        plugin_loader = ctx.obj.get('plugin_loader') if ctx.obj else None
        
        # Pre-command hook
        if plugin_loader:
            plugin_loader.emit('pre_command', command_name=self.name, ctx=ctx, vars=vars_dict)
        
        try:
            # Execute the actual command
            result = super().invoke(ctx)
            
            # Post-command hook (success)
            if plugin_loader:
                plugin_loader.emit('post_command', command_name=self.name, ctx=ctx, result=result, vars=vars_dict)
            
            return result
            
        except Exception as e:
            # Command error hook
            if plugin_loader:
                plugin_loader.emit('command_error', command_name=self.name, ctx=ctx, error=e, vars=vars_dict)
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
