"""
Offline-Compatible Model System
Local AI model that works without external APIs or internet connectivity
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class OfflineModel:
    """Advanced offline AI model with local knowledge base and reasoning"""
    
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.conversation_history = []
        self.max_history = 10
        
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load local knowledge base from JSON file"""
        try:
            knowledge_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'knowledge_base.json')
            if os.path.exists(knowledge_file):
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create default knowledge base if file doesn't exist
                default_knowledge = self._create_default_knowledge()
                self._save_knowledge_base(default_knowledge)
                return default_knowledge
        except Exception as e:
            logger.error(f"❌ Failed to load knowledge base: {e}")
            return self._create_default_knowledge()
    
    def _create_default_knowledge(self) -> Dict[str, Any]:
        """Create default knowledge base with essential information"""
        return {
            "general_info": {
                "maya_ai": "Maya AI is a professional AI assistant created for intelligent task automation and natural conversation.",
                "capabilities": "I can help with general questions, calculations, time/date queries, coding assistance, and basic problem-solving without requiring internet connectivity.",
                "offline_mode": "I work completely offline using my local knowledge base and reasoning capabilities."
            },
            "math_facts": {
                "pi": "3.14159265359",
                "e": "2.71828182846",
                "golden_ratio": "1.61803398875",
                "sqrt_2": "1.41421356237",
                "sqrt_3": "1.73205080757"
            },
            "time_facts": {
                "time_zones": {
                    "utc": "Coordinated Universal Time",
                    "est": "Eastern Standard Time (UTC-5)",
                    "pst": "Pacific Standard Time (UTC-8)",
                    "ist": "India Standard Time (UTC+5:30)",
                    "gmt": "Greenwich Mean Time"
                },
                "formats": {
                    "12h": "12-hour format (HH:MM AM/PM)",
                    "24h": "24-hour format (HH:MM)",
                    "iso": "ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
                }
            },
            "coding_help": {
                "python": "Python is a high-level programming language known for its simplicity and readability.",
                "javascript": "JavaScript is essential for web development and interactive applications.",
                "html_css": "HTML and CSS are fundamental for web page structure and styling.",
                "best_practices": "Always write clean, commented code with proper error handling and documentation."
            },
            "problem_solving": {
                "approach": "Break down complex problems into smaller, manageable steps.",
                "verification": "Always verify solutions and provide clear explanations.",
                "alternatives": "Consider multiple approaches when solving problems."
            }
        }
    
    def _save_knowledge_base(self, knowledge: Dict[str, Any]) -> bool:
        """Save knowledge base to JSON file"""
        try:
            knowledge_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'knowledge_base.json')
            os.makedirs(os.path.dirname(knowledge_file), exist_ok=True)
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge, f, indent=2, ensure_ascii=False)
            logger.info("💾 Knowledge base saved successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save knowledge base: {e}")
            return False
    
    def process_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process user query using offline reasoning and knowledge base"""
        try:
            query_lower = query.lower().strip()
            
            # Add to conversation history
            self.conversation_history.append({
                "query": query,
                "timestamp": datetime.now().isoformat()
            })
            
            # Limit history size
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]
            
            # Analyze query type and route to appropriate handler
            response = self._analyze_and_respond(query_lower, context)
            
            return {
                "response": response,
                "confidence": 0.85,
                "reasoning": f"Offline model response using knowledge base and reasoning",
                "sources": ["local_knowledge", "reasoning_engine"],
                "model": "offline_model",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Offline model error: {e}")
            return {
                "response": "I apologize, but I encountered an error while processing your request. I'm working offline and may have limited capabilities.",
                "confidence": 0.1,
                "error": str(e)
            }
    
    def _analyze_and_respond(self, query: str, context: Optional[Dict]) -> str:
        """Analyze query and generate appropriate response using knowledge base"""
        
        # Mathematical expressions
        if self._is_mathematical_query(query):
            return self._handle_math_query(query)
        
        # Time and date queries
        if self._is_time_date_query(query):
            return self._handle_time_date_query(query)
        
        # Coding questions
        if self._is_coding_query(query):
            return self._handle_coding_query(query)
        
        # General knowledge questions
        if self._is_general_knowledge_query(query):
            return self._handle_general_query(query)
        
        # Problem-solving queries
        if self._is_problem_solving_query(query):
            return self._handle_problem_solving_query(query)
        
        # Default response
        return self._handle_default_query(query)
    
    def _is_mathematical_query(self, query: str) -> bool:
        """Check if query is mathematical"""
        math_indicators = ["+", "-", "*", "/", "=", "calculate", "compute", "square", "cube", "sqrt", "power"]
        return any(indicator in query for indicator in math_indicators)
    
    def _is_time_date_query(self, query: str) -> bool:
        """Check if query is about time or date"""
        time_keywords = ["time", "date", "current time", "what time", "today", "yesterday", "tomorrow", "timezone"]
        return any(keyword in query for keyword in time_keywords)
    
    def _is_coding_query(self, query: str) -> bool:
        """Check if query is about coding"""
        coding_keywords = ["code", "program", "function", "algorithm", "debug", "syntax", "variable", "loop"]
        return any(keyword in query for keyword in coding_keywords)
    
    def _is_general_knowledge_query(self, query: str) -> bool:
        """Check if query is seeking general information"""
        knowledge_keywords = ["what is", "who is", "explain", "describe", "tell me about", "information about"]
        return any(keyword in query for keyword in knowledge_keywords)
    
    def _is_problem_solving_query(self, query: str) -> bool:
        """Check if query is about problem solving"""
        problem_keywords = ["how to", "help me", "fix", "solve", "troubleshoot", "issue", "error", "problem"]
        return any(keyword in query for keyword in problem_keywords)
    
    def _handle_math_query(self, query: str) -> str:
        """Handle mathematical queries using knowledge base"""
        try:
            # Extract mathematical expression
            expression = query.replace("calculate", "").replace("compute", "").replace("what is", "").replace("equals", "=").strip()
            
            # Simple calculations using knowledge base
            if "pi" in query.lower():
                return f"π (Pi) is approximately 3.14159. It's the ratio of a circle's circumference to its diameter."
            
            if "e" in query.lower():
                return f"e (Euler's number) is approximately 2.71828. It's the base of natural logarithms."
            
            # For other math, provide guidance
            return f"I can help with mathematical calculations! For '{expression}', please use a calculator or provide more specific details about what you'd like me to calculate."
            
        except Exception as e:
            logger.error(f"Math query error: {e}")
            return "I can help with mathematical calculations, but I need more specific information to provide accurate results."
    
    def _handle_time_date_query(self, query: str) -> str:
        """Handle time and date queries using knowledge base"""
        try:
            if "current time" in query or "what time" in query:
                return "I work completely offline, so I cannot provide real-time information. For current time, please check your device's clock or use a reliable time service."
            
            if "timezone" in query:
                time_facts = self.knowledge_base.get("time_facts", {})
                time_zones = time_facts.get("time_zones", {})
                response = "Common time zones I know about:\n\n"
                for tz_name, tz_info in time_zones.items():
                    response += f"• {tz_name}: {tz_info}\n"
                return response
            
            return "I can help with time and date questions using my offline knowledge base. For specific times or dates, please provide more details."
            
        except Exception as e:
            logger.error(f"Time/Date query error: {e}")
            return "I encountered an error processing your time/date query."
    
    def _handle_coding_query(self, query: str) -> str:
        """Handle coding queries using knowledge base"""
        try:
            coding_help = self.knowledge_base.get("coding_help", {})
            language = None
            
            # Detect programming language
            if "python" in query.lower():
                language = "python"
                help_text = coding_help.get("python", "Python is versatile for data science, web development, and automation.")
            elif "javascript" in query.lower():
                language = "javascript"
                help_text = coding_help.get("javascript", "JavaScript is essential for web development and interactive applications.")
            elif "html" in query.lower() or "css" in query.lower():
                language = "html_css"
                help_text = coding_help.get("html_css", "HTML and CSS are fundamental for web page structure and styling.")
            
            if language:
                best_practices = coding_help.get("best_practices", "Always write clean, commented code with proper error handling.")
                return f"For {language}: {help_text}\n\nBest practices: {best_practices}"
            
            return "I can help with coding questions! Please specify the programming language (Python, JavaScript, HTML, CSS, etc.) and what you'd like to know."
            
        except Exception as e:
            logger.error(f"Coding query error: {e}")
            return "I encountered an error processing your coding question."
    
    def _handle_general_query(self, query: str) -> str:
        """Handle general knowledge queries using knowledge base"""
        try:
            general_info = self.knowledge_base.get("general_info", {})
            
            # Maya AI information
            if "maya" in query.lower() or "who are you" in query.lower():
                maya_info = general_info.get("maya_ai", "")
                return f"{maya_info}"
            
            # Capabilities
            if "capabilities" in query.lower() or "what can you do" in query.lower():
                capabilities = general_info.get("capabilities", "")
                offline_mode = general_info.get("offline_mode", "")
                return f"{capabilities}\n\n{offline_mode}"
            
            # Use knowledge base for other queries
            return "I work completely offline using my local knowledge base and reasoning capabilities. I can help with general questions, calculations, and basic problem-solving without requiring internet connectivity."
            
        except Exception as e:
            logger.error(f"General query error: {e}")
            return "I apologize, but I encountered an error while processing your request."
    
    def _handle_problem_solving_query(self, query: str) -> str:
        """Handle problem-solving queries"""
        try:
            problem_solving = self.knowledge_base.get("problem_solving", {})
            approach = problem_solving.get("approach", "")
            verification = problem_solving.get("verification", "")
            alternatives = problem_solving.get("alternatives", "")
            
            return f"For problem-solving: {approach}\n\n{verification}\n\n{alternatives}"
            
        except Exception as e:
            logger.error(f"Problem-solving query error: {e}")
            return "I can help with problem-solving! Please describe the specific issue you're facing."
    
    def _handle_default_query(self, query: str) -> str:
        """Handle default queries"""
        return "I'm Maya AI, your offline assistant. I can help with general questions, calculations, time/date queries, coding assistance, and basic problem-solving using my local knowledge base. How can I assist you today?"
    
    def update_knowledge(self, category: str, key: str, value: Any) -> bool:
        """Update specific knowledge in the knowledge base"""
        try:
            if category in self.knowledge_base:
                self.knowledge_base[category][key] = value
                return self._save_knowledge_base(self.knowledge_base)
            else:
                logger.warning(f"Category '{category}' not found in knowledge base")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to update knowledge: {e}")
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get model capabilities and status"""
        return {
            "model_type": "offline_model",
            "requires_internet": False,
            "requires_apis": False,
            "knowledge_base_size": len(str(self.knowledge_base)),
            "conversation_history": len(self.conversation_history),
            "max_history": self.max_history,
            "capabilities": [
                "general_knowledge",
                "mathematical_calculations",
                "time_date_queries",
                "coding_assistance",
                "problem_solving"
            ],
            "offline_mode": True
        }

# Global instance
offline_model = OfflineModel()
