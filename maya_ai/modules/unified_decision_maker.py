"""
MAYA AI - Unified Decision Making Brain
=======================================
Intelligent request analysis and routing system that:
1. Understands user intent accurately
2. Detects if request needs live/current information
3. Routes to best model, API, or feature
4. Manages fallback chains and multi-step workflows

Features:
- NLP-based classification with spaCy
- Dynamic capability mapping from README.md
- Comprehensive intent detection with priorities
- Intelligent fallback chains
- Multi-step workflow orchestration
"""

import time
import logging
import re
import hashlib
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import spaCy for NLP processing
try:
    import spacy
    SPACY_AVAILABLE = True
    nlp = spacy.load("en_core_web_sm")
    logger.info("🧠 spaCy NLP model loaded for enhanced decision making")
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None
    logger.warning("⚠️ spaCy not available, using rule-based classification")
except Exception as e:
    SPACY_AVAILABLE = False
    nlp = None
    logger.error(f"❌ Failed to load spaCy model: {e}")


class OllamaManager:
    """Manages Ollama service lifecycle"""
    
    def __init__(self):
        self.is_running = False
    
    def is_ollama_running(self) -> bool:
        """Check if Ollama is running"""
        try:
            import subprocess
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            self.is_running = result.returncode == 0
            return self.is_running
        except:
            self.is_running = False
            return False
    
    def start_ollama(self):
        """Start Ollama service"""
        try:
            import subprocess
            subprocess.Popen(['ollama', 'serve'], shell=True)
            time.sleep(2)
            self.is_running = True
            logger.info("✅ Ollama service started")
        except Exception as e:
            logger.error(f"❌ Failed to start Ollama: {e}")
    
    def stop_ollama(self):
        """Stop Ollama service"""
        try:
            import subprocess
            subprocess.run(['pkill', '-f', 'ollama'], capture_output=True)
            self.is_running = False
            logger.info("✅ Ollama service stopped")
        except Exception as e:
            logger.error(f"❌ Failed to stop Ollama: {e}")


