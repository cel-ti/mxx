import os
from pathlib import Path
from typing import Dict, Optional

from mxx.plugin_system.plugin import MxxPlugin
from mxx.maaconfig.model import MaaProfile

class ScoopPlugin(MxxPlugin):
    def loadMaaProfiles(self, mgr, ctx) -> Dict[str, MaaProfile]:
        """
        Iterates through existing profiles in the manager.
        If a profile's path starts with 'scoop', it resolves the path and updates the profile.
        """
        for name, profile in mgr.profiles.items():
            path_val = profile.path
            
            if path_val and isinstance(path_val, str) and path_val.startswith("scoop"):
                app_name = self._extract_app_name(path_val, name)
                resolved_path = self._resolve_scoop_path(app_name)
                
                if resolved_path:
                    print(f"ScoopPlugin: Resolving '{name}' path '{path_val}' -> '{resolved_path}'")
                    profile.path = str(resolved_path)
                else:
                    print(f"ScoopPlugin: Warning - Could not resolve scoop app '{app_name}' for profile '{name}'")
        
        return {}

    def _extract_app_name(self, path_val: str, profile_name: str) -> str:
        """Determine the app name from the path string or profile name."""
        if path_val == "scoop":
            return profile_name
        elif path_val.startswith("scoop:"):
            return path_val.split(":", 1)[1]
        return profile_name

    def _resolve_scoop_path(self, app_name: str) -> Optional[Path]:
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
