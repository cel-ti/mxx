"""Plugin to ensure only one instance of MXX is running."""

import sys
import os
import psutil
import click
from typing import Optional
from mxx.plugin_system.plugin import MxxPlugin


class CheckSingleInstancePlugin(MxxPlugin):
    """Ensures only one instance of MXX is running at a time."""
    
    def init(self, ctx: Optional[click.Context] = None) -> None:
        """Check for other running MXX instances and exit if found.
        
        Only checks if invoked from the 'run' command group.
        
        Args:
            ctx: Optional Click context to determine command group
        """
        # Only check if we're in the run group
        if ctx and not self._is_run_group(ctx):
            return
        
        # Get current process and walk up to find mxx.exe if we're a child process
        current = psutil.Process()
        current_mxx_pid = None
        
        # Check if current process is mxx.exe or find parent mxx.exe
        while current:
            try:
                if current.name() == 'mxx.exe':
                    current_mxx_pid = current.pid
                    break
                current = current.parent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
        
        # If we couldn't find our own mxx.exe parent, use current PID as fallback
        if current_mxx_pid is None:
            current_mxx_pid = os.getpid()
        
        mxx_processes = []
        
        # Find all mxx.exe processes excluding ourselves
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                if proc.info['name'] == 'mxx.exe' and proc.info['pid'] != current_mxx_pid:
                    mxx_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Exit if other instances found
        if mxx_processes:
            print(f"CheckSingleInstance: Found {len(mxx_processes)} other MXX instance(s) running.")
            print("CheckSingleInstance: Only one instance of MXX is allowed. Exiting...")
            sys.exit(1)
    
    def _is_run_group(self, ctx: click.Context) -> bool:
        """Check if context is within the run command group.
        
        Args:
            ctx: Click context
            
        Returns:
            True if in run group, False otherwise
        """
        current = ctx
        while current:
            if hasattr(current, 'info_name') and current.info_name == 'run':
                return True
            current = current.parent
        return False


plugin = CheckSingleInstancePlugin()
