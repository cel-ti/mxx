"""Plugin to track profile completions and prevent duplicate runs per day.

This plugin checks if a profile has already been completed today using
a JSON file stored in ~/.mxx/completion/{date}.json.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from mxx.plugin_system.plugin import MxxPlugin


class CheckCompletionPlugin(MxxPlugin):
    """Prevents duplicate profile runs by tracking daily completions."""
    
    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
        self.completion_dir = Path.home() / ".mxx" / "completion"
        self._ensure_completion_dir()
    
    def _ensure_completion_dir(self) -> None:
        """Ensure the completion directory exists."""
        self.completion_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_completion_file(self) -> Path:
        """Get the completion file path for today.
        
        Returns:
            Path to today's completion JSON file
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return self.completion_dir / f"{today}.json"
    
    def _load_completions(self) -> Dict[str, bool]:
        """Load today's completion records.
        
        Returns:
            Dictionary mapping profile names to completion status
        """
        completion_file = self._get_completion_file()
        if completion_file.exists():
            try:
                with open(completion_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_completion(self, profile_name: str) -> None:
        """Mark a profile as completed for today.
        
        Args:
            profile_name: Name of the profile to mark as completed
        """
        completions = self._load_completions()
        completions[profile_name] = True
        
        completion_file = self._get_completion_file()
        try:
            with open(completion_file, 'w') as f:
                json.dump(completions, f, indent=2)
        except IOError as e:
            print(f"[CheckCompletion] Warning: Could not save completion: {e}")
    
    def _is_completed(self, profile_name: str) -> bool:
        """Check if a profile has been completed today.
        
        Args:
            profile_name: Name of the profile to check
            
        Returns:
            True if already completed today, False otherwise
        """
        completions = self._load_completions()
        return completions.get(profile_name, False)
    
    def _reset_completion(self, profile_name: str) -> None:
        """Reset completion status for a specific profile.
        
        Args:
            profile_name: Name of the profile to reset
        """
        completions = self._load_completions()
        if profile_name in completions:
            del completions[profile_name]
            completion_file = self._get_completion_file()
            try:
                with open(completion_file, 'w') as f:
                    json.dump(completions, f, indent=2)
                print(f"[CheckCompletion] Reset completion status for '{profile_name}'.")
            except IOError as e:
                print(f"[CheckCompletion] Warning: Could not reset completion: {e}")
        else:
            print(f"[CheckCompletion] Profile '{profile_name}' was not marked as completed.")
    
    def pre_profile_start(self, profile, ctx: Dict[str, Any]) -> None:
        """Check completion before profile starts and exit if already completed.
        
        Args:
            profile: Profile being started
            ctx: Runtime context (contains 'profile_name' and 'vars')
        """
        # Get vars from context
        vars = ctx.get('vars', {})
        
        # Get profile name from runtime context
        profile_name = ctx.get('profile_name')
        if not profile_name:
            return
        
        # Handle reset-completion flag
        if vars.get('reset-completion') == 'true':
            self._reset_completion(profile_name)
            # Continue with execution after reset
        
        # Only check/track completion if --var by-completion is passed
        if vars.get('by-completion') != 'true':
            return
        
        # Check if already completed today
        if self._is_completed(profile_name):
            print(f"[CheckCompletion] Profile '{profile_name}' already completed today.")
            print(f"[CheckCompletion] Completion file: {self._get_completion_file()}")
            print("[CheckCompletion] Skipping execution.")
            sys.exit(0)  # Exit early without error
        
        print(f"[CheckCompletion] Profile '{profile_name}' not yet completed today.")
        print("[CheckCompletion] Will track completion after successful run.")
    
    def post_profile_start(self, profile, ctx: Dict[str, Any]) -> None:
        """Record completion after profile starts successfully.
        
        Args:
            profile: Profile that was started
            ctx: Runtime context (contains 'profile_name' and 'vars')
        """
        # Get vars from context
        vars = ctx.get('vars', {})
        
        # Only track if --var by-completion=true is passed
        if vars.get('by-completion') != 'true':
            return
        
        # Get profile name from runtime context
        profile_name = ctx.get('profile_name')
        if not profile_name:
            return
        
        # Mark as completed
        self._save_completion(profile_name)
        print(f"[CheckCompletion] Marked '{profile_name}' as completed for today.")


plugin = CheckCompletionPlugin()
