"""
Maya AI Tools Module
APIs: Weather, News, Search (SerpAPI, Zenserp), etc.
"""

import requests
import json
import logging
import wolframalpha
from typing import Dict, List
from config import (WEATHER_API_KEY, SERP_API_KEY, ZENSERP_API_KEY, 
                    NEWS_API_KEY, WOLFRAM_API_ID, DEBUG_MODE)

from .system_info import system_info

logger = logging.getLogger(__name__)

class WeatherAPI:
    """Weather information"""
    
    def __init__(self):
        self.api_key = WEATHER_API_KEY
        self.base_url = "https://api.weatherapi.com/v1"
    
    def get_weather(self, city: str) -> dict:
        """Get current weather"""
        try:
            url = f"{self.base_url}/current.json"
            params = {
                "key": self.api_key,
                "q": city,
                "aqi": "yes"
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            weather = {
                "city": data["location"]["name"],
                "country": data["location"]["country"],
                "temp_c": data["current"]["temp_c"],
                "temp_f": data["current"]["temp_f"],
                "condition": data["current"]["condition"]["text"],
                "humidity": data["current"]["humidity"],
                "wind_kph": data["current"]["wind_kph"],
                "aqi": data["current"]["air_quality"].get("us-epa-index", "N/A") if "air_quality" in data["current"] else "N/A"
            }
            
            return weather
        except Exception as e:
            logger.error(f"❌ Weather API error: {e}")
            return None
    
    def get_hinglish_weather(self, city: str) -> str:
        """Get weather in Hinglish"""
        # If city is "current" or "here", use system_info
        if city.lower() in ["current", "here", "my location", "mera location"]:
            loc = system_info.get_location_context()
            city = loc.get("city", "New Delhi")
            logger.info(f"📍 Using detected location for weather: {city}")
        
        weather = self.get_weather(city)
        
        if not weather:
            return f"❌ {city} ka weather nahi mil paya"
        
        condition_hi = {
            "sunny": "dhoop",
            "clear": "saaf",
            "cloudy": "badal",
            "rain": "barish",
            "snow": "barf",
            "partly cloudy": "kuch badal"
        }
        
        cond = condition_hi.get(weather["condition"].lower(), weather["condition"])
        
        return f"""🌍 {weather['city']}, {weather['country']} ka weather:
🌡️  Temp: {weather['temp_c']}°C ({weather['temp_f']}°F)
☁️  Condition: {cond}
💧 Humidity: {weather['humidity']}%
💨 Wind: {weather['wind_kph']} km/h
🌫️  AQI: {weather['aqi']}"""


class NewsAPI:
    """News information"""
    
    def __init__(self):
        self.api_key = NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
    
    def get_news(self, query: str = "india", limit: int = 5) -> list:
        """Get news articles"""
        try:
            url = f"{self.base_url}/everything"
            params = {
                "q": query,
                "sortBy": "publishedAt",
                "language": "en",
                "apiKey": self.api_key,
                "pageSize": limit
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get("articles", []):
                articles.append({
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "source": article.get("source", {}).get("name"),
                    "url": article.get("url"),
                    "published": article.get("publishedAt")
                })
            
            return articles
        except Exception as e:
            logger.error(f"❌ News API error: {e}")
            return []
    
    def get_hinglish_news(self, query: str = "india", limit: int = 3) -> str:
        """Get news in Hinglish format"""
        articles = self.get_news(query, limit)
        
        if not articles:
            return f"❌ {query} ke news nahi mil paaye"
        
        result = f"📰 {query.capitalize()} ki latest news:\n\n"
        
        for i, article in enumerate(articles, 1):
            result += f"{i}. {article['title']}\n"
            result += f"   Source: {article['source']}\n"
            if article['description']:
                result += f"   {article['description'][:100]}...\n"
            result += "\n"
        
        return result


class SearchAPI:
    """Web search using DuckDuckGo (privacy-focused, no API keys)"""
    
    def __init__(self, provider: str = "duckduckgo"):
        self.provider = provider
        # Import DuckDuckGo search
        try:
            from .duckduckgo_search import DuckDuckGoSearch
            self.ddg_search = DuckDuckGoSearch()
        except ImportError as e:
            logger.error(f"❌ DuckDuckGo search import failed: {e}")
            self.ddg_search = None
    
    def search_serpapi(self, query: str, limit: int = 5) -> list:
        """Search using SerpAPI"""
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.serp_key,
                "num": limit,
                "engine": "google"
            }
            
            # Increase timeout and add retry logic
            response = requests.get(url, params=params, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("organic_results", [])[:limit]:
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet")
                })
            
            return results
        except requests.exceptions.Timeout:
            logger.error("❌ SerpAPI timeout - trying fallback")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ SerpAPI request error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ SerpAPI error: {e}")
            return []
    
    def search_zenserp(self, query: str, limit: int = 5) -> list:
        """Search using Zenserp"""
        try:
            url = "https://api.zenserp.com/search"
            params = {
                "q": query,
                "apikey": self.zenserp_key,
                "num": limit,
                "source": "google"
            }
            
            # Increase timeout and add headers
            response = requests.get(url, params=params, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            })
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("organic", [])[:limit]:
                results.append({
                    "title": item.get("title"),
                    "link": item.get("url"),
                    "snippet": item.get("snippet")
                })
            
            return results
        except requests.exceptions.Timeout:
            logger.error("❌ Zenserp timeout - trying fallback")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Zenserp request error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Zenserp error: {e}")
            return []
    
    def search(self, query: str, limit: int = 5) -> list:
        """Universal search using DuckDuckGo"""
        if self.ddg_search:
            try:
                results = self.ddg_search.search(query, limit)
                if results:
                    return results[:limit]
                else:
                    # Fallback to mock if search returns empty
                    logger.warning("⚠️ DuckDuckGo search returned empty, creating mock results")
                    return self._create_mock_results(query, limit)
            except Exception as e:
                logger.error(f"❌ DuckDuckGo search error: {e}")
                return self._create_mock_results(query, limit)
        else:
            logger.error("❌ DuckDuckGo search not available")
            return self._create_mock_results(query, limit)
    
    def search_images(self, query: str, limit: int = 3) -> list:
        """Search for images using DuckDuckGo"""
        if self.ddg_search:
            try:
                return self.ddg_search.search_images(query, limit)
            except Exception as e:
                logger.error(f"❌ DuckDuckGo image search error: {e}")
                return []
        return []
    
    def _create_mock_results(self, query: str, limit: int = 5) -> list:
        """Create mock search results when real search fails"""
        logger.warning(f"⚠️ Creating mock results for: {query}")
        return [
            {
                'title': f'Latest information about {query}',
                'link': f'https://duckduckgo.com/?q={query.replace(" ", "%20")}',
                'snippet': f'This is a simulated search result for {query}. The actual DuckDuckGo search is currently being debugged.'
            }
        ]
    
    def get_hinglish_search(self, query: str, limit: int = 3) -> str:
        """Get search results in Hinglish with local context"""
        # Append location for "near me" or local queries
        loc_query = query
        if any(kw in query.lower() for kw in ["near me", "nearby", "local", "here"]):
            loc = system_info.get_location_context()
            city = loc.get("city", "")
            if city:
                loc_query = f"{query} in {city}"
                logger.info(f"📍 Localizing search: {loc_query}")

        results = self.search(loc_query, limit)
        
        if not results:
            return f"❌ '{query}' ka search result nahi mila"
        
        output = f"🦆 DuckDuckGo search results for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            output += f"{i}. {result['title']}\n"
            output += f"   {result['snippet'][:80]}...\n"
            output += f"   🔗 {result['link']}\n\n"
        
        return output


