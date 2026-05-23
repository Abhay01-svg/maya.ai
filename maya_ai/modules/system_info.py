"""
Maya AI System Info Module
Collects real-time device and location information for context-aware responses.
"""

import psutil
import platform
import socket
import requests
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class SystemInfo:
    """Collects real-time device and location information"""
    
    def __init__(self):
        self.os_info = f"{platform.system()} {platform.release()}"
        self.hostname = socket.gethostname()
        self.processor = platform.processor()
    
    def get_location_context(self) -> dict:
        """Get detailed location info via IP"""
        try:
            # Using ip-api.com for speed and reliability
            response = requests.get("http://ip-api.com/json/", timeout=3)
            if response.status_code == 200:
                data = response.json()
                return {
                    "city": data.get("city", "Unknown"),
                    "region": data.get("regionName", "Unknown"),
                    "country": data.get("country", "Unknown"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "isp": data.get("isp"),
                    "ip": data.get("query")
                }
        except Exception as e:
            logger.error(f"⚠️ Location detection error: {e}")
        return {"city": "Unknown", "country": "Unknown"}

    def get_device_stats(self) -> dict:
        """Get real-time hardware statistics"""
        try:
            battery = psutil.sensors_battery()
            battery_percent = battery.percent if battery else "N/A"
            is_plugged = battery.power_plugged if battery else "N/A"
            
            return {
                "cpu_usage": f"{psutil.cpu_percent()}%",
                "ram_usage": f"{psutil.virtual_memory().percent}%",
                "battery": f"{battery_percent}%",
                "power_status": "Plugged in" if is_plugged == True else "On Battery",
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"⚠️ Device stats error: {e}")
            return {}

    def get_full_context_string(self) -> str:
        """Return a formatted string for Llama context"""
        loc = self.get_location_context()
        dev = self.get_device_stats()
        
        context = f"[CONTEXT] User Location: {loc.get('city')}, {loc.get('country')}. "
        context += f"Device: {self.os_info}. CPU: {dev.get('cpu_usage')}, RAM: {dev.get('ram_usage')}, "
        context += f"Battery: {dev.get('battery')} ({dev.get('power_status')}). "
        context += f"Current Time: {datetime.now().strftime('%H:%M:%S')}."
        return context

# Singleton
system_info = SystemInfo()
