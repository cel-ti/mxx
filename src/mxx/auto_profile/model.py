

import os
from pydantic import BaseModel

from mxx.utils.kill import kill_processes_by_path
from mxx.utils.subprocess import launch_detached
from mxx.plugin_system.loader import mxx_plugin_loader

class MxxAutoProfile(BaseModel):
    maa : str
    ld : int = None
    waitTime : int = 15
    lifetime : int = 2400

    model_config = {
        "extra": "allow",
    }

    def start(self):
        """starts the auto"""
        # resolve
        from ..maaconfig.mgr import mxxmaa
        if self.maa not in mxxmaa.profiles:
            print(f"MAA app '{self.maa}' not found in configuration.")
            return

        if mxx_plugin_loader.canRunProfile(self) is False:
            print(f"Profile '{self.maa}' run prevented by plugin.")
            return

        mxx_plugin_loader.preProfileStart(self)
        # ld
        mxx_plugin_loader.emit("pre_ld_start", self)

        if self.ld:
            try:
                os.system(f"ldpx console launch --index {self.ld}")
            except Exception as e:
                print(f"Error launching LD: {e}")

        # now wait for waitTime
        mxx_plugin_loader.emit("pre_wait_time", self)

        import time
        time.sleep(self.waitTime)

        # now start MAA
        mxx_plugin_loader.emit("pre_maa_launch", self)
        profile = mxxmaa.profiles[self.maa]
        launch_detached(profile.appPath)

        mxx_plugin_loader.postProfileStart(self)

    def kill(self):
        """kills the auto"""
        # kill MAA
        from ..maaconfig.mgr import mxxmaa
        if self.maa not in mxxmaa.profiles:
            print(f"MAA app '{self.maa}' not found in configuration.")
            return
        
        if mxx_plugin_loader.canKillProfile(self) is False:
            print(f"Profile '{self.maa}' kill prevented by plugin.")
            return

        mxx_plugin_loader.preProfileKill(self)

        mxx_plugin_loader.emit("pre_maa_kill", self)
        profile = mxxmaa.profiles[self.maa]
        # kill 
        kill_processes_by_path(profile.appPath)
        # kill LD if specified
        if self.ld:
            mxx_plugin_loader.emit("pre_ld_kill", self)
            try:
                os.system(f"ldpx console quit --index {self.ld}")
            except Exception as e:
                print(f"Error killing LD: {e}")
        mxx_plugin_loader.postProfileKill(self)