class WolframAlphaAPI:
    """Wolfram Alpha Computational Knowledge Engine"""
    
    def __init__(self):
        self.app_id = WOLFRAM_API_ID
        if self.app_id:
            try:
                self.client = wolframalpha.Client(self.app_id)
            except Exception as e:
                logger.error(f"❌ WolframAlpha initialization error: {e}")
                self.client = None
        else:
            self.client = None
            logger.warning("⚠️ WOLFRAM_API_ID not found in config")

    def query(self, query: str) -> str:
        """Query WolframAlpha for facts, math, or science questions"""
        if not self.client:
            return "❌ Wolfram Alpha API not configured"
            
        try:
            logger.info(f"🔮 Querying WolframAlpha: {query}")
            res = self.client.query(query)
            
            # WolframAlpha returns results in pods
            # The "Result" pod usually contains the primary answer
            answer = ""
            
            # Simple result extraction
            if hasattr(res, 'results'):
                for result in res.results:
                    if hasattr(result, 'text'):
                        answer = result.text
                        break
            
            # If no direct result, look for the most relevant pod
            if not answer and hasattr(res, 'pods'):
                for pod in res.pods:
                    # Look for pods titled Result, Definition, Basic information, etc.
                    if pod.title in ['Result', 'Definition', 'Basic information', 'Solution', 'Value']:
                        if hasattr(pod, 'text'):
                            answer = pod.text
                            break
                        elif hasattr(pod, 'subpod'):
                            # Handle multiple subpods
                            if isinstance(pod.subpod, list):
                                answer = pod.subpod[0].text
                            else:
                                answer = pod.subpod.text
                            break

            if answer:
                return answer
            else:
                return "❌ Wolfram Alpha ne koi clear answer nahi diya"
                
        except Exception as e:
            logger.error(f"❌ Wolfram Alpha error: {e}")
            return f"❌ Wolfram Alpha error: {str(e)}"

    def get_hinglish_wolfram(self, query: str) -> str:
        """Get WolframAlpha result in Hinglish context"""
        result = self.query(query)
        if result.startswith("❌"):
            return result
            
        return f"🔮 WolframAlpha ka answer '{query}' ke liye:\n\n{result}"


class UtilityTools:
    """Other utility functions"""
    
    @staticmethod
    def get_time_in_city(city: str) -> str:
        """Get current time in a city"""
        try:
            url = f"https://worldtimeapi.org/api/timezone/Etc/UTC"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"❌ Time API error: {e}")
        return None
    
    @staticmethod
    def get_currency_rate(from_currency: str, to_currency: str) -> float:
        """Get currency conversion rate"""
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            rate = data.get("rates", {}).get(to_currency)
            return rate
        except Exception as e:
            logger.error(f"❌ Currency API error: {e}")
            return None
    
    @staticmethod
    def get_ip_info() -> dict:
        """Get IP information"""
        try:
            # Try ip-api.com as primary (no API key required, higher limits)
            response = requests.get("http://ip-api.com/json/", timeout=5)
            if response.status_code == 200:
                return response.json()
            
            # Fallback to ipapi.co
            response = requests.get("https://ipapi.co/json/", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ IP API error: {e}")
            return None


# Initialize API clients
weather_api = WeatherAPI()
news_api = NewsAPI()
search_api = SearchAPI(provider="duckduckgo")
wolfram_api = WolframAlphaAPI()
utils = UtilityTools()

if DEBUG_MODE:
    print("🔗 Maya Tools (APIs) initialized")
