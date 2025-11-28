import ctypes
from ctypes import wintypes
from mxx.plugin_system.plugin import MxxPlugin

class CheckFreePlugin(MxxPlugin):
    def canRunProfile(self, profile, ctx) -> bool:
        if "x" in ctx:
            return True  # Bypass checks in test mode

        # Check for fullscreen applications
        if self._is_fullscreen_app_running():
            print("CheckFree: Fullscreen app detected, preventing profile run.")
            return False

        # Check if user is very active (e.g. >10 clicks in 10 seconds)
        if self._is_user_very_active(threshold_clicks=10, duration_seconds=10):
            print("CheckFree: User is very active, preventing profile run.")
            return False
            
        return True

    def _is_user_very_active(self, threshold_clicks=10, duration_seconds=10) -> bool:
        """Monitor mouse clicks for a duration to see if activity exceeds threshold."""
        import time
        
        start_time = time.time()
        clicks = 0
        # Track previous state of buttons (Left=0x01, Right=0x02)
        was_down = {0x01: False, 0x02: False}
        
        print(f"CheckFree: Monitoring user activity for {duration_seconds}s...")
        
        while (time.time() - start_time) < duration_seconds:
            for btn in [0x01, 0x02]:
                # Check if key is currently down (MSB set)
                is_down = (ctypes.windll.user32.GetAsyncKeyState(btn) & 0x8000) != 0
                
                if is_down and not was_down[btn]:
                    clicks += 1
                
                was_down[btn] = is_down
            
            if clicks >= threshold_clicks:
                return True
            
            time.sleep(0.05)
            
        return False

    def _is_fullscreen_app_running(self) -> bool:
        """Check if the foreground window is fullscreen."""
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return False
            
            # Get screen size
            screen_w = user32.GetSystemMetrics(0) # SM_CXSCREEN
            screen_h = user32.GetSystemMetrics(1) # SM_CYSCREEN
            
            # Get window rect
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            
            # Check if window covers the whole screen
            # Note: This is a basic check. Multi-monitor setups might need more complex logic,
            # but this covers the primary monitor case requested.
            return (rect.left <= 0 and rect.top <= 0 and 
                    rect.right >= screen_w and rect.bottom >= screen_h)
        except Exception:
            return False

plugin = CheckFreePlugin()