class UnifiedDecisionMaker:
    """
    Intelligent decision-making brain that:
    - Analyzes user requests with NLP
    - Detects live vs historical information needs
    - Routes to best available model/API/tool
    - Handles fallback chains
    """
    
    def __init__(self):
        """Initialize the decision maker"""
        self.ollama = OllamaManager()
        
        # Capability mapping
        self.capability_map = {
            'models': {},
            'tools': {},
            'apis': {},
            'features': {}
        }
        
        # README.md auto-refresh
        self.readme_path = Path(__file__).parent.parent / 'README.md'
        self.last_readme_hash = None
        self.auto_refresh_enabled = True
        
        # Backward compatibility attributes
        self.available_modules = [
            "calculator", "weather_api", "news_api", "search_api", 
            "pc_control", "memory", "qwen_coder", "llama_general", 
            "time_date_module", "vision", "document", "coding"
        ]
        self.module_performance = {}
        
        # Intent classification keywords
        self.intent_keywords = {
            'calculation': {
                'keywords': ["calculate", "compute", "solve", "add", "subtract", "multiply", 
                           "divide", "square", "cube", "root", "power", "equation", "math"],
                'patterns': [r'^[\d\s\+\-\*\/\(\)\.]+$', r'sin|cos|tan|sqrt|log|exp'],
                'priority': 1
            },
            'weather': {
                'keywords': ["weather", "temperature", "forecast", "rain", "sunny", "climate", 
                           "humid", "wind", "precipitation", "weather"],
                'priority': 2
            },
            'news': {
                'keywords': ["news", "headlines", "breaking", "latest", "current events", 
                           "updates", "breaking news"],
                'priority': 3
            },
            'time_date': {
                'keywords': ["time", "date", "current time", "what time", "now", "timezone", 
                           "convert time", "world time"],
                'priority': 4
            },
            'search': {
                'keywords': ["search", "find", "look for", "information about", "tell me about"],
                'live_keywords': ["latest", "today", "current", "now", "recent", "live", 
                                "updated", "breaking"],
                'priority': 5
            },
            'coding': {
                'action_keywords': ["write code", "make website", "create script", "fix error", 
                                   "debug code", "build", "develop", "code"],
                'concept_keywords': ["what is loop", "explain function", "what is api"],
                'priority': 6
            },
            'vision': {
                'keywords': ["screenshot", "image", "photo", "picture", "analyze screen", 
                           "read image", "what is on screen"],
                'priority': 7
            },
            'document': {
                'keywords': ["pdf", "document", "file", "read pdf", "extract from", "summarize"],
                'priority': 8
            },
            'memory': {
                'keywords': ["remember", "save", "note", "store", "keep this", "yad rakhna", 
                           "future me yaad dilana"],
                'priority': 9
            },
            'pc_control': {
                'keywords': ["open", "close", "launch", "start", "stop", "shutdown", "restart", 
                           "mute", "screenshot", "volume", "brightness"],
                'priority': 10
            },
            'greeting': {
                'keywords': ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"],
                'priority': 11
            }
        }
        
        # Initialize capabilities
        self._read_capabilities()
        self._start_auto_refresh()
        
        logger.info("🧠 Unified Decision Maker initialized")
    
    # ==================== Capability Management ====================
    
    def _read_capabilities(self):
        """Read README.md and build capability map"""
        try:
            if not self.readme_path.exists():
                logger.warning("⚠️ README.md not found, using default capabilities")
                self._set_default_capabilities()
                return
            
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if content changed
            current_hash = hashlib.md5(content.encode()).hexdigest()
            if self.last_readme_hash == current_hash:
                return
            
            self.last_readme_hash = current_hash
            self._parse_readme(content)
            
            logger.info(f"✅ Capabilities updated: {len(self.capability_map['models'])} models, "
                       f"{len(self.capability_map['tools'])} tools, "
                       f"{len(self.capability_map['apis'])} APIs")
            
        except Exception as e:
            logger.error(f"❌ Error reading README.md: {e}")
            self._set_default_capabilities()
    
    def _parse_readme(self, content: str):
        """Parse README.md to extract capabilities"""
        current_section = None
        
        for line in content.split('\n'):
            line_stripped = line.strip()
            
            if line_stripped.startswith('##'):
                section_text = line_stripped.replace('##', '').strip().lower()
                import unicodedata
                section_text = unicodedata.normalize('NFKD', section_text).encode('ascii', 'ignore').decode('ascii').strip()
                
                if 'models' in section_text:
                    current_section = 'models'
                elif 'tools' in section_text:
                    current_section = 'tools'
                elif 'apis' in section_text:
                    current_section = 'apis'
                elif 'features' in section_text:
                    current_section = 'features'
                continue
            
            if line_stripped.startswith('###'):
                continue
            
            # Parse entries
            if current_section and line_stripped.startswith('-') and '**' in line_stripped:
                match = re.search(r'\*\*(.*?)\*\*', line_stripped)
                if match:
                    name = match.group(1).replace('.py', '')
                    description = line_stripped.split('-', 1)[-1].strip() if '-' in line_stripped else "Available"
                    self.capability_map[current_section][name.lower()] = {
                        'name': name,
                        'description': description,
                        'available': True
                    }
    
    def _set_default_capabilities(self):
        """Set default capabilities"""
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
                'weather api': {'name': 'Weather API', 'description': 'Weather', 'available': True},
                'news api': {'name': 'News API', 'description': 'News', 'available': True}
            },
            'features': {
                'voice input': {'name': 'Voice Input', 'description': 'Speech recognition', 'available': True},
                'voice output': {'name': 'Voice Output', 'description': 'Text-to-speech', 'available': True},
                'code generation': {'name': 'Code Generation', 'description': 'Programming', 'available': True},
                'rag': {'name': 'RAG', 'description': 'Deep research', 'available': True}
            }
        }
    
    def _start_auto_refresh(self):
        """Auto-refresh capabilities every minute"""
        if not self.auto_refresh_enabled:
            return
        
        def refresh_loop():
            while self.auto_refresh_enabled:
                time.sleep(60)
                self._read_capabilities()
        
        refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        refresh_thread.start()
    
    # ==================== Intent Detection & Classification ====================
    
    def _detect_intent_nlp(self, message: str) -> Tuple[str, float, str]:
        """Use spaCy NLP for accurate intent classification"""
        if not SPACY_AVAILABLE or not nlp:
            return self._detect_intent_rule_based(message)
        
        try:
            doc = nlp(message.lower())
            entities = [ent.text for ent in doc.ents]
            tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
            
            # Mathematical patterns
            math_indicators = ["+", "-", "*", "/", "=", "calculate", "compute", "solve", 
                             "square", "cube", "root", "power"]
            if any(indicator in message.lower() for indicator in math_indicators):
                return "calculation", 0.95, "Mathematical expression detected via NLP"
            
            # Weather queries
            weather_keywords = ["weather", "temperature", "forecast", "climate", "rain", "sunny"]
            if any(keyword in message.lower() for keyword in weather_keywords):
                return "weather", 0.92, "Weather query detected via NLP"
            
            # News queries
            news_keywords = ["news", "headlines", "breaking"]
            if any(keyword in message.lower() for keyword in news_keywords):
                return "news", 0.90, "News query detected via NLP"
            
            # Coding detection
            code_keywords = ["code", "program", "script", "function", "debug", "error"]
            if any(keyword in message.lower() for keyword in code_keywords):
                return "coding", 0.88, "Programming query detected via NLP"
            
            # Time/Date detection
            time_keywords = ["time", "date", "timezone", "convert time"]
            if any(keyword in message.lower() for keyword in time_keywords):
                return "time_date", 0.95, "Time/Date query detected via NLP"
            
            # PC Control detection
            control_verbs = ["open", "close", "launch", "start", "stop", "shutdown"]
            if any(verb in tokens for verb in control_verbs):
                return "pc_control", 0.92, "Control command detected via NLP"
            
            # Greeting detection
            greeting_tokens = ["hello", "hi", "hey", "good", "morning"]
            if any(token in greeting_tokens for token in tokens) and len(tokens) <= 3:
                return "greeting", 0.90, "Greeting detected via NLP"
            
            return "general_chat", 0.70, "General conversation detected via NLP"
            
        except Exception as e:
            logger.error(f"NLP classification error: {e}")
            return self._detect_intent_rule_based(message)
    
    def _detect_intent_rule_based(self, message: str) -> Tuple[str, float, str]:
        """Fallback rule-based intent classification"""
        message_lower = message.lower()
        
        # Priority-based detection
        intents_by_priority = [
            ('calculation', ["+", "-", "*", "/", "calculate", "solve", "math"]),
            ('weather', ["weather", "temperature", "forecast", "rain", "sunny"]),
            ('news', ["news", "headlines", "breaking"]),
            ('time_date', ["time", "date", "timezone"]),
            ('coding', ["code", "program", "script", "debug", "error"]),
            ('vision', ["screenshot", "image", "photo", "analyze screen"]),
            ('document', ["pdf", "document", "read file"]),
            ('memory', ["remember", "save", "note", "yad rakhna"]),
            ('pc_control', ["open", "close", "launch", "shutdown"]),
            ('greeting', ["hello", "hi", "hey", "good morning"])
        ]
        
        for intent, keywords in intents_by_priority:
            if any(keyword in message_lower for keyword in keywords):
                return intent, 0.80, f"Intent detected: {intent}"
        
        return "general_chat", 0.60, "Default classification"
    
    def _has_live_info_keywords(self, message: str) -> bool:
        """Check if message requests live/current information"""
        live_keywords = ["latest", "today", "current", "now", "recent", "live", 
                        "updated", "breaking", "this week", "today's"]
        return any(keyword in message.lower() for keyword in live_keywords)
    
    # ==================== Decision Making & Routing ====================
    
    def decide(self, message: str) -> Dict[str, Any]:
        """
        Main decision-making function
        
        Returns:
        {
            'intent': str,
            'confidence': float,
            'reasoning': str,
            'primary_module': str,
            'fallback_modules': List[str],
            'requires_model': bool,
            'model_type': str,
            'chain': List[str],
            'classification_method': str,
            'requires_live_info': bool
        }
        """
        
        # Step 1: Detect intent
        if SPACY_AVAILABLE:
            intent, confidence, nlp_reasoning = self._detect_intent_nlp(message)
            classification_method = "NLP"
        else:
            intent, confidence, nlp_reasoning = self._detect_intent_rule_based(message)
            classification_method = "Rule-based"
        
        # Step 2: Check if live info is needed
        requires_live_info = self._has_live_info_keywords(message)
        
        # Step 3: Route to best module
        decision = self._route_to_module(intent, message, requires_live_info)
        
        # Step 4: Build final decision
        final_decision = {
            'intent': intent,
            'confidence': confidence,
            'reasoning': nlp_reasoning,
            'requires_live_info': requires_live_info,
            'classification_method': classification_method,
            **decision
        }
        
        logger.info(f"🎯 Decision: {decision['primary_module']} (intent: {intent}, confidence: {confidence:.2f})")
        
        return final_decision
    
    def _route_to_module(self, intent: str, message: str, requires_live_info: bool) -> Dict[str, Any]:
        """Route intent to appropriate module based on capabilities and needs"""
        
        base_decision = {
            'primary_module': 'general_chat',
            'fallback_modules': ['brain'],
            'requires_model': False,
            'model_type': None,
            'chain': []
        }
        
        # ============ CALCULATION ============
        if intent == 'calculation':
            if 'calculator' in self.capability_map['tools']:
                return {
                    'primary_module': 'calculator',
                    'fallback_modules': ['llama_general', 'qwen_coder'],
                    'requires_model': False,
                    'chain': []
                }
        
        # ============ WEATHER ============
        elif intent == 'weather':
            if 'weather api' in self.capability_map['apis']:
                return {
                    'primary_module': 'weather_api',
                    'fallback_modules': ['search_api', 'llama_general'],
                    'requires_model': False,
                    'chain': []
                }
        
        # ============ NEWS ============
        elif intent == 'news':
            if 'news api' in self.capability_map['apis']:
                return {
                    'primary_module': 'news_api',
                    'fallback_modules': ['search_api', 'llama_general'],
                    'requires_model': False,
                    'chain': []
                }
            else:
                return {
                    'primary_module': 'search_api',
                    'fallback_modules': ['llama_general'],
                    'requires_model': False,
                    'chain': []
                }
        
        # ============ TIME/DATE ============
        elif intent == 'time_date':
            return {
                'primary_module': 'time_date_module',
                'fallback_modules': ['llama_general'],
                'requires_model': False,
                'chain': []
            }
        
        # ============ SEARCH (Live Info) ============
        elif intent == 'search' or (requires_live_info and intent == 'general_chat'):
            if requires_live_info:
                if 'duckduckgo' in self.capability_map['apis'] or 'search' in self.capability_map['tools']:
                    return {
                        'primary_module': 'search_api',
                        'fallback_modules': ['llama_general'],
                        'requires_model': False,
                        'chain': ['search', 'summarize'] if 'rag' in self.capability_map['features'] else ['search']
                    }
            return {
                'primary_module': 'llama_general',
                'fallback_modules': ['brain'],
                'requires_model': True,
                'model_type': 'llama',
                'chain': []
            }
        
        # ============ CODING ============
        elif intent == 'coding':
            best_model = self._select_best_model(['qwen2.5', 'qwen coder', 'llama 3.2 3b'])
            return {
                'primary_module': 'coding',
                'fallback_modules': ['llama_general'],
                'requires_model': True,
                'model_type': best_model,
                'chain': ['code_generation', 'syntax_check']
            }
        
        # ============ VISION ============
        elif intent == 'vision':
            if 'moondream' in self.capability_map['models']:
                return {
                    'primary_module': 'vision',
                    'fallback_modules': ['llama_general'],
                    'requires_model': True,
                    'model_type': 'moondream',
                    'chain': ['vision_analysis', 'describe']
                }
        
        # ============ DOCUMENT ============
        elif intent == 'document':
            return {
                'primary_module': 'document',
                'fallback_modules': ['llama_general'],
                'requires_model': True,
                'model_type': 'llama',
                'chain': ['pdf_read', 'rag_summarize'] if 'rag' in self.capability_map['features'] else ['pdf_read']
            }
        
        # ============ MEMORY ============
        elif intent == 'memory':
            if 'memory' in self.capability_map['tools']:
                return {
                    'primary_module': 'memory',
                    'fallback_modules': ['llama_general'],
                    'requires_model': False,
                    'chain': []
                }
        
        # ============ PC CONTROL ============
        elif intent == 'pc_control':
            if 'pc_control' in self.capability_map['tools']:
                return {
                    'primary_module': 'pc_control',
                    'fallback_modules': ['llama_general'],
                    'requires_model': False,
                    'chain': []
                }
        
        # ============ GREETING ============
        elif intent == 'greeting':
            best_model = self._select_best_model(['llama 3.2 3b', 'qwen2.5'])
            return {
                'primary_module': 'general_chat',
                'fallback_modules': ['brain'],
                'requires_model': True,
                'model_type': best_model,
                'chain': []
            }
        
        # ============ GENERAL CHAT (DEFAULT) ============
        else:
            if requires_live_info:
                return {
                    'primary_module': 'search_api',
                    'fallback_modules': ['llama_general'],
                    'requires_model': False,
                    'chain': ['search', 'contextualize']
                }
            else:
                best_model = self._select_best_model(['llama 3.2 3b', 'qwen2.5'])
                return {
                    'primary_module': 'general_chat',
                    'fallback_modules': ['brain'],
                    'requires_model': True,
                    'model_type': best_model,
                    'chain': []
                }
    
    def _select_best_model(self, model_options: List[str]) -> str:
        """Select the best available model from options"""
        for model in model_options:
            if model.lower() in self.capability_map['models']:
                return model.lower()
        return 'llama'
    
    # ==================== Execution & Fallbacks ====================
    
    def execute_decision(self, decision: Dict[str, Any], message: str) -> Optional[Dict[str, Any]]:
        """Execute the decision and run primary/fallback modules"""
        
        try:
            # Try primary module
            result = self._execute_module(decision['primary_module'], message)
            if result:
                return {
                    **result,
                    'module_used': decision['primary_module'],
                    'fallback_used': False
                }
            
            # Try fallback modules
            for fallback_module in decision.get('fallback_modules', []):
                result = self._execute_module(fallback_module, message)
                if result:
                    return {
                        **result,
                        'module_used': fallback_module,
                        'fallback_used': True
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error executing decision: {e}")
            return None
    
    def _execute_module(self, module_name: str, message: str) -> Optional[Dict[str, Any]]:
        """Execute a specific module"""
        
        try:
            if module_name == 'calculator':
                from modules.calculator import calculator
                result = calculator.calculate(message)
                return {'response': result}
            
            elif module_name == 'weather_api':
                from modules.tools import weather_api
                result = weather_api.get_weather(message)
                return result
            
            elif module_name == 'news_api':
                from modules.tools import news_api
                result = news_api.get_news(message)
                return result
            
            elif module_name == 'search_api':
                from modules.duckduckgo_search import search
                result = search(message)
                return {'response': result}
            
            elif module_name == 'time_date_module':
                from modules.time_date import get_time_date
                result = get_time_date(message)
                return {'response': result}
            
            elif module_name == 'pc_control':
                from modules.pc_control import control_pc
                result = control_pc(message)
                return {'response': result}
            
            elif module_name == 'memory':
                from modules.memory import get_memory
                result = get_memory(message)
                return {'response': result}
            
            elif module_name == 'coding':
                from modules.models import local_models
                result = local_models.smart_routing(message, "coding")
                return result
            
            elif module_name == 'vision':
                from modules.enhanced_moondream import EnhancedMoondream
                result = EnhancedMoondream.get_response(message)
                return result
            
            elif module_name == 'document':
                from modules.rag_search import analyze_document
                result = analyze_document(message)
                return {'response': result}
            
            elif module_name == 'general_chat' or module_name == 'llama_general':
                from modules.models import local_models
                result = local_models.smart_routing(message, "general_chat")
                return result
            
            elif module_name == 'brain':
                from modules.brain import process_query
                result = process_query(message)
                return {'response': result if isinstance(result, str) else result.get('response', '')}
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to execute module {module_name}: {e}")
            return None
    
    def get_execution_chain(self, decision: Dict[str, Any]) -> List[str]:
        """Get the execution chain for multi-step workflows"""
        chain = [decision['primary_module']]
        chain.extend(decision.get('chain', []))
        return chain
    
    def estimate_response_time(self, module: str) -> float:
        """Estimate response time in seconds"""
        time_estimates = {
            'calculator': 0.1,
            'time_date_module': 0.1,
            'weather_api': 1.0,
            'news_api': 2.0,
            'search_api': 1.5,
            'pc_control': 0.5,
            'memory': 0.2,
            'coding': 3.0,
            'vision': 2.0,
            'document': 2.5,
            'general_chat': 2.5,
            'brain': 2.0
        }
        return time_estimates.get(module, 2.0)
    
    # ==================== Backward Compatibility API ====================
    # These methods maintain compatibility with existing code
    
    def decide_module(self, context: str, message: str) -> Dict[str, Any]:
        """
        Backward compatibility wrapper for old API
        
        Old API: decide_module(context, message)
        Returns dict with fields compatible with old code
        """
        decision = self.decide(message)
        
        # Transform to old API format
        return {
            'primary_module': decision['primary_module'],
            'confidence': decision['confidence'],
            'reasoning': decision['reasoning'],
            'classification_method': decision['classification_method'],
            'requires_live_info': decision['requires_live_info'],
            'fallback_modules': decision.get('fallback_modules', []),
            'requires_model': decision.get('requires_model', False),
            'model_type': decision.get('model_type'),
            'chain': decision.get('chain', []),
            'intent': decision['intent'],
            'start_ollama': decision.get('requires_model', False),  # Start Ollama if model required
            'stop_ollama_after': False,
            'entities': {}  # Placeholder for entity extraction if needed
        }
    
    def validate_output(self, response: str, intent: str) -> Tuple[bool, str]:
        """Validate response quality"""
        if not response or len(response.strip()) < 3:
            return False, "Response too short"
        
        if response.startswith("Error:") or response.startswith("❌"):
            return False, "Error in response"
        
        return True, "Response valid"
    
    def get_fallback_response(self, fallback_modules: List[str], message: str) -> Optional[Dict[str, Any]]:
        """Try fallback modules in sequence"""
        for module in fallback_modules:
            try:
                result = self._execute_module(module, message)
                if result:
                    return {
                        "response": result.get('response', ''),
                        "module": module
                    }
            except Exception as e:
                logger.warning(f"Fallback module {module} failed: {e}")
                continue
        
        return None


# ===================== Global Instance =====================
unified_decision_maker = UnifiedDecisionMaker()


# ===================== Helper Functions =====================

def analyze_user_input(message: str) -> Dict[str, Any]:
    """
    Simple wrapper function to analyze user input
    
    Usage:
        decision = analyze_user_input("What's the weather today?")
        print(decision['primary_module'])  # 'weather_api'
    """
    return unified_decision_maker.decide(message)


def execute_request(message: str) -> Optional[Dict[str, Any]]:
    """
    Complete workflow: analyze -> decide -> execute
    
    Usage:
        result = execute_request("Write a Python function to calculate factorial")
        print(result['response'])
    """
    decision = unified_decision_maker.decide(message)
    return unified_decision_maker.execute_decision(decision, message)


if __name__ == "__main__":
    # Test examples
    test_messages = [
        "What's 15 * 23?",
        "What's the weather in Delhi today?",
        "Latest news about AI",
        "Write a Python function for binary search",
        "Remember to call mom tomorrow",
        "Open Chrome browser",
        "Hello, how are you?",
        "What is gravity?"
    ]
    
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    print("\n" + "="*60)
    print("MAYA AI - Unified Decision Maker Test")
    print("="*60 + "\n")
    
    for message in test_messages:
        decision = analyze_user_input(message)
        print(f"📝 Input: {message}")
        print(f"🎯 Intent: {decision['intent']}")
        print(f"📊 Confidence: {decision['confidence']:.2f}")
        print(f"🔧 Primary Module: {decision['primary_module']}")
        print(f"⏱️ Est. Time: {unified_decision_maker.estimate_response_time(decision['primary_module']):.1f}s")
        print(f"✅ Requires Live Info: {decision['requires_live_info']}")
        print()
