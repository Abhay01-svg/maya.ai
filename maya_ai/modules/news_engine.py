"""
Maya AI Latest News Engine
Real-time news aggregation with web search and intelligent summarization
"""

import logging
import time
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from config import DEBUG_MODE
from .tools import news_api, search_api
from .rag_search import rag_engine

logger = logging.getLogger(__name__)

class NewsEngine:
    """Advanced news engine with real-time updates and intelligent analysis"""
    
    def __init__(self):
        self.news_categories = {
            'general': ['latest news', 'today news', 'current news', 'breaking news'],
            'business': ['market news', 'stock news', 'business news', 'economy news'],
            'technology': ['tech news', 'AI news', 'technology news', 'startup news'],
            'sports': ['sports news', 'cricket news', 'football news', 'match results'],
            'politics': ['political news', 'election news', 'government news'],
            'entertainment': ['movie news', 'celebrity news', 'entertainment news'],
            'science': ['science news', 'research news', 'discovery news'],
            'health': ['health news', 'medical news', 'covid news']
        }
        
        self.news_sources = [
            'reuters', 'bbc', 'cnn', 'al jazeera', 'associated press',
            'hindustan times', 'times of india', 'the hindu', 'indian express',
            'techcrunch', 'wired', 'venturebeat', 'the verge'
        ]
        
        self.time_patterns = [
            r'(?:today|today\'s|current|latest|breaking|live|real-time)',
            r'(?:this morning|this afternoon|this evening)',
            r'(?:yesterday|last night)',
            r'(?:past 24 hours|last 24 hours)',
            r'(?:this week|recent)'
        ]
        
        if DEBUG_MODE:
            logger.info("📰 Latest News Engine initialized")
    
    def get_latest_news(self, query: str = None, category: str = None, 
                       max_articles: int = 10, include_analysis: bool = True) -> Dict:
        """Get latest news with intelligent analysis"""
        start_time = time.time()
        
        try:
            # Determine search strategy
            search_query = self._build_news_query(query, category)
            
            # Get news from multiple sources
            news_results = self._aggregate_news(search_query, max_articles)
            
            if not news_results:
                return {
                    'success': False,
                    'query': search_query,
                    'error': 'No news found',
                    'response': f"❌ '{search_query}' ke liye koi news nahi mili"
                }
            
            # Analyze news if requested
            analysis = None
            if include_analysis:
                analysis = self._analyze_news(news_results, query, category)
            
            # Generate comprehensive response
            response = self._generate_news_response(news_results, analysis, query, category)
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'query': search_query,
                'category': category,
                'news_results': news_results,
                'analysis': analysis,
                'processing_time': processing_time,
                'articles_found': len(news_results),
                'response': response
            }
            
        except Exception as e:
            logger.error(f"❌ News engine error: {e}")
            return {
                'success': False,
                'query': query,
                'error': str(e),
                'response': f"❌ News fetch mein error: {str(e)}"
            }
    
    def _build_news_query(self, query: str, category: str) -> str:
        """Build optimized news search query"""
        base_query = ""
        
        # Add time keywords for latest news
        if query and any(re.search(pattern, query, re.IGNORECASE) for pattern in self.time_patterns):
            base_query = query
        elif category:
            # Use category-specific keywords
            category_keywords = self.news_categories.get(category, self.news_categories['general'])
            base_query = f"latest {category_keywords[0]}"
        else:
            # Default to latest news
            base_query = "latest breaking news today"
        
        # Add source diversity
        if not query or category:
            source_filter = f"site:{self.news_sources[0]} OR site:{self.news_sources[1]}"
            base_query += f" {source_filter}"
        
        return base_query
    
    def _aggregate_news(self, search_query: str, max_articles: int) -> List[Dict]:
        """Aggregate news from multiple sources"""
        all_news = []
        
        # Method 1: Use news API
        try:
            news_results = news_api.get_hinglish_news(search_query, limit=max_articles//2)
            if news_results and not news_results.startswith('❌'):
                # Parse news results (simplified)
                parsed_news = self._parse_news_results(news_results, 'news_api')
                all_news.extend(parsed_news)
        except Exception as e:
            logger.warning(f"⚠️  News API failed: {e}")
        
        # Method 2: Use web search for additional sources
        try:
            web_results = rag_engine.deep_search(search_query, max_results=max_articles//2, depth=1)
            if web_results['success']:
                web_news = self._convert_web_to_news(web_results)
                all_news.extend(web_news)
        except Exception as e:
            logger.warning(f"⚠️  Web search failed: {e}")
        
        # Remove duplicates and sort by relevance
        unique_news = self._deduplicate_news(all_news)
        
        return unique_news[:max_articles]
    
    def _parse_news_results(self, news_text: str, source: str) -> List[Dict]:
        """Parse news API results"""
        news_items = []
        
        # Simple parsing - would be more sophisticated in production
        lines = news_text.split('\n')
        current_item = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith(f"{len(news_items)+1}."):
                if current_item:
                    news_items.append(current_item)
                current_item = {
                    'title': line[3:].strip(),
                    'source': source,
                    'timestamp': datetime.now().isoformat()
                }
            elif line.startswith('   '):
                if 'description' not in current_item:
                    current_item['description'] = line[3:].strip()
                elif 'url' not in current_item and 'http' in line:
                    current_item['url'] = line.split('Link:')[-1].strip()
        
        if current_item:
            news_items.append(current_item)
        
        return news_items
    
    def _convert_web_to_news(self, web_results: Dict) -> List[Dict]:
        """Convert web search results to news format"""
        news_items = []
        
        for result in web_results.get('search_results', []):
            news_item = {
                'title': result.get('title', ''),
                'description': result.get('snippet', ''),
                'url': result.get('link', ''),
                'source': 'web_search',
                'timestamp': datetime.now().isoformat()
            }
            news_items.append(news_item)
        
        return news_items
    
    def _deduplicate_news(self, news_items: List[Dict]) -> List[Dict]:
        """Remove duplicate news items"""
        seen_titles = set()
        unique_news = []
        
        for item in news_items:
            title = item.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(item)
        
        return unique_news
    
    def _analyze_news(self, news_results: List[Dict], query: str, category: str) -> Dict:
        """Analyze news patterns and insights"""
        try:
            analysis = {
                'trending_topics': [],
                'sentiment_summary': {},
                'source_diversity': {},
                'time_distribution': {},
                'key_insights': []
            }
            
            # Extract trending topics
            all_titles = [item.get('title', '') for item in news_results]
            analysis['trending_topics'] = self._extract_trending_topics(all_titles)
            
            # Analyze source diversity
            sources = [item.get('source', 'unknown') for item in news_results]
            analysis['source_diversity'] = self._analyze_source_diversity(sources)
            
            # Generate key insights
            analysis['key_insights'] = self._generate_news_insights(news_results, query, category)
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ News analysis error: {e}")
            return {'error': str(e)}
    
    def _extract_trending_topics(self, titles: List[str]) -> List[str]:
        """Extract trending topics from news titles"""
        # Simple keyword extraction - would use NLP in production
        common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should']
        
        word_count = {}
        for title in titles:
            words = re.findall(r'\b\w+\b', title.lower())
            for word in words:
                if word not in common_words and len(word) > 2:
                    word_count[word] = word_count.get(word, 0) + 1
        
        # Get top trending topics
        trending = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:5]
        return [f"{word} ({count} mentions)" for word, count in trending]
    
    def _analyze_source_diversity(self, sources: List[str]) -> Dict:
        """Analyze source diversity"""
        source_count = {}
        for source in sources:
            source_count[source] = source_count.get(source, 0) + 1
        
        return {
            'total_sources': len(source_count),
            'source_distribution': source_count,
            'most_frequent': max(source_count.items(), key=lambda x: x[1]) if source_count else None
        }
    
    def _generate_news_insights(self, news_results: List[Dict], query: str, category: str) -> List[str]:
        """Generate key insights from news"""
        insights = []
        
        # Basic insights
        insights.append(f"Found {len(news_results)} relevant news articles")
        
        # Category-specific insights
        if category:
            insights.append(f"Focused on {category} news category")
        
        # Query-specific insights
        if query:
            insights.append(f"Tailored to your query: {query}")
        
        # Time-based insights
        current_hour = datetime.now().hour
        if 6 <= current_hour <= 12:
            insights.append("Morning news update - fresh articles available")
        elif 12 <= current_hour <= 18:
            insights.append("Afternoon news - comprehensive coverage")
        else:
            insights.append("Evening/night news - latest developments")
        
        # Source insights
        unique_sources = len(set(item.get('source', 'unknown') for item in news_results))
        if unique_sources > 3:
            insights.append(f"Comprehensive coverage from {unique_sources} different sources")
        
        return insights
    
    def _generate_news_response(self, news_results: List[Dict], analysis: Dict, 
                              query: str, category: str) -> str:
        """Generate comprehensive Hinglish news response"""
        response_parts = []
        
        # Header
        if query:
            response_parts.append(f"📰 Latest News for: {query}")
        elif category:
            response_parts.append(f"📰 {category.title()} News Updates")
        else:
            response_parts.append("📰 Latest Breaking News")
        
        # Key insights
        if analysis and analysis.get('key_insights'):
            response_parts.append(f"\n💡 Key Insights:")
            for insight in analysis['key_insights']:
                response_parts.append(f"• {insight}")
        
        # Trending topics
        if analysis and analysis.get('trending_topics'):
            response_parts.append(f"\n🔥 Trending Topics:")
            for topic in analysis['trending_topics']:
                response_parts.append(f"• {topic}")
        
        # News articles
        response_parts.append(f"\n📰 Top News Stories:")
        for i, article in enumerate(news_results[:5], 1):
            title = article.get('title', 'No title')
            description = article.get('description', 'No description')
            source = article.get('source', 'Unknown')
            
            response_parts.append(f"{i}. {title}")
            if description and description != 'No description':
                response_parts.append(f"   {description[:120]}...")
            response_parts.append(f"   Source: {source}")
        
        # Source diversity
        if analysis and analysis.get('source_diversity'):
            source_div = analysis['source_diversity']
            response_parts.append(f"\n📊 Coverage Analysis:")
            response_parts.append(f"• Total sources: {source_div.get('total_sources', 0)}")
            
            if source_div.get('most_frequent'):
                most_freq_source, count = source_div['most_frequent']
                response_parts.append(f"• Most active: {most_freq_source} ({count} articles)")
        
        return '\n'.join(response_parts)
    
    def get_market_news(self, symbols: List[str] = None) -> Dict:
        """Get market and financial news"""
        try:
            market_query = "latest market news stock market financial news"
            
            if symbols:
                symbol_query = " ".join([f"{symbol} stock news" for symbol in symbols[:3]])
                market_query += f" {symbol_query}"
            
            return self.get_latest_news(market_query, category='business', max_articles=8)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ Market news failed: {str(e)}"
            }
    
    def get_sports_news(self, sports: List[str] = None) -> Dict:
        """Get sports news"""
        try:
            sports_query = "latest sports news"
            
            if sports:
                sports_query += " " + " ".join([f"{sport} news" for sport in sports[:3]])
            
            return self.get_latest_news(sports_query, category='sports', max_articles=8)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ Sports news failed: {str(e)}"
            }
    
    def get_tech_news(self, topics: List[str] = None) -> Dict:
        """Get technology news"""
        try:
            tech_query = "latest technology news AI news startup news"
            
            if topics:
                tech_query += " " + " ".join([f"{topic} tech news" for topic in topics[:3]])
            
            return self.get_latest_news(tech_query, category='technology', max_articles=8)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ Tech news failed: {str(e)}"
            }
    
    def compare_news_sources(self, query: str, sources: List[str] = None) -> Dict:
        """Compare news from different sources"""
        try:
            if not sources:
                sources = self.news_sources[:4]  # Use top 4 sources by default
            
            comparison_results = []
            
            for source in sources:
                source_query = f"{query} site:{source}"
                result = self.get_latest_news(source_query, max_articles=3, include_analysis=False)
                
                if result['success']:
                    comparison_results.append({
                        'source': source,
                        'articles': result['news_results'],
                        'count': len(result['news_results'])
                    })
            
            # Generate comparison
            comparison = self._generate_source_comparison(comparison_results, query)
            
            return {
                'success': True,
                'query': query,
                'sources_compared': sources,
                'comparison_results': comparison_results,
                'comparison': comparison,
                'response': comparison
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ Source comparison failed: {str(e)}"
            }
    
    def _generate_source_comparison(self, results: List[Dict], query: str) -> str:
        """Generate source comparison analysis"""
        comparison_parts = []
        
        comparison_parts.append(f"📰 News Source Comparison for: {query}")
        
        for result in results:
            source = result['source']
            articles = result['articles']
            count = result['count']
            
            comparison_parts.append(f"\n📡 {source.title()}:")
            comparison_parts.append(f"   Articles found: {count}")
            
            if articles:
                top_article = articles[0]
                comparison_parts.append(f"   Top story: {top_article.get('title', 'No title')}")
        
        return '\n'.join(comparison_parts)

# Global news engine instance
news_engine = NewsEngine()
