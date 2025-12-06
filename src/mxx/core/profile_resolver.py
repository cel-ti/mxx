"""Profile resolution utilities."""

from typing import Optional, Any

from mxx.core.model_load import load_model, get_all_files
from mxx.plugin_system import PluginLoader
from mxx.models.profile import MxxProfile
from mxx.models.ld import LDModel
from mxx.models.maa import MaaModel


def get_model_type(model: Any) -> str:
    """Determine model type from instance.
    
    Args:
        model: Model instance
        
    Returns:
        Model type: "LD", "MAA", or "PROFILE"
    """
    if isinstance(model, LDModel):
        return "LD"
    elif isinstance(model, MaaModel):
        return "MAA"
    else:
        return "PROFILE"


def get_type_from_name(name: str) -> str:
    """Determine model type from filename.
    
    Args:
        name: File stem (e.g., "profile.ld", "profile.maa", "profile")
        
    Returns:
        Model type: "LD", "MAA", or "PROFILE"
    """
    if ".ld" in name:
        return "LD"
    elif ".maa" in name:
        return "MAA"
    else:
        return "PROFILE"


def is_profile_part(name: str) -> bool:
    """Check if name represents a model part (not full profile).
    
    Args:
        name: Model name
        
    Returns:
        True if it's a part (.ld or .maa), False otherwise
    """
    return '.' in name


class ProfileResolver:
    """Resolves profiles from files or plugins."""
    
    def __init__(self):
        """Initialize resolver with plugin loader."""
        self._plugin_loader = PluginLoader()
        self._plugin_profiles = None
    
    @property
    def plugin_profiles(self):
        """Lazy load plugin profiles."""
        if self._plugin_profiles is None:
            self._plugin_profiles = self._plugin_loader.load_plugin_profiles()
        return self._plugin_profiles
    
    def get_profile(self, name: str) -> tuple[MxxProfile, bool]:
        """Get profile by name from plugins or files.
        
        Supports name formats:
        - "profile_name" -> loads profile_name.toml as MxxProfile
        - "profile_name.ld" -> loads profile_name.ld.toml as LDModel
        - "profile_name.maa" -> loads profile_name.maa.toml as MaaModel
        
        Args:
            name: Profile name (with optional .ld or .maa suffix)
            
        Returns:
            Tuple of (profile/model, is_plugin)
            
        Raises:
            FileNotFoundError: If profile not found
        """
        # Check plugin profiles first (only for full profiles, not parts)
        if '.' not in name and name in self.plugin_profiles:
            return self.plugin_profiles[name], True
        
        # Check file-based profiles/models
        profile = load_model(name)
        if profile is None:
            raise FileNotFoundError(f"Profile '{name}' not found")
        
        return profile, False
    
    def get_plugin_items(self) -> dict[str, tuple[Any, bool, Optional[Exception]]]:
        """Get all plugin-provided items.
        
        Returns:
            Dictionary mapping name to (model, is_plugin=True, error)
        """
        results = {}
        for name, profile in self.plugin_profiles.items():
            results[name] = (profile, True, None)
        return results
    
    def get_file_items(self) -> dict[str, tuple[Optional[Any], bool, Optional[Exception]]]:
        """Get all file-based items.
        
        Returns:
            Dictionary mapping name to (model, is_plugin=False, error)
        """
        results = {}
        for file, stem, part in get_all_files():
            try:
                model = load_model(stem)
                results[stem] = (model, False, None)
            except Exception as e:
                results[stem] = (None, False, e)
        return results
    
    def list_all_profiles(self) -> dict[str, tuple[Optional[MxxProfile], bool, Optional[Exception]]]:
        """List all profiles and model parts with their status.
        
        Lists:
        - Full profiles (xxx.toml)
        - LD parts (xxx.ld.toml)
        - MAA parts (xxx.maa.toml)
        
        Returns:
            Dictionary mapping name to (model, is_plugin, error)
        """
        results = {}
        results.update(self.get_plugin_items())
        results.update(self.get_file_items())
        return results
    
    @property
    def plugin_loader(self):
        """Get the plugin loader instance."""
        return self._plugin_loader


# Global resolver instance
profile_resolver = ProfileResolver()
