"""CLI commands for completion tracking."""

import click
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .manager import CompletionManager


def register_notify_command(run_group, manager: "CompletionManager"):
    """Register the 'notify' command under the run group.
    
    Args:
        run_group: The Click run command group
        manager: CompletionManager instance
    """
    @run_group.command(name='notify')
    @click.argument('profile', required=True)
    def run_notify(profile: str):
        """Mark a profile to be treated as successful even if processes exit early.
        
        This is useful when MAA has "quit when done" settings that would otherwise
        be detected as failures. Profiles in the notify list will be marked as
        successful instead of failed when processes exit during the lifetime period.
        
        \b
        Example:
            mxx run notify maa
            
        \b
        This will:
        - Add 'maa' to today's notify list
        - When 'maa' runs and MAA quits, mark it as successful instead of failed
        - Prevent repeated runs of profiles that intentionally quit early
        
        Args:
            profile: Name of the profile to add to notify list
        """
        manager.add_to_notify_list(profile)
        notify_file = manager.get_notify_file()
        notify_list = manager.load_notify_list()
        
        click.echo(f"[CheckCompletion] Added '{profile}' to today's notify list.")
        click.echo(f"[CheckCompletion] Notify file: {notify_file}")
        click.echo(f"[CheckCompletion] Current notify list: {', '.join(notify_list)}")


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
