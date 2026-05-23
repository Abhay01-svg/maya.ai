"""
MAYA AI - Enhanced Smart Decision Making Module
===============================================
Intelligent request analysis and routing with:
- Elite NLP Engine for deep language understanding
- NLP-based classification (spaCy when available)
- Live vs historical information detection
- Comprehensive intent detection with priorities
- Dynamic capability mapping
- Intelligent fallback chains
- Multi-step workflow support
"""

import time
import logging
import re
import hashlib
import threading
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# Offline-first configuration: default to offline mode unless explicitly allowed
# Set `MAYA_OFFLINE_MODE=0` to disable offline mode (NOT RECOMMENDED).
# Set `MAYA_ALLOW_CLOUD_FALLBACK=1` to allow cloud fallbacks (requires network).
OFFLINE_MODE = os.getenv('MAYA_OFFLINE_MODE', '1') != '0'
ALLOW_CLOUD_FALLBACK = os.getenv('MAYA_ALLOW_CLOUD_FALLBACK', '0') == '1'

if OFFLINE_MODE:
    logger.info("🔒 Offline mode enabled (MAYA_OFFLINE_MODE=1). Cloud services disabled by default")
else:
    logger.info("🌐 Offline mode disabled; cloud fallbacks may be enabled via environment variables")
# Try to import Elite NLP Engine
try:
    from modules.elite_nlp_engine import elite_nlp, NLPResult
    ELITE_NLP_AVAILABLE = True
    logger.info("🧠 Elite NLP Engine loaded")
except ImportError:
    ELITE_NLP_AVAILABLE = False
    logger.warning("⚠️ Elite NLP Engine not available, using fallback")

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



@dataclass
class UserIntent:
    """Analyzed user intent with all metadata"""
    intent: str
    confidence: float
    reasoning: str
    keywords: List[str]
    entities: Dict[str, str]
    requires_live_info: bool
    classification_method: str
    primary_module: str
    fallback_modules: List[str]
    requires_model: bool
    model_type: Optional[str]
    response_type: str
    voice_tone: str
    chain: List[str]
    context: str  # Domain/context of the question
    source_hint: str  # Likely source (e.g., "academic", "casual", "technical")
    # Elite NLP Engine fields
    nlp_language: str = "english"
    nlp_emotion: str = "neutral"
    nlp_urgency: str = "low"
    nlp_ambiguity_score: float = 0.0
    nlp_clarify_required: bool = False
    nlp_memory_fetch_score: float = 0.0
    nlp_followup: bool = False
    nlp_tool_signals: List[str] = None
    nlp_response_style: str = "neutral"
    nlp_context_links: List[str] = None


class OllamaManager:
    """Manages Ollama service lifecycle"""
    
    def __init__(self):
        self.is_running = False
    
    def is_ollama_running(self) -> bool:
        """Check if Ollama is running"""
        if OFFLINE_MODE:
            logger.debug("Ollama check skipped due to OFFLINE_MODE")
            self.is_running = False
            return False

        try:
            import subprocess
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            self.is_running = result.returncode == 0
            return self.is_running
        except Exception:
            self.is_running = False
            return False
    
    def start_ollama(self):
        """Start Ollama service"""
        if OFFLINE_MODE:
            logger.info("Ollama start requested but skipped due to OFFLINE_MODE")
            return

        try:
            import subprocess
            subprocess.Popen(['ollama', 'serve'])
            time.sleep(2)
            self.is_running = True
            logger.info("✅ Ollama service started")
        except Exception as e:
            logger.error(f"❌ Failed to start Ollama: {e}")
    
    def stop_ollama(self):
        """Stop Ollama service"""
        if OFFLINE_MODE:
            logger.info("Ollama stop requested but skipped due to OFFLINE_MODE")
            self.is_running = False
            return

        try:
            import subprocess
            # Use platform-appropriate stop command; try pkill on POSIX
            subprocess.run(['pkill', '-f', 'ollama'], capture_output=True)
            self.is_running = False
            logger.info("✅ Ollama service stopped")
        except Exception as e:
            logger.error(f"❌ Failed to stop Ollama: {e}")


