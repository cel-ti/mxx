import subprocess
import shutil
from pathlib import Path


def resolve_editor(file_path: Path) -> None:
    """
    Resolve and launch a text editor to open the specified file.
    Prefers VS Code on Windows.
    
    Args:
        file_path: Path to the file to open
        
    Raises:
        RuntimeError: If no suitable editor is found
    """
    file_path = Path(file_path)
    
    # Try VS Code first
    vscode_commands = ["code", "code.cmd"]
    for cmd in vscode_commands:
        editor_path = shutil.which(cmd)
        if editor_path:
            subprocess.Popen([editor_path, "--new-window", str(file_path)])
            return
    
    # Fallback to notepad (always available on Windows)
    subprocess.Popen(["notepad.exe", str(file_path)])