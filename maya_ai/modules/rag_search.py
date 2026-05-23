"""
Maya AI RAG + Web Search Engine
Advanced search with real-time web access, deep reading, and intelligent summarization
"""

import logging
import requests
import time
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json

from config import DEBUG_MODE, SERP_API_KEY, ZENSERP_API_KEY
from .tools import search_api

logger = logging.getLogger(__name__)

class WebRAGEngine:
    """RAG (Retrieval-Augmented Generation) with Web Search capabilities"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Content extraction patterns
        self.content_selectors = [
            'article', 'main', '.content', '.post-content', 
            '.article-content', '.entry-content', '.story-body',
            '[role="main"]', '.main-content', '#content'
        ]
        
        # Junk content patterns to remove
        self.junk_patterns = [
            r'advertisement', r'sponsored', r'ad-', r'promo',
            r'cookie', r'privacy', r'terms', r'subscribe',
            r'newsletter', r'social', r'footer', r'header'
        ]
        
        if DEBUG_MODE:
            logger.info("🔍 RAG + Web Search Engine initialized")
    
    def deep_search(self, query: str, max_results: int = 10, depth: int = 2) -> Dict:
        """Perform deep web search with multiple sources and content extraction"""
        start_time = time.time()
        
        try:
            # Step 1: Initial web search
            search_results = self._perform_web_search(query, max_results)
            
            if not search_results:
                return {
                    'success': False,
                    'query': query,
                    'error': 'No search results found',
                    'response': f"❌ '{query}' ke liye koi search results nahi mile"
                }
            
            # Step 2: Extract content from search snippets (faster, more reliable)
            extracted_content = self._extract_content_from_snippets(search_results[:5])
            
            # Step 3: Generate summary from snippets
            summary = self._generate_summary_from_snippets(extracted_content, query)
            
            # Step 4: Generate comprehensive Q&A response
            response = self._generate_qa_response(query, search_results, summary)
            
            search_time = time.time() - start_time
            
            return {
                'success': True,
                'query': query,
                'search_time': search_time,
                'search_results': search_results,
                'extracted_content': extracted_content,
                'summary': summary,
                'response': response,
                'sources_count': len(search_results),
                'content_sources': len(extracted_content)
            }
            
        except Exception as e:
            logger.error(f"❌ Deep search error: {e}")
            return {
                'success': False,
                'query': query,
                'error': str(e),
                'response': f"❌ Search mein error aaya: {str(e)}"
            }
    
    def _perform_web_search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Perform initial web search"""
        try:
            # Use existing search API
            search_results_text = search_api.get_hinglish_search(query, limit=max_results)
            
            if search_results_text.startswith('❌'):
                return []
            
            # Parse search results (improved parsing)
            results = []
            lines = search_results_text.split('\n')
            
            current_result = {}
            for line in lines:
                line_stripped = line.strip()
                
                # Check if line starts with a number (new result)
                if line_stripped and line_stripped[0].isdigit() and '.' in line_stripped[:5]:
                    if current_result:
                        results.append(current_result)
                    current_result = {'title': line_stripped.split('.', 1)[1].strip()}
                
                # Check for snippet (indented line without URL)
                elif line.startswith('   ') and 'http' not in line and '🔗' not in line:
                    if 'snippet' not in current_result:
                        current_result['snippet'] = line_stripped
                    else:
                        current_result['snippet'] += ' ' + line_stripped
                
                # Check for link
                elif '🔗' in line or 'http' in line:
                    link = line_stripped.replace('🔗', '').strip()
                    current_result['link'] = link
            
            if current_result:
                results.append(current_result)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Web search error: {e}")
            return []
    
    def _extract_content_from_snippets(self, search_results: List[Dict]) -> List[Dict]:
        """Extract content from search result snippets (faster, more reliable)"""
        extracted_content = []
        
        for result in search_results:
            content = {
                'title': result.get('title', 'No title'),
                'snippet': result.get('snippet', ''),
                'link': result.get('link', ''),
                'content': result.get('snippet', ''),  # Use snippet as content
                'word_count': len(result.get('snippet', '').split())
            }
            extracted_content.append(content)
        
        return extracted_content
    
    def _extract_single_page_content(self, url: str, depth: int = 2) -> Optional[Dict]:
        """Extract content from a single web page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Find main content
            main_content = self._find_main_content(soup)
            
            if not main_content:
                return None
            
            # Clean and extract text
            text_content = self._clean_text(main_content.get_text())
            
            # Extract metadata
            title = soup.find('title')
            title_text = title.get_text().strip() if title else 'No title'
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ''
            
            # Extract key information
            key_info = self._extract_key_information(text_content)
            
            return {
                'title': title_text,
                'description': description,
                'content': text_content,
                'key_info': key_info,
                'word_count': len(text_content.split()),
                'extraction_time': time.time()
            }
            
        except Exception as e:
            logger.warning(f"⚠️  Page extraction error for {url}: {e}")
            return None
    
    def _find_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Find the main content area of the page"""
        for selector in self.content_selectors:
            main_element = soup.select_one(selector)
            if main_element:
                return main_element
        
        # Fallback to body
        return soup.find('body')
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove junk content
        for pattern in self.junk_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s.,!?;:()-]', '', text)
        
        # Remove multiple consecutive punctuation
        text = re.sub(r'[.,!?;:]{2,}', '.', text)
        
        return text.strip()
    
    def _extract_key_information(self, text: str) -> Dict:
        """Extract key information from text"""
        key_info = {}
        
        # Extract numbers and statistics
        numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?\b', text)
        if numbers:
            key_info['numbers'] = numbers[:10]  # Limit to first 10 numbers
        
        # Extract dates
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}\b', text)
        if dates:
            key_info['dates'] = dates[:5]  # Limit to first 5 dates
        
        # Extract key phrases (simplified)
        sentences = text.split('.')
        key_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        if key_sentences:
            key_info['key_sentences'] = key_sentences[:3]  # Top 3 sentences
        
        return key_info
    
    def _generate_summary_from_snippets(self, extracted_content: List[Dict], query: str) -> Dict:
        """Generate summary from snippets"""
        if not extracted_content:
            return {'summary': 'No content available', 'insights': []}
        
        # Combine all snippets
        all_snippets = ' '.join([content['snippet'] for content in extracted_content])
        
        # Create summary
        summary = self._create_simple_summary(all_snippets, query)
        
        # Extract insights
        insights = [f"Found {len(extracted_content)} relevant sources"]
        
        return {
            'summary': summary,
            'insights': insights,
            'total_words': len(all_snippets.split()),
            'sources_analyzed': len(extracted_content)
        }
    
    def _generate_qa_response(self, query: str, search_results: List[Dict], summary: Dict) -> str:
        """Generate Q&A response instead of links"""
        response_parts = []
        
        # Answer header
        response_parts.append(f"🔍 Answer for: '{query}'")
        
        # Main answer from summary
        if summary.get('summary'):
            response_parts.append(f"\n📝 Answer:\n{summary['summary']}")
        
        # Additional context from snippets
        response_parts.append(f"\n📚 Key Information:")
        for i, content in enumerate(search_results[:3], 1):
            title = content.get('title', 'No title')
            snippet = content.get('snippet', '')
            if snippet:
                response_parts.append(f"{i}. {title}")
                response_parts.append(f"   {snippet[:150]}...")
        
        return '\n'.join(response_parts)
    
    def _create_simple_summary(self, text: str, query: str) -> str:
        """Create a simple summary (would use LLM in production)"""
        # This is a simplified summary - in production would use Llama or similar
        sentences = text.split('.')
        
        # Find sentences most relevant to query
        query_words = query.lower().split()
        relevant_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30 and any(word in sentence.lower() for word in query_words):
                relevant_sentences.append(sentence)
        
        if relevant_sentences:
            summary = '. '.join(relevant_sentences[:3]) + '.'
        else:
            # Take first few sentences as fallback
            summary = '. '.join(sentences[:3]) + '.'
        
        return summary
    
    def _analyze_and_summarize_content(self, extracted_content: List[Dict], query: str) -> Dict:
        """Analyze extracted content and create summary"""
        if not extracted_content:
            return {'summary': 'No content available for analysis', 'insights': []}
        
        # Combine all content
        all_text = ' '.join([content['content'] for content in extracted_content])
        
        # Generate summary (simplified - would use LLM in production)
        summary = self._create_simple_summary(all_text, query)
        
        # Extract insights
        insights = self._extract_insights(extracted_content, query)
        
        return {
            'summary': summary,
            'insights': insights,
            'total_words': len(all_text.split()),
            'sources_analyzed': len(extracted_content)
        }
    
    def _extract_insights(self, extracted_content: List[Dict], query: str) -> List[str]:
        """Extract insights from analyzed content"""
        insights = []
        
        # Common themes across sources
        all_titles = [content['title'] for content in extracted_content]
        if len(all_titles) > 1:
            insights.append(f"Found {len(all_titles)} relevant sources about {query}")
        
        # Content depth
        total_words = sum(content['word_count'] for content in extracted_content)
        if total_words > 1000:
            insights.append(f"Analyzed {total_words} words of content")
        
        # Key information patterns
        all_numbers = []
        all_dates = []
        
        for content in extracted_content:
            key_info = content.get('key_info', {})
            all_numbers.extend(key_info.get('numbers', []))
            all_dates.extend(key_info.get('dates', []))
        
        if all_numbers:
            insights.append(f"Found {len(all_numbers)} numerical data points")
        
        if all_dates:
            insights.append(f"Content spans multiple time periods")
        
        return insights
    
    def _generate_comprehensive_response(self, query: str, search_results: List[Dict], 
                                      extracted_content: List[Dict], summary: Dict) -> str:
        """Generate comprehensive Hinglish response"""
        response_parts = []
        
        # Header
        response_parts.append(f"🔍 '{query}' ke liye deep search results:")
        
        # Summary
        if summary.get('summary'):
            response_parts.append(f"\n📝 Summary:\n{summary['summary']}")
        
        # Key insights
        if summary.get('insights'):
            response_parts.append(f"\n💡 Key Insights:")
            for insight in summary['insights']:
                response_parts.append(f"• {insight}")
        
        # Top sources
        response_parts.append(f"\n🌐 Top Sources:")
        for i, result in enumerate(search_results[:3], 1):
            title = result.get('title', 'No title')
            snippet = result.get('snippet', 'No description')
            response_parts.append(f"{i}. {title}")
            if snippet and snippet != 'No description':
                response_parts.append(f"   {snippet[:100]}...")
        
        # Content analysis
        if extracted_content:
            response_parts.append(f"\n📊 Content Analysis:")
            response_parts.append(f"• Analyzed {len(extracted_content)} sources in detail")
            total_words = sum(content['word_count'] for content in extracted_content)
            response_parts.append(f"• Processed {total_words} words of content")
        
        return '\n'.join(response_parts)
    
    def compare_sources(self, query: str, sources: List[str]) -> Dict:
        """Compare information from multiple specific sources"""
        try:
            comparison_results = []
            
            for source in sources:
                content = self._extract_single_page_content(source)
                if content:
                    comparison_results.append({
                        'source': source,
                        'content': content,
                        'key_points': self._extract_key_information(content['content'])
                    })
            
            # Generate comparison
            comparison = self._generate_comparison(comparison_results, query)
            
            return {
                'success': True,
                'query': query,
                'sources': sources,
                'comparison_results': comparison_results,
                'comparison': comparison,
                'response': comparison
            }
            
        except Exception as e:
            return {
                'success': False,
                'query': query,
                'error': str(e),
                'response': f"❌ Source comparison failed: {str(e)}"
            }
    
    def _generate_comparison(self, results: List[Dict], query: str) -> str:
        """Generate comparison of sources"""
        if not results:
            return f"❌ Could not compare sources for '{query}'"
        
        comparison_parts = []
        comparison_parts.append(f"🔍 Source Comparison for '{query}':")
        
        for i, result in enumerate(results, 1):
            source = result['source']
            content = result['content']
            
            comparison_parts.append(f"\n{i}. {source}")
            comparison_parts.append(f"   Title: {content['title']}")
            
            key_info = content.get('key_info', {})
            if key_info.get('key_sentences'):
                comparison_parts.append(f"   Key points: {'; '.join(key_info['key_sentences'][:2])}")
        
        return '\n'.join(comparison_parts)
    
    def real_time_search(self, query: str) -> Dict:
        """Perform real-time search for latest information"""
        try:
            # Add time-based keywords for real-time search
            time_keywords = ['latest', 'current', 'today', 'now', 'recent', 'breaking']
            
            enhanced_query = query
            if not any(keyword in query.lower() for keyword in time_keywords):
                enhanced_query = f"latest {query}"
            
            # Perform search with focus on recent content
            result = self.deep_search(enhanced_query, max_results=8, depth=1)
            
            if result['success']:
                result['response'] = f"⏰ Real-time search results:\n\n{result['response']}"
                result['search_type'] = 'real_time'
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'query': query,
                'error': str(e),
                'response': f"❌ Real-time search failed: {str(e)}"
            }

# Global RAG search engine instance
rag_engine = WebRAGEngine()
