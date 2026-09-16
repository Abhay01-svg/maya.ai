#!/usr/bin/env python3
"""
🤖 MAYA AI - Advanced Personal Desktop Assistant
Unified Architecture - All modules in one file
Version: 2.0 | Last Updated: September 2026
"""

import os
import sys
import json
import re
import time
import threading
import subprocess
import logging
import argparse
import pickle
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import importlib

# ==================== CONFIGURATION ====================

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('maya_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Central configuration"""
    # API Keys
    WEATHER_API_KEY: str = os.getenv('WEATHER_API_KEY', '')
    SERP_API_KEY: str = os.getenv('SERP_API_KEY', '')
    NEWS_API_KEY: str = os.getenv('NEWS_API_KEY', '')
    
    # Model Configuration
    LLAMA_PATH: str = os.getenv('LLAMA_PATH', 'llama3.2:3b')
    QWEN_PATH: str = os.getenv('QWEN_PATH', 'qwen2.5-coder:3b')
    MOONDREAM_PATH: str = os.getenv('MOONDREAM_PATH', 'moondream:latest')
    
    # User Settings
    OWNER_NAME: str = os.getenv('OWNER_NAME', 'Bhai')
    WAKE_WORD: str = os.getenv('WAKE_WORD', 'Hey Maya')
    VOICE_ID: str = os.getenv('VOICE_ID', 'female_1')
    
    # Feature Flags
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    AUTO_LEARN: bool = os.getenv('AUTO_LEARN', 'True').lower() == 'true'
    HINGLISH_MODE: bool = os.getenv('HINGLISH_MODE', 'True').lower() == 'true'
    VOICE_MODE: bool = os.getenv('VOICE_MODE', 'False').lower() == 'true'
    OWNER_ONLY_MODE: bool = os.getenv('OWNER_ONLY_MODE', 'True').lower() == 'true'
    
    # Performance
    MAX_RESPONSE_TIME: int = int(os.getenv('MAX_RESPONSE_TIME', '30'))
    CACHE_ENABLED: bool = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'


# ==================== CALCULATOR MODULE ====================

class Calculator:
    """Engineering Mathematics Engine"""
    
    def __init__(self):
        self.logger = logging.getLogger('Calculator')
        self.last_result = None
        
    def parse_expression(self, expr: str) -> Optional[float]:
        """Parse and evaluate mathematical expression"""
        try:
            # Security: Only allow safe characters
            safe_chars = set('0123456789+-*/.()^ sincostan logln sqrtpiexabs ')
            if not all(c.lower() in safe_chars or c.isspace() for c in expr):
                return None
            
            # Replace common math functions
            expr = expr.lower()
            expr = expr.replace('sin', 'math.sin')
            expr = expr.replace('cos', 'math.cos')
            expr = expr.replace('tan', 'math.tan')
            expr = expr.replace('sqrt', 'math.sqrt')
            expr = expr.replace('log', 'math.log10')
            expr = expr.replace('ln', 'math.log')
            expr = expr.replace('pi', 'math.pi')
            expr = expr.replace('e', 'math.e')
            expr = expr.replace('^', '**')
            
            import math
            result = eval(expr, {"__builtins__": {}, "math": math})
            self.last_result = result
            return float(result)
        except Exception as e:
            self.logger.error(f"Calculation error: {e}")
            return None
    
    def calculate(self, query: str) -> str:
        """Process calculation request"""
        # Extract expression
        expr = query.replace('calculate', '').replace('?', '').strip()
        
        result = self.parse_expression(expr)
        if result is not None:
            return f"Result: {result}"
        return "Could not calculate. Check your expression."


# ==================== ROUTER MODULE ====================

class Router:
    """Intelligent Intent Detection and Routing"""
    
    def __init__(self):
        self.logger = logging.getLogger('Router')
        self.intent_patterns = {
            'calculation': [
                r'\d+\s*[\+\-\*\/\^]\s*\d+',
                r'calculate', r'math', r'solve',
                r'sin\d+', r'cos\d+', r'tan\d+'
            ],
            'weather': [r'weather', r'temperature', r'forecast', r'climate'],
            'news': [r'news', r'headlines', r'latest', r'trending'],
            'search': [r'search', r'find', r'look for', r'google'],
            'coding': [r'code', r'program', r'python', r'javascript', r'debug'],
            'pc_control': [r'open', r'close', r'run', r'launch', r'shutdown'],
            'time': [r'time', r'date', r'when', r'what time'],
            'memory': [r'remember', r'save', r'yad rakhna', r'note'],
            'general_chat': []
        }
    
    def detect_intent(self, query: str) -> Tuple[str, float]:
        """Detect user intent from query"""
        query_lower = query.lower()
        scores = defaultdict(float)
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    scores[intent] += 1.0
        
        if scores:
            best_intent = max(scores, key=scores.get)
            confidence = min(scores[best_intent] / len(self.intent_patterns[best_intent]), 1.0)
            return best_intent, confidence
        
        return 'general_chat', 0.5
    
    def extract_entities(self, query: str, intent: str) -> Dict[str, str]:
        """Extract entities from query"""
        entities = {}
        
        # City detection for weather
        cities = ['delhi', 'mumbai', 'bangalore', 'hyderabad', 'pune']
        for city in cities:
            if city in query.lower():
                entities['city'] = city
        
        # App detection for PC control
        apps = ['chrome', 'firefox', 'vs code', 'notepad', 'calculator']
        for app in apps:
            if app in query.lower():
                entities['app'] = app
        
        return entities


# ==================== MEMORY SYSTEM ====================

class Memory:
    """User Memory and Chat History Management"""
    
    def __init__(self, db_path: str = 'maya_memory.db'):
        self.logger = logging.getLogger('Memory')
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Chat history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_query TEXT,
                    maya_response TEXT,
                    intent TEXT,
                    confidence FLOAT
                )
            ''')
            
            # User memory
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_memory (
                    id INTEGER PRIMARY KEY,
                    key TEXT UNIQUE,
                    value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Habits
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY,
                    app_name TEXT,
                    usage_count INTEGER DEFAULT 1,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("✅ Database initialized")
        except Exception as e:
            self.logger.error(f"❌ DB init failed: {e}")
    
    def save_chat(self, user_query: str, response: str, intent: str, confidence: float):
        """Save chat to history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_history (user_query, maya_response, intent, confidence)
                VALUES (?, ?, ?, ?)
            ''', (user_query, response, intent, confidence))
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to save chat: {e}")
    
    def get_chat_history(self, limit: int = 10) -> List[Dict]:
        """Retrieve chat history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_query, maya_response, intent, timestamp
                FROM chat_history
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'query': row[0],
                    'response': row[1],
                    'intent': row[2],
                    'timestamp': row[3]
                })
            conn.close()
            return history
        except Exception as e:
            self.logger.error(f"Failed to get history: {e}")
            return []
    
    def remember(self, key: str, value: str):
        """Store user memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_memory (key, value)
                VALUES (?, ?)
            ''', (key, value))
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to remember: {e}")
    
    def recall(self, key: str) -> Optional[str]:
        """Retrieve user memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM user_memory WHERE key = ?', (key,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            self.logger.error(f"Failed to recall: {e}")
            return None


# ==================== HINGLISH PROCESSOR ====================

class HinglishProcessor:
    """Hinglish (Hindi + English) Response Generation"""
    
    def __init__(self):
        self.logger = logging.getLogger('HinglishProcessor')
        self.hinglish_greetings = [
            "Namaste bhai!",
            "Kya haal hai?",
            "Aaj kaisa din tha?",
            "Kya kaam hai?"
        ]
        self.hinglish_affirmations = {
            'yes': ["Bilkul", "Haan bhai", "Theek hai", "Done ho gaya"],
            'no': ["Nahi bhai", "Kuch nahi", "Aise kaise", "Na na na"],
            'thanks': ["Koi baat nahi", "Swagat hai", "Anytime bhai", "Busy rehta hoon"]
        }
    
    def convert_to_hinglish(self, text: str) -> str:
        """Convert English response to Hinglish"""
        # Simple conversion rules
        conversions = {
            'hello': 'namaste',
            'yes': 'haan',
            'no': 'nahi',
            'ok': 'theek hai',
            'good': 'accha',
            'bad': 'kharab'
        }
        
        text_lower = text.lower()
        for eng, hin in conversions.items():
            text_lower = text_lower.replace(eng, hin)
        
        return text_lower + " 😊"
    
    def add_personality(self, response: str, intent: str) -> str:
        """Add personality to response based on intent"""
        if intent == 'calculation':
            return f"Calculation kar diya! {response} ✨"
        elif intent == 'weather':
            return f"Mausam ki baat karte ho? {response} 🌤️"
        elif intent == 'pc_control':
            return f"Ho gaya bhai! {response} ✅"
        else:
            return f"{response} 😊"


# ==================== PC CONTROL MODULE ====================

class PCControl:
    """Windows PC Automation and Control"""
    
    def __init__(self):
        self.logger = logging.getLogger('PCControl')
        self.is_windows = sys.platform.startswith('win')
    
    def execute_command(self, command: str) -> str:
        """Execute system command"""
        try:
            if self.is_windows:
                if 'open' in command.lower():
                    app = command.split('open', 1)[1].strip()
                    os.system(f'start {app}')
                    return f"Opening {app}..."
                elif 'close' in command.lower():
                    return "Close command executed"
                elif 'screenshot' in command.lower():
                    os.system('screenshot')
                    return "Screenshot taken!"
            else:
                return "PC control not available on this platform"
        except Exception as e:
            self.logger.error(f"Command execution error: {e}")
            return "Error executing command"
    
    def get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        import platform
        return {
            'os': platform.system(),
            'version': platform.version(),
            'processor': platform.processor(),
            'python': platform.python_version()
        }


# ==================== API TOOLS ====================

class APITools:
    """External API Integration"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger('APITools')
    
    def get_weather(self, city: str) -> str:
        """Fetch weather data"""
        try:
            if not self.config.WEATHER_API_KEY:
                return "Weather API key not configured"
            
            # Simulated weather response
            return f"🌤️ {city}: 28°C, Clear skies, Humidity: 45%"
        except Exception as e:
            self.logger.error(f"Weather API error: {e}")
            return "Could not fetch weather"
    
    def search_web(self, query: str) -> List[str]:
        """Web search using available APIs"""
        try:
            # Simulated search results
            results = [
                f"Result 1: {query} information",
                f"Result 2: More details about {query}",
                f"Result 3: Additional resources"
            ]
            return results
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return []
    
    def get_news(self, category: str = 'general') -> List[str]:
        """Fetch news headlines"""
        try:
            # Simulated news
            news = [
                "Breaking: Tech industry seeing rapid growth",
                "AI advancement reaches new milestone",
                "Markets show positive trend today"
            ]
            return news
        except Exception as e:
            self.logger.error(f"News API error: {e}")
            return []


# ==================== DECISION MAKER ====================

class DecisionMaker:
    """Intelligent Decision Engine"""
    
    def __init__(self, config: Config, calculator: Calculator, router: Router, 
                 memory: Memory, api_tools: APITools, pc_control: PCControl):
        self.config = config
        self.logger = logging.getLogger('DecisionMaker')
        self.calculator = calculator
        self.router = router
        self.memory = memory
        self.api_tools = api_tools
        self.pc_control = pc_control
        self.hinglish = HinglishProcessor()
        self.cache = {}
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query and generate response"""
        start_time = time.time()
        
        # Check cache
        if self.config.CACHE_ENABLED and query in self.cache:
            self.logger.info(f"⚡ Cache hit for: {query}")
            return self.cache[query]
        
        # Detect intent
        intent, confidence = self.router.detect_intent(query)
        entities = self.router.extract_entities(query, intent)
        
        # Route to appropriate handler
        response = self._route_query(query, intent, entities)
        
        # Add personality if Hinglish mode
        if self.config.HINGLISH_MODE:
            response = self.hinglish.add_personality(response, intent)
        
        # Calculate response time
        response_time = (time.time() - start_time) * 1000
        
        result = {
            'response': response,
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'response_time_ms': response_time,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to memory
        self.memory.save_chat(query, response, intent, confidence)
        
        # Cache result
        if self.config.CACHE_ENABLED:
            self.cache[query] = result
        
        return result
    
    def _route_query(self, query: str, intent: str, entities: Dict) -> str:
        """Route query to appropriate handler"""
        handlers = {
            'calculation': self._handle_calculation,
            'weather': self._handle_weather,
            'news': self._handle_news,
            'search': self._handle_search,
            'pc_control': self._handle_pc_control,
            'time': self._handle_time,
            'memory': self._handle_memory,
            'coding': self._handle_coding,
            'general_chat': self._handle_chat
        }
        
        handler = handlers.get(intent, handlers['general_chat'])
        return handler(query, entities)
    
    def _handle_calculation(self, query: str, entities: Dict) -> str:
        return self.calculator.calculate(query)
    
    def _handle_weather(self, query: str, entities: Dict) -> str:
        city = entities.get('city', 'your location')
        return self.api_tools.get_weather(city)
    
    def _handle_news(self, query: str, entities: Dict) -> str:
        news = self.api_tools.get_news()
        return "📰 Latest News:\n" + "\n".join(news[:3])
    
    def _handle_search(self, query: str, entities: Dict) -> str:
        results = self.api_tools.search_web(query)
        return "🔍 Search Results:\n" + "\n".join(results[:3])
    
    def _handle_pc_control(self, query: str, entities: Dict) -> str:
        return self.pc_control.execute_command(query)
    
    def _handle_time(self, query: str, entities: Dict) -> str:
        return f"Current time: {datetime.now().strftime('%H:%M:%S on %Y-%m-%d')}"
    
    def _handle_memory(self, query: str, entities: Dict) -> str:
        if 'remember' in query.lower():
            return "I will remember this for you!"
        return "Retrieved from memory"
    
    def _handle_coding(self, query: str, entities: Dict) -> str:
        return "I can help with coding! What do you need?"
    
    def _handle_chat(self, query: str, entities: Dict) -> str:
        greetings = [
            "Hello! How can I help you today?",
            "Hi there! What's on your mind?",
            "Hey! Excited to chat with you!",
            "Hello bhai! Kya kaam hai?"
        ]
        import random
        return random.choice(greetings)


# ==================== MAIN CLI ====================

class MayaCLI:
    """Maya CLI Interface"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.logger = logging.getLogger('MayaCLI')
        
        # Initialize modules
        self.calculator = Calculator()
        self.router = Router()
        self.memory = Memory()
        self.api_tools = APITools(self.config)
        self.pc_control = PCControl()
        self.hinglish = HinglishProcessor()
        
        # Initialize decision maker
        self.brain = DecisionMaker(
            self.config, self.calculator, self.router, 
            self.memory, self.api_tools, self.pc_control
        )
        
        self.running = True
    
    def print_banner(self):
        """Print Maya banner"""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        🤖 MAYA AI - Unified Personal Assistant            ║
║      Smart • Fast • Intelligent • Multilingual             ║
║                                                           ║
║  Type 'help' for commands or start chatting with Maya!    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def cmd_help(self):
        """Show help"""
        help_text = """
📖 Available Commands:
  help          - Show this help
  status        - Show system status
  history       - Show chat history
  remember      - Save memory
  recall        - Retrieve memory
  exit/quit     - Exit Maya
  
💬 Just type anything to chat with Maya!
        """
        print(help_text)
    
    def cmd_status(self):
        """Show system status"""
        info = self.pc_control.get_system_info()
        print("\n🖥️  System Status:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    def cmd_history(self):
        """Show chat history"""
        history = self.memory.get_chat_history(5)
        print("\n📜 Chat History (last 5):")
        for item in history:
            print(f"  You: {item['query'][:50]}")
            print(f"  Maya: {item['response'][:50]}\n")
    
    def run_interactive(self):
        """Interactive mode"""
        self.print_banner()
        print(f"👋 Hello {self.config.OWNER_NAME}!\n")
        
        while self.running:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() == 'exit' or user_input.lower() == 'quit':
                    print("👋 Goodbye! See you soon!")
                    break
                elif user_input.lower() == 'help':
                    self.cmd_help()
                elif user_input.lower() == 'status':
                    self.cmd_status()
                elif user_input.lower() == 'history':
                    self.cmd_history()
                else:
                    # Process as query
                    result = self.brain.process_query(user_input)
                    print(f"\nMaya: {result['response']}\n")
                    print(f"[{result['intent']} | {result['confidence']:.1%} confidence]\n")
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted. Type 'exit' to quit.")
            except Exception as e:
                self.logger.error(f"Error: {e}")
                print(f"❌ Error: {e}")
    
    def run_single_query(self, query: str):
        """Single query mode"""
        result = self.brain.process_query(query)
        print(f"\nMaya: {result['response']}")


# ==================== MAIN ENTRY POINT ====================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🤖 Maya AI - Unified Personal Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('query', nargs='*', help='Query for Maya')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--history', action='store_true', help='Show chat history')
    parser.add_argument('--version', action='version', version='Maya AI v2.0')
    
    args = parser.parse_args()
    
    # Initialize Maya
    maya = MayaCLI()
    
    # Handle modes
    if args.status:
        maya.cmd_status()
    elif args.history:
        maya.cmd_history()
    elif args.query:
        query = " ".join(args.query)
        maya.run_single_query(query)
    else:
        maya.run_interactive()


if __name__ == "__main__":
    print("🚀 Starting Maya AI...\n")
    main()
