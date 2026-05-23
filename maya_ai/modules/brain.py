"""
Maya AI Brain Module
Master brain that orchestrates all modules
"""

import logging
import time
from typing import Dict, Any
from config import DEBUG_MODE, LOGS_DIR, OWNER_NAME, GROQ_API_KEY, AGENTIC_MODE, HINGLISH_MODE
from .hinglish import HinglishConverter

# Import all modules
from modules.router import router
from modules.decision_making import DecisionMaker
from modules.calculator import calculator
from modules.tools import weather_api, news_api, search_api
from modules.pc_control import pc_control
from modules.models import local_models, model_cache
from modules.memory import memory
from modules.autonomous_agent import autonomous_agent
from modules.rag_search import WebRAGEngine
from modules.time_date import TimeDateModule
from modules.groq_api import GroqAPI
from modules.system_info import system_info
from modules.xai import xai_engine
from modules.smart_agent_response import smart_agent

logger = logging.getLogger(__name__)

class MayaBrain:
    """Master brain that orchestrates all modules"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.cache = {}
        self.hinglish_converter = HinglishConverter()
        self.last_query = None
        self.last_response = None
        self.direct_mode = True  # Answer only what user asks
        self.response_times = []
        self.router = router  # Add router reference
        self.decision_maker = DecisionMaker()
        
        # Initialize advanced engines
        self.rag_engine = WebRAGEngine()
        self.time_date = TimeDateModule()
        self.groq = GroqAPI(GROQ_API_KEY) if GROQ_API_KEY else None
        
        if DEBUG_MODE:
            logger.info("🧠 Maya Brain initialized")
            logger.info("🗣️ Hinglish converter ready")
    
    def process_query(self, query: str) -> dict:
        """Main query processing function with enhanced intelligence"""
        start_time = time.time()
        self.request_count += 1
        self.last_query = query
        
        response = {
            "query": query,
            "response": None,
            "hinglish_response": None,
            "intent": None,
            "tool_used": None,
            "model_used": None,
            "tokens_used": 0,
            "time_taken": 0,
            "success": False,
            "thought": None,
            "xai_report": None
        }
        
        try:
            # 0. Start XAI Trace
            xai_engine.start_trace(query)

            # 1. Thinking Phase (Self-thinking capability)
            thought = self._think_about_query(query)
            response["thought"] = thought
            xai_engine.add_step("Thought Process", "Analyze", thought, "Internal reasoning about user intent and context")
            
            # 2. Check cache first (The 'C' for fast response)
            cache_key = f"thought_cache:{query}"
            cached = model_cache.get(cache_key)
            if cached:
                response["response"] = cached["value"]
                response["hinglish_response"] = cached["value"]
                response["success"] = True
                response["model_used"] = "Cache"
                if DEBUG_MODE:
                    logger.info("💾 Retrieved from cache")
                return response

            # 3. Route the query using enhanced Decision Maker + Thought
            decision = self.decision_maker.decide_module("unknown", query)
            intent = decision["intent"]
            xai_engine.add_step("Intent Classification", "Classify", intent, f"Model predicted intent as {intent} with reasoning: {decision.get('reasoning')}")
            
            # Special override for identity and creator questions
            if intent == "identity" or any(kw in query.lower() for kw in ["who developed", "who created", "who made", "creator", "developed by", "made by", "developer"]):
                from config import DEVELOPER_NAME, AI_NAME
                response["intent"] = "identity"
                if any(kw in query.lower() for kw in ["your name", "who are you", "kaun ho", "aapka naam"]):
                    response["response"] = f"I am {AI_NAME}, your AI assistant, developed by {DEVELOPER_NAME}."
                    response["hinglish_response"] = f"Main {AI_NAME} hoon, aapki AI assistant. Mujhe {DEVELOPER_NAME} ne develop kiya hai."
                else:
                    response["response"] = f"I was developed and created by {DEVELOPER_NAME}."
                    response["hinglish_response"] = f"Mujhe {DEVELOPER_NAME} ne develop aur create kiya hai."
                
                response["model_used"] = "System Identity"
                return response

            response["intent"] = intent
            response["tool_used"] = decision["primary_module"]
            
            # Extract entities
            entities = decision.get("entities", {})
            
            routing_decision = {
                "intent": intent,
                "tool": response["tool_used"],
                "entities": entities
            }
            
            if DEBUG_MODE:
                logger.info(f"🧠 Processing: {query[:50]}...")
                logger.info(f"💭 Thought: {thought}")
            
            # 4. Collect information from multiple sources
            sources = {"thought": thought}
            
            # Detect multiple intents
            detected_intents = self._detect_all_intents(query)
            
            for intent_item in detected_intents:
                intent_name = intent_item["intent"]
                primary_module = intent_item["primary_module"]
                
                exec_decision = {
                    "intent": intent_name,
                    "tool": primary_module,
                    "entities": intent_item["entities"]
                }
                
                tool_result = self._execute_tool(exec_decision, query)
                if tool_result.get("success"):
                    sources[f"tool_{intent_name}"] = tool_result.get("response")
                    xai_engine.add_step(f"Tool Execution: {intent_name}", "Execute", primary_module, f"Retrieved data from {primary_module}")
            
            # Groq Cloud Source for deep intelligence
            if self.groq and self.groq.is_ready():
                groq_resp = self.groq.infer(f"Context: {thought}\nUser: {query}")
                if not groq_resp.startswith("❌"):
                    sources["groq_cloud"] = groq_resp
            
            # 5. Synthesize and Filter with high intelligence
            history_tuples = memory.get_chat_history(limit=5)
            # Convert tuples to dicts for smart_agent compatibility
            history = [
                {'query': h[0], 'response': h[1], 'intent': h[2], 'timestamp': h[3]}
                for h in history_tuples
            ] if history_tuples else []
            verified_response = self._synthesize_with_llama(query, sources, history_tuples)
            
            if verified_response:
                # Apply smart agent response enhancement
                smart_response = smart_agent.generate_smart_response(
                    query=query,
                    intent=intent,
                    entities=entities,
                    raw_response=verified_response,
                    conversation_history=history,
                    user_preferences=memory.get_all_preferences()
                )
                
                # Format final response with smart agent features
                final_response = smart_agent.format_final_response(smart_response, verified_response)
                
                response["response"] = final_response
                response["hinglish_response"] = self._make_direct_response(final_response)
                response["model_used"] = "Intelligent Synthesis + Smart Agent"
                response["success"] = True
                response["smart_agent_features"] = smart_agent.get_response_summary(smart_response)
                xai_engine.add_step("Multi-Source Synthesis", "Synthesize", "Llama 3.2", "Filtered and combined data from all sources into a final natural response")
                
                # Generate XAI report
                from modules.elite_nlp_engine import elite_nlp
                nlp_data = elite_nlp.process(query)
                xai_engine.current_report.attention_map = xai_engine.generate_attention_map(query, nlp_data)
                response["xai_report"] = xai_engine.finalize_report(intent, decision.get('confidence', 0.0), list(sources.keys()))

                # Cache final result
                model_cache.set(cache_key, response["hinglish_response"])
            else:
                fallback = sources.get("tool_search") or sources.get("groq_cloud") or "❌ Maaf kijiye, koi jaankari nahi mili."
                
                # Apply smart agent enhancement if agentic mode is enabled
                if AGENTIC_MODE:
                    smart_fallback = smart_agent.generate_smart_response(
                        query=query,
                        intent=intent,
                        entities=entities,
                        raw_response=fallback,
                        conversation_history=history,
                        user_preferences=memory.get_all_preferences()
                    )
                    formatted_fallback = smart_agent.format_final_response(smart_fallback, fallback)
                    response["response"] = formatted_fallback
                    response["hinglish_response"] = self._make_direct_response(formatted_fallback)
                else:
                    response["response"] = fallback
                    response["hinglish_response"] = self._make_direct_response(fallback)
                
                response["success"] = True
            
            # Save to memory
            memory.save_chat(query, response["hinglish_response"], response["intent"], response["tokens_used"])
            
            # Track response time
            response_time = time.time() - start_time
            response["time_taken"] = response_time
            self.response_times.append(response_time)
            
            return response

        except Exception as e:
            logger.error(f"❌ Brain error: {str(e)}")
            response["response"] = f"❌ Error: {str(e)}"
            response["hinglish_response"] = f"❌ Kuch galat huva: {str(e)}"
            response["success"] = False
            return response
    
    def _detect_all_intents(self, query: str) -> list:
        """Detect all relevant intents in a query for multi-tool execution"""
        query_lower = query.lower()
        all_intents = []
        
        # Primary decision
        primary = self.decision_maker.decide_module("unknown", query)
        all_intents.append(primary)
        
        # Check for other high-confidence intents (simple keyword check for multi-turn)
        # Avoid duplicate tools for the same query
        seen_tools = {primary["primary_module"]}
        
        check_list = [
            ("weather", ["weather", "mausam", "temperature"]),
            ("news", ["news", "khabar", "headlines"]),
            ("calculation", ["+", "-", "*", "/", "sin ", "cos ", "sqrt"]),
            ("time_date", ["time", "date", "waqt", "samay"]),
            ("wolfram", ["distance", "mass", "weight", "formula", "molecular", "orbit", "planet", "integral", "derivative", "solve equation"]),
            ("search", ["who is", "what is", "where is", "tell me about"]),
            ("pc_control", ["open", "close", "start", "stop", "screenshot"])
        ]
        
        for intent_name, keywords in check_list:
            if any(kw in query_lower for kw in keywords):
                # Only add if not already primary and not general_chat
                if intent_name != primary["intent"]:
                    # Create a mini-decision
                    secondary = self.decision_maker.analyze_user_input(query)
                    # Force the intent if keywords matched
                    if secondary.primary_module not in seen_tools:
                         all_intents.append({
                             "intent": intent_name,
                             "primary_module": self.decision_maker._route_to_module(intent_name, False)["primary_module"],
                             "entities": self.decision_maker._extract_entities(query, intent_name)
                         })
                         seen_tools.add(all_intents[-1]["primary_module"])
        
        return all_intents

    def _execute_tool(self, routing_decision: dict, query: str) -> dict:
        """Execute appropriate tool based on routing"""
        result = {
            "response": None,
            "hinglish_response": None,
            "model_used": None,
            "tokens_used": 0,
            "success": False
        }
        
        intent = routing_decision["intent"]
        entities = routing_decision["entities"]
        
        try:
            # ==================== CALCULATOR ====================
            if intent == "calculation":
                expr = entities.get("expression", query)
                calc_result = calculator.parse_and_calculate(expr)
                result["response"] = calc_result.get("result")
                result["hinglish_response"] = calc_result.get("hinglish")
                result["success"] = True
            
            # ==================== WEATHER ====================
            elif intent == "weather":
                city = entities.get("city", "current")
                try:
                    weather = weather_api.get_hinglish_weather(city)
                    if weather and not weather.startswith("❌"):
                        result["response"] = weather
                        result["hinglish_response"] = weather
                        result["success"] = True
                    else:
                        result["success"] = False
                except Exception as e:
                    result["success"] = False
            
            # ==================== NEWS ====================
            elif intent == "news":
                topic = entities.get("topic", "india")
                try:
                    news = news_api.get_hinglish_news(topic, limit=3)
                    if news and not news.startswith("❌"):
                        result["response"] = news
                        result["hinglish_response"] = news
                        result["success"] = True
                    else:
                        result["success"] = False
                except Exception as e:
                    result["success"] = False
            
            # ==================== SEARCH ====================
            elif intent == "search":
                search_query = entities.get("query", query)
                try:
                    search_results = search_api.get_hinglish_search(search_query, limit=3)
                    if search_results and not search_results.startswith("❌"):
                        result["response"] = search_results
                        result["hinglish_response"] = search_results
                        result["success"] = True
                    else:
                        result["success"] = False
                except Exception as e:
                    result["success"] = False

            # ==================== WOLFRAM ALPHA ====================
            elif intent == "wolfram":
                wolfram_query = entities.get("query", query)
                try:
                    wolfram_results = wolfram_api.get_hinglish_wolfram(wolfram_query)
                    if wolfram_results and not wolfram_results.startswith("❌"):
                        result["response"] = wolfram_results
                        result["hinglish_response"] = wolfram_results
                        result["success"] = True
                    else:
                        result["success"] = False
                except Exception as e:
                    result["success"] = False

            # ==================== RAG (Research) ====================
            elif intent == "rag":
                search_query = entities.get("query", query)
                try:
                    rag_result = self.rag_engine.deep_search(search_query)
                    if rag_result.get("success"):
                        result["response"] = rag_result.get("response")
                        result["hinglish_response"] = self._translate_to_hinglish(rag_result.get("response"))
                        result["success"] = True
                    else:
                        result["success"] = False
                except Exception as e:
                    result["success"] = False

            # ==================== TIME / DATE ====================
            elif intent == "time_date":
                try:
                    city = entities.get("city", "ist")
                    time_info = self.time_date.get_current_time(city)
                    if "error" not in time_info:
                        resp = f"Current time in {time_info['timezone_full']} is {time_info['time_12h']} ({time_info['date']})"
                        result["response"] = resp
                        result["hinglish_response"] = f"Abhi {time_info['timezone_full']} mein {time_info['time_12h']} ho rahe hain."
                        result["success"] = True
                    else:
                        result["success"] = False
                except Exception as e:
                    result["success"] = False
            
            # ==================== PC CONTROL ====================
            elif intent == "pc_control":
                action = entities.get("action")
                app = entities.get("app")
                
                if action == "open" and app:
                    pc_result = pc_control.open_app(app)
                elif action == "close" and app:
                    pc_result = pc_control.close_app(app)
                elif action == "shutdown":
                    pc_result = pc_control.shutdown(delay=0)
                elif action == "restart":
                    pc_result = pc_control.restart(delay=0)
                elif action == "sleep":
                    pc_result = pc_control.sleep_mode()
                elif action == "screenshot":
                    pc_result = pc_control.screenshot()
                else:
                    pc_result = {"hinglish": "❌ Command samajh nahi aaya"}
                
                result["response"] = pc_result.get("message", "Done")
                result["hinglish_response"] = pc_result.get("hinglish", "Done")
                result["success"] = pc_result.get("success", False)
            
            # ==================== AUTONOMOUS ====================
            elif intent == "autonomous":
                agent_result = autonomous_agent.process_request(query)
                result["response"] = agent_result.get("summary", "Task completed")
                result["hinglish_response"] = f"✅ Kaam ho gaya bhai! {agent_result.get('summary', '')}"
                result["success"] = agent_result.get("success", False)
            
            # ==================== CODING ====================
            elif intent == "coding":
                model_result = local_models.smart_routing(query, "coding")
                result["response"] = model_result.get("response")
                result["hinglish_response"] = model_result.get("response")
                result["model_used"] = model_result.get("model_used")
                result["tokens_used"] = model_result.get("tokens_used", 0)
                result["success"] = True
            
            # ==================== GENERAL CHAT ====================
            elif intent == "general_chat" or intent == "greeting":
                model_result = local_models.smart_routing(query, "general_chat")
                result["response"] = model_result.get("response")
                result["hinglish_response"] = self._translate_to_hinglish(model_result.get("response"))
                result["model_used"] = model_result.get("model_used")
                result["tokens_used"] = model_result.get("tokens_used", 0)
                result["success"] = True
            
            else:
                # Unknown intent - use general model
                model_result = local_models.smart_routing(query, "general_chat")
                result["response"] = model_result.get("response")
                result["hinglish_response"] = self._translate_to_hinglish(model_result.get("response"))
                result["model_used"] = model_result.get("model_used")
                result["success"] = True
        
        except Exception as e:
            logger.error(f"❌ Tool execution error: {str(e)}")
            result["success"] = False
        
        return result
    
    def _think_about_query(self, query: str) -> str:
        """Self-thinking phase: Analyze query before acting"""
        try:
            prompt = f"""### TASK:
