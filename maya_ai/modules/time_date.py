"""
Time and Date Module
Accurate time and date queries with timezone support
"""

import datetime
import pytz
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class TimeDateModule:
    """Advanced time and date handling with timezone support"""
    
    def __init__(self):
        self.common_timezones = {
            'utc': 'UTC',
            'est': 'US/Eastern',
            'pst': 'US/Pacific',
            'mst': 'US/Mountain',
            'cst': 'US/Central',
            'gmt': 'GMT',
            'ist': 'Asia/Kolkata',
            'cst': 'Asia/Shanghai',
            'jst': 'Asia/Tokyo',
            'aest': 'Australia/Sydney',
            'bst': 'Europe/London',
            'cest': 'Europe/Paris',
            'msk': 'Europe/Moscow'
        }
        
        self.time_formats = {
            '12h': '%I:%M %p',
            '24h': '%H:%M',
            'full': '%Y-%m-%d %H:%M:%S %Z',
            'date': '%Y-%m-%d',
            'time': '%H:%M:%S'
        }
    
    def get_current_time(self, timezone: str = 'utc') -> Dict[str, Any]:
        """Get current time in specified timezone"""
        try:
            # Get timezone identifier
            tz_identifier = self.common_timezones.get(timezone.lower(), 'UTC')
            
            # Get current time in UTC first
            utc_now = datetime.datetime.now(pytz.UTC)
            
            # Convert to requested timezone
            target_tz = pytz.timezone(tz_identifier)
            local_time = utc_now.astimezone(target_tz)
            
            # Format time in different ways
            result = {
                'timezone': timezone.upper(),
                'timezone_full': tz_identifier,
                'time_12h': local_time.strftime(self.time_formats['12h']),
                'time_24h': local_time.strftime(self.time_formats['24h']),
                'full_datetime': local_time.strftime(self.time_formats['full']),
                'date': local_time.strftime(self.time_formats['date']),
                'day_of_week': local_time.strftime('%A'),
                'day_name': local_time.strftime('%d').lstrip('0'),
                'month_name': local_time.strftime('%B'),
                'year': local_time.strftime('%Y'),
                'utc_offset': local_time.strftime('%z'),
                'is_dst': local_time.dst() != datetime.timedelta(0)
            }
            
            logger.info(f"🕐 Time retrieved for {timezone}: {result['time_12h']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting time for {timezone}: {e}")
            return {
                'error': f"Failed to get time for {timezone}: {str(e)}",
                'timezone': timezone.upper()
            }
    
    def get_time_in_multiple_zones(self, zones: list = None) -> Dict[str, Any]:
        """Get current time in multiple timezones"""
        if zones is None:
            zones = ['utc', 'est', 'pst', 'ist', 'gmt', 'jst']
        
        results = {}
        for zone in zones:
            results[zone] = self.get_current_time(zone)
        
        return results
    
    def get_world_clock(self) -> Dict[str, Any]:
        """Get world clock with major cities"""
        world_cities = {
            'new_york': 'US/Eastern',
            'london': 'Europe/London',
            'tokyo': 'Asia/Tokyo',
            'sydney': 'Australia/Sydney',
            'dubai': 'Asia/Dubai',
            'singapore': 'Asia/Singapore',
            'hong_kong': 'Asia/Hong_Kong',
            'mumbai': 'Asia/Kolkata',
            'paris': 'Europe/Paris',
            'moscow': 'Europe/Moscow'
        }
        
        results = {}
        for city, tz in world_cities.items():
            results[city] = self.get_current_time(tz)
        
        return results
    
    def convert_time(self, from_tz: str, to_tz: str, time_str: str = None) -> Dict[str, Any]:
        """Convert time from one timezone to another"""
        try:
            from_timezone = pytz.timezone(self.common_timezones.get(from_tz.lower(), 'UTC'))
            to_timezone = pytz.timezone(self.common_timezones.get(to_tz.lower(), 'UTC'))
            
            if time_str:
                # Parse the input time
                time_obj = datetime.datetime.strptime(time_str, '%H:%M').time()
                today = datetime.date.today()
                dt = datetime.datetime.combine(today, time_obj)
                
                # Set timezone and convert
                dt_with_tz = from_timezone.localize(dt)
                converted_dt = dt_with_tz.astimezone(to_timezone)
            else:
                # Use current time
                utc_now = datetime.datetime.now(pytz.UTC)
                converted_dt = utc_now.astimezone(to_timezone)
            
            result = {
                'from_timezone': from_tz.upper(),
                'to_timezone': to_tz.upper(),
                'original_time': time_str,
                'converted_time': converted_dt.strftime(self.time_formats['12h']) if time_str else converted_dt.strftime(self.time_formats['12h']),
                'converted_24h': converted_dt.strftime(self.time_formats['24h']) if time_str else converted_dt.strftime(self.time_formats['24h']),
                'date': converted_dt.strftime(self.time_formats['date']) if time_str else converted_dt.strftime(self.time_formats['date']),
                'utc_offset': converted_dt.strftime('%z'),
                'is_dst': converted_dt.dst() != datetime.timedelta(0)
            }
            
            logger.info(f"🌍 Time converted from {from_tz} to {to_tz}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error converting time: {e}")
            return {
                'error': f"Failed to convert time: {str(e)}",
                'from_timezone': from_tz.upper(),
                'to_timezone': to_tz.upper()
            }
    
    def get_time_difference(self, tz1: str, tz2: str) -> Dict[str, Any]:
        """Calculate time difference between two timezones"""
        try:
            time1 = self.get_current_time(tz1)
            time2 = self.get_current_time(tz2)
            
            if 'error' in time1 or 'error' in time2:
                return {'error': 'Failed to get time for comparison'}
            
            # Parse times for calculation
            dt1 = datetime.datetime.strptime(time1['full_datetime'], '%Y-%m-%d %H:%M:%S %z')
            dt2 = datetime.datetime.strptime(time2['full_datetime'], '%Y-%m-%d %H:%M:%S %z')
            
            # Calculate difference
            diff = abs(int((dt2 - dt1).total_seconds() / 3600))
            hours = diff // 60
            minutes = diff % 60
            
            result = {
                'timezone1': tz1.upper(),
                'timezone2': tz2.upper(),
                'time1': time1['time_12h'],
                'time2': time2['time_12h'],
                'difference_hours': hours,
                'difference_minutes': minutes,
                'difference_str': f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m",
                'time1_ahead': dt2 > dt1,
                'time2_ahead': dt1 > dt2
            }
            
            logger.info(f"⏰ Time difference calculated: {result['difference_str']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error calculating time difference: {e}")
            return {
                'error': f"Failed to calculate time difference: {str(e)}"
            }
    
    def format_time_response(self, query: str) -> str:
        """Format time query response"""
        query_lower = query.lower()
        
        # Check for specific time zones
        for tz_code, tz_name in self.common_timezones.items():
            if tz_code in query_lower:
                time_info = self.get_current_time(tz_code)
                if 'error' in time_info:
                    return f"❌ {time_info['error']}"
                
                return (
                    f"🕐 Current time in {tz_name.upper()} ({tz_code.upper()}): "
                    f"{time_info['time_12h']} on {time_info['day_of_week']}, "
                    f"{time_info['date']}. "
                    f"UTC offset: {time_info['utc_offset']}."
                )
        
        # Check for time conversion queries
        if 'convert' in query_lower or 'time in' in query_lower:
            # Extract timezones from query
            words = query_lower.split()
            tz1, tz2 = None, None
            
            for i, word in enumerate(words):
                if word in self.common_timezones:
                    if tz1 is None:
                        tz1 = word
                    elif tz2 is None:
                        tz2 = word
            
            if tz1 and tz2:
                conversion = self.convert_time(tz1, tz2)
                if 'error' in conversion:
                    return f"❌ {conversion['error']}"
                
                return (
                    f"🌍 Time conversion from {tz1.upper()} to {tz2.upper()}: "
                    f"{conversion['converted_time']} ({conversion['date']})."
                )
        
        # Check for world time queries
        if 'world time' in query_lower or 'time around the world' in query_lower:
            world_times = self.get_world_clock()
            response = "🌍 World Times:\n\n"
            for city, time_info in world_times.items():
                if 'error' not in time_info:
                    response += f"📍 {city.replace('_', ' ').title()}: {time_info['time_12h']} ({time_info['date']})\n"
            return response
        
        # Check for current time queries
        if 'current time' in query_lower or 'what time' in query_lower or 'time now' in query_lower:
            time_info = self.get_current_time('ist')
            if 'error' in time_info:
                return f"❌ {time_info['error']}"

            return (
                f"🕐 Current time (IST): {time_info['time_12h']} on {time_info['day_of_week']}, "
                f"{time_info['date']}. "
                f"UTC offset: {time_info['utc_offset']}."
            )
        
        # Default response
        return "🕐 I can help you with time queries! Try:\n" \
               "• 'What time is it in New York?'\n" \
               "• 'Current time in Tokyo'\n" \
               "• 'Convert 3 PM EST to IST'\n" \
               "• 'World time'\n" \
               "• 'Time difference between London and New York'"

# Global instance
time_date_module = TimeDateModule()
