"""Profile execution commands."""

import sys

import click

from mxx.cli.plugin_aware import PluginAwareGroup
from mxx.core.profile_resolver import profile_resolver
from mxx.core.runner import ProfileRunner


@click.group(cls=PluginAwareGroup)
def run():
    """Run profile commands."""
    pass


@run.command()
@click.argument("profiles", nargs=-1, required=True)
@click.option("--waittime", type=int, help="Override wait time between LD and MAA start (seconds)")
@click.option("--kill", is_flag=True, help="Kill the profile after lifetime expires")
@click.option("--kill-all", is_flag=True, help="Kill all processes after lifetime expires")
def up(profiles: tuple[str, ...], waittime: int | None, kill: bool, kill_all: bool):
    """Start one or more profiles.
    
    Args:
        profiles: Profile names (without .toml extension)
        waittime: Optional wait time override between LD and MAA start
        kill: Kill the specific profile after lifetime
        kill_all: Kill all processes after lifetime
    """
    from mxx.core.parser import validate_profile
    from mxx.utils.nofuss.sleep import sleep_with_countdown
    
    runner = ProfileRunner(profile_resolver.plugin_loader)
    
    for profile_name in profiles:
        try:
            profile, is_plugin = profile_resolver.get_profile(profile_name)
            
            # Update plugin loader context with current profile name
            current_context = profile_resolver.plugin_loader.context.copy()
            current_context['profile_name'] = profile_name
            profile_resolver.plugin_loader.set_context(current_context)
            
            source = "[PLUGIN]" if is_plugin else ""
            
            # Validate before starting
            validate_profile(profile)
            
            click.echo(f"Starting profile: {profile_name} {source}")
            
            # Use CLI override or profile's waittime or default
            ld_wait = waittime if waittime is not None else (profile.waittime or 15)
            runner.start_profile(profile, wait_time=ld_wait, validate=False)
            
            click.echo(f"✓ Profile '{profile_name}' started successfully")
            
            # Handle lifetime and killing
            if kill or kill_all:
                if profile.lifetime:
                    success = sleep_with_countdown(profile.lifetime, profile, f"Profile '{profile_name}' running")
                    
                    # Update context to mark failure if processes terminated early
                    if not success:
                        current_context = profile_resolver.plugin_loader.context.copy()
                        current_context['profile_failed'] = True
                        current_context['profile_name'] = profile_name
                        profile_resolver.plugin_loader.set_context(current_context)
                        
                        # Notify plugins of the failure (calls post_profile_start with failed=True context)
                        runner.notify_profile_failure(profile)
                        
                        click.echo(f"✗ Profile '{profile_name}' failed during execution", err=True)
                        sys.exit(1)
                    
                    if kill_all:
                        click.echo("Lifetime expired, stopping all processes...")
                        ctx = click.get_current_context()
                        ctx.invoke(down)
                    elif kill:
                        click.echo(f"Lifetime expired, stopping profile '{profile_name}'...")
                        runner.kill_profile(profile)
                        click.echo(f"✓ Profile '{profile_name}' stopped")
                else:
                    click.echo("Warning: --kill or --kill-all specified but profile has no lifetime")
            
        except FileNotFoundError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"Error starting profile '{profile_name}': {e}", err=True)
            sys.exit(1)


@run.command()
@click.argument("profiles", nargs=-1)
def down(profiles: tuple[str, ...]):
    """Kill running profiles.
    
    If profile names are provided, kills only those profiles.
    If no profiles specified, kills all MAA and LD processes.
    """
    import os
    from mxx.utils.kill import kill_processes_by_path
    from mxx.core.parser import get_maa_app_path
    
    runner = ProfileRunner(profile_resolver.plugin_loader)
    
    if profiles:
        # Kill specific profiles
        click.echo(f"Stopping {len(profiles)} profile(s)...")
        for profile_name in profiles:
            try:
                profile, _ = profile_resolver.get_profile(profile_name)
                runner.kill_profile(profile)
                click.echo(f"✓ Stopped profile '{profile_name}'")
            except Exception as e:
                click.echo(f"Error stopping profile '{profile_name}': {e}", err=True)
    else:
        # Kill all MAA and LD processes
        click.echo("Stopping all profiles...")
        
        try:
            total_killed = 0
            
            # Kill all MAA processes by scanning for MAA executables
            for name, model in profile_resolver.list_all_profiles():
                if hasattr(model, 'maa') and model.maa:
                    try:
                        app_path = get_maa_app_path(model.maa)
                        killed = kill_processes_by_path(app_path)
                        total_killed += killed
                    except Exception:
                        pass
            
            # Kill all LD processes using ldpx
            os.system("ldpx console quitall")
            
            if total_killed > 0:
                click.echo(f"✓ Stopped {total_killed} MAA process(es) and all LD instances")
            else:
                click.echo("✓ Stopped all LD instances (no MAA processes found)")
                
        except Exception as e:
            click.echo(f"Error stopping profiles: {e}", err=True)
            sys.exit(1)
