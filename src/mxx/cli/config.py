"""Config management commands."""

import sys
from pathlib import Path
from typing import Any, Optional

import click

from mxx.core.config import get_profile_path
from mxx.core.profile_resolver import (
    profile_resolver,
    get_model_type,
    get_type_from_name,
    is_profile_part
)
from mxx.core.parser import validate_profile
from mxx.utils.nofuss.resolveEditor import resolve_editor


def get_model_badge(name: str, model: Any = None) -> str:
    """Get display badge for a model.
    
    Args:
        name: Model name
        model: Model instance (optional)
        
    Returns:
        Badge string like "[LD]" or "[MAA]" or ""
    """
    model_type = get_type_from_name(name)
    if model_type == "LD":
        return "[LD]"
    elif model_type == "MAA":
        return "[MAA]"
    elif model:
        detected_type = get_model_type(model)
        if detected_type == "LD":
            return "[LD]"
        elif detected_type == "MAA":
            return "[MAA]"
    return ""


def validate_model(model: Any, name: str) -> tuple[str, Optional[Exception]]:
    """Validate a model and return status.
    
    Args:
        model: Model to validate
        name: Model name
        
    Returns:
        Tuple of (status_icon, error)
    """
    if is_profile_part(name):
        # Parts don't need full validation
        return "✓", None
    
    try:
        validate_profile(model)
        return "✓", None
    except Exception as e:
        return "✗", e


def format_model_line(name: str, model: Any, error: Optional[Exception]) -> str:
    """Format a single model line for display.
    
    Args:
        name: Model name
        model: Model instance (can be None if error)
        error: Error during loading (if any)
        
    Returns:
        Formatted display string
    """
    badge = get_model_badge(name, model)
    badge_str = f" {badge}" if badge else ""
    
    if error:
        return f"  ✗ {name}{badge_str} - {error}"
    
    status, validation_error = validate_model(model, name)
    if validation_error:
        return f"  {status} {name}{badge_str} - {validation_error}"
    
    return f"  {status} {name}{badge_str}"


def display_model_details(model: Any, name: str, is_plugin: bool) -> None:
    """Display detailed information about a model.
    
    Args:
        model: Model instance
        name: Model name
        is_plugin: Whether it's from a plugin
    """
    model_type = get_model_type(model)
    
    if is_plugin:
        if model_type == "PROFILE":
            click.echo(f"Profile: {model.name}")
            if model.ld:
                click.echo(f"  LD: index={model.ld.index}")
            if model.maa:
                click.echo(f"  MAA: {model.maa.directory or 'default'}")
        elif model_type == "LD":
            click.echo(f"LD: index={model.index}, name={model.name}")
        elif model_type == "MAA":
            click.echo(f"MAA: directory={model.directory}")
    else:
        profiles_dir = get_profile_path()
        config_path = profiles_dir / f"{name}.toml"
        click.echo(config_path.read_text())


@click.group()
def config():
    """Manage configuration profiles."""
    pass


@config.command()
@click.argument("name")
@click.option("--template", "-t", type=click.Choice(["maa", "ld", "profile"]), default="profile",
              help="Template to use (maa, ld, or profile)")
def new(name: str, template: str):
    """Create a new config from template and open in editor.
    
    Supports creating:
    - Full profiles: "profile_name" -> profile_name.toml
    - LD parts: "profile_name.ld" -> profile_name.ld.toml
    - MAA parts: "profile_name.maa" -> profile_name.maa.toml
    
    Args:
        name: Name of the config (e.g., "myprofile" or "myprofile.ld")
        template: Template type (maa, ld, or profile)
    """
    profiles_dir = get_profile_path()
    profiles_dir.mkdir(parents=True, exist_ok=True)
    
    config_path = profiles_dir / f"{name}.toml"
    
    if config_path.exists():
        click.echo(f"Error: Config '{name}' already exists at {config_path}", err=True)
        sys.exit(1)
    
    # Load template
    template_path = Path(__file__).parent.parent / "templates" / f"{template}.template.toml"
    
    if not template_path.exists():
        click.echo(f"Error: Template '{template}' not found at {template_path}", err=True)
        sys.exit(1)
    
    # Copy template to config location
    template_content = template_path.read_text()
    config_path.write_text(template_content)
    
    click.echo(f"Created config: {config_path}")
    
    # Open in editor
    try:
        resolve_editor(config_path)
    except Exception as e:
        click.echo(f"Warning: Failed to open editor: {e}", err=True)
@config.command()
@click.argument("name", required=False)
def cat(name: str = None):
    """Display config contents.
    
    Args:
        name: Name of config to display (without .toml). If omitted, lists all configs.
    """
    if name:
        _display_single_config(name)
    else:
        _list_all_configs()


def _display_single_config(name: str) -> None:
    """Display a single config by name.
    
    Args:
        name: Config name to display
    """
    try:
        model, is_plugin = profile_resolver.get_profile(name)
        
        # Determine status
        model_type = get_model_type(model)
        if is_profile_part(name):
            status = "OK"
        else:
            try:
                validate_profile(model)
                status = "VALID"
            except Exception as e:
                status = f"INVALID: {e}"
        
        source = "PLUGIN" if is_plugin else "FILE"
        click.echo(f"--- {name} [{model_type} - {source} - {status}] ---")
        
        display_model_details(model, name, is_plugin)
        
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def _list_all_configs() -> None:
    """List all available configs."""
    all_items = profile_resolver.list_all_profiles()
    
    if not all_items:
        click.echo("No configs found.")
        return
    
    # Separate by source
    plugin_items = {n: item for n, item in all_items.items() if item[1]}
    file_items = {n: item for n, item in all_items.items() if not item[1]}
    
    # Display plugins
    if plugin_items:
        click.echo("Plugin profiles:")
        for name in sorted(plugin_items.keys()):
            model, _, error = plugin_items[name]
            click.echo(format_model_line(name, model, error))
    
    # Display files
    if file_items:
        if plugin_items:
            click.echo("\nFile configs:")
        else:
            click.echo("Available configs:")
        
        for name in sorted(file_items.keys()):
            model, _, error = file_items[name]
            click.echo(format_model_line(name, model, error))
