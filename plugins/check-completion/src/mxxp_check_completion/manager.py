"""Completion tracking storage manager."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class CompletionManager:
    """Manages completion tracking storage and retrieval."""
    
    def __init__(self, completion_dir: Path):
        """Initialize the completion manager.
        
        Args:
            completion_dir: Directory to store completion files
        """
        self.completion_dir = completion_dir
        self._ensure_completion_dir()
    
    def _ensure_completion_dir(self) -> None:
        """Ensure the completion directory exists."""
        self.completion_dir.mkdir(parents=True, exist_ok=True)
    
    def get_completion_file(self, date: Optional[str] = None) -> Path:
        """Get the completion file path for a specific date.
        
        Args:
            date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            Path to the completion JSON file
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return self.completion_dir / f"{date}.json"
    
    def load_completions(self, date: Optional[str] = None) -> Dict[str, bool]:
        """Load completion records for a specific date.
        
        Args:
            date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            Dictionary mapping profile names to completion status
        """
        completion_file = self.get_completion_file(date)
        if completion_file.exists():
            try:
                with open(completion_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def save_completion(self, profile_name: str, success: bool = True, date: Optional[str] = None) -> None:
        """Save completion status for a profile.
        
        Args:
            profile_name: Name of the profile
            success: True if successful, False if failed
            date: Date string (YYYY-MM-DD), defaults to today
        """
        completions = self.load_completions(date)
        completions[profile_name] = success
        
        completion_file = self.get_completion_file(date)
        try:
            with open(completion_file, 'w') as f:
                json.dump(completions, f, indent=2)
        except IOError as e:
            print(f"[CheckCompletion] Warning: Could not save completion: {e}")
    
    def is_completed(self, profile_name: str, include_failed: bool = False, date: Optional[str] = None) -> bool:
        """Check if a profile has been completed.
        
        Args:
            profile_name: Name of the profile to check
            include_failed: If True, also consider failed runs as completed
            date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            True if completed (with appropriate success criteria), False otherwise
        """
        completions = self.load_completions(date)
        status = completions.get(profile_name)
        
        if status is None:
            return False
        
        if include_failed:
            return True
        
        return status is True
    
    def reset_completion(self, profile_name: str, date: Optional[str] = None) -> bool:
        """Reset completion status for a specific profile.
        
        Args:
            profile_name: Name of the profile to reset
            date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            True if profile was reset, False if not found
        """
        completions = self.load_completions(date)
        if profile_name in completions:
            del completions[profile_name]
            completion_file = self.get_completion_file(date)
            try:
                with open(completion_file, 'w') as f:
                    json.dump(completions, f, indent=2)
                return True
            except IOError as e:
                print(f"[CheckCompletion] Warning: Could not reset completion: {e}")
                return False
        return False
    
    def get_incomplete_profiles(self, all_profiles: List[str], include_failed: bool = False, date: Optional[str] = None) -> List[str]:
        """Get list of profiles that haven't been completed.
        
        Failed profiles are sorted to the end of the list to give other profiles
        a chance to run first, preventing infinite retries of a single failing profile.
        
        Args:
            all_profiles: List of all available profile names
            include_failed: If True, exclude failed runs from incomplete list
            date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            List of profile names that are not completed, with failed profiles at the end
        """
        completions = self.load_completions(date)
        
        # Separate profiles into never-run and failed
        never_run = []
        failed = []
        
        for profile in all_profiles:
            if self.is_completed(profile, include_failed=include_failed, date=date):
                continue
            
            status = completions.get(profile)
            if status is False:
                # Profile failed previously
                failed.append(profile)
            else:
                # Profile never run or no record
                never_run.append(profile)
        
        # Return never-run profiles first, failed profiles last
        return never_run + failed
