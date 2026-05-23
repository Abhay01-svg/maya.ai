"""
Maya AI PC Control Module
Full Windows PC control via commands
Uses: pyautogui, psutil, subprocess, keyboard, mouse
"""

import os
import sys
import subprocess
import logging
import psutil
import pyautogui
import keyboard
import mouse
from datetime import datetime
from pathlib import Path
from config import DEBUG_MODE

logger = logging.getLogger(__name__)

class PCControl:
    """Windows PC control system"""
    
    def __init__(self):
        self.common_apps = {
            "chrome": "chrome",
            "firefox": "firefox",
            "edge": "msedge",
            "vs code": "code",
            "notepad": "notepad",
            "calculator": "calc",
            "paint": "mspaint",
            "explorer": "explorer",
            "cmd": "cmd",
            "powershell": "powershell",
            "task manager": "taskmgr",
            "word": "winword",
            "excel": "excel",
            "vlc": "vlc",
            "teams": "teams",
            "discord": "discord"
        }
    
    # ==================== APPLICATION CONTROL ====================
    
    def open_app(self, app_name: str) -> dict:
        """Open application"""
        result = {
            "success": False,
            "message": None,
            "hinglish": None
        }
        
        try:
            app_lower = app_name.lower().strip()
            
            # Check common apps
            if app_lower in self.common_apps:
                exe = self.common_apps[app_lower]
            else:
                exe = app_lower
            
            # Try to launch
            subprocess.Popen(exe)
            result["success"] = True
            result["message"] = f"Opening {app_name}"
            result["hinglish"] = f"✅ {app_name} khol diya"
            
            logger.info(f"✅ Opened: {app_name}")
            
        except Exception as e:
            result["message"] = f"❌ Cannot open {app_name}: {str(e)}"
            result["hinglish"] = f"❌ {app_name} nahi khuل sakta: {str(e)}"
            logger.error(f"❌ Error opening app: {e}")
        
        return result
    
    def close_app(self, app_name: str) -> dict:
        """Close application"""
        result = {
            "success": False,
            "message": None,
            "hinglish": None
        }
        
        try:
            app_lower = app_name.lower().strip()
            
            # Find and kill process
            for proc in psutil.process_iter(['pid', 'name']):
                if app_lower in proc.info['name'].lower():
                    proc.kill()
                    result["success"] = True
                    result["message"] = f"Closed {app_name}"
                    result["hinglish"] = f"✅ {app_name} band kar diya"
                    logger.info(f"✅ Closed: {app_name}")
                    return result
            
            result["message"] = f"⚠️  {app_name} running nahi hai"
            result["hinglish"] = f"⚠️  {app_name} chal nahi raha"
            
        except Exception as e:
            result["message"] = f"❌ Error: {str(e)}"
            result["hinglish"] = f"❌ Kuch galat huva: {str(e)}"
            logger.error(f"❌ Error closing app: {e}")
        
        return result
    
    def list_running_apps(self, limit: int = 10) -> list:
        """List running applications"""
        try:
            apps = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                if proc.info['memory_percent'] > 0.1:  # More than 0.1%
                    apps.append({
                        "name": proc.info['name'],
                        "pid": proc.info['pid'],
                        "memory": proc.info['memory_percent']
                    })
            
            # Sort by memory usage
            apps.sort(key=lambda x: x['memory'], reverse=True)
            return apps[:limit]
        except Exception as e:
            logger.error(f"❌ Error listing apps: {e}")
            return []
    
    # ==================== SYSTEM CONTROL ====================
    
    def shutdown(self, delay: int = 0) -> dict:
        """Shutdown PC"""
        result = {
            "success": False,
            "message": None,
            "hinglish": None
        }
        
        try:
            if delay > 0:
                cmd = f"shutdown /s /t {delay}"
            else:
                cmd = "shutdown /s /t 0"
            
            os.system(cmd)
            result["success"] = True
            result["message"] = f"Shutting down in {delay} seconds"
            result["hinglish"] = f"✅ PC {delay} seconds mein band ho jayega"
            
        except Exception as e:
            result["message"] = str(e)
            result["hinglish"] = f"❌ Error: {str(e)}"
        
        return result
    
    def restart(self, delay: int = 0) -> dict:
        """Restart PC"""
        result = {
            "success": False,
            "message": None,
            "hinglish": None
        }
        
        try:
            if delay > 0:
                cmd = f"shutdown /r /t {delay}"
            else:
                cmd = "shutdown /r /t 0"
            
            os.system(cmd)
            result["success"] = True
            result["message"] = f"Restarting in {delay} seconds"
            result["hinglish"] = f"✅ PC {delay} seconds mein restart hoga"
            
        except Exception as e:
            result["message"] = str(e)
            result["hinglish"] = f"❌ Error: {str(e)}"
        
        return result
    
    def sleep_mode(self) -> dict:
        """Sleep mode"""
        result = {
            "success": False,
            "message": None,
            "hinglish": None
        }
        
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            result["success"] = True
            result["message"] = "PC is sleeping"
            result["hinglish"] = "✅ PC sone gaya"
            
        except Exception as e:
            result["message"] = str(e)
            result["hinglish"] = f"❌ Error: {str(e)}"
        
        return result
    
    def lock_pc(self) -> dict:
        """Lock PC"""
        result = {
            "success": False,
            "message": None,
            "hinglish": None
        }
        
        try:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            result["success"] = True
            result["message"] = "PC locked"
            result["hinglish"] = "✅ PC lock ho gaya"
            
        except Exception as e:
            result["message"] = str(e)
            result["hinglish"] = f"❌ Error: {str(e)}"
        
        return result
    
    # ==================== AUDIO CONTROL ====================
    
    def set_volume(self, level: int) -> dict:
        """Set volume level (0-100)"""
        result = {
            "success": False,
            "message": None,
            "hinglish": None
        }
        
        try:
            level = max(0, min(100, level))
            # Windows volume control via WMI
            os.system(f'powershell -Command "Add-Type -ComObject WScript.Shell; $shell = New-Object -ComObject WScript.Shell; $shell.SendKeys([char]174) * {level // 5}"')
            
            result["success"] = True
            result["message"] = f"Volume set to {level}%"
            result["hinglish"] = f"✅ Volume {level}% kar diya"
            
        except Exception as e:
            result["message"] = str(e)
            result["hinglish"] = f"❌ Error: {str(e)}"
        
        return result
    
    def mute(self) -> dict:
        """Mute audio"""
        result = {
            "success": False,
            "message": None,
            "hinglish": None
        }
        
        try:
            # Windows mute shortcut
            pyautogui.press('volumemute')
            result["success"] = True
            result["message"] = "Audio muted"
            result["hinglish"] = "✅ Sound mute ho gaya"
            
        except Exception as e:
            result["message"] = str(e)
            result["hinglish"] = f"❌ Error: {str(e)}"
        
        return result
    
    def unmute(self) -> dict:
        """Unmute audio"""
        result = {
            "success": False,
            "message": None,
            "hinglish": None
        }
        
        try:
            pyautogui.press('volumemute')
            result["success"] = True
            result["message"] = "Audio unmuted"
            result["hinglish"] = "✅ Sound unmute ho gaya"
            
        except Exception as e:
            result["message"] = str(e)
            result["hinglish"] = f"❌ Error: {str(e)}"
        
        return result
    
    # ==================== DISPLAY CONTROL ====================
    
    def screenshot(self, filename: str = None) -> dict:
        """Take screenshot"""
        result = {
            "success": False,
            "message": None,
            "hinglish": None,
            "filepath": None
        }
        
        try:
            if not filename:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            filepath = Path("./screenshots") / filename
            filepath.parent.mkdir(exist_ok=True)
            
            img = pyautogui.screenshot()
            img.save(str(filepath))
            
            result["success"] = True
            result["message"] = f"Screenshot saved: {filepath}"
            result["hinglish"] = f"✅ Screenshot save ho gaya: {filename}"
            result["filepath"] = str(filepath)
            
        except Exception as e:
            result["message"] = str(e)
            result["hinglish"] = f"❌ Screenshot error: {str(e)}"
        
        return result
    
    # ==================== FILE OPERATIONS ====================
    
    def create_folder(self, folder_path: str) -> dict:
        """Create folder"""
        result = {
            "success": False,
            "message": None,
            "hinglish": None
        }
        
        try:
            Path(folder_path).mkdir(parents=True, exist_ok=True)
            result["success"] = True
            result["message"] = f"Folder created: {folder_path}"
            result["hinglish"] = f"✅ Folder bana diya: {folder_path}"
            
        except Exception as e:
            result["message"] = str(e)
            result["hinglish"] = f"❌ Error: {str(e)}"
        
        return result
    
    def delete_file(self, file_path: str) -> dict:
        """Delete file"""
        result = {
            "success": False,
            "message": None,
            "hinglish": None
        }
        
        try:
            file = Path(file_path)
            if file.exists():
                file.unlink()
                result["success"] = True
                result["message"] = f"File deleted: {file_path}"
                result["hinglish"] = f"✅ File delete ho gaya"
            else:
                result["message"] = f"File not found: {file_path}"
                result["hinglish"] = f"❌ File nahi mila"
            
        except Exception as e:
            result["message"] = str(e)
            result["hinglish"] = f"❌ Error: {str(e)}"
        
        return result
    
    def rename_file(self, old_path: str, new_path: str) -> dict:
        """Rename file"""
        result = {
            "success": False,
            "message": None,
            "hinglish": None
        }
        
        try:
            old_file = Path(old_path)
            new_file = Path(new_path)
            
            if old_file.exists():
                old_file.rename(new_file)
                result["success"] = True
                result["message"] = f"Renamed: {old_path} -> {new_path}"
                result["hinglish"] = f"✅ File rename ho gaya"
            else:
                result["message"] = f"File not found"
                result["hinglish"] = f"❌ File nahi mila"
            
        except Exception as e:
            result["message"] = str(e)
            result["hinglish"] = f"❌ Error: {str(e)}"
        
        return result
    
    def open_file_explorer(self, path: str = ".") -> dict:
        """Open file explorer"""
        result = {
            "success": False,
            "message": None,
            "hinglish": None
        }
        
        try:
            os.startfile(path)
            result["success"] = True
            result["message"] = f"Explorer opened: {path}"
            result["hinglish"] = f"✅ File explorer khul gaya"
            
        except Exception as e:
            result["message"] = str(e)
            result["hinglish"] = f"❌ Error: {str(e)}"
        
        return result
    
    # ==================== MOUSE & KEYBOARD ====================
    
    def mouse_move(self, x: int, y: int) -> dict:
        """Move mouse"""
        try:
            pyautogui.moveTo(x, y, duration=0.5)
            return {
                "success": True,
                "message": f"Mouse moved to ({x}, {y})",
                "hinglish": f"✅ Mouse move ho gaya"
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "hinglish": f"❌ Error: {str(e)}"
            }
    
    def mouse_click(self, x: int = None, y: int = None, button: str = "left") -> dict:
        """Click mouse"""
        try:
            if x and y:
                pyautogui.click(x, y, button=button)
            else:
                pyautogui.click(button=button)
            
            return {
                "success": True,
                "message": f"Clicked {button} button",
                "hinglish": f"✅ Click kar diya"
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "hinglish": f"❌ Error: {str(e)}"
            }
    
    def type_text(self, text: str) -> dict:
        """Type text"""
        try:
            pyautogui.typewrite(text, interval=0.05)
            return {
                "success": True,
                "message": f"Typed: {text}",
                "hinglish": f"✅ Type kar diya"
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "hinglish": f"❌ Error: {str(e)}"
            }
    
    # ==================== SYSTEM INFO ====================
    
    def get_system_stats(self) -> dict:
        """Get PC system statistics"""
        try:
            stats = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "running_processes": len(psutil.pids())
            }
            return stats
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return None
    
    def get_system_info_hinglish(self) -> str:
        """Get system info in Hinglish"""
        try:
            stats = self.get_system_stats()
            if stats:
                return f"""
💻 PC Status:
  🔥 CPU: {stats['cpu_percent']}%
  🧠 Memory: {stats['memory_percent']}%
  💾 Disk: {stats['disk_percent']}%
  ⚙️  Processes: {stats['running_processes']}
                """
            return "❌ Cannot get system info"
        except Exception as e:
            return f"❌ Error: {str(e)}"

# Singleton
pc_control = PCControl()

if DEBUG_MODE:
    print("🖥️  Maya PC Control initialized")
