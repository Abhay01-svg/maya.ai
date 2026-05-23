import assistant.config as config
import os

class SystemPlugin:
    def __init__(self, assistant):
        self.assistant = assistant

    def _check_allowed(self):
        if not config.ALLOW_SYSTEM_COMMANDS:
            return False, "System commands are disabled in config for safety."
        return True, None

    def shutdown(self, args=""):
        ok, msg = self._check_allowed()
        if not ok:
            return msg
        # Require explicit confirmation/PIN in args
        if config.OWNER_PIN not in args:
            return "Owner PIN required to perform shutdown."
        # Perform shutdown (Windows)
        try:
            os.system("shutdown /s /t 1")
            return "Shutting down PC."
        except Exception as e:
            return f"Shutdown failed: {e}"

    def restart(self, args=""):
        ok, msg = self._check_allowed()
        if not ok:
            return msg
        if config.OWNER_PIN not in args:
            return "Owner PIN required to perform restart."
        try:
            os.system("shutdown /r /t 1")
            return "Restarting PC."
        except Exception as e:
            return f"Restart failed: {e}"

    def lock(self, args=""):
        ok, msg = self._check_allowed()
        if not ok:
            return msg
        try:
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            return "Locked PC."
        except Exception as e:
            return f"Lock failed: {e}"


def get_plugin(assistant):
    return SystemPlugin(assistant)
