"""
Maya AI Router Module
Intelligent routing to determine best tool/model for each query
Minimizes model usage, prioritizes fast tools
"""

import re
import logging
from typing import Dict
from config import DEBUG_MODE

logger = logging.getLogger(__name__)

class IntentRouter:
    """Intelligent intent detection and routing"""
    
    def __init__(self):
        self.intent_patterns = self._init_patterns()
    
    def _init_patterns(self) -> dict:
        """Initialize intent detection patterns"""
        return {
            "calculation": {
                "patterns": [
                    r"[\+\-\*\/]",
                    r"(?:calculate|compute|solve|equals?)",
                    r"(?:what is|what's|give me)[\s\S]*(?:answer|result)",
                    r"(?:square|cube|power|root|sqrt|log|sin|cos|tan|integrate|derivative)",
                    r"\d+\s*(?:plus|minus|multiply|divide|times|by)",
                ],
                "priority": 1,
                "tool": "calculator"
            },
            
            "weather": {
                "patterns": [
                    r"(?:weather|temperature|temp|climate|forecast|rain|sunny)",
                    r"(?:how is the|what's the)[\s\S]*(?:weather|temperature)",
                    r"(?:today|tomorrow)[\s\S]*(?:weather|temp)",
                ],
                "priority": 1,
                "tool": "weather_api"
            },
            
            "news": {
                "patterns": [
                    r"(?:news|latest|breaking|today's|current events)",
                    r"(?:tell me about|give me|show me)[\s\S]*(?:news|headlines)",
                    r"(?:india|tech|sports|finance)[\s\S]*(?:news|updates)",
                ],
                "priority": 1,
                "tool": "news_api"
            },
            
            "search": {
                "patterns": [
                    r"(?:search for|find|look for|google)",
                    r"(?:how to|tutorial|guide on|best)",
                    r"(?:where|what|who|when)[\s\S]*(?:is|are|find)",
                    r"(?:tell me about|what are|what's)[\s\S]*(?:recent|latest|current|developments|news|trends)",
                    r"(?:recent|latest|current)[\s\S]*(?:developments|news|trends|updates|breakthroughs)",
                ],
                "priority": 1,
                "tool": "search_api"
            },
            
            "pc_control": {
                "patterns": [
                    r"(?:open|close|shut|launch|start|exit|stop)",
                    r"(?:chrome|firefox|vs code|notepad|calculator|explorer)",
                    r"(?:shutdown|restart|sleep|lock|mute|volume)",
                    r"(?:screenshot|take a picture|click|type)",
                ],
                "priority": 1,
                "tool": "pc_control"
            },
            
            "autonomous": {
                "patterns": [
                    r"(?:research|create document|make pdf|make word|create report|save as pdf)",
                    r"(?:search and create|document about|report on|create a file)",
                    r"(?:open ms office|open word|open excel|open powerpoint)",
                    r"(?:find images|search pictures|search photos|find photos)",
                ],
                "priority": 1,
                "tool": "autonomous_agent"
            },
            
            "coding": {
                "patterns": [
                    r"(?:code|program|script|write|function|algorithm)",
                    r"(?:python|javascript|java|c\+\+|html|css|sql)",
                    r"(?:debug|fix|error|bug|exception|trace)",
                    r"(?:how to code|make a program|create a script)",
                ],
                "priority": 2,
                "tool": "qwen_coder"
            },
            
            "memory": {
                "patterns": [
                    r"(?:remember|save|add to memory|store|remind me)",
                    r"(?:what did i|did i tell|my preference)",
                    r"(?:my custom command|my routine)",
                ],
                "priority": 1,
                "tool": "memory"
            },
            
            "greeting": {
                "patterns": [
                    r"(?:hello|hi|hey|hii|hy|hlo|good morning|good afternoon|good evening|greetings)",
                    r"(?:how are you|how do you do|nice to meet you)",
                    r"^(?:hi|hello|hey|hii|hy|hlo)[\s]*$",
                    r"^(?:hii|hey|hi)[\s]*$",
                ],
                "priority": 2,
                "tool": "llama_general"
            },
            
            "general_chat": {
                "patterns": [],  # Default
                "priority": 3,
                "tool": "llama_general"
            }
        }
    
    def detect_intent(self, query: str) -> dict:
        """Detect user intent and route appropriately"""
        query_lower = query.lower()
        
        # Initialize result
        result = {
            "intent": None,
            "tool": None,
            "priority": 999,
            "confidence": 0.0,
            "raw_query": query
        }
        
        # Check each intent
        for intent_name, intent_data in self.intent_patterns.items():
            if not intent_data["patterns"]:  # Skip default
                continue
            
            for pattern in intent_data["patterns"]:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    result["intent"] = intent_name
                    result["tool"] = intent_data["tool"]
                    result["priority"] = intent_data["priority"]
                    result["confidence"] = 0.9
                    
                    if DEBUG_MODE:
                        logger.info(f"✅ Intent detected: {intent_name} -> {intent_data['tool']}")
                    
                    return result
        
        # Default to general chat
        result["intent"] = "general_chat"
        result["tool"] = "llama_general"
        result["priority"] = 3
        result["confidence"] = 0.3
        
        return result
    
    def extract_entities(self, query: str, intent: str) -> dict:
        """Extract relevant entities from query"""
        entities = {}
        
        if intent == "weather":
            # Extract city name - multiple patterns
            city_patterns = [
                r"(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$)",
                r"weather\s+(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$)",
                r"weather\s+([A-Za-z\s]+?)(?:\?|$)",
                r"([A-Za-z\s]+?)\s+weather(?:\?|$)"
            ]
            
            for pattern in city_patterns:
                city_match = re.search(pattern, query, re.IGNORECASE)
                if city_match:
                    entities["city"] = city_match.group(1).strip()
                    break
            else:
                entities["city"] = "current_location"
        
        elif intent == "search":
            # Extract search query
            search_match = re.search(r"(?:search for|find|look for|google)\s+(.+?)(?:\?|$)", query)
            if search_match:
                entities["query"] = search_match.group(1).strip()
        
        elif intent == "pc_control":
            # Extract app/command name
            action_match = re.search(r"(?:open|close|launch|start|shut)\s+([A-Za-z\s]+?)(?:\?|$)", query)
            if action_match:
                entities["app"] = action_match.group(1).strip()
            
            # Extract action
            action = None
            if re.search(r"(?:open|launch|start)", query):
                action = "open"
            elif re.search(r"(?:close|shut|stop|exit)", query):
                action = "close"
            elif re.search(r"shutdown", query):
                action = "shutdown"
            elif re.search(r"restart", query):
                action = "restart"
            elif re.search(r"sleep", query):
                action = "sleep"
            elif re.search(r"screenshot", query):
                action = "screenshot"
            
            entities["action"] = action
        
        elif intent == "calculation":
            # Extract mathematical expression
            # Remove common words
            expr = re.sub(r"(?:what is|calculate|compute|equals?|give me the|the answer|answer is)", "", query, flags=re.IGNORECASE)
            entities["expression"] = expr.strip()
        
        elif intent == "coding":
            # Extract language
            languages = ["python", "javascript", "java", "c\\+\\+", "go", "rust", "html", "css", "sql"]
            for lang in languages:
                if re.search(lang, query, re.IGNORECASE):
                    entities["language"] = lang.replace("\\", "")
                    break
        
        return entities
    
    def should_use_model(self, intent: str) -> bool:
        """Determine if query needs AI model inference"""
        no_model_intents = [
            "calculation",
            "weather",
            "news",
            "search",
            "pc_control",
            "memory",
            "autonomous" # AutonomousAgent handles its own models if needed
        ]
        
        return intent not in no_model_intents
    
    def get_cost_estimate(self, intent: str) -> dict:
        """Estimate computational cost"""
        costs = {
            "calculation": {"tokens": 0, "time": 0.1, "model": None},
            "weather": {"tokens": 0, "time": 0.5, "model": None},
            "news": {"tokens": 0, "time": 0.5, "model": None},
            "search": {"tokens": 0, "time": 0.5, "model": None},
            "pc_control": {"tokens": 0, "time": 0.1, "model": None},
            "memory": {"tokens": 0, "time": 0.1, "model": None},
            "autonomous": {"tokens": 512, "time": 10.0, "model": "Llama 3.2"},
            "coding": {"tokens": 256, "time": 5.0, "model": "Qwen Coder"},
            "general_chat": {"tokens": 256, "time": 3.0, "model": "Llama 3.2"}
        }
        
        return costs.get(intent, costs["general_chat"])