class DecisionMaker:
    """
    Smart decision-making brain that:
    - Analyzes user requests with NLP
    - Detects live vs historical information needs
    - Routes to best available model/API/tool
    - Handles fallback chains
    """
    
    def __init__(self):
        """Initialize the decision maker"""
        self.ollama = OllamaManager()
        
        # Initialize Groq API as cloud fallback
        self.groq_client = None
        self.groq_available = False

        # Cloud fallbacks are disabled by default in offline-first mode. To enable,
        # set MAYA_OFFLINE_MODE=0 and MAYA_ALLOW_CLOUD_FALLBACK=1 and provide GROQ_API_KEY.
        if not OFFLINE_MODE and ALLOW_CLOUD_FALLBACK:
            try:
                from modules.groq_api import get_groq_client
                groq_api_key = os.getenv('GROQ_API_KEY')
                if groq_api_key:
                    self.groq_client = get_groq_client(groq_api_key)
                    if self.groq_client and getattr(self.groq_client, 'is_ready', lambda: False)():
                        self.groq_available = True
                        logger.info("✅ Groq API initialized as cloud fallback")
                    else:
                        logger.warning("⚠️ Groq API client not ready")
                else:
                    logger.warning("⚠️ GROQ_API_KEY not found in environment")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Groq: {e}")
        else:
            logger.info("🔒 Groq/cloud fallbacks disabled (offline-first policy)")
        
        # Capability mapping
        self.capability_map = {
            'models': {},
            'tools': {},
            'apis': {},
            'features': {}
        }
        
        # Performance tracking
        self.module_performance = {}
        self.available_modules = [
            "calculator", "weather_api", "news_api", "search_api", 
            "pc_control", "memory", "qwen_coder", "llama_general", 
            "time_date_module", "vision", "document", "coding", "rag"
        ]
        
        # README.md auto-refresh
        self.readme_path = Path(__file__).parent.parent / 'README.md'
        self.last_readme_hash = None
        self.auto_refresh_enabled = True
        
        # Intent keywords with priorities
        self.intent_keywords = {
            'calculation': {
                'keywords': ["calculate", "compute", "solve", "add", "subtract", "multiply", 
                           "divide", "square", "cube", "root", "power", "equation", "math"],
                'patterns': [r'^[\d\s\+\-\*\/\(\)\.]+$', r'sin|cos|tan|sqrt|log|exp'],
                'priority': 1
            },
            'weather': {
                'keywords': ["weather", "temperature", "forecast", "rain", "sunny", "climate", 
                           "humid", "wind", "precipitation"],
                'priority': 2
            },
            'news': {
                'keywords': ["news", "headlines", "breaking", "latest", "current events", "updates"],
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
            },
            'rag': {
                'keywords': ["research", "deep dive", "analyze in depth", "comprehensive", 
                           "detailed analysis", "investigate", "study", "explore", "find all about"],
                'priority': 12
            }
        }
        
        # Response templates for natural/baby-like tone (legacy - now using smart_agent_response.py)
        self.response_templates = {
            'calculation': "Oh calculation! Abhi solve karti hoon! 🧮",
            'weather': "Weather check karte hain! ☁️",
            'news': "News dhundti hoon! 📰",
            'search': "Dekhti hoon kya milta hai! 🔍",
            'coding': "Code likh deti hoon! 💻",
            'time_date': "Time bata deti hoon! 🕐",
            'memory': "Yaad rakh lungi! 💾",
            'pc_control': "Kar deti hoon! ⚡",
            'greeting': "Hi! Kya kar rahe ho? 🤖",
            'rag': "Research karti hoon! 📚",
            'general_chat': "Bol dijiye! Sun rahi hoon! 👂"
        }
        
        # Import smart agent response system
        try:
            from modules.smart_agent_response import smart_agent
            self.smart_agent = smart_agent
            logger.info("🤖 Smart Agent Response System loaded")
        except ImportError:
            self.smart_agent = None
            logger.warning("⚠️ Smart Agent Response System not available, using legacy templates")
        
        # Initialize capabilities
        self._read_capabilities()
        
        # Ensure RAG is available in features
        if 'rag' not in self.capability_map['features']:
            self.capability_map['features']['rag'] = {
                'name': 'RAG',
                'description': 'Deep research',
                'available': True
            }
        
        self._start_auto_refresh()
        
        logger.info("🧠 Smart Decision Maker initialized")
    
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
            
            logger.info(f"✅ Capabilities updated: {len(self.capability_map['models'])} models")
            
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
                'rag': {'name': 'RAG', 'description': 'Deep research', 'available': True},
                'rag deep research': {'name': 'RAG Deep Research', 'description': 'Advanced research with web content extraction', 'available': True}
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
        """Use Elite NLP Engine for full sentence semantic understanding"""
        message_lower = message.lower()
        logger.info(f"🔍 _detect_intent_nlp called with: '{message_lower}'")

        # Use Elite NLP for full sentence semantic understanding
        if ELITE_NLP_AVAILABLE:
            try:
                nlp_result = elite_nlp.process(message)

                # Use Elite NLP's intent candidates for routing
                # Map Elite NLP intents to Maya intents
                intent_mapping = {
                    'ask': 'general_chat',
                    'command': 'coding',
                    'create': 'coding',
                    'compare': 'general_chat',
                    'recall': 'memory',
                    'emotional': 'general_chat',
                    'planning': 'general_chat',
                    'urgent': 'general_chat',
                    'calculation': 'calculation',
                    'weather': 'weather',
                    'news': 'news',
                    'research': 'rag',
                    'document': 'document',
                    'vision': 'vision',
                    'pc_control': 'pc_control',
                    'time_date': 'time_date'
                }

                # Check if Elite NLP has high confidence intent candidates
                if nlp_result.intent_candidates and nlp_result.top_intent_confidence > 0.6:
                    top_intent = nlp_result.intent_candidates[0]['intent']
                    confidence = nlp_result.top_intent_confidence

                    if top_intent in intent_mapping:
                        mapped_intent = intent_mapping[top_intent]
                        reasoning = f"Elite NLP intent: {top_intent} (confidence: {confidence:.2f})"
                        logger.info(f"🧠 Elite NLP routed to {mapped_intent} ({confidence:.2f}): {reasoning}")
                        return mapped_intent, confidence, reasoning

                # Also use tool signals as secondary indicator
                tool_signals = nlp_result.tool_signals
                signal_to_intent = {
                    'calculator': 'calculation',
                    'coding': 'coding',
                    'search': 'search',
                    'chat': 'greeting',
                    'reasoning': 'general_chat',
                    'summarization': 'general_chat'
                }

                if len(tool_signals) > 0 and nlp_result.confidence > 0.7:
                    for signal in tool_signals:
                        if signal in signal_to_intent:
                            intent = signal_to_intent[signal]
                            confidence = nlp_result.confidence
                            reasoning = f"Elite NLP tool signal: {signal}"
                            logger.info(f"🧠 Elite NLP routed to {intent} ({confidence:.2f}): {reasoning}")
                            return intent, confidence, reasoning
            except Exception as e:
                logger.warning(f"⚠️ Elite NLP analysis failed: {e}")

        # Fall back to spaCy NLP for detailed linguistic analysis
        if not SPACY_AVAILABLE or not nlp:
            return self._detect_intent_rule_based(message)

        try:
            doc = nlp(message.lower())

            # Extract linguistic features
            pos_tags = [token.pos_ for token in doc]
            dep_tags = [token.dep_ for token in doc]
            entities = [ent.label_ for ent in doc.ents]
            lemmas = [token.lemma_ for token in doc]

            # Count key linguistic patterns
            verb_count = sum(1 for tag in pos_tags if tag == "VERB")
            noun_count = sum(1 for tag in pos_tags if tag == "NOUN")
            question_words = [token.text for token in doc if token.tag_ in ["WDT", "WP", "WRB"]]
            imperative_verb = any(token.dep_ == "ROOT" and token.pos_ == "VERB" for token in doc)

            # Check for mathematical expressions using NLP patterns
            has_math_symbols = any(char in message for char in "+-*/=")
            has_numbers = any(token.like_num for token in doc)

            # 1. Greeting detection using NLP - check for greeting words directly
            # Check in original message first to avoid tokenization issues
            message_lower = message.lower()
            greeting_words = ["hello", "hi", "hey", "namaste", "hola"]
            if any(greeting in message_lower for greeting in greeting_words):
                return "greeting", 0.95, "Greeting detected via NLP"
            # Fallback to lemma check
            greeting_lemmas = ["hello", "hi", "hey", "namaste", "hola"]
            if any(lemma in greeting_lemmas for lemma in lemmas):
                return "greeting", 0.95, "Greeting detected via NLP"
            if len(doc) <= 3 and any(token.pos_ == "INTJ" for token in doc):
                return "greeting", 0.95, "Greeting detected via NLP"

            # 2. Time/Date queries - check BEFORE general knowledge
            if any(ent in ["DATE", "TIME"] for ent in entities) and any(lemma in ["time", "date", "timezone"] for lemma in lemmas):
                return "time_date", 0.95, "Time/Date query detected via NLP"
            if any(lemma in ["time", "date", "timezone"] for lemma in lemmas):
                return "time_date", 0.92, "Time/Date intent detected via NLP"

            # 3. Weather queries - check BEFORE general knowledge
            if any(ent in ["GPE", "LOC"] for ent in entities) and any(lemma in ["weather", "temperature", "forecast"] for lemma in lemmas):
                return "weather", 0.93, "Weather query detected via NLP"
            if any(lemma in ["weather", "temperature", "forecast"] for lemma in lemmas):
                return "weather", 0.90, "Weather intent detected via NLP"

            # 4. Memory queries - check BEFORE general knowledge
            if any(lemma in ["remember", "save", "store", "note"] for lemma in lemmas) and any(token.text in ["me", "my", "i"] for token in doc):
                return "memory", 0.90, "Memory query detected via NLP"
            if any(lemma in ["remember", "save", "store", "note"] for lemma in lemmas):
                return "memory", 0.85, "Memory intent detected via NLP"

            # 5. News queries - check BEFORE general knowledge
            if any(ent in ["DATE", "TIME"] for ent in entities) and any(lemma in ["news", "headline", "breaking"] for lemma in lemmas):
                return "news", 0.92, "News query detected via NLP"
            if any(lemma in ["news", "headline", "breaking"] for lemma in lemmas):
                return "news", 0.88, "News intent detected via NLP"

            # 6. Explanation/General knowledge - check AFTER specific intents
            explain_verbs = ["explain", "describe", "tell", "compare"]
            abstract_nouns = ["difference", "how", "what", "why"]
            if any(lemma in explain_verbs for lemma in lemmas) or len(question_words) > 0:
                return "general_chat", 0.85, "General knowledge query detected via NLP"
            if any(lemma in abstract_nouns for lemma in lemmas) and verb_count > 0:
                return "general_chat", 0.80, "Explanation intent detected via NLP"

            # 7. Coding queries - check BEFORE math to catch "function" in coding context
            # Exclude comparison queries from coding
            if "compare" not in message.lower() and "vs" not in message.lower():
                coding_verbs = ["write", "create", "implement", "debug", "fix", "sort"]
                coding_nouns = ["function", "code", "program", "script", "algorithm", "array", "api", "class"]
                if any(lemma in coding_verbs for lemma in lemmas) and any(lemma in coding_nouns for lemma in lemmas):
                    return "coding", 0.90, "Coding query detected via NLP"
                if imperative_verb and any(lemma in coding_nouns for lemma in lemmas):
                    return "coding", 0.88, "Imperative coding request detected via NLP"

            # 8. RAG/Deep research - research verbs + depth adjectives (check BEFORE math to avoid false positives)
            research_verbs = ["research", "investigate", "study", "explore", "analyze"]
            depth_adjectives = ["deep", "comprehensive", "detailed", "thorough"]
            if any(lemma in research_verbs for lemma in lemmas) or any(lemma in depth_adjectives for lemma in lemmas):
                return "rag", 0.88, "Deep research detected via NLP"

            # 9. Mathematical calculation - numbers + math symbols + calculation verbs + trigonometric functions
            if has_math_symbols and has_numbers:
                return "calculation", 0.95, "Mathematical expression detected via NLP"
            if has_numbers and any(lemma in ["calculate", "compute", "solve"] for lemma in lemmas):
                return "calculation", 0.92, "Math calculation intent detected via NLP"
            # Trigonometric and math functions - check in original message too
            math_functions = ["sin", "cos", "tan", "sqrt", "log", "exp", "power", "square", "cube"]
            if any(lemma in math_functions for lemma in lemmas):
                return "calculation", 0.90, "Math function detected via NLP"
            # Check for math functions in original message (handles "sin30" case)
            if any(func in message.lower() for func in math_functions):
                return "calculation", 0.88, "Math function detected in message via NLP"

            # 10. PC Control - action verbs + system nouns
            control_verbs = ["open", "close", "launch", "start", "stop", "shutdown"]
            system_nouns = ["chrome", "browser", "application", "program", "file"]
            if any(lemma in control_verbs for lemma in lemmas) and any(lemma in system_nouns for lemma in lemmas):
                return "pc_control", 0.92, "PC control detected via NLP"

            # Default to general chat
            return "general_chat", 0.70, "General conversation detected via NLP"

        except Exception as e:
            logger.error(f"NLP classification error: {e}")
            return self._detect_intent_rule_based(message)
    
    def _detect_intent_rule_based(self, message: str) -> Tuple[str, float, str]:
        """Fallback rule-based intent classification"""
        message_lower = message.lower()
        
        # Priority-based detection - ORDER MATTERS!
        # General chat explanation keywords moved to higher priority to catch explanation queries
        intents_by_priority = [
            ('calculation', ["+", "-", "*", "/", "calculate", "math", "sin", "cos", "tan", "sqrt", "log", "exp"]),
            ('general_chat', ["explain", "what is", "tell me about", "describe", "difference between", "how does", "compare"]),
            ('weather', ["weather", "temperature", "forecast", "rain", "what is the weather"]),
            ('news', ["news", "headlines", "breaking", "latest news", "tech news", "current news"]),
            ('time_date', ["time", "date", "timezone", "what time", "current time"]),
            ('memory', ["remember", "save", "note", "yad rakhna", "what do you remember", "my name", "about me"]),
            ('coding', ["write a function", "write code", "create a function", "implement", "debug", "fix error", "sort array", "quicksort", "mergesort", "binary search", "api endpoint", "rest api", "class definition", "def ", "algorithm"]),
            ('vision', ["screenshot", "image", "photo", "analyze screen"]),
            ('document', ["pdf", "document", "read file"]),
            ('pc_control', ["open", "close", "launch", "shutdown"]),
            ('rag', ["research", "deep dive", "comprehensive", "detailed analysis", "investigate", "study"]),
            ('greeting', ["hello", "hi", "hey", "good morning", "good evening", "good night", "namaste", "hola"])
        ]
        
        for intent, keywords in intents_by_priority:
            if any(keyword in message_lower for keyword in keywords):
                return intent, 0.80, f"Intent detected: {intent}"
        
        return "general_chat", 0.60, "Default classification"
    
    def _has_live_info_keywords(self, message: str) -> bool:
        """Check if message requests live/current information"""
        live_keywords = ["latest", "today", "current", "now", "recent", "live",
                        "updated", "breaking", "this week"]
        return any(keyword in message.lower() for keyword in live_keywords)
    
    def _detect_context(self, message: str, intent: str) -> Tuple[str, str]:
        """
        Detect the context/domain of the question using NLP
        Returns (context, source_hint)
        """
        message_lower = message.lower()
        
        # Academic/Scientific context
        academic_keywords = ["research", "study", "paper", "theory", "hypothesis",
                           "experiment", "analysis", "scientific", "academic",
                           "journal", "publication", "thesis", "dissertation"]
        if any(kw in message_lower for kw in academic_keywords):
            return "academic_research", "academic"

        # Technical/Programming context
        technical_keywords = ["code", "function", "api", "database", "algorithm",
                            "bug", "debug", "stack overflow", "github", "repository",
                            "framework", "library", "implementation", "architecture"]
        if any(kw in message_lower for kw in technical_keywords):
            return "technical_development", "technical"

        # Business/Professional context
        business_keywords = ["business", "company", "market", "revenue", "profit",
                          "strategy", "investment", "startup", "enterprise",
                          "corporate", "management", "finance"]
        if any(kw in message_lower for kw in business_keywords):
            return "business_professional", "business"

        # Educational/Learning context
        educational_keywords = ["learn", "teach", "explain", "tutorial", "course",
                             "lesson", "study", "understand", "concept", "what is",
                             "how does", "why is"]
        if any(kw in message_lower for kw in educational_keywords):
            return "educational_learning", "educational"

        # Casual/Personal context
        casual_keywords = ["my", "i need", "help me", "can you", "please",
                        "thanks", "just", "maybe", "think", "feel"]
        if any(kw in message_lower for kw in casual_keywords):
            return "casual_personal", "casual"

        # Default based on intent
        context_map = {
            'calculation': 'mathematical_computation',
            'weather': 'environmental_info',
            'news': 'current_events',
            'search': 'information_retrieval',
            'coding': 'software_development',
            'vision': 'visual_analysis',
            'document': 'document_processing',
            'memory': 'personal_information',
            'pc_control': 'system_automation',
            'greeting': 'social_interaction',
            'rag': 'deep_research'
        }

        return context_map.get(intent, 'general_inquiry'), 'general'
    
    def _analyze_context_with_llama(self, message: str, initial_context: str) -> str:
        """
        Use Llama model for enhanced context analysis when available
        This provides deeper understanding of question origin and domain
        """
        try:
            # Try to use local Llama for context analysis
            # This is a placeholder - actual implementation would call the Llama model
            # For now, return the initial context detected by NLP
            logger.info(f"🧠 Context analysis: {initial_context} (NLP-based)")
            return initial_context
        except Exception as e:
            logger.warning(f"⚠️ Llama context analysis failed: {e}, using NLP context")
            return initial_context
    
    # ==================== Decision Making & Routing ====================
    
    def analyze_user_input(self, message: str) -> UserIntent:
        """
        Analyze user input comprehensively
        Returns full UserIntent with all metadata
        """

        # Initialize Elite NLP fields with defaults
        nlp_language = "english"
        nlp_emotion = "neutral"
        nlp_urgency = "low"
        nlp_ambiguity_score = 0.0
        nlp_clarify_required = False
        nlp_memory_fetch_score = 0.0
        nlp_followup = False
        nlp_tool_signals = []
        nlp_response_style = "neutral"
        nlp_context_links = []

        # Step 0: Inject device context for smart automation
        enhanced_message = message
        context_used = []
        try:
            from modules.device_context import device_context
            enhanced_message, context_used = device_context.inject_context(message)
            if context_used:
                logger.info(f"🔍 Context injected: {context_used}")
                logger.info(f"📝 Enhanced query: '{message}' -> '{enhanced_message}'")
        except Exception as e:
            logger.warning(f"⚠️ Device context injection failed: {e}")
            enhanced_message = message

        # Step 0.5: Use Elite NLP Engine if available
        if ELITE_NLP_AVAILABLE:
            try:
                nlp_result = elite_nlp.process(enhanced_message)
                nlp_language = nlp_result.language
                nlp_emotion = nlp_result.emotion
                nlp_urgency = nlp_result.urgency
                nlp_ambiguity_score = nlp_result.ambiguity_score
                nlp_clarify_required = nlp_result.clarify_required
                nlp_memory_fetch_score = nlp_result.memory_fetch_score
                nlp_followup = nlp_result.followup
                nlp_tool_signals = nlp_result.tool_signals
                nlp_response_style = nlp_result.response_style
                nlp_context_links = nlp_result.context_links

                # Use NLP confidence if higher
                nlp_confidence = nlp_result.confidence

                logger.info(f"🧠 Elite NLP: language={nlp_language}, emotion={nlp_emotion}, confidence={nlp_confidence:.2f}")
            except Exception as e:
                logger.warning(f"⚠️ Elite NLP processing failed: {e}")

        # Step 1: Detect intent
        if SPACY_AVAILABLE:
            intent, confidence, reasoning = self._detect_intent_nlp(enhanced_message)
            classification_method = "NLP"
        else:
            intent, confidence, reasoning = self._detect_intent_rule_based(enhanced_message)
            classification_method = "Rule-based"

        logger.info(f"🎯 Detected intent: {intent}, confidence: {confidence}, reasoning: {reasoning}")

        # Step 2: Check if live info is needed
        requires_live_info = self._has_live_info_keywords(enhanced_message)

        # Step 3: Extract keywords and entities
        keywords, entities = self._extract_keywords_entities(enhanced_message, intent)

        # Step 4: Route to best module
        routing = self._route_to_module(intent, requires_live_info)
        logger.info(f"🚀 Routing to module: {routing['primary_module']} for intent: {intent}")
        logger.info(f"📋 Routing details: {routing}")

        # Step 5: Determine response type and voice tone
        response_type = self._get_response_type(intent, entities)
        voice_tone = self._get_voice_tone(intent)

        # Step 6: Detect context and source
        context, source_hint = self._detect_context(message, intent)

        # Step 7: Build execution chain
        chain = routing.get('chain', [])

        logger.info(f"🎯 Final UserIntent - intent: {intent}, primary_module: {routing['primary_module']}")

        return UserIntent(
            intent=intent,
            confidence=confidence,
            reasoning=reasoning,
            keywords=keywords,
            entities=entities,
            requires_live_info=requires_live_info,
            classification_method=classification_method,
            primary_module=routing['primary_module'],
            fallback_modules=routing['fallback_modules'],
            requires_model=routing['requires_model'],
            model_type=routing['model_type'],
            response_type=response_type,
            voice_tone=voice_tone,
            chain=chain,
            context=context,
            source_hint=source_hint,
            nlp_language=nlp_language,
            nlp_emotion=nlp_emotion,
            nlp_urgency=nlp_urgency,
            nlp_ambiguity_score=nlp_ambiguity_score,
            nlp_clarify_required=nlp_clarify_required,
            nlp_memory_fetch_score=nlp_memory_fetch_score,
            nlp_followup=nlp_followup,
            nlp_tool_signals=nlp_tool_signals,
            nlp_response_style=nlp_response_style,
            nlp_context_links=nlp_context_links
        )
    
    def _extract_keywords_entities(self, message: str, intent: str) -> Tuple[List[str], Dict[str, str]]:
        """Extract keywords and entities from message"""
        keywords = []
        entities = {}
        
        # Extract NLP entities if available
        if SPACY_AVAILABLE and nlp:
            try:
                doc = nlp(message.lower())
                for ent in doc.ents:
                    entity_type = ent.label_.lower()
                    entities[entity_type] = ent.text
                
                keywords = [token.text for token in doc if not token.is_stop and not token.is_punct]
            except:
                pass
        
        # Extract based on intent patterns
        if intent == 'search':
            match = re.search(r'(?:search|find|look for)\s+(?:for\s+)?(.+)', message, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                entities['query'] = query
                keywords.extend(query.split())
        
        elif intent == 'weather':
            match = re.search(r'weather\s+(?:in|of|for)?\s*(.+)', message, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                entities['location'] = location
                keywords.append(location)
        
        elif intent == 'calculation':
            # Extract mathematical expression
            match = re.search(r'calculate\s+(.+)|([0-9+\-*/().\s]+)', message, re.IGNORECASE)
            if match:
                expr = match.group(1) or match.group(2)
                if expr:
                    entities['expression'] = expr.strip()
        
        keywords = list(set(keywords))  # Remove duplicates
        return keywords, entities
    
    def _route_to_module(self, intent: str, requires_live_info: bool) -> Dict[str, Any]:
        """Route intent to appropriate module"""
        logger.info(f"🔀 _route_to_module called with intent: '{intent}' (type: {type(intent)}), requires_live_info: {requires_live_info}")

        base_routing = {
            'primary_module': 'general_chat',
            'fallback_modules': ['llama_general'],
            'requires_model': False,
            'model_type': None,
            'chain': []
        }

        # ============ CALCULATION ============
        if intent == 'calculation':
            fallbacks = ['llama_general', 'qwen_coder']
            if self.groq_available:
                fallbacks.append('groq_api')
            return {
                'primary_module': 'calculator',
                'fallback_modules': fallbacks,
                'requires_model': False,
                'model_type': None,
                'chain': []
            }
        
        # ============ WEATHER ============
        elif intent == 'weather':
            fallbacks = ['search_api', 'llama_general']
            if self.groq_available:
                fallbacks.append('groq_api')
            return {
                'primary_module': 'weather_api',
                'fallback_modules': fallbacks,
                'requires_model': False,
                'model_type': None,
                'chain': []
            }

        # ============ NEWS ============
        elif intent == 'news':
            fallbacks = ['search_api', 'llama_general']
            if self.groq_available:
                fallbacks.append('groq_api')
            return {
                'primary_module': 'news_api',
                'fallback_modules': fallbacks,
                'requires_model': False,
                'model_type': None,
                'chain': []
            }
        
        # ============ TIME/DATE ============
        elif intent == 'time_date':
            fallbacks = ['llama_general']
            if self.groq_available:
                fallbacks.append('groq_api')
            return {
                'primary_module': 'time_date_module',
                'fallback_modules': fallbacks,
                'requires_model': False,
                'model_type': None,
                'chain': []
            }
        
        # ============ SEARCH (Live Info) ============
        elif intent == 'search' or (requires_live_info and intent == 'general_chat'):
            if requires_live_info:
                if 'duckduckgo' in self.capability_map['apis'] or 'search' in self.capability_map['tools']:
                    fallbacks = ['llama_general']
                    if self.groq_available:
                        fallbacks.append('groq_api')
                    return {
                        'primary_module': 'search_api',
                        'fallback_modules': fallbacks,
                        'requires_model': False,
                        'model_type': None,
                        'chain': ['search', 'summarize']
                    }
            fallbacks = ['llama_general']
            if self.groq_available:
                fallbacks.append('groq_api')
            return {
                'primary_module': 'llama_general',
                'fallback_modules': fallbacks,
                'requires_model': True,
                'model_type': 'llama',
                'chain': []
            }
        
        # ============ CODING ============
        elif intent == 'coding':
            fallbacks = ['llama_general']
            if self.groq_available:
                fallbacks.append('groq_api')
            return {
                'primary_module': 'coding',
                'fallback_modules': fallbacks,
                'requires_model': True,
                'model_type': 'qwen_coder',
                'chain': ['code_generation', 'syntax_check']
            }
        
        # ============ VISION ============
        elif intent == 'vision':
            logger.info(f"✅ VISION routing matched")
            fallbacks = ['llama_general']
            if self.groq_available:
                fallbacks.append('groq_api')
            return {
                'primary_module': 'vision',
                'fallback_modules': fallbacks,
                'requires_model': True,
                'model_type': 'llama',
                'chain': ['capture', 'analyze']
            }

        # ============ DOCUMENT ============
        elif intent == 'document':
            logger.info(f"✅ DOCUMENT routing matched")
            fallbacks = ['llama_general']
            if self.groq_available:
                fallbacks.append('groq_api')
            return {
                'primary_module': 'document',
                'fallback_modules': fallbacks,
                'requires_model': True,
                'model_type': 'llama',
                'chain': ['read', 'summarize']
            }

        # ============ MEMORY ============
        elif intent == 'memory':
            logger.info(f"✅ MEMORY routing matched")
            fallbacks = ['llama_general']
            if self.groq_available:
                fallbacks.append('groq_api')
            return {
                'primary_module': 'memory',
                'fallback_modules': fallbacks,
                'requires_model': False,
                'model_type': None,
                'chain': []
            }

        # ============ PC CONTROL ============
        elif intent == 'pc_control':
            logger.info(f"✅ PC CONTROL routing matched")
            fallbacks = ['llama_general']
            if self.groq_available:
                fallbacks.append('groq_api')
            return {
                'primary_module': 'pc_control',
                'fallback_modules': fallbacks,
                'requires_model': False,
                'model_type': None,
                'chain': []
            }

        # ============ GREETING ============
        elif intent == 'greeting':
            fallbacks = ['llama_general']
            if self.groq_available:
                fallbacks.append('groq_api')
            return {
                'primary_module': 'general_chat',
                'fallback_modules': fallbacks,
                'requires_model': True,
                'model_type': 'llama',
                'chain': []
            }

        # ============ RAG (Deep Research) ============
        elif intent == 'rag':
            if 'rag' in self.capability_map['features']:
                fallbacks = ['llama_general']
                if self.groq_available:
                    fallbacks.append('groq_api')
                return {
                    'primary_module': 'rag',
                    'fallback_modules': fallbacks,
                    'requires_model': True,
                    'model_type': 'llama',
                    'chain': ['retrieve', 'analyze', 'synthesize']
                }
            # Fallback if RAG not in capabilities
            fallbacks = ['llama_general']
            if self.groq_available:
                fallbacks.append('groq_api')
            return {
                'primary_module': 'llama_general',
                'fallback_modules': fallbacks,
                'requires_model': True,
                'model_type': 'llama',
                'chain': []
            }
        
        # Default
        logger.info(f"⚠️ No specific routing matched for intent: {intent}, using default")
        fallbacks = ['llama_general']
        if self.groq_available:
            fallbacks.append('groq_api')
        base_routing['fallback_modules'] = fallbacks
        base_routing['requires_model'] = True
        base_routing['model_type'] = 'llama'
        base_routing['unclear_response'] = "Sir, I am unable to understand. Can you please clarify?"
        return base_routing
    
    def _get_response_type(self, intent: str, entities: Dict[str, str]) -> str:
        """Determine response type"""
        type_map = {
            'calculation': 'math_result',
            'weather': 'weather_info',
            'news': 'news_update',
            'search': 'search_result',
            'coding': 'code_snippet',
            'time_date': 'time_info',
            'vision': 'image_analysis',
            'document': 'document_summary',
            'memory': 'memory_operation',
            'pc_control': 'system_command',
            'greeting': 'greeting_response',
            'rag': 'research_report'
        }
        return type_map.get(intent, 'chat_response')
    
    def _get_voice_tone(self, intent: str) -> str:
        """Get voice tone for TTS"""
        tones = {
            'calculation': 'playful_smart',
            'weather': 'gentle_caring',
            'news': 'excited_energetic',
            'search': 'sweet_curious',
            'coding': 'professional_capable',
            'time_date': 'helpful_clear',
            'vision': 'amazed_descriptive',
            'document': 'thoughtful_analytical',
            'memory': 'friendly_supportive',
            'pc_control': 'confident_capable',
            'greeting': 'affectionate_charming',
            'rag': 'academic_professional'
        }
        return tones.get(intent, 'sweet_friendly')
    
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
            'llama_general': 2.0,
            'rag': 5.0
        }
        return time_estimates.get(module, 2.0)
    
    # ==================== Legacy API (Backward Compatibility) ====================
    
    def decide_module(self, context: str, message: str) -> Dict[str, Any]:
        """
        Legacy API wrapper for backward compatibility
        Converts new UserIntent to old format
        """
        user_intent = self.analyze_user_input(message)

        # Get routing to check for unclear response
        routing = self._route_to_module(user_intent.intent, user_intent.requires_live_info)

        return {
            'primary_module': user_intent.primary_module,
            'confidence': user_intent.confidence,
            'reasoning': user_intent.reasoning,
            'classification_method': user_intent.classification_method,
            'requires_live_info': user_intent.requires_live_info,
            'fallback_modules': user_intent.fallback_modules,
            'requires_model': user_intent.requires_model,
            'model_type': user_intent.model_type,
            'chain': user_intent.chain,
            'intent': user_intent.intent,
            'start_ollama': user_intent.requires_model,
            'stop_ollama_after': False,
            'entities': user_intent.entities,
            'response_type': user_intent.response_type,
            'voice_tone': user_intent.voice_tone,
            'context': user_intent.context,
            'source_hint': user_intent.source_hint,
            'unclear_response': routing.get('unclear_response', "Sir, I am unable to understand. Can you please clarify?"),
            # Elite NLP Engine fields
            'nlp_language': user_intent.nlp_language,
            'nlp_emotion': user_intent.nlp_emotion,
            'nlp_urgency': user_intent.nlp_urgency,
            'nlp_ambiguity_score': user_intent.nlp_ambiguity_score,
            'nlp_clarify_required': user_intent.nlp_clarify_required,
            'nlp_memory_fetch_score': user_intent.nlp_memory_fetch_score,
            'nlp_followup': user_intent.nlp_followup,
            'nlp_tool_signals': user_intent.nlp_tool_signals,
            'nlp_response_style': user_intent.nlp_response_style,
            'nlp_context_links': user_intent.nlp_context_links
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
                logger.info(f"Trying fallback module: {module}")
                
                # Groq API cloud fallback
                if module == "groq_api":
                    if self.groq_available and self.groq_client:
                        result = self.groq_client.chat([{"role": "user", "content": message}])
                        if result and not result.startswith("❌"):
                            return {
                                "response": result,
                                "module": "groq_api",
                                "source": "cloud"
                            }
                        logger.warning("Groq API returned error or unavailable")
                    else:
                        logger.warning("Groq API not available for fallback")
                    continue
                
                # Placeholder for other module execution
                # In real implementation, execute the module here
                return {
                    "response": f"Response from {module}",
                    "module": module
                }
            except Exception as e:
                logger.warning(f"Fallback module {module} failed: {e}")
                continue
        
        return None


# Global decision maker instance
decision_maker = DecisionMaker()