Analyze the user's query and decide what they really want. 
Think about the context, entities, and the most intelligent way to respond.
If the query is a single name (like 'Cristiano Ronaldo'), realize they want an interesting overview or latest news about that person.

User Query: "{query}"

### RULES:
1. Provide a 1-sentence thought on how to handle this intelligently.
2. Identify the main entities.
3. Decide if we need real-time data or general knowledge.

### THOUGHT:"""
            thought = local_models.smart_routing(prompt, "general_chat")
            return thought.get("response", "Analyzing query...")
        except Exception:
            return "Analyzing query..."

    def _synthesize_with_llama(self, query: str, info_sources: dict, history: list) -> str:
        """Synthesize a final intelligent response using Llama by filtering multiple info sources"""
        try:
            # Get real-time context
            context = system_info.get_full_context_string()
            
            # Format history (history is a list of tuples: (query, response, intent, timestamp))
            hist_str = ""
            for h in reversed(history): # Show oldest to newest
                query_text = h[0]
                resp_text = h[1]
                hist_str += f"User: {query_text}\nMaya: {resp_text}\n"

            prompt = f"""### SYSTEM CONTEXT:
{context}

### CONVERSATION HISTORY:
{hist_str}

### INFORMATION SOURCES:
{info_sources}

### TASK:
Synthesize a highly intelligent, conversational, and natural answer.
Do NOT just list facts. Connect the dots. 
If the user asks about a famous person, provide a summary that sounds like a human expert.
Be respectful (Sir/Boss) and use female grammar in Hinglish.

User Question: "{query}"

### RULES:
1. Address as "Sir" or "Boss".
2. Use natural Hinglish with female grammar.
3. Be smart: if the user mentions two people in a row, they might be comparing them or following a theme.
4. Respond ONLY with the final verified answer text.

### FINAL INTELLIGENT ANSWER:"""

            # Use local llama for synthesis
            synthesis = local_models.smart_routing(prompt, "general_chat")
            final_text = synthesis.get("response", "")
            
            if final_text and not final_text.startswith("❌"):
                return final_text
            return None
        except Exception as e:
            logger.error(f"⚠️ Synthesis error: {e}")
            return None

    def _make_direct_response(self, text: str) -> str:
        """Make response direct and concise"""
        if not text or not self.direct_mode:
            return text

        # If this is a creator response, don't strip names if that's the point
        if self.last_response and self.last_response.get("intent") == "creator_info":
             return text

        import re
        
        # Aggressively remove creator mention if not specifically asked
        if "Abhay Kumar Rudrapaul" in text:
             text = re.sub(r'(?:Mujhe\s+)?Abhay Kumar Rudrapaul\s+(?:ne\s+)?(?:develop\s+aur\s+create\s+)?(?:kiya\s+hai|banaya\s+hai)[.,!\s]*', '', text, flags=re.I)
             text = re.sub(r'\bAbhay Kumar Rudrapaul\b', '', text, flags=re.I)

        # Normalize
        text = text.strip()
        
        # Remove context echoing if present
        text = re.sub(r'\[CONTEXT\].*?Current Time: \d{2}:\d{2}:\d{2}\.?', '', text, flags=re.S).strip()
        text = re.sub(r'### SYSTEM CONTEXT:.*?### FINAL VERIFIED ANSWER:', '', text, flags=re.S).strip()

        # If multi-paragraph, prefer the last paragraph
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        if len(paragraphs) > 1:
            text = paragraphs[-1]

        # Split into sentences and remove pure-intro sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)

        intro_pattern = re.compile(r'^(?:namaste|hello|hi|bilkul|main|mujhe|mera|dear|hello|hi|hey|greetings|abha?y|user)\b', re.I)
        filtered = [s for s in sentences if not intro_pattern.search(s.strip())]

        # Compose candidate from filtered sentences if available
        if filtered:
            candidate = " ".join([s.strip() for s in filtered]).strip()
        else:
            # Fallback: use original text but strip common salutations
            prefixes_to_strip = [r"^Bilkul[,!\s]*", r"^Namaste[,!\s]*", r"^Hello[,!\s]*", r"^Hi[,!\s]*", r"^Hey[,!\s]*", r"^Mujhe[,!\s]*", r"^Main[,!\s]*"]
            candidate = text
            for p in prefixes_to_strip:
                candidate = re.sub(p, '', candidate, flags=re.I).strip()

        # Remove repetitive ownership mentions
        candidate = re.sub(r'\bAbhay Kumar Rudrapaul\b[,;:\-\s]*', '', candidate, flags=re.I)
        candidate = re.sub(r'\bAbhay\b[,;:\-\s]*', '', candidate, flags=re.I)
        candidate = re.sub(r'^[,;:\-\s]+', '', candidate)

        # Collapse whitespace
        candidate = re.sub(r'\s+', ' ', candidate).strip()

        # Prefer the first one or two sentences
        sent_parts = re.split(r'(?<=[.!?])\s+', candidate)
        if len(sent_parts) > 2:
            candidate = ' '.join(sent_parts[:2]).strip()

        # Trim overly long replies
        if len(candidate) > 300:
            candidate = candidate[:300].rsplit(' ', 1)[0] + '...'

        return candidate
    
    def _translate_to_hinglish(self, text: str) -> str:
        """Convert response to Hinglish (simple version)"""
        if not HINGLISH_MODE or not text:
            return text
        
        # Simple phrase replacements for Hinglish
        replacements = {
            "hello": "Namaste",
            "hi": "Hi",
            "goodbye": "Bye",
            "please": "Kripaya",
            "thank you": "Shukriya",
            "yes": "Haan",
            "no": "Nahi",
            "ok": "Theek hai",
            "okay": "Theek hai",
        }
        
        result = text
        for eng, hindi in replacements.items():
            result = result.replace(eng, hindi)
            result = result.replace(eng.capitalize(), hindi)
        
        return result
    
    # ==================== SYSTEM INFO ====================
    
    def get_smart_greeting(self, vui_mode: bool = False) -> str:
        """Get greeting - username only in CLI mode, not VUI"""
        from datetime import datetime
        hour = datetime.now().hour
        name_prefix = f"{OWNER_NAME}, " if not vui_mode else ""
        if 5 <= hour < 12:
            return f"Good morning, {name_prefix}Aaj kya plan hai?"
        elif 12 <= hour < 17:
            return f"Good afternoon, {name_prefix}Kaise chal raha hai kaam?"
        elif 17 <= hour < 21:
            return f"Good evening, {name_prefix}Thoda break le lo."
        else:
            return f"Hello, {name_prefix}Der ho gayi hai, par main ready hoon."
    
    def get_statistics(self) -> dict:
        """Get system statistics"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        routing_stats = router.get_stats()
        
        return {
            "total_queries": self.request_count,
            "avg_response_time": avg_response_time,
            "model_efficiency": {
                "total_requests": routing_stats["total_requests"],
                "model_calls": routing_stats["model_calls"],
                "tool_only_calls": routing_stats["tool_only_calls"],
                "model_ratio": f"{routing_stats['model_ratio']:.1%}"
            },
            "memory_stats": {
                "chat_history": len(memory.get_chat_history(limit=1000)),
                "preferences": len(memory.get_all_preferences()),
                "routines": len(memory.get_routines())
            }
        }


# Singleton
brain = MayaBrain()

if DEBUG_MODE:
    print("🧠 Maya Brain initialized")
