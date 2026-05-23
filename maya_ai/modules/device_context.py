"""
Maya AI Device Context Collector
Gathers local device information for context-aware NLP processing
"""

import logging
import platform
import socket
import subprocess
import re
from datetime import datetime
from pathlib import Path
from config import DEBUG_MODE

logger = logging.getLogger(__name__)

class DeviceContextCollector:
    """Collects local device context for smart automation"""
    
    def __init__(self):
        self.context_cache = {}
        self.last_cache_update = None
        self.cache_duration = 300  # 5 minutes cache
    
    def get_device_context(self, force_refresh=False) -> dict:
        """Get complete device context"""
        current_time = datetime.now()
        
        # Check if cache is valid
        if (not force_refresh and 
            self.last_cache_update and 
            (current_time - self.last_cache_update).seconds < self.cache_duration):
            return self.context_cache
        
        # Collect fresh context
        context = {
            'location': self._get_location(),
            'camera': self._get_camera_info(),
            'system': self._get_system_info(),
            'network': self._get_network_info(),
            'time': self._get_time_context(),
            'timestamp': current_time.isoformat()
        }
        
        self.context_cache = context
        self.last_cache_update = current_time
        
        if DEBUG_MODE:
            logger.info(f"📍 Device context collected: {context}")
        
        return context
    
    def _get_location(self) -> dict:
        """Get device location information"""
        location = {
            'detected': False,
            'city': None,
            'country': None,
            'timezone': None,
            'coordinates': None
        }
        
        try:
            # Try to get timezone as a proxy for location
            import time
            timezone_name = time.tzname[0]
            location['timezone'] = timezone_name
            location['detected'] = True
            
            # Try to get more precise location using IP (if available)
            try:
                # This would require external API, for now use timezone
                import geocoder
                g = geocoder.ip('me')
                if g.ok:
                    location['city'] = g.city
                    location['country'] = g.country
                    location['coordinates'] = f"{g.latlng[0]},{g.latlng[1]}"
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error getting location: {e}")
        
        return location
    
    def _get_camera_info(self) -> dict:
        """Get camera/device information"""
        camera = {
            'available': False,
            'type': None,
            'name': None
        }
        
        try:
            # Check for camera availability
            if platform.system() == 'Windows':
                try:
                    result = subprocess.run(
                        ['powershell', '-Command', 'Get-PnpDevice -Class Camera -Status OK'],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0 and result.stdout:
                        camera['available'] = True
                        camera['type'] = 'webcam'
                        # Extract camera name
                        match = re.search(r'FriendlyName\s+:\s+(.+)', result.stdout)
                        if match:
                            camera['name'] = match.group(1).strip()
                except:
                    pass
            
            elif platform.system() == 'Linux':
                try:
                    result = subprocess.run(
                        ['ls', '/dev/video*'],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        camera['available'] = True
                        camera['type'] = 'webcam'
                        camera['name'] = 'Linux Camera Device'
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Error getting camera info: {e}")
        
        return camera
    
    def _get_system_info(self) -> dict:
        """Get system information"""
        system = {
            'os': platform.system(),
            'os_version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'hostname': socket.gethostname(),
            'username': None
        }
        
        try:
            if platform.system() == 'Windows':
                system['username'] = platform.uname().username
            else:
                import getpass
                system['username'] = getpass.getuser()
        except:
            pass
        
        return system
    
    def _get_network_info(self) -> dict:
        """Get network information"""
        network = {
            'connected': False,
            'ip_address': None,
            'wifi_ssid': None
        }
        
        try:
            # Get local IP
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            network['ip_address'] = ip_address
            network['connected'] = True
            
            # Try to get WiFi SSID
            if platform.system() == 'Windows':
                try:
                    result = subprocess.run(
                        ['netsh', 'wlan', 'show', 'interfaces'],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        match = re.search(r'SSID\s+:\s+(.+)', result.stdout)
                        if match:
                            network['wifi_ssid'] = match.group(1).strip()
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Error getting network info: {e}")
        
        return network
    
    def _get_time_context(self) -> dict:
        """Get time context"""
        now = datetime.now()
        return {
            'current_time': now.strftime('%H:%M:%S'),
            'current_date': now.strftime('%Y-%m-%d'),
            'day_of_week': now.strftime('%A'),
            'timezone': datetime.now().astimezone().tzinfo.tzname(None) if datetime.now().astimezone().tzinfo else None
        }
    
    def inject_context(self, query: str) -> tuple:
        """
        Inject device context into query for better NLP understanding
        Returns (enhanced_query, context_used)
        """
        import re
        context = self.get_device_context()
        context_used = []
        enhanced_query = query.lower()
        
        # Weather queries without location
        if 'weather' in enhanced_query or 'temperature' in enhanced_query:
            # Check if location is already specified (whole word match)
            location_words = [' in ', ' at ', ' of ']
            has_location = any(word in enhanced_query for word in location_words)
            if not has_location:
                # Use timezone as location proxy if city not available
                location_info = context['location']['city'] if context['location']['city'] else context['location']['timezone']
                if location_info:
                    enhanced_query += f" in {location_info}"
                    context_used.append('location')
        
        # Camera/vision queries
        if any(word in enhanced_query for word in ['selfie', 'photo', 'picture', 'capture', 'screenshot', 'camera']):
            if context['camera']['available']:
                enhanced_query += f" from {context['camera']['type']}"
                context_used.append('camera')
        
        # Time queries
        if any(word in enhanced_query for word in ['time', 'clock', 'hour']):
            if 'what time' in enhanced_query and ' in ' not in enhanced_query:
                # Use timezone as location proxy if city not available
                location_info = context['location']['city'] if context['location']['city'] else context['location']['timezone']
                if location_info:
                    enhanced_query += f" in {location_info}"
                    context_used.append('location_time')
        
        return enhanced_query, context_used
    
    def get_context_summary(self) -> str:
        """Get human-readable context summary"""
        context = self.get_device_context()
        
        summary = []
        if context['location']['city']:
            summary.append(f"📍 Location: {context['location']['city']}")
        if context['location']['timezone']:
            summary.append(f"🌍 Timezone: {context['location']['timezone']}")
        if context['camera']['available']:
            summary.append(f"📷 Camera: {context['camera']['name'] or 'Available'}")
        if context['network']['connected']:
            summary.append(f"🌐 Network: Connected")
        if context['network']['wifi_ssid']:
            summary.append(f"📶 WiFi: {context['network']['wifi_ssid']}")
        
        return "\n".join(summary) if summary else "No context available"

# Singleton
device_context = DeviceContextCollector()

if DEBUG_MODE:
    print("🔍 Device Context Collector initialized")
