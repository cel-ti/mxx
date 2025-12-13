"""Plugin to track profile completions and prevent duplicate runs per day.

This plugin checks if a profile has already been completed today using
a JSON file stored in ~/.mxx/completion/{date}.json.
"""

import sys
from pathlib import Path
from typing import Dict, Any

from mxx.plugin_system.plugin import MxxPlugin
from .manager import CompletionManager
from .commands import register_next_command, register_notify_command


class CheckCompletionPlugin(MxxPlugin):
    """Prevents duplicate profile runs by tracking daily completions."""
    
    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
        completion_dir = Path.home() / ".mxx" / "completion"
        self.manager = CompletionManager(completion_dir)
    
    def pre_profile_start(self, profile, ctx: Dict[str, Any]) -> None:
        """Check completion before profile starts and exit if already completed.
        
        Args:
            profile: Profile being started
            ctx: Runtime context (contains 'profile_name' and 'vars')
        """
        vars = ctx.get('vars', {})
        profile_name = ctx.get('profile_name')
        
        if not profile_name:
            return
        
        # Handle reset-completion flag
        if vars.get('reset-completion') == 'true':
            if self.manager.reset_completion(profile_name):
                print(f"[CheckCompletion] Reset completion status for '{profile_name}'.")
            else:
                print(f"[CheckCompletion] Profile '{profile_name}' was not marked as completed.")
        
        # Only check/track completion if --var by-completion is passed
        if vars.get('by-completion') != 'true':
            return
        
        # Check if include-failed option is set
        include_failed = vars.get('include-failed') == 'true'
        
        # Check if already completed today
        if self.manager.is_completed(profile_name, include_failed=include_failed):
            completions = self.manager.load_completions()
            status = completions.get(profile_name)
            status_text = "successfully" if status else "with failure"
            
            print(f"[CheckCompletion] Profile '{profile_name}' already completed today {status_text}.")
            print(f"[CheckCompletion] Completion file: {self.manager.get_completion_file()}")
            print("[CheckCompletion] Skipping execution.")
            sys.exit(0)
        
        print(f"[CheckCompletion] Profile '{profile_name}' not yet completed today.")
        print("[CheckCompletion] Will track completion after run.")
        
    def post_profile_start(self, profile, ctx: Dict[str, Any]) -> None:
        """Record completion status after profile execution.
        
        This hook is called twice:
        1. After profile starts successfully (profile_failed=False)
        2. After profile fails during lifetime (profile_failed=True) via notify_profile_failure
        
        Args:
            profile: Profile that was started
            ctx: Runtime context (contains 'profile_name', 'vars', and 'profile_failed')
        """
        vars = ctx.get('vars', {})
        
        # Only track if --var by-completion=true is passed
        if vars.get('by-completion') != 'true':
            return
        
        profile_name = ctx.get('profile_name')
        if not profile_name:
            return
        
        # Check if profile failed during execution
        failed = ctx.get('profile_failed', False)
        
        # Check if profile is in notify list (should be treated as successful)
        in_notify_list = self.manager.is_in_notify_list(profile_name)
        
        # If in notify list, treat as successful even if it failed
        if in_notify_list and failed:
            print(f"[CheckCompletion] Profile '{profile_name}' is in notify list.")
            print(f"[CheckCompletion] Treating early exit as successful completion.")
            failed = False
        
        # Save the appropriate status
        self.manager.save_completion(profile_name, success=not failed)
        
        if failed:
            print(f"[CheckCompletion] Marked '{profile_name}' as failed for today.")
        else:
            print(f"[CheckCompletion] Marked '{profile_name}' as completed successfully for today.")
        if failed:
            print(f"[CheckCompletion] Marked '{profile_name}' as failed for today.")
        else:
            print(f"[CheckCompletion] Marked '{profile_name}' as completed successfully for today.")
    
    def register_commands(self, cli_group):
        """Register custom CLI commands.
        
        This registers commands under their appropriate groups.
        
        Args:
            cli_group: Main CLI group (not used, we target run group directly)
        """
        # Import here to avoid issues during plugin discovery
        from mxx.cli.run import run
        
        # Register commands under the 'run' group
        register_next_command(run, self.manager)
        register_notify_command(run, self.manager)


plugin = CheckCompletionPlugin()
