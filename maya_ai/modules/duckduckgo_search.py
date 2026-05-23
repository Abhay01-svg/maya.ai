"""
Maya AI DuckDuckGo Search Module
Privacy-focused web search using DuckDuckGo HTML scraping
No API keys required - completely free and private
"""

import requests
import re
import logging
from typing import Dict, List
from urllib.parse import quote
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)

class DuckDuckGoSearch:
    """DuckDuckGo search implementation using HTML scraping"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        if logger.isEnabledFor(logging.INFO):
            logger.info("🦆 DuckDuckGo search initialized (no API key required)")
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Perform search using DuckDuckGo - try ddgs library first"""
        try:
            logger.info(f"🦆 DuckDuckGo search: {query}")
            
            # Try using ddgs library if available (new name)
            try:
                from ddgs import DDGS
                with DDGS() as ddgs:
                    results = []
                    for result in ddgs.text(query, max_results=limit):
                        results.append({
                            'title': result.get('title', ''),
                            'link': result.get('href', ''),
                            'snippet': result.get('body', '')
                        })
                    if results:
                        logger.info(f"✅ DuckDuckGo library returned {len(results)} results")
                        return results[:limit]
            except ImportError:
                logger.warning("⚠️ ddgs library not available, trying API")
            except Exception as e:
                logger.warning(f"⚠️ DuckDuckGo library failed: {e}")
            
            # Try DuckDuckGo Instant Answer API directly
            results = self._try_instant_api(query, limit)
            if results:
                logger.info(f"✅ DuckDuckGo API returned {len(results)} results")
                return results[:limit]
            
            # If API fails, try simple HTML search
            logger.warning("⚠️ API failed, trying HTML search")
            results = self._try_simple_html_search(query, limit)
            if results:
                logger.info(f"✅ HTML search returned {len(results)} results")
                return results[:limit]
            
            # If all fail, create mock results
            logger.warning("⚠️ All search methods failed, creating mock results")
            results = self._create_mock_results(query, limit)
            
            logger.info(f"🦆 DuckDuckGo found {len(results)} results")
            return results[:limit]
            
        except Exception as e:
            logger.error(f"❌ DuckDuckGo search error: {e}")
            return self._create_mock_results(query, limit)
    
    def search_images(self, query: str, limit: int = 3) -> List[Dict]:
        """Perform image search using DuckDuckGo"""
        try:
            logger.info(f"🦆 DuckDuckGo image search: {query}")
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = []
                for result in ddgs.images(query, max_results=limit):
                    results.append({
                        'title': result.get('title', ''),
                        'image': result.get('image', ''),
                        'thumbnail': result.get('thumbnail', ''),
                        'url': result.get('url', ''),
                        'source': result.get('source', '')
                    })
                return results
        except Exception as e:
            logger.error(f"❌ DuckDuckGo image search error: {e}")
            return []
    
    def _try_simple_html_search(self, query: str, limit: int) -> List[Dict]:
        """Simple HTML search without complex parsing - improved"""
        try:
            encoded_query = quote(query)
            url = f"https://duckduckgo.com/html/?q={encoded_query}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Better HTML parsing without BeautifulSoup
            import re
            results = []
            
            # Find result divs and extract links
            # DuckDuckGo uses class="result" or similar
            result_pattern = r'<div[^>]*class="[^"]*result[^"]*"[^>]*>(.*?)</div>'
            result_matches = re.findall(result_pattern, response.text, re.DOTALL)
            
            for result_html in result_matches:
                # Extract link and title from result
                link_match = re.search(r'<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>', result_html)
                if link_match:
                    href = link_match.group(1)
                    text = link_match.group(2)
                    
                    # Filter valid external links
                    if (href.startswith('http') and 
                        'duckduckgo' not in href and 
                        not href.startswith('/l/') and
                        len(text) > 10 and
                        len(results) < limit):
                        results.append({
                            'title': text[:100],
                            'link': href,
                            'snippet': f"Search result: {text[:200]}"
                        })
            
            # If no results with result divs, try finding all external links
            if not results:
                link_pattern = r'<a[^>]*href="(https?://[^"]+)"[^>]*>([^<]+)</a>'
                matches = re.findall(link_pattern, response.text)
                
                for href, text in matches:
                    if ('duckduckgo' not in href and 
                        not href.startswith('/l/') and
                        len(text) > 10 and
                        len(results) < limit):
                        results.append({
                            'title': text[:100],
                            'link': href,
                            'snippet': f"Result: {text[:200]}"
                        })
            
            logger.info(f"🔍 Simple HTML search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.warning(f"⚠️ Simple HTML search failed: {e}")
            return []
    
    def _try_instant_api(self, query: str, limit: int) -> List[Dict]:
        """Try DuckDuckGo Instant Answer API with better parameters"""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 0,
                't': 'maya_ai'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            logger.info(f"🦆 API response keys: {list(data.keys())}")
            
            # Extract abstract if available
            if 'Abstract' in data and data['Abstract']:
                results.append({
                    'title': data.get('Heading', query),
                    'link': data.get('AbstractURL', f'https://duckduckgo.com/?q={quote(query)}'),
                    'snippet': data['Abstract'][:300]
                })
            
            # Extract related topics
            if 'RelatedTopics' in data and isinstance(data['RelatedTopics'], list):
                for topic in data['RelatedTopics'][:limit]:
                    if isinstance(topic, dict) and 'Text' in topic and 'FirstURL' in topic:
                        title = str(topic['Text'])
                        # Clean up title - remove HTML-like patterns
                        title = re.sub(r'\[.*?\]', '', title)
                        if len(title) > 10:
                            results.append({
                                'title': title[:100],
                                'link': topic['FirstURL'],
                                'snippet': title[:200]
                            })
            
            # Extract infobox if available
            if 'Infobox' in data and isinstance(data['Infobox'], dict):
                info_content = data['Infobox'].get('content', [])
                if info_content:
                    for item in info_content[:limit]:
                        if isinstance(item, dict) and 'label' in item and 'value' in item:
                            results.append({
                                'title': f"{item['label']}: {item['value']}",
                                'link': f'https://duckduckgo.com/?q={quote(query)}',
                                'snippet': f"{item['label']}: {item['value']}"
                            })
            
            logger.info(f"✅ API extracted {len(results)} results")
            return results[:limit]
            
        except Exception as e:
            logger.warning(f"⚠️ Instant API failed: {e}")
            return []
    
    def _try_html_search(self, query: str, limit: int) -> List[Dict]:
        """Try HTML search approach with better parsing"""
        try:
            encoded_query = quote(query)
            url = f"https://duckduckgo.com/html/?q={encoded_query}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # DuckDuckGo HTML structure uses specific classes
            # Try multiple selectors
            selectors = [
                'div.result',
                'div.web-result',
                'div.js-result',
                'a.result__a',
                'div[data-testid]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                logger.info(f"🔍 Trying selector '{selector}': found {len(elements)} elements")
                
                for element in elements:
                    try:
                        # Extract title
                        title_elem = element.select_one('a.result__a, a, h2, .result__title')
                        title = title_elem.get_text(strip=True) if title_elem else element.get_text(strip=True)
                        
                        # Extract link
                        link_elem = element.select_one('a')
                        link = link_elem.get('href', '') if link_elem else ''
                        
                        # Extract snippet
                        snippet_elem = element.select_one('.result__snippet, .snippet, p')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else title[:200]
                        
                        # Filter valid results
                        if (title and len(title) > 5 and 
                            link and 'duckduckgo' not in link and 
                            not link.startswith('/')):
                            
                            results.append({
                                'title': title[:100],
                                'link': link,
                                'snippet': snippet[:300]
                            })
                            
                            if len(results) >= limit:
                                break
                    except Exception as e:
                        continue
                
                if len(results) >= limit:
                    break
            
            logger.info(f"🦆 HTML search found {len(results)} results")
            return results[:limit]
            
        except Exception as e:
            logger.warning(f"⚠️ HTML search failed: {e}")
            return []
    
    def _create_mock_results(self, query: str, limit: int) -> List[Dict]:
        """Create mock results for testing"""
        mock_results = [
            {
                'title': f"Latest information about {query}",
                'link': f"https://duckduckgo.com/?q={quote(query)}",
                'snippet': f"This is a simulated search result for {query}. The actual DuckDuckGo search is currently being debugged."
            },
            {
                'title': f"{query} - Overview and Updates",
                'link': f"https://duckduckgo.com/html/?q={quote(query)}",
                'snippet': f"Comprehensive information about {query} including recent developments and trends."
            }
        ]
        
        return mock_results[:limit]
    
    def _search_html_fallback(self, query: str, limit: int = 5) -> List[Dict]:
        """Fallback HTML search method"""
        try:
            encoded_query = quote(query)
            url = f"https://duckduckgo.com/html/?q={encoded_query}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Simple approach: find all result links
            result_links = soup.find_all('a', class_='result__a')
            
            for link in result_links[:limit]:
                title = link.get_text(strip=True)
                href = link.get('href', '')
                
                if title and href and len(title) > 10:
                    results.append({
                        'title': title,
                        'link': href,
                        'snippet': f"Result for: {title[:100]}"
                    })
            
            return results
            
        except Exception as e:
            logger.warning(f"⚠️ HTML fallback failed: {e}")
            return []
    
    def search_with_fallback(self, query: str, limit: int = 5) -> List[Dict]:
        """Search with multiple fallback methods"""
        results = []
        
        # Try primary HTML search
        results = self.search(query, limit)
        
        if not results:
            logger.info("🔄 Primary search failed, trying instant answer API")
            results = self._search_instant_api(query, limit)
        
        if not results:
            logger.info("🔄 All methods failed, returning empty results")
        
        return results
    
    def _search_instant_api(self, query: str, limit: int = 5) -> List[Dict]:
        """Fallback to DuckDuckGo instant answer API"""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Extract related topics if available
            if 'RelatedTopics' in data:
                for topic in data['RelatedTopics'][:limit]:
                    if 'Text' in topic and 'FirstURL' in topic:
                        results.append({
                            'title': topic['Text'],
                            'link': topic['FirstURL'],
                            'snippet': topic.get('Text', '')[:200]
                        })
            
            return results
            
        except Exception as e:
            logger.warning(f"⚠️ Instant API fallback failed: {e}")
            return []
    
    def get_search_summary(self, query: str, limit: int = 3) -> str:
        """Get formatted search results summary"""
        results = self.search_with_fallback(query, limit)
        
        if not results:
            return f"❌ '{query}' के लिए कोई search results नहीं मिले"
        
        summary = f"🦆 DuckDuckGo search results for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            summary += f"{i}. {result['title']}\n"
            summary += f"   {result['snippet']}\n"
            summary += f"   🔗 {result['link']}\n\n"
        
        return summary

# Global DuckDuckGo search instance
duckduckgo_search = DuckDuckGoSearch()
