"""Parser module for validating profiles before execution."""

from pathlib import Path
from typing import Optional
from mxx.models.profile import MxxProfile
from mxx.models.ld import LDModel
from mxx.models.maa import MaaModel


class ValidationError(Exception):
    """Raised when profile validation fails."""
    pass


def validate_ld_model(ld: LDModel) -> None:
    """Validate LD model configuration.
    
    Args:
        ld: LDModel instance to validate
        
    Raises:
        ValidationError: If validation fails
    """
    # LDModel already validates name XOR index in __post_init__
    # Just verify it exists
    if not ld:
        raise ValidationError("LD configuration is None")


def validate_maa_model(maa: MaaModel, skip_path_check: bool = False) -> None:
    """Validate MAA model configuration.
    
    Args:
        maa: MaaModel instance to validate
        skip_path_check: If True, skips filesystem path validation (useful for plugin-resolved paths)
        
    Raises:
        ValidationError: If validation fails
    """
    if not maa:
        raise ValidationError("MAA configuration is None")
    
    if not maa.path:
        raise ValidationError("MAA path cannot be empty")
    
    # Skip path validation for plugin-managed paths (like "scoop:app")
    if skip_path_check or (isinstance(maa.path, str) and maa.path.startswith("scoop")):
        # Only check that required fields are present
        if not maa.app:
            raise ValidationError("MAA app executable must be specified")
        return
    
    # Check if path exists
    path = Path(maa.path)
    if not path.exists():
        raise ValidationError(f"MAA path does not exist: {maa.path}")
    
    # Check if app is specified
    if not maa.app:
        raise ValidationError("MAA app executable must be specified")
    
    # Construct full app path
    app_path = path / maa.app
    if not app_path.exists():
        raise ValidationError(f"MAA app executable not found: {app_path}")
    
    # Validate config directory if specified
    if maa.configDir:
        config_path = path / maa.configDir
        if not config_path.exists():
            raise ValidationError(f"MAA config directory not found: {config_path}")


def validate_profile(profile: MxxProfile) -> None:
    """Validate a complete profile configuration.
    
    Args:
        profile: MxxProfile instance to validate
        
    Raises:
        ValidationError: If validation fails
    """
    if not profile:
        raise ValidationError("Profile is None")
    
    # At least one of ld or maa must be present
    if not profile.ld and not profile.maa:
        raise ValidationError("Profile must have at least LD or MAA configuration")
    
    # Validate lifetime if present
    if profile.lifetime is not None and profile.lifetime <= 0:
        raise ValidationError("Profile lifetime must be positive")
    
    # Validate waittime if present
    if profile.waittime is not None and profile.waittime < 0:
        raise ValidationError("Profile waittime cannot be negative")
    
    # Validate LD if present
    if profile.ld:
        validate_ld_model(profile.ld)
    
    # Validate MAA if present
    if profile.maa:
        validate_maa_model(profile.maa)


def get_maa_app_path(maa: MaaModel) -> Path:
    """Get the full path to the MAA application executable.
    
    Args:
        maa: MaaModel instance
        
    Returns:
        Full path to the MAA executable
    """
    return Path(maa.path) / maa.app


def get_maa_config_path(maa: MaaModel) -> Optional[Path]:
    """Get the full path to the MAA config directory.
    
    Args:
        maa: MaaModel instance
        
    Returns:
        Full path to config directory, or None if not specified
    """
    if not maa.configDir:
        return None
    return Path(maa.path) / maa.configDir
