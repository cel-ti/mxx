
from pydantic import BaseModel, Field, field_validator
from typing import Tuple, Any
from pathlib import Path
import copy


class MaaConfig(BaseModel):
    exclude : list[str] = Field(default_factory=list)
    overwrite : dict[str, Any] = Field(default_factory=dict)
    includeFiles : list[str] = Field(default_factory=list)
    excludeFiles : list[str] = Field(default_factory=list)


class MaaProfile(BaseModel):
    path : str
    app : str
    configFolder : str = "config"
    config : MaaConfig = Field(default_factory=MaaConfig)
    

    @field_validator('path')
    @classmethod
    def validate_path_exists(cls, v: str) -> str:
        """Validate that the path exists (supports symlinks)."""
        if not v:
            raise ValueError("Path cannot be empty")
        
        path = Path(v)
        
        # Check if path exists (follows symlinks to check target exists)
        if not path.exists():
            raise ValueError(f"Path does not exist: {v}")
        
        # Return the original path as-is (preserves symlinks)
        return v

    def _parse_exclude_string(self, exclude_str: str) -> Tuple[str, str]:
        """Parse exclude string like 'config.toml/key1..key2..key3' into filename and key path.
        
        Rules:
        - Single dot (.) in a key is treated as literal dot character
        - Double dot (..) is the separator between nested keys
        
        Examples:
        - "config.toml/some.key" -> filename="config.toml", key="some.key" (literal dot)
        - "config.toml/some..key..name" -> filename="config.toml", key="some/key/name" (nested)
        
        Args:
            exclude_str: String in format "filename/key.path" or "filename/key..path"
            
        Returns:
            Tuple of (filename, key_path) where key_path uses '/' separators
        """
        if '/' not in exclude_str:
            raise ValueError(f"Invalid exclude format: {exclude_str}")
        
        filename, key_path = exclude_str.split('/', 1)
        # Convert double-dot (..) to slash (/) for nested keys
        # Single dots (.) remain as literal dots in key names
        key_path = key_path.replace('..', '/')
        return filename, key_path

    def _get_config_path(self, filename: str) -> Path:
        """Get the full path to a config file.
        
        Args:
            filename: Config filename (e.g., "config.toml")
            
        Returns:
            Path to the config file in the profile's config folder
        """
        return Path(self.path) / self.configFolder / filename

    def _filter_by_exclude(self, data: dict, exclude_str: str) -> dict:
        """Filter a dict by removing the path specified in a single exclude string.
        
        Args:
            data: Dictionary to filter
            exclude_str: Single exclude pattern like "config.toml/key1.key2.key3"
            
        Returns:
            Filtered copy of the dict with excluded path removed
        """
        from mxx.utils.nested import nested_remove
        
        try:
            filename, key_path = self._parse_exclude_string(exclude_str)
            
            # Make a copy and remove the excluded key
            result = copy.deepcopy(data)
            nested_remove(result, key_path)
            return result
            
        except ValueError:
            # Invalid format, return data unchanged
            return data

    def _filter_dict(self, data: dict, filename: str) -> dict:
        """Apply all exclude filters to a dictionary for a specific config file.
        
        Supports wildcard patterns in key paths using * and ? wildcards.
        
        Args:
            data: Dictionary to filter
            filename: Config filename to match against (e.g., "config.toml")
            
        Returns:
            Filtered copy of the dict with all excluded paths removed
        """
        from mxx.utils.nested import nested_remove
        
        result = copy.deepcopy(data)
        
        for exclude_str in self.config.exclude:
            try:
                excl_filename, key_path = self._parse_exclude_string(exclude_str)
                
                # Only apply if the filename matches
                if excl_filename != filename:
                    continue
                
                # Check if pattern contains wildcards
                if '*' in key_path or '?' in key_path or '[' in key_path:
                    # Pattern matching - remove all keys that match
                    self._remove_matching_keys(result, key_path)
                else:
                    # Exact match - remove specific key
                    nested_remove(result, key_path)
                    
            except ValueError:
                # Skip invalid exclude patterns
                continue
        
        return result

    def _remove_matching_keys(self, data: dict, pattern: str) -> None:
        """Remove all keys matching a wildcard pattern from nested dict.
        
        Args:
            data: Dictionary to modify in-place
            pattern: Key path pattern with wildcards (e.g., "level1/wxx*/set*")
        """
        from mxx.utils.pattern import matches_pattern
        
        # Split pattern into parts
        parts = pattern.split('/')
        
        def remove_recursive(current: dict, parts_list: list, current_path: str = ""):
            if not parts_list:
                return
            
            pattern_part = parts_list[0]
            remaining_parts = parts_list[1:]
            
            # Get keys that match current pattern part
            keys_to_process = []
            for key in list(current.keys()):
                if matches_pattern(key, pattern_part):
                    keys_to_process.append(key)
            
            for key in keys_to_process:
                key_path = f"{current_path}/{key}" if current_path else key
                
                if not remaining_parts:
                    # Last part of pattern - remove the key
                    if key in current:
                        del current[key]
                elif isinstance(current.get(key), dict):
                    # More parts to match - recurse into nested dict
                    remove_recursive(current[key], remaining_parts, key_path)
        
        remove_recursive(data, parts)

    def _apply_overwrite(self, data: dict, filename: str) -> dict:
        """Apply overwrite configuration to a dictionary for a specific config file.
        
        Args:
            data: Dictionary to apply overwrites to
            filename: Config filename to match against (e.g., "config.toml")
            
        Returns:
            New dict with overwrites applied
        """
        from mxx.utils.nested import nested_set
        
        result = copy.deepcopy(data)
        
        for overwrite_path, value in self.config.overwrite.items():
            try:
                ovr_filename, key_path = self._parse_exclude_string(overwrite_path)
                
                # Only apply if the filename matches
                if ovr_filename == filename:
                    nested_set(result, key_path, value)
                    
            except ValueError:
                # Skip invalid overwrite patterns
                continue
        
        return result

    def backup(self, path: str) -> None:
        """Backup application configuration to a zip file.
        
        Reads all files from configFolder, applies include/exclude file filters,
        applies exclude field filters, and saves to a zip file.
        
        Args:
            path: Target zip file path
        """
        from mxx.utils.file import filter_files, load_config_file, create_zip_from_dict
        
        config_dir = Path(self.path) / self.configFolder
        zip_path = Path(path)
        
        # Filter files based on include/exclude patterns
        files = filter_files(
            config_dir,
            include_patterns=self.config.includeFiles if self.config.includeFiles else None,
            exclude_patterns=self.config.excludeFiles if self.config.excludeFiles else None
        )
        
        # Load and filter each file
        files_dict = {}
        for file_path in files:
            try:
                # Load the file
                data = load_config_file(file_path)
                
                # Apply exclude filters for this specific file
                filename = file_path.name
                filtered_data = self._filter_dict(data, filename)
                
                # Store with relative path as key
                rel_path = file_path.relative_to(config_dir)
                files_dict[str(rel_path)] = filtered_data
                
            except Exception as e:
                # Skip files that can't be loaded
                print(f"Warning: Failed to load {file_path}: {e}")
                continue
        
        # Create zip file
        create_zip_from_dict(zip_path, files_dict)

    def restore(self, source: str) -> None:
        """Restore application configuration from a zip file.
        
        Loads the zip file, reads current config exclude fields,
        applies excludes to loaded files, applies overwrites, and writes to configFolder.
        
        Args:
            source: Source zip file path
        """
        from mxx.utils.file import load_zip_to_dict, save_config_file
        
        config_dir = Path(self.path) / self.configFolder
        zip_path = Path(source)
        
        # Load zip contents
        files_dict = load_zip_to_dict(zip_path)
        
        # Process each file
        for rel_path, data in files_dict.items():
            try:
                # Get filename for filtering
                filename = Path(rel_path).name
                
                # Apply exclude filters
                filtered_data = self._filter_dict(data, filename)
                
                # Apply overwrites
                final_data = self._apply_overwrite(filtered_data, filename)
                
                # Determine output path
                output_path = config_dir / rel_path
                
                # Save the file
                save_config_file(output_path, final_data)
                
            except Exception as e:
                # Skip files that can't be processed
                print(f"Warning: Failed to restore {rel_path}: {e}")
                continue

    @property
    def appPath(self) -> Path:
        """Get the Path object for the application path."""
        return Path(self.path) / self.app