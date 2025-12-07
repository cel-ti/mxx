"""Sleep utility with countdown display."""

import sys
import time
import subprocess
import psutil
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from mxx.models.profile import MxxProfile


def _check_ld_running(profile: "MxxProfile") -> bool:
    """Check if LD emulator is still running using ldpx.
    
    Args:
        profile: Profile to check
        
    Returns:
        True if LD is running, False otherwise
    """
    if not profile.ld:
        return True  # No LD to check
    
    try:
        index = profile.ld.index
        if index is None:
            return True  # Can't check without index
        
        result = subprocess.run(
            ['ldpx', 'console', 'isrunning', '--index', str(index)],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # ldpx returns "running" or "stop"
        return result.stdout.strip().lower() == 'running'
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return True  # Assume running if we can't check


def _check_maa_running(profile: "MxxProfile") -> bool:
    """Check if MAA app process is still running.
    
    Args:
        profile: Profile to check
        
    Returns:
        True if MAA app is running, False otherwise
    """
    if not profile.maa or not profile.maa.app:
        return True  # No MAA to check
    
    app_name = profile.maa.app.lower()
    if not app_name.endswith('.exe'):
        app_name += '.exe'
    
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == app_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return False


def _check_profile_running(profile: "MxxProfile") -> Tuple[bool, str]:
    """Check if profile processes are still running.
    
    Args:
        profile: Profile to check
        
    Returns:
        Tuple of (is_running, failure_reason)
    """
    ld_running = _check_ld_running(profile)
    maa_running = _check_maa_running(profile)
    
    if not ld_running and not maa_running:
        return False, "Both LD and MAA processes terminated"
    elif not ld_running:
        return False, "LD emulator terminated"
    elif not maa_running:
        return False, "MAA app process terminated"
    
    return True, ""


def sleep_with_countdown(seconds: int, profile: "MxxProfile" = None, prefix: str = "Waiting") -> bool:
    """Sleep for specified seconds with live countdown display.
    
    Checks every 10 seconds if profile processes are still running.
    If processes fail 10 consecutive times, terminates early.
    Can be interrupted with Ctrl+C.
    
    Args:
        seconds: Number of seconds to sleep
        profile: Profile to monitor (optional)
        prefix: Text to display before countdown (default: "Waiting")
        
    Returns:
        True if completed successfully, False if profile processes failed
        
    Example:
        >>> success = sleep_with_countdown(60, profile, "Profile running")
        Profile running: 60s remaining...
        Profile running: 59s remaining...
        ...
        
    Raises:
        KeyboardInterrupt: If user presses Ctrl+C
    """
    if seconds <= 0:
        return True
    
    failure_count = 0
    max_failures = 10
    
    try:
        for remaining in range(seconds, 0, -1):
            # Use carriage return to overwrite the same line
            sys.stdout.write(f"\r{prefix}: {remaining}s remaining...    ")
            sys.stdout.flush()
            time.sleep(1)
            
            # Check if profile processes are still running every 10 seconds
            if profile and remaining % 10 == 0:
                is_running, failure_reason = _check_profile_running(profile)
                
                if not is_running:
                    failure_count += 1
                    print(f"\n[Warning] {failure_reason} (failure {failure_count}/{max_failures})")
                    
                    if failure_count >= max_failures:
                        sys.stdout.write("\r" + " " * 60 + "\r")
                        sys.stdout.flush()
                        print(f"\n[Error] Profile processes failed {max_failures} times. Terminating.")
                        return False
                else:
                    # Reset counter if processes are running again
                    if failure_count > 0:
                        print("\n[Info] Processes recovered, resetting failure counter.")
                    failure_count = 0
        
        # Clear the line and move to next line
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()
        return True
        
    except KeyboardInterrupt:
        # Clear the line on interrupt
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()
        print("\nInterrupted by user")
