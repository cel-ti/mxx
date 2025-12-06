"""Subprocess utilities for launching detached processes."""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def launch_detached(
    command: List[str],
    cwd: Optional[Path] = None,
    shell: bool = False
) -> subprocess.Popen:
    """Launch a detached subprocess that continues running after parent exits.
    
    The process is fully detached:
    - Does not inherit file handles
    - Has its own process group
    - Stdout/stderr are redirected to null
    - Parent can exit without affecting child
    
    Args:
        command: Command and arguments as a list
        cwd: Working directory for the subprocess
        shell: Whether to run through shell
        
    Returns:
        Popen object (but process is detached)
        
    Example:
        >>> launch_detached(["notepad.exe", "file.txt"])
        >>> launch_detached(["python", "script.py"], cwd=Path("/some/dir"))
    """
    creation_flags = 0
    
    if sys.platform == "win32":
        # Windows: Create new process group and detach from console
        creation_flags = (
            subprocess.CREATE_NEW_PROCESS_GROUP |
            subprocess.DETACHED_PROCESS |
            subprocess.CREATE_NO_WINDOW
        )
    
    # Redirect all output to null
    null_device = subprocess.DEVNULL
    
    process = subprocess.Popen(
        command,
        cwd=cwd,
        shell=shell,
        stdin=null_device,
        stdout=null_device,
        stderr=null_device,
        creationflags=creation_flags,
        close_fds=True,  # Close file descriptors
        start_new_session=True if sys.platform != "win32" else False  # Unix: new session
    )
    
    return process


def launch_detached_visible(
    command: List[str],
    cwd: Optional[Path] = None,
    shell: bool = False
) -> subprocess.Popen:
    """Launch a detached subprocess with visible window/output.
    
    Similar to launch_detached but allows the process window to be visible.
    Useful for launching GUI applications or terminal programs.
    
    Args:
        command: Command and arguments as a list
        cwd: Working directory for the subprocess
        shell: Whether to run through shell
        
    Returns:
        Popen object (but process is detached)
        
    Example:
        >>> launch_detached_visible(["cmd.exe", "/k", "echo Hello"])
    """
    creation_flags = 0
    
    if sys.platform == "win32":
        # Windows: Create new process group but allow window
        creation_flags = (
            subprocess.CREATE_NEW_PROCESS_GROUP |
            subprocess.DETACHED_PROCESS
        )
    
    process = subprocess.Popen(
        command,
        cwd=cwd,
        shell=shell,
        stdin=subprocess.DEVNULL,
        creationflags=creation_flags,
        close_fds=True,
        start_new_session=True if sys.platform != "win32" else False
    )
    
    return process


def launch_and_forget(
    command: List[str],
    cwd: Optional[Path] = None,
    shell: bool = False,
    visible: bool = False
) -> None:
    """Launch a process and immediately forget about it.
    
    This is a fire-and-forget launcher that doesn't return the process object.
    The process is completely detached and independent.
    
    Args:
        command: Command and arguments as a list
        cwd: Working directory for the subprocess
        shell: Whether to run through shell
        visible: Whether to show process window/output
        
    Example:
        >>> launch_and_forget(["python", "background_task.py"])
        >>> launch_and_forget(["notepad.exe"], visible=True)
    """
    if visible:
        launch_detached_visible(command, cwd, shell)
    else:
        launch_detached(command, cwd, shell)
