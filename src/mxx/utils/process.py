"""
Process and window utilities for adapter startup conditions.

Requires optional [service] dependencies:
    pip install mxx-run[service]
"""

# Check for optional service dependencies
try:
    import psutil
    import win32gui # type: ignore
    import win32process # type: ignore
    PROCESS_UTILS_AVAILABLE = True
except ImportError as e:
    PROCESS_UTILS_AVAILABLE = False
    _IMPORT_ERROR = str(e)


def _check_available():
    """Raise error if process utilities are not available."""
    if not PROCESS_UTILS_AVAILABLE:
        raise ImportError(
            f"Process utilities require optional dependencies. Install with: pip install mxx-run[service]\n"
            f"Original error: {_IMPORT_ERROR}"
        )


def is_process_running(process_name: str) -> bool:
    """
    Check if a process with the given name is currently running.
    
    Args:
        process_name: Name of the process (e.g., "notepad.exe", "game.exe")
        
    Returns:
        True if process is running, False otherwise
        
    Raises:
        ImportError: If optional [service] dependencies not installed
    """
    _check_available()
    process_name = process_name.lower()
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() == process_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def is_window_focused(title_substring: str) -> bool:
    """
    Check if a window with the given title substring is currently focused.
    
    Args:
        title_substring: Substring to match in window title (case-insensitive)
        
    Returns:
        True if matching window is focused, False otherwise
        
    Raises:
        ImportError: If optional [service] dependencies not installed
    """
    _check_available()
    try:
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        return title_substring.lower() in window_title.lower()
    except Exception:
        return False


def get_process_by_window_title(title_substring: str) -> str | None:
    """
    Get the process name for a window with matching title.
    
    Args:
        title_substring: Substring to match in window title
        
    Returns:
        Process name if found, None otherwise
        
    Raises:
        ImportError: If optional [service] dependencies not installed
    """
    _check_available()
    
    def callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if title_substring.lower() in window_title.lower():
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    process = psutil.Process(pid)
                    results.append(process.name())
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        return True
    
    results = []
    win32gui.EnumWindows(callback, results)
    return results[0] if results else None


def list_running_processes() -> list[str]:
    """
    Get list of all running process names.
    
    Returns:
        List of process names
        
    Raises:
        ImportError: If optional [service] dependencies not installed
    """
    _check_available()
    processes = []
    for proc in psutil.process_iter(['name']):
        try:
            processes.append(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes
