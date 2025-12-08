"""CLI commands for completion tracking."""

import click
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .manager import CompletionManager


def register_next_command(run_group, manager: "CompletionManager"):
    """Register the 'next' command under the run group.
    
    Args:
        run_group: The Click run command group
        manager: CompletionManager instance
    """
    @run_group.command(name='next')
    def run_next():
        """Run the first non-completed profile automatically.
        
        Discovers all available profiles, checks which haven't been 
        completed successfully today, and runs the first incomplete one.
        
        Automatically runs with --kill and --var by-completion flags.
        
        \b
        Example:
            mxx run next
            
        \b
        This will:
        - Discover all profiles from ~/.mxx/configs/
        - Check which profiles are incomplete (not successfully run today)
        - Run the first incomplete profile with --kill flag
        - Track completion automatically
        """
        # Import here to avoid circular dependency
        from mxx.core.profile_resolver import profile_resolver
        from mxx.cli.run import up
        
        # Get all available profiles
        try:
            all_profiles = profile_resolver.list_profiles()
        except Exception as e:
            click.echo(f"[CheckCompletion] Error discovering profiles: {e}", err=True)
            return
        
        if not all_profiles:
            click.echo("[CheckCompletion] No profiles found in ~/.mxx/configs/")
            return
        
        # Get incomplete profiles
        incomplete = manager.get_incomplete_profiles(all_profiles)
        
        if not incomplete:
            click.echo(f"[CheckCompletion] All {len(all_profiles)} profiles already completed today.")
            return
        
        # Run the first incomplete profile
        next_profile = incomplete[0]
        click.echo(f"[CheckCompletion] Found {len(incomplete)} incomplete profiles out of {len(all_profiles)} total.")
        click.echo(f"[CheckCompletion] Running next incomplete profile: {next_profile}")
        if len(incomplete) > 1:
            click.echo(f"[CheckCompletion] Remaining: {', '.join(incomplete[1:])}")
        
        # Set the by-completion var in context
        current_context = profile_resolver.plugin_loader.context.copy()
        current_vars = current_context.get('vars', {})
        current_vars['by-completion'] = 'true'
        current_context['vars'] = current_vars
        profile_resolver.plugin_loader.set_context(current_context)
        
        # Invoke up command with kill flag
        ctx = click.get_current_context()
        ctx.invoke(up, profiles=(next_profile,), waittime=None, kill=True, kill_all=False)
