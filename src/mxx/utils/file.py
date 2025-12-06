"""File utilities for filtering, zipping, and loading config files."""

from pathlib import Path
from typing import List, Dict, Any
import zipfile
import fnmatch


def filter_files(
    directory: Path,
    include_patterns: List[str] = None,
    exclude_patterns: List[str] = None
) -> List[Path]:
    """Filter files in a directory based on include and exclude patterns.
    
    Args:
        directory: Directory to search in
        include_patterns: List of glob patterns to include (e.g., ["*.toml", "*.json"])
        exclude_patterns: List of glob patterns to exclude
        
    Returns:
        List of matching file paths
    """
    if not directory.exists():
        return []
    
    all_files = [f for f in directory.rglob("*") if f.is_file()]
    
    # Apply include patterns
    if include_patterns:
        included = set()
        for pattern in include_patterns:
            for file in all_files:
                rel_path = file.relative_to(directory)
                if fnmatch.fnmatch(str(rel_path), pattern) or fnmatch.fnmatch(file.name, pattern):
                    included.add(file)
        all_files = list(included)
    
    # Apply exclude patterns
    if exclude_patterns:
        filtered = []
        for file in all_files:
            rel_path = file.relative_to(directory)
            excluded = False
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(str(rel_path), pattern) or fnmatch.fnmatch(file.name, pattern):
                    excluded = True
                    break
            if not excluded:
                filtered.append(file)
        all_files = filtered
    
    return all_files


def load_config_file(file_path: Path) -> Dict[str, Any]:
    """Load a config file (supports .toml and .json).
    
    Args:
        file_path: Path to config file
        
    Returns:
        Dictionary with file contents
    """
    suffix = file_path.suffix.lower()
    
    if suffix == '.toml':
        from mxx.utils.nofuss.toml import load_toml
        return load_toml(str(file_path))
    elif suffix == '.json':
        from mxx.utils.nofuss.json import load_json
        return load_json(str(file_path))
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def save_config_file(file_path: Path, data: Dict[str, Any]) -> None:
    """Save a config file (supports .toml and .json).
    
    Args:
        file_path: Path to config file
        data: Dictionary to save
    """
    suffix = file_path.suffix.lower()
    
    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if suffix == '.toml':
        from mxx.utils.nofuss.toml import save_toml
        save_toml(data, str(file_path))
    elif suffix == '.json':
        from mxx.utils.nofuss.json import save_json
        save_json(data, str(file_path))
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def create_zip_from_dict(zip_path: Path, files_dict: Dict[str, Dict[str, Any]]) -> None:
    """Create a zip file from a dictionary of file contents.
    
    Args:
        zip_path: Path where zip file should be created
        files_dict: Dictionary mapping relative file paths to their contents
    """
    import json
    
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for rel_path, content in files_dict.items():
            # Store as JSON in the zip for easy reading
            json_content = json.dumps(content, indent=2, ensure_ascii=False)
            zipf.writestr(rel_path, json_content)


def load_zip_to_dict(zip_path: Path) -> Dict[str, Dict[str, Any]]:
    """Load a zip file contents into a dictionary.
    
    Args:
        zip_path: Path to zip file
        
    Returns:
        Dictionary mapping relative file paths to their contents
    """
    import json
    
    if not zip_path.exists():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")
    
    files_dict = {}
    
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for name in zipf.namelist():
            content = zipf.read(name).decode('utf-8')
            files_dict[name] = json.loads(content)
    
    return files_dict