class Router:
    """Main router combining all logic"""
    
    def __init__(self):
        self.intent_router = IntentRouter()
        self.request_count = 0
        self.model_calls = 0
    
    def route(self, query: str) -> dict:
        """Main routing function"""
        self.request_count += 1
        
        # Detect intent
        intent_result = self.intent_router.detect_intent(query)
        
        # Extract entities
        entities = self.intent_router.extract_entities(query, intent_result["intent"])
        
        # Determine if model needed
        needs_model = self.intent_router.should_use_model(intent_result["intent"])
        if needs_model:
            self.model_calls += 1
        
        # Get cost estimate
        cost = self.intent_router.get_cost_estimate(intent_result["intent"])
        
        routing_decision = {
            "intent": intent_result["intent"],
            "tool": intent_result["tool"],
            "entities": entities,
            "needs_model": needs_model,
            "confidence": intent_result["confidence"],
            "cost": cost,
            "raw_query": query
        }
        
        if DEBUG_MODE:
            logger.info(f"🔀 Routing decision: {routing_decision['intent']} -> {routing_decision['tool']}")
        
        return routing_decision
    
    def get_stats(self) -> dict:
        """Get routing statistics"""
        return {
            "total_requests": self.request_count,
            "model_calls": self.model_calls,
            "tool_only_calls": self.request_count - self.model_calls,
            "model_ratio": self.model_calls / max(1, self.request_count)
        }


# Singleton
router = Router()

if DEBUG_MODE:
    print("🔀 Maya Router initialized")
