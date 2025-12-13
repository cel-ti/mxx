"""Plugin to ensure only one instance of MXX is running."""

import sys
import os
import psutil
import click
from mxx.plugin_system.plugin import MxxPlugin


class CheckSingleInstancePlugin(MxxPlugin):
    """Ensures only one instance of MXX is running at a time when executing run commands."""
    
    def pre_command(self, command_name: str, ctx: click.Context) -> None:
        """Check for other running MXX instances before executing run commands.
        
        Args:
            command_name: Name of the command being executed
            ctx: Click context
        """
        # Only check for run group commands
        # Check if this command is under the 'run' group
        if not self._is_run_command(ctx):
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
    
    def _is_run_command(self, ctx: click.Context) -> bool:
        """Check if the current command is under the 'run' group.
        
        Args:
            ctx: Click context
            
        Returns:
            True if command is under run group, False otherwise
        """
        # Walk up the context chain to find parent groups
        current = ctx
        while current:
            if hasattr(current, 'info_name') and current.info_name == 'run':
                return True
            current = current.parent
        return False


plugin = CheckSingleInstancePlugin()
