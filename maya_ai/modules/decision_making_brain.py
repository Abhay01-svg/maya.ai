"""
MAYA AI - Enhanced Decision Making Brain
Reads README.md to dynamically detect available capabilities
Intelligently routes tasks to appropriate systems
"""

import re
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class MayaDecisionBrain:
    """Intelligent decision-making brain that reads README.md and routes tasks"""
    
    def __init__(self):
        self.capability_map = {
            'models': {},
            'tools': {},
            'apis': {},
            'features': {}
        }
        self.readme_path = Path(__file__).parent.parent / 'README.md'
        self.last_readme_hash = None
        self.auto_refresh_enabled = True
        
        # Initialize by reading README.md
        self._read_capabilities()
        self._start_auto_refresh()
        
        logger.info("🧠 MAYA Decision Brain initialized with dynamic capability detection")
    
    def _read_capabilities(self):
        """Read README.md and build capability map"""
        try:
            if not self.readme_path.exists():
                logger.warning("⚠️ README.md not found, using default capabilities")
                self._set_default_capabilities()
                return
            
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calculate hash for change detection
            import hashlib
            current_hash = hashlib.md5(content.encode()).hexdigest()
            
            if self.last_readme_hash == current_hash:
                logger.debug("📄 README.md unchanged, skipping re-read")
                return
            
            self.last_readme_hash = current_hash
            logger.info("📖 Reading README.md to update capabilities...")
            
            # Parse README.md to build capability map
            self._parse_readme(content)
            
            logger.info(f"✅ Capabilities updated: {len(self.capability_map['models'])} models, "
                       f"{len(self.capability_map['tools'])} tools, "
                       f"{len(self.capability_map['apis'])} APIs, "
                       f"{len(self.capability_map['features'])} features")
            
        except Exception as e:
            logger.error(f"❌ Error reading README.md: {e}")
            self._set_default_capabilities()
    
    def _parse_readme(self, content: str):
        """Parse README.md content to extract capabilities"""
        current_section = None
        
        logger.debug(f"📖 Parsing README.md ({len(content)} chars)")
        
        for line in content.split('\n'):
            line_stripped = line.strip()
            
            # Detect sections
            if line_stripped.startswith('##'):
                section_text = line_stripped.replace('##', '').strip().lower()
                # Normalize section text (remove emojis for matching)
                import unicodedata
                section_text = unicodedata.normalize('NFKD', section_text).encode('ascii', 'ignore').decode('ascii').strip()
                
                # Map section names
                if 'models' in section_text:
                    current_section = 'models'
                    logger.debug(f"📂 Section: models")
                elif 'tools' in section_text:
                    current_section = 'tools'
                    logger.debug(f"📂 Section: tools")
                elif 'apis' in section_text:
                    current_section = 'apis'
                    logger.debug(f"📂 Section: apis")
                elif 'features' in section_text:
                    current_section = 'features'
                    logger.debug(f"📂 Section: features")
                continue
            
            # Skip subsection headers
            if line_stripped.startswith('###'):
                continue
            
            # Parse based on section
            if current_section == 'models':
                self._parse_models(line_stripped)
            elif current_section == 'tools':
                self._parse_tools(line_stripped)
            elif current_section == 'apis':
                self._parse_apis(line_stripped)
            elif current_section == 'features':
                self._parse_features(line_stripped)
    
    def _parse_models(self, line: str):
        """Parse model information"""
        # Skip subsection headers
        if line.startswith('###'):
            return
        # Parse model entries
        if line.startswith('-') and '**' in line:
            # Extract model name
            match = re.search(r'\*\*(.*?)\*\*', line)
            if match:
                model_name = match.group(1)
                # Extract description after the dash
                if '-' in line:
                    description = line.split('-', 1)[-1].strip()
                else:
                    description = "Available"
                self.capability_map['models'][model_name.lower()] = {
                    'name': model_name,
                    'description': description,
                    'available': True
                }
    
    def _parse_tools(self, line: str):
        """Parse tool information"""
        # Skip subsection headers
        if line.startswith('###'):
            return
        # Parse tool entries
        if line.startswith('-') and '**' in line:
            match = re.search(r'\*\*(.*?)\*\*', line)
            if match:
                tool_name = match.group(1).replace('.py', '')
                # Extract description after the dash
                if '-' in line:
                    description = line.split('-', 1)[-1].strip()
                else:
                    description = "Available"
                self.capability_map['tools'][tool_name.lower()] = {
                    'name': tool_name,
                    'description': description,
                    'available': True
                }
    
    def _parse_apis(self, line: str):
        """Parse API information"""
        # Skip subsection headers
        if line.startswith('###'):
            return
        # Parse API entries
        if line.startswith('-') and '**' in line:
            match = re.search(r'\*\*(.*?)\*\*', line)
            if match:
                api_name = match.group(1)
                # Extract description after the dash
                if '-' in line:
                    description = line.split('-', 1)[-1].strip()
                else:
                    description = "Available"
                self.capability_map['apis'][api_name.lower()] = {
                    'name': api_name,
                    'description': description,
                    'available': True
                }
    
    def _parse_features(self, line: str):
        """Parse feature information"""
        # Skip subsection headers
        if line.startswith('###'):
            return
        # Parse feature entries
        if line.startswith('-') and '**' in line:
            match = re.search(r'\*\*(.*?)\*\*', line)
            if match:
                feature_name = match.group(1)
                # Extract description after the dash
                if '-' in line:
                    description = line.split('-', 1)[-1].strip()
                else:
                    description = "Available"
                self.capability_map['features'][feature_name.lower()] = {
                    'name': feature_name,
                    'description': description,
                    'available': True
                }
    
    def _set_default_capabilities(self):
        """Set default capabilities if README.md not available"""
        logger.info("📋 Setting default capabilities...")
        
        self.capability_map = {
            'models': {
                'llama 3.2 3b': {'name': 'Llama 3.2 3B', 'description': 'General reasoning', 'available': True},
                'qwen coder': {'name': 'Qwen Coder', 'description': 'Programming', 'available': True},
                'moondream': {'name': 'Moondream', 'description': 'Vision', 'available': True}
            },
            'tools': {
                'calculator': {'name': 'calculator', 'description': 'Engineering math', 'available': True},
                'pc_control': {'name': 'pc_control', 'description': 'PC automation', 'available': True},
                'memory': {'name': 'memory', 'description': 'User memory', 'available': True},
                'search': {'name': 'search', 'description': 'Web search', 'available': True}
            },
            'apis': {
                'duckduckgo': {'name': 'DuckDuckGo', 'description': 'Search', 'available': True},
                'weather api': {'name': 'Weather API', 'description': 'Weather', 'available': True}
            },
            'features': {
                'voice input': {'name': 'Voice Input', 'description': 'Speech recognition', 'available': True},
                'voice output': {'name': 'Voice Output', 'description': 'Text-to-speech', 'available': True},
                'code generation': {'name': 'Code Generation', 'description': 'Programming', 'available': True}
            }
        }
    
    def _start_auto_refresh(self):
        """Start auto-refresh thread for README.md changes"""
        if not self.auto_refresh_enabled:
            return
        
        import threading
        
        def refresh_loop():
            while self.auto_refresh_enabled:
                time.sleep(60)  # Check every minute
                self._read_capabilities()
        
        refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        refresh_thread.start()
    
    def decide_module(self, context: str, message: str) -> Dict[str, Any]:
        """Decide which module should handle the request"""
        
        message_lower = message.lower()
        intent_type = self._detect_intent(message_lower)
        
        # Debug logging
        logger.info(f"🔍 Detected intent: {intent_type} for message: {message_lower}")
        
        # Route based on intent and available capabilities
        decision = self._route_intent(intent_type, message_lower)
        
        logger.info(f"🧠 Decision: {decision['primary_module']} (intent: {intent_type}, confidence: {decision['confidence']:.2f})")
        
        return decision
    
    def _detect_intent(self, message: str) -> str:
        """Detect the intent type of the message with comprehensive analysis"""
        
        message_lower = message.lower()
        
        # Priority 1: Direct math expressions (highest priority)
        if re.search(r'^[\d\s\+\-\*\/\(\)\.]+$', message):
            return 'calculation'
        
        # Priority 2: Trigonometric functions (before general math)
        trig_patterns = ['sin', 'cos', 'tan', 'sqrt', 'log', 'exp']
        if any(pattern in message_lower for pattern in trig_patterns):
            return 'calculation'
        
        # Priority 3: News queries (higher priority than general)
        news_patterns = ['news', 'headlines', 'breaking']
        if any(pattern in message_lower for pattern in news_patterns):
            return 'news'
        
        # Priority 4: Weather queries (higher priority than general)
        weather_patterns = ['weather', 'temperature', 'forecast', 'climate', 'rain', 'sunny', 'humid']
        if any(pattern in message_lower for pattern in weather_patterns):
            return 'weather'
        
        # Priority 5: Time queries
        time_patterns = ['time', 'date']
        if any(pattern in message_lower for pattern in time_patterns):
            return 'time_date'
        
        # Priority 6: Math expressions with keywords (must have numbers)
        math_patterns = ['calculate', 'math', 'add', 'subtract', 'multiply', 'divide', '=']
        # Only match if it has explicit math keywords AND numbers
        if any(pattern in message_lower for pattern in math_patterns) and re.search(r'\d', message):
            return 'calculation'
        
        # Priority 7: Coding Decision Logic
        coding_action_patterns = ['write code', 'make website', 'create script', 'fix error', 'debug code', 'build', 'develop']
        coding_concept_patterns = ['what is loop', 'explain function', 'what is api', 'explain', 'what does']
        
        has_coding_action = any(pattern in message_lower for pattern in coding_action_patterns)
        has_coding_concept = any(pattern in message_lower for pattern in coding_concept_patterns)
        coding_keywords = ['code', 'program', 'function', 'algorithm', 'python', 'javascript', 'java', 'html', 'css', 'fix', 'create']
        
        if has_coding_action or (any(keyword in message_lower for keyword in coding_keywords) and not has_coding_concept):
            return 'coding'
        
        # Priority 8: Vision / File Decision (before search)
        vision_patterns = ['screenshot', 'image', 'photo', 'picture', 'analyze screen', 'what is on screen', 'read image']
        file_patterns = ['pdf', 'document', 'file', 'read pdf', 'extract from', 'summarize pdf']
        
        if any(pattern in message_lower for pattern in vision_patterns):
            return 'vision'
        if any(pattern in message_lower for pattern in file_patterns):
            return 'document'
        
        # Priority 9: Search vs RAG Logic (only if not news/weather)
        # Quick live results: prices, scores, trends, specific facts
        live_info_keywords = ['latest', 'today', 'current', 'now', 'recent', 'live', 'updated', 'this week', 'breaking']
        has_live_info = any(keyword in message_lower for keyword in live_info_keywords)
        
        search_patterns = ['price', 'score', 'result', 'rate', 'value', 'cost', 'search', 'find', 'look for']
        # Only trigger search if not already matched by news/weather
        if (any(pattern in message_lower for pattern in search_patterns) or has_live_info) and not any(pattern in message_lower for pattern in news_patterns + weather_patterns):
            return 'search'
        
        # Deep research: analyze, summarize, research, detailed information
        rag_patterns = ['analyze', 'summarize', 'research', 'detailed', 'in-depth', 'explain in detail', 'comprehensive']
        if any(pattern in message_lower for pattern in rag_patterns):
            return 'rag'
        
        # Priority 10: Memory Decision
        memory_patterns = ['remember', 'save', 'yad rakhna', 'note this', 'store', 'keep this', 'future me yaad dilana']
        if any(pattern in message_lower for pattern in memory_patterns):
            return 'memory'
        
        # Priority 11: Automation / PC Control
        pc_patterns = ['open', 'close', 'shutdown', 'restart', 'volume', 'brightness', 'launch', 'start', 'stop', 'mute', 'screenshot', 'selfie', 'capture']
        if any(pattern in message_lower for pattern in pc_patterns):
            return 'pc_control'
        
        # Priority 12: Simple greetings
        greeting_patterns = ['hello', 'hi', 'hey', 'greetings']
        if any(pattern in message_lower for pattern in greeting_patterns):
            return 'greeting'
        
        # Default to general chat for timeless/general knowledge
        return 'general_chat'
    
    def _route_intent(self, intent_type: str, message: str) -> Dict[str, Any]:
        """Route intent to appropriate module based on available capabilities"""
        
        decision = {
            'primary_module': 'general_chat',
            'confidence': 0.70,
            'reasoning': 'Default routing',
            'requires_model': False,
            'model_type': None,
            'chain': []
        }
        
        # Coding - Use Qwen2.5 for coding tasks
        if intent_type == 'coding':
            if 'qwen2.5' in self.capability_map['models']:
                decision['primary_module'] = 'coding'
                decision['confidence'] = 0.95
                decision['reasoning'] = 'Qwen2.5 available for programming tasks'
                decision['requires_model'] = True
                decision['model_type'] = 'qwen2.5'
            elif 'qwen coder' in self.capability_map['models']:
                decision['primary_module'] = 'coding'
                decision['confidence'] = 0.90
                decision['reasoning'] = 'Qwen Coder available for programming tasks'
                decision['requires_model'] = True
                decision['model_type'] = 'qwen_coder'
            elif 'llama 3.2 3b' in self.capability_map['models']:
                decision['primary_module'] = 'coding'
                decision['confidence'] = 0.85
                decision['reasoning'] = 'Llama 3.2 available for coding'
                decision['requires_model'] = True
                decision['model_type'] = 'llama'
            else:
                decision['primary_module'] = 'coding'
                decision['confidence'] = 0.75
                decision['reasoning'] = 'No coding model available, using fallback'
        
        # News - Use News API
        elif intent_type == 'news':
            if 'news api' in self.capability_map['apis']:
                decision['primary_module'] = 'news_api'
                decision['confidence'] = 0.95
                decision['reasoning'] = 'News API available for live news'
            else:
                decision['primary_module'] = 'search_api'
                decision['confidence'] = 0.80
                decision['reasoning'] = 'News API not available, using search'
        
        # Weather - Use Weather API
        elif intent_type == 'weather':
            if 'weather api' in self.capability_map['apis']:
                decision['primary_module'] = 'weather_api'
                decision['confidence'] = 0.95
                decision['reasoning'] = 'Weather API available for live weather'
            else:
                decision['primary_module'] = 'search_api'
                decision['confidence'] = 0.80
                decision['reasoning'] = 'Weather API not available, using search'
        
        # Search - Use Search API
        elif intent_type == 'search':
            if 'duckduckgo' in self.capability_map['apis'] or 'serp api' in self.capability_map['apis']:
                decision['primary_module'] = 'search_api'
                decision['confidence'] = 0.95
                decision['reasoning'] = 'Search API available for live information'
            else:
                decision['primary_module'] = 'offline_model'
                decision['confidence'] = 0.70
                decision['reasoning'] = 'No search API, using offline knowledge'
                decision['requires_model'] = True
                decision['model_type'] = 'llama'
        
        # RAG - Use RAG for deep research
        elif intent_type == 'rag':
            if 'rag' in self.capability_map['features']:
                decision['primary_module'] = 'rag'
                decision['confidence'] = 0.95
                decision['reasoning'] = 'RAG available for deep research'
                decision['chain'] = ['search', 'rag']
            else:
                # Fallback to search + offline model
                decision['primary_module'] = 'search_api'
                decision['confidence'] = 0.80
                decision['reasoning'] = 'RAG not available, using search + model'
                decision['requires_model'] = True
                decision['model_type'] = 'llama'
                decision['chain'] = ['search', 'offline_model']
        
        # Vision - Use Vision model
        elif intent_type == 'vision':
            if 'moondream' in self.capability_map['models']:
                decision['primary_module'] = 'vision'
                decision['confidence'] = 0.95
                decision['reasoning'] = 'Moondream available for vision analysis'
                decision['requires_model'] = True
                decision['model_type'] = 'moondream'
            else:
                decision['primary_module'] = 'offline_model'
                decision['confidence'] = 0.70
                decision['reasoning'] = 'No vision model, using fallback'
                decision['requires_model'] = True
                decision['model_type'] = 'llama'
        
        # Document - Use PDF Reading + RAG
        elif intent_type == 'document':
            if 'pdf reading' in self.capability_map['features']:
                decision['primary_module'] = 'document'
                decision['confidence'] = 0.95
                decision['reasoning'] = 'PDF Reading available for document analysis'
                decision['requires_model'] = True
                decision['model_type'] = 'llama'
            else:
                decision['primary_module'] = 'offline_model'
                decision['confidence'] = 0.70
                decision['reasoning'] = 'Document features not available'
                decision['requires_model'] = True
                decision['model_type'] = 'llama'
        
        # Memory - Use Memory system
        elif intent_type == 'memory':
            if 'memory' in self.capability_map['tools']:
                decision['primary_module'] = 'memory'
                decision['confidence'] = 0.95
                decision['reasoning'] = 'Memory system available for storage/recall'
            else:
                decision['primary_module'] = 'offline_model'
                decision['confidence'] = 0.70
                decision['reasoning'] = 'Memory system not available'
                decision['requires_model'] = True
                decision['model_type'] = 'llama'
        
        # PC Control - Use PC Control
        elif intent_type == 'pc_control':
            if 'pc_control' in self.capability_map['tools']:
                decision['primary_module'] = 'pc_control'
                decision['confidence'] = 0.95
                decision['reasoning'] = 'PC Control available for automation'
            else:
                decision['primary_module'] = 'offline_model'
                decision['confidence'] = 0.70
                decision['reasoning'] = 'PC Control not available'
                decision['requires_model'] = True
                decision['model_type'] = 'llama'
        
        # Greeting - Use Llama 3.2
        elif intent_type == 'greeting':
            if 'llama 3.2 3b' in self.capability_map['models']:
                decision['primary_module'] = 'greeting'
                decision['confidence'] = 0.90
                decision['reasoning'] = 'Llama 3.2 available for conversation'
                decision['requires_model'] = True
                decision['model_type'] = 'llama'
            elif 'qwen2.5' in self.capability_map['models']:
                decision['primary_module'] = 'greeting'
                decision['confidence'] = 0.85
                decision['reasoning'] = 'Qwen2.5 available for conversation'
                decision['requires_model'] = True
                decision['model_type'] = 'qwen2.5'
            else:
                decision['primary_module'] = 'greeting'
                decision['confidence'] = 0.70
                decision['reasoning'] = 'No model available for greeting'
        
        # Time/Date - Use Time/Date module
        elif intent_type == 'time_date':
            # Always use time_date_module for time queries (module exists)
            decision['primary_module'] = 'time_date_module'
            decision['confidence'] = 0.95
            decision['reasoning'] = 'Time/Date module available for time queries'
        
        # Calculation - Use Calculator
        elif intent_type == 'calculation':
            if 'calculator' in self.capability_map['tools']:
                decision['primary_module'] = 'calculator'
                decision['confidence'] = 0.95
                decision['reasoning'] = 'Calculator available for math'
            else:
                decision['primary_module'] = 'offline_model'
                decision['confidence'] = 0.70
                decision['reasoning'] = 'Calculator not available, using model'
                decision['requires_model'] = True
                decision['model_type'] = 'llama'
        
        # Default to general chat
        else:
            decision['primary_module'] = 'general_chat'
            decision['confidence'] = 0.70
            decision['reasoning'] = 'Default routing'
        
        return decision

# Global instance
maya_decision_brain = MayaDecisionBrain()
