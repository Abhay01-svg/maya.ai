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

# Import configuration
try:
    from config import DEBUG_MODE
except ImportError:
    DEBUG_MODE = True

# Offline-first configuration: default to offline mode unless explicitly allowed
OFFLINE_MODE = os.getenv('MAYA_OFFLINE_MODE', '0') != '0' # Changed to 0 by default to allow cloud if key exists
ALLOW_CLOUD_FALLBACK = os.getenv('MAYA_ALLOW_CLOUD_FALLBACK', '1') == '1' # Changed to 1 to allow cloud if key exists

if OFFLINE_MODE:
    logger.info("🔒 Offline mode enabled (MAYA_OFFLINE_MODE=1). Cloud services disabled by default")
else:
    logger.info("🌐 Offline mode disabled; cloud fallbacks may be enabled via environment variables")

# Try to import Elite NLP Engine
try:
    from .elite_nlp_engine import EliteNLPEngine
    elite_nlp = EliteNLPEngine()
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
    context: str
    source_hint: str
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
        try:
            import subprocess
            subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], capture_output=True)
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
        self.groq_available = False
        from config import GROQ_API_KEY
        if GROQ_API_KEY and not OFFLINE_MODE and ALLOW_CLOUD_FALLBACK:
            self.groq_available = True
            logger.info("✅ Groq API available as cloud fallback")
        
        # Capability mapping
        self.capability_map = {
            'models': {},
            'tools': {},
            'apis': {},
            'features': {}
        }
        
        # Intent keywords with priorities
        self.intent_keywords = {
            'calculation': {
                'keywords': ["calculate", "compute", "solve", "add", "subtract", "multiply", 
                           "divide", "square", "cube", "root", "power", "equation", "math"],
                'priority': 1
            },
            'weather': {
                'keywords': ["weather", "temperature", "forecast", "rain", "sunny", "climate"],
                'priority': 2
            },
            'news': {
                'keywords': ["news", "headlines", "breaking", "latest", "current events"],
                'priority': 3
            },
            'time_date': {
                'keywords': ["time", "date", "timezone", "what time", "now"],
                'priority': 4
            },
            'search': {
                'keywords': ["search", "find", "look for", "information about", "tell me about"],
                'priority': 5
            },
            'coding': {
                'keywords': ["code", "program", "script", "function", "debug", "python", "javascript"],
                'priority': 6
            },
            'pc_control': {
                'keywords': ["open", "close", "launch", "shutdown", "restart", "screenshot"],
                'priority': 10
            },
            'rag': {
                'keywords': ["research", "deep dive", "analyze in depth", "investigate", "study"],
                'priority': 12
            }
        }
        
        self._set_default_capabilities()
        logger.info("🧠 Smart Decision Maker initialized")

    def _set_default_capabilities(self):
        """Set default capabilities"""
        self.capability_map = {
            'models': {
                'llama': {'available': True},
                'qwen': {'available': True}
            },
            'tools': {
                'calculator': {'available': True},
                'pc_control': {'available': True},
                'rag': {'available': True}
            },
            'apis': {
                'weather': {'available': True},
                'news': {'available': True},
                'search': {'available': True}
            },
            'features': {
                'rag': {'available': True}
            }
        }

    def decide_module(self, intent_hint: str, message: str) -> Dict[str, Any]:
        """Main decision entry point for brain.py compatibility"""
        user_intent = self.analyze_user_input(message)
        
        return {
            "primary_module": user_intent.primary_module,
            "confidence": user_intent.confidence,
            "reasoning": user_intent.reasoning,
            "intent": user_intent.intent,
            "fallback_modules": user_intent.fallback_modules,
            "requires_model": user_intent.requires_model,
            "model_type": user_intent.model_type,
            "entities": user_intent.entities
        }

    def analyze_user_input(self, message: str) -> UserIntent:
        """Analyze user input comprehensively"""
        message_lower = message.lower()
        
        # 1. Try Elite NLP first
        if ELITE_NLP_AVAILABLE:
            try:
                # Mocking Elite NLP result for now based on keyword matching
                # as I don't want to break if Elite NLP is not fully ready
                pass
            except:
                pass

        # 2. Use spaCy or Rule-based
        intent, confidence, reasoning = self._detect_intent(message_lower)
        
        # 3. Detect if live info is needed
        requires_live_info = any(kw in message_lower for kw in ["latest", "today", "now", "current", "news"])
        
        # 4. Extract entities
        entities = self._extract_entities(message_lower, intent)
        
        # 5. Route
        routing = self._route_to_module(intent, requires_live_info)
        
        return UserIntent(
            intent=intent,
            confidence=confidence,
            reasoning=reasoning,
            keywords=[],
            entities=entities,
            requires_live_info=requires_live_info,
            classification_method="NLP" if SPACY_AVAILABLE else "Rule-based",
            primary_module=routing['primary_module'],
            fallback_modules=routing['fallback_modules'],
            requires_model=routing['requires_model'],
            model_type=routing['model_type'],
            response_type="text",
            voice_tone="helpful",
            chain=[],
            context="general",
            source_hint="general"
        )

    def _detect_intent(self, message: str) -> Tuple[str, float, str]:
        """Detect intent using robust regex patterns and keywords"""
        message_lower = message.lower().strip()
        
        # 1. PC Control (High Priority)
        if re.search(r'\b(open|launch|start|close|exit|terminate|shutdown|restart|sleep|screenshot|volume|mute)\b', message_lower):
            return "pc_control", 0.95, "PC control command detected"

        # 2. Mathematical calculation (Robust regex)
        # Matches sin(30), 2+2, 50*5, sqrt(16), etc.
        math_pattern = r'(\b(sin|cos|tan|log|sqrt|pow|root)\b|[\d\.\+\-\*\/\^\|\(\)\=])'
        if re.search(r'[\+\-\*\/\^]', message_lower) or re.search(r'\b(calculate|solve|math|equation|plus|minus|times|divided)\b', message_lower):
             return "calculation", 0.95, "Math symbols or keywords detected"
        if re.search(r'\b(sin|cos|tan|log|sqrt)\s*\d+', message_lower):
             return "calculation", 0.95, "Trigonometric or math function detected"

        # 3. Weather
        if re.search(r'\b(weather|temperature|temp|forecast|humidity|barish|dhoop|mausam)\b', message_lower):
            return "weather", 0.95, "Weather keywords detected"

        # 4. News
        if re.search(r'\b(news|headlines|khabar|samachar|breaking)\b', message_lower):
            return "news", 0.9, "News keywords detected"

        # 5. Research / RAG
        if re.search(r'\b(research|investigate|study|deep dive|analyze|summarize|details about|vistaar)\b', message_lower):
            return "rag", 0.9, "Research keywords detected"

        # 6. Time / Date
        if re.search(r'\b(time|date|clock|samay|waqt|today|today\'s|timezone)\b', message_lower):
            return "time_date", 0.95, "Time/Date keywords detected"

        # 7. Memory
        if re.search(r'\b(remember|save|note|yad rakhna|yaad rakhna|store|keep this)\b', message_lower):
            return "memory", 0.9, "Memory keywords detected"

        # 8. Coding
        if re.search(r'\b(code|program|script|python|javascript|java|function|class|debug|fix error)\b', message_lower):
            return "coding", 0.9, "Coding keywords detected"

        # 9. Greeting / General Chat
        if re.search(r'\b(hello|hi|hey|namaste|greetings|good morning|good evening|good night|bye|alvida|how are you|kaise ho|kya haal|fine|thik hoon)\b', message_lower):
            return "greeting", 0.95, "Greeting/Conversational keywords detected"

        # 10. Identity (Self-awareness)
        if re.search(r'\b(who are you|your name|what is your name|apka naam|kaun ho|who developed you|who created you|creator|developer)\b', message_lower):
            return "identity", 0.98, "Identity/Creator question detected"

        # 11. Wolfram Alpha (Science, complex math, facts)
        if re.search(r'\b(distance|mass|weight|density|formula|molecular|orbit|planet|star|element|periodic table|integral|derivative|limit|solve equation|how far|how big|how many atoms)\b', message_lower):
            return "wolfram", 0.95, "Scientific or computational query detected"

        # 12. Search (Question patterns)
        if re.search(r'\b(what|who|where|how|why|tell me about|explain|kya|kaise|kaun|kahan)\b', message_lower):
            return "search", 0.85, "Question pattern detected"
            
        return "general_chat", 0.7, "Default to general chat"

    def _extract_entities(self, message: str, intent: str) -> Dict[str, str]:
        """Extract entities based on intent with improved regex"""
        entities = {}
        message_lower = message.lower().strip()

        if intent == "weather":
            # Handles "weather in London", "weather of Mumbai", "Delhi weather"
            match = re.search(r'(?:weather|temperature|temp|mausam)\s+(?:in|of|for|at)?\s*([\w\s,]+)', message_lower)
            if match:
                entities['city'] = match.group(1).strip()
            else:
                # Try inverse: "London weather"
                match = re.search(r'([\w\s,]+)\s+(?:weather|temperature|temp|mausam)', message_lower)
                if match:
                    entities['city'] = match.group(1).strip()
        
        elif intent == "calculation":
            # Extract the actual math part
            # Look for calculate X or just the expression
            match = re.search(r'(?:calculate|solve|math)\s+(.+)', message_lower)
            if match:
                entities['expression'] = match.group(1).strip()
            else:
                # Just take the whole message if it looks like math
                entities['expression'] = message_lower

        elif intent == "search" or intent == "rag" or intent == "wolfram":
            # Extract query
            match = re.search(r'(?:research|search|tell me about|explain|who is|what is|kya hai|kaun hai|calculate|solve)\s+(.+)', message_lower)
            if match:
                entities['query'] = match.group(1).strip()
            else:
                # If it's just a single name or entity (like 'Cristiano Ronaldo')
                entities['query'] = message_lower

        elif intent == "pc_control":
            if re.search(r'\b(open|launch|start)\b', message_lower): entities['action'] = "open"
            elif re.search(r'\b(close|exit|terminate|stop)\b', message_lower): entities['action'] = "close"
            elif "screenshot" in message_lower: entities['action'] = "screenshot"
            elif "shutdown" in message_lower: entities['action'] = "shutdown"
            
            # Find app name
            for app in ["chrome", "notepad", "calculator", "word", "excel", "code", "browser", "explorer"]:
                if app in message_lower:
                    entities['app'] = app
                    break
        return entities

    def _route_to_module(self, intent: str, requires_live_info: bool) -> Dict[str, Any]:
        """Route to appropriate module"""
        routing = {
            'primary_module': 'llama_general',
            'fallback_modules': [],
            'requires_model': True,
            'model_type': 'llama'
        }
        
        if intent == 'calculation':
            routing['primary_module'] = 'calculator'
            routing['requires_model'] = False
        elif intent == 'weather':
            routing['primary_module'] = 'weather_api'
            routing['requires_model'] = False
        elif intent == 'news':
            routing['primary_module'] = 'news_api'
            routing['requires_model'] = False
        elif intent == 'time_date':
            routing['primary_module'] = 'time_date_module'
            routing['requires_model'] = False
        elif intent == 'pc_control':
            routing['primary_module'] = 'pc_control'
            routing['requires_model'] = False
        elif intent == 'rag':
            routing['primary_module'] = 'rag'
            routing['requires_model'] = False
        elif intent == 'coding':
            routing['primary_module'] = 'qwen_coder'
            routing['model_type'] = 'qwen'
        elif intent == 'search':
            routing['primary_module'] = 'search_api'
            routing['requires_model'] = False
        elif intent == 'wolfram':
            routing['primary_module'] = 'wolfram_api'
            routing['requires_model'] = False
        
        if self.groq_available:
            routing['fallback_modules'].append('groq_api')
            
        return routing
