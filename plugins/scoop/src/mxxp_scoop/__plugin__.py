import os
from pathlib import Path
from typing import Dict, Any

from mxx.plugin_system.plugin import MxxPlugin
from mxx.models.profile import MxxProfile

class ScoopPlugin(MxxPlugin):
    """Plugin to resolve MAA paths starting with 'scoop' to actual Scoop installation paths.
    
    Examples:
        - directory = "scoop" → resolves using profile name as app name
        - directory = "scoop:maa-beta" → resolves to maa-beta's installation
    """
    
    def pre_profile_start(self, profile: MxxProfile, ctx: Dict[str, Any]) -> None:
        """Resolve scoop paths before profile starts."""
        if profile.maa and profile.maa.path:
            path = profile.maa.path
            
            if isinstance(path, str) and path.startswith("scoop"):
                # Extract app name from "scoop" or "scoop:app_name"
                if path == "scoop":
                    # Use profile name as app name
                    app_name = getattr(profile, 'name', 'maa')
                elif path.startswith("scoop:"):
                    # Use specified app name
                    app_name = path.split(":", 1)[1]
                else:
                    app_name = "maa"
                
                resolved_path = self._resolve_scoop_path(app_name)
                
                if resolved_path:
                    print(f"ScoopPlugin: Resolved '{path}' -> '{resolved_path}'")
                    profile.maa.path = str(resolved_path)
                else:
                    print(f"ScoopPlugin: Warning - Could not resolve scoop app '{app_name}'")

    def _resolve_scoop_path(self, app_name: str) -> Path | None:
        """Find the installation path for a Scoop app."""
        # 1. Try SCOOP environment variable
        scoop_root = os.environ.get("SCOOP")
        if scoop_root:
            app_path = Path(scoop_root) / "apps" / app_name / "current"
            if app_path.exists():
                return app_path
        
        # 2. Try default user scoop directory (~/scoop)
        user_scoop = Path.home() / "scoop" / "apps" / app_name / "current"
        if user_scoop.exists():
            return user_scoop
            
        # 3. Try global scoop directory (ProgramData/scoop)
        program_data = os.environ.get("ProgramData", "C:\\ProgramData")
        global_scoop = Path(program_data) / "scoop" / "apps" / app_name / "current"
        if global_scoop.exists():
            return global_scoop
            
        # 4. Try SCOOP_GLOBAL environment variable
        scoop_global = os.environ.get("SCOOP_GLOBAL")
        if scoop_global:
            global_path = Path(scoop_global) / "apps" / app_name / "current"
            if global_path.exists():
                return global_path

        return None

plugin = ScoopPlugin()
