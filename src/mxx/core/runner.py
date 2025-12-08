"""Runner module for starting and stopping profiles."""

import os
import time
from typing import Optional, Dict, Any
from mxx.models.profile import MxxProfile
from mxx.core.parser import validate_profile, get_maa_app_path
from mxx.utils.kill import kill_processes_by_path


class ProfileRunner:
    """Manages profile execution with plugin hook support."""
    
    def __init__(self, plugin_loader: Optional[Any] = None):
        """Initialize the runner.
        
        Args:
            plugin_loader: Optional plugin loader instance
        """
        self.runtime: Dict[str, Any] = {}
        self._plugin_loader: Optional[Any] = plugin_loader
    
    def set_plugin_loader(self, loader: Any) -> None:
        """Set the plugin loader for hook support.
        
        Args:
            loader: Plugin loader instance
        """
        self._plugin_loader = loader
    
    def set_runtime(self, runtime: Dict[str, Any]) -> None:
        """Set runtime variables.
        
        Args:
            runtime: Dictionary of runtime variables
        """
        self.runtime.update(runtime)
    
    def _emit(self, hook_name: str, *args, **kwargs) -> None:
        """Emit a plugin hook event.
        
        Args:
            hook_name: Name of the hook to emit
            *args: Positional arguments for the hook
            **kwargs: Keyword arguments for the hook
        """
        if self._plugin_loader:
            self._plugin_loader.emit(hook_name, *args, **kwargs)
    
    def _can_run_profile(self, profile: MxxProfile) -> bool:
        """Check if profile can run via plugin hooks.
        
        Args:
            profile: Profile to check
            
        Returns:
            True if profile can run, False otherwise
        """
        if self._plugin_loader:
            return self._plugin_loader.can_run_profile(profile, self.runtime)
        return True
    
    def _can_kill_profile(self, profile: MxxProfile) -> bool:
        """Check if profile can be killed via plugin hooks.
        
        Args:
            profile: Profile to check
            
        Returns:
            True if profile can be killed, False otherwise
        """
        if self._plugin_loader:
            return self._plugin_loader.can_kill_profile(profile, self.runtime)
        return True
    
    def start_profile(
        self,
        profile: MxxProfile,
        wait_time: int = 15,
        validate: bool = True
    ) -> bool:
        """Start a profile (launch LD player and/or MAA).
        
        Args:
            profile: Profile to start
            wait_time: Seconds to wait between LD launch and MAA launch
            validate: Whether to validate profile before starting
            
        Returns:
            True if started successfully, False otherwise
        """
        try:
            # Validate profile
            if validate:
                validate_profile(profile)
            
            # Check if plugins allow running
            if not self._can_run_profile(profile):
                print("Profile run prevented by plugin.")
                return False
            
            # Pre-start hook
            if self._plugin_loader:
                self._plugin_loader.pre_profile_start(profile, self.runtime)
            
            # Start LD if configured
            if profile.ld:
                self._emit("pre_ld_start", profile)
                self._start_ld(profile.ld)
            
            # Wait if both LD and MAA are configured
            if profile.ld and profile.maa:
                self._emit("pre_wait_time", profile)
                time.sleep(wait_time)
            
            # Start MAA if configured
            if profile.maa:
                self._emit("pre_maa_launch", profile)
                self._start_maa(profile.maa)
            
            # Post-start hook
            if self._plugin_loader:
                self._plugin_loader.post_profile_start(profile, self.runtime)
            
            return True
            
        except Exception as e:
            print(f"Error starting profile: {e}")
            return False
    
    def notify_profile_failure(self, profile: MxxProfile) -> None:
        """Notify plugins that a profile has failed during lifetime.
        
        This is called when a profile fails after start_profile() has succeeded
        but during the lifetime wait period.
        
        Args:
            profile: The profile that failed
        """
        if self._plugin_loader:
            self._plugin_loader.post_profile_start(profile, self.runtime)
    
    def _start_ld(self, ld) -> None:
        """Start LD player.
        
        Args:
            ld: LDModel instance
        """
        try:
            if ld.index is not None:
                os.system(f"ldpx console launch --index {ld.index}")
            elif ld.name:
                os.system(f"ldpx console launch --name {ld.name}")
        except Exception as e:
            print(f"Error launching LD: {e}")
            raise
    
    def _start_maa(self, maa) -> None:
        """Start MAA application.
        
        Args:
            maa: MaaModel instance
        """
        from mxx.utils.nofuss.subprocess import launch_detached
        
        app_path = get_maa_app_path(maa)
        launch_detached([str(app_path)])
    
    def kill_profile(self, profile: MxxProfile) -> bool:
        """Kill a running profile (stop MAA and/or LD).
        
        Args:
            profile: Profile to kill
            
        Returns:
            True if killed successfully, False otherwise
        """
        try:
            # Check if plugins allow killing
            if not self._can_kill_profile(profile):
                print("Profile kill prevented by plugin.")
                return False
            
            # Pre-kill hook
            if self._plugin_loader:
                self._plugin_loader.pre_profile_kill(profile, self.runtime)
            
            # Kill MAA if configured
            if profile.maa:
                self._emit("pre_maa_kill", profile)
                self._kill_maa(profile.maa)
            
            # Kill LD if configured
            if profile.ld:
                self._emit("pre_ld_kill", profile)
                self._kill_ld(profile.ld)
            
            # Post-kill hook
            if self._plugin_loader:
                self._plugin_loader.post_profile_kill(profile, self.runtime)
            
            return True
            
        except Exception as e:
            print(f"Error killing profile: {e}")
            return False
    
    def _kill_maa(self, maa) -> None:
        """Kill MAA application.
        
        Args:
            maa: MaaModel instance
        """
        app_path = get_maa_app_path(maa)
        kill_processes_by_path(str(app_path))
    
    def _kill_ld(self, ld) -> None:
        """Kill LD player.
        
        Args:
            ld: LDModel instance
        """
        try:
            if ld.index is not None:
                os.system(f"ldpx console quit --index {ld.index}")
            elif ld.name:
                os.system(f"ldpx console quit --name {ld.name}")
        except Exception as e:
            print(f"Error quitting LD: {e}")


# Global runner instance
runner = ProfileRunner()
