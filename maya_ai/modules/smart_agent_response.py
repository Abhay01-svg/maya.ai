"""
Smart Agent Response Module
Enhances Maya's responses with intelligent, context-aware, agent-like behavior
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ResponseContext:
    """Context for generating smart responses"""
    query: str
    intent: str
    entities: Dict[str, str]
    conversation_history: List[Dict]
    user_preferences: Dict[str, Any]
    time_of_day: str
    previous_queries: List[str]


class SmartAgentResponse:
    """
    Smart Agent Response Generator
    Makes Maya respond like an intelligent agent with:
    - Contextual awareness
    - Proactive suggestions
    - Clarifying questions
    - Natural conversation flow
    - Multi-step reasoning
    """
    
    def __init__(self):
        # Enhanced response templates - more sophisticated and agent-like
        self.response_templates = {
            'calculation': {
                'acknowledgment': "I'll calculate that for you.",
                'working': "Processing the mathematical expression...",
                'completion': "Here's the result.",
                'follow_up': "Would you like me to explain the steps or try another calculation?"
            },
            'weather': {
                'acknowledgment': "Let me check the weather conditions for you.",
                'working': "Fetching current weather data...",
                'completion': "Here's the weather information you requested.",
                'follow_up': "Do you need the forecast for a different location or time?"
            },
            'news': {
                'acknowledgment': "I'll gather the latest news for you.",
                'working': "Searching for current news updates...",
                'completion': "Here are the top news stories.",
                'follow_up': "Would you like news on a specific topic or from a particular source?"
            },
            'search': {
                'acknowledgment': "I'll search for that information.",
                'working': "Looking through available sources...",
                'completion': "Based on my search, here's what I found.",
                'follow_up': "Would you like me to go deeper into any specific aspect?"
            },
            'coding': {
                'acknowledgment': "I'll help you with the code.",
                'working': "Analyzing the requirements and generating code...",
                'completion': "Here's the code solution.",
                'follow_up': "Do you need explanations, optimizations, or help with implementation?"
            },
            'time_date': {
                'acknowledgment': "Let me get the current time for you.",
                'working': "Retrieving time information...",
                'completion': "Here's the current time and date.",
                'follow_up': "Would you like the time in a different timezone?"
            },
            'memory': {
                'acknowledgment': "I'll save that information for you.",
                'working': "Storing in memory...",
                'completion': "I've remembered that for future reference.",
                'follow_up': "Is there anything else you'd like me to remember?"
            },
            'pc_control': {
                'acknowledgment': "I'll execute that command for you.",
                'working': "Processing the system command...",
                'completion': "Command executed successfully.",
                'follow_up': "Do you need any other system operations?"
            },
            'greeting': {
                'acknowledgment': "Hello! I'm ready to assist you.",
                'working': "",
                'completion': "How can I help you today?",
                'follow_up': ""
            },
            'rag': {
                'acknowledgment': "I'll conduct a deep research on that topic.",
                'working': "Analyzing multiple sources and synthesizing information...",
                'completion': "Here's a comprehensive analysis based on my research.",
                'follow_up': "Would you like me to explore any specific angle in more detail?"
            },
            'general_chat': {
                'acknowledgment': "I understand your question.",
                'working': "Processing your request...",
                'completion': "Here's my response.",
                'follow_up': "Is there anything else you'd like to know?"
            }
        }
        
        # Proactive suggestions based on intent
        self.proactive_suggestions = {
            'calculation': [
                "Need help with a complex formula?",
                "Want to convert units?",
                "Need statistical analysis?"
            ],
            'weather': [
                "Check the forecast for the week?",
                "Get weather alerts?",
                "Compare weather between cities?"
            ],
            'news': [
                "Filter by category (tech, sports, politics)?",
                "Get news from specific sources?",
                "Set up news alerts?"
            ],
            'search': [
                "Need more detailed information?",
                "Want to compare sources?",
                "Looking for recent updates?"
            ],
            'coding': [
                "Need code review?",
                "Want debugging help?",
                "Need documentation?"
            ],
            'time_date': [
                "Set a reminder?",
                "Convert between timezones?",
                "Calculate time differences?"
            ],
            'pc_control': [
                "Automate this task?",
                "Create a shortcut?",
                "Schedule this action?"
            ],
            'rag': [
                "Need academic sources?",
                "Want statistical data?",
                "Need expert opinions?"
            ]
        }
        
        # Clarifying question patterns for ambiguous queries
        self.clarification_patterns = {
            'weather': [
                "Which city would you like the weather for?",
                "Do you need current conditions or a forecast?",
                "What date range are you interested in?"
            ],
            'news': [
                "What topic are you interested in?",
                "Do you prefer recent news or a specific time period?",
                "Any particular news sources?"
            ],
            'search': [
                "Could you be more specific about what you're looking for?",
                "Are you looking for recent information or general knowledge?",
                "Any specific sources or types of content?"
            ],
            'pc_control': [
                "Which application would you like to open?",
                "Do you want to open, close, or perform another action?",
                "Any specific parameters or settings?"
            ],
            'coding': [
                "What programming language do you prefer?",
                "What should the code accomplish?",
                "Any specific requirements or constraints?"
            ]
        }
        
        # Conversation state tracking
        self.conversation_state = {
            'last_intent': None,
            'follow_up_count': 0,
            'clarification_needed': False,
            'context_stack': []
        }
        
        logger.info("🤖 Smart Agent Response Module initialized")
    
    def generate_smart_response(self, 
                                query: str, 
                                intent: str, 
                                entities: Dict[str, str],
                                raw_response: str,
                                conversation_history: List[Dict] = None,
                                user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a smart, agent-like response
        
        Args:
            query: User's original query
            intent: Detected intent
            entities: Extracted entities
            raw_response: The raw response from tools/models
            conversation_history: Previous conversation turns
            user_preferences: User's preferences and settings
            
        Returns:
            Dictionary with enhanced response including:
            - response: The main response
            - acknowledgment: Smart acknowledgment
            - proactive_suggestions: Relevant suggestions
            - clarifying_question: If clarification needed
            - context_aware: Whether context was used
        """
        if conversation_history is None:
            conversation_history = []
        if user_preferences is None:
            user_preferences = {}
        
        # Build response context
        context = self._build_context(query, intent, entities, conversation_history, user_preferences)
        
        # Generate enhanced response
        result = {
            'response': raw_response,
            'acknowledgment': self._generate_acknowledgment(intent, context),
            'proactive_suggestions': self._generate_proactive_suggestions(intent, context),
            'clarifying_question': self._check_clarification_needed(intent, entities, context),
            'context_aware': self._is_context_aware(context),
            'conversation_flow': self._maintain_conversation_flow(intent, context),
            'multi_step_hint': self._suggest_multi_step(intent, entities, context)
        }
        
        # Update conversation state
        self._update_conversation_state(intent, context)
        
        return result
    
    def _build_context(self, 
                      query: str, 
                      intent: str, 
                      entities: Dict[str, str],
                      conversation_history: List[Dict],
                      user_preferences: Dict[str, Any]) -> ResponseContext:
        """Build response context from available information"""
        now = datetime.now()
        hour = now.hour
        
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        previous_queries = [turn.get('query', '') for turn in conversation_history[-5:]]
        
        return ResponseContext(
            query=query,
            intent=intent,
            entities=entities,
            conversation_history=conversation_history,
            user_preferences=user_preferences,
            time_of_day=time_of_day,
            previous_queries=previous_queries
        )
    
    def _generate_acknowledgment(self, intent: str, context: ResponseContext) -> str:
        """Generate intelligent acknowledgment based on intent and context"""
        templates = self.response_templates.get(intent, self.response_templates['general_chat'])
        
        acknowledgment = templates['acknowledgment']
        
        # Add time-based personalization
        time_prefixes = {
            'morning': "Good morning! ",
            'afternoon': "Good afternoon! ",
            'evening': "Good evening! ",
            'night': "Hello! "
        }
        
        # Add context from previous queries
        if context.previous_queries:
            last_query = context.previous_queries[-1].lower()
            if 'weather' in last_query and intent == 'news':
                acknowledgment = "I see you're interested in current events. " + acknowledgment
            elif 'calculation' in last_query and intent == 'coding':
                acknowledgment = "Moving from calculations to coding. " + acknowledgment
        
        # Personalize based on user preferences
        if context.user_preferences.get('formal_mode'):
            acknowledgment = acknowledgment.replace("I'll", "I shall")
        
        return time_prefixes.get(context.time_of_day, "") + acknowledgment
    
    def _generate_proactive_suggestions(self, intent: str, context: ResponseContext) -> List[str]:
        """Generate proactive suggestions based on intent and context"""
        suggestions = self.proactive_suggestions.get(intent, [])
        
        # Filter suggestions based on context
        filtered_suggestions = []
        
        for suggestion in suggestions:
            # Avoid repeating suggestions from recent queries
            if not any(suggestion.lower() in q.lower() for q in context.previous_queries):
                filtered_suggestions.append(suggestion)
        
        # Add context-aware suggestions
        if context.intent == 'weather' and 'city' not in context.entities:
            filtered_suggestions.insert(0, "Specify a city for accurate weather?")
        
        if context.intent == 'search' and len(context.query.split()) < 3:
            filtered_suggestions.insert(0, "Try being more specific for better results?")
        
        return filtered_suggestions[:3]  # Return top 3 suggestions
    
    def _check_clarification_needed(self, intent: str, entities: Dict[str, str], context: ResponseContext) -> Optional[str]:
        """Check if clarification is needed and generate appropriate question"""
        # Check if essential entities are missing
        if intent in self.clarification_patterns:
            patterns = self.clarification_patterns[intent]
            
            # Weather needs city
            if intent == 'weather' and 'city' not in entities:
                return patterns[0]
            
            # News needs topic
            if intent == 'news' and 'topic' not in entities:
                return patterns[0]
            
            # Search needs specificity
            if intent == 'search' and len(context.query.split()) < 3:
                return patterns[0]
            
            # PC control needs action and app
            if intent == 'pc_control':
                if 'action' not in entities:
                    return patterns[1]
                if 'app' not in entities and entities.get('action') in ['open', 'close']:
                    return patterns[0]
            
            # Coding needs language or purpose
            if intent == 'coding' and 'language' not in entities:
                return patterns[0]
        
        return None
    
    def _is_context_aware(self, context: ResponseContext) -> bool:
        """Check if response is using context from conversation"""
        return len(context.previous_queries) > 0 or len(context.entities) > 0
    
    def _maintain_conversation_flow(self, intent: str, context: ResponseContext) -> str:
        """Generate conversation flow continuation"""
        if self.conversation_state['last_intent'] == intent:
            self.conversation_state['follow_up_count'] += 1
            if self.conversation_state['follow_up_count'] > 2:
                return "Would you like to move on to a different topic?"
        else:
            self.conversation_state['follow_up_count'] = 0
        
        templates = self.response_templates.get(intent, self.response_templates['general_chat'])
        return templates['follow_up']
    
    def _suggest_multi_step(self, intent: str, entities: Dict[str, str], context: ResponseContext) -> Optional[str]:
        """Suggest multi-step operations if applicable"""
        multi_step_scenarios = {
            'weather': "I can also set up weather alerts or create a daily forecast routine.",
            'news': "I can create a personalized news digest or set up topic alerts.",
            'pc_control': "I can automate this task or create a workflow for repeated actions.",
            'coding': "I can help with testing, documentation, or deployment as well.",
            'search': "I can save this information or set up monitoring for updates."
        }
        
        # Only suggest if entities are well-defined
        if intent in multi_step_scenarios and len(entities) >= 2:
            return multi_step_scenarios[intent]
        
        return None
    
    def _update_conversation_state(self, intent: str, context: ResponseContext):
        """Update conversation state tracking"""
        self.conversation_state['last_intent'] = intent
        
        # Manage context stack
        if len(self.conversation_state['context_stack']) > 5:
            self.conversation_state['context_stack'].pop(0)
        self.conversation_state['context_stack'].append({
            'intent': intent,
            'query': context.query,
            'timestamp': datetime.now()
        })
    
    def format_final_response(self, smart_response: Dict[str, Any], raw_response: str) -> str:
        """
        Format the final response combining all smart agent features
        
        Args:
            smart_response: The smart response dictionary
            raw_response: The actual content response
            
        Returns:
            Formatted final response string
        """
        parts = []
        
        # Add acknowledgment if available
        if smart_response.get('acknowledgment'):
            parts.append(smart_response['acknowledgment'])
        
        # Add the main response
        parts.append(raw_response)
        
        # Add clarifying question if needed
        if smart_response.get('clarifying_question'):
            parts.append(f"\n\n❓ {smart_response['clarifying_question']}")
        
        # Add proactive suggestions if available
        if smart_response.get('proactive_suggestions'):
            suggestions = smart_response['proactive_suggestions']
            if suggestions:
                parts.append("\n\n💡 Suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    parts.append(f"   {i}. {suggestion}")
        
        # Add multi-step hint if available
        if smart_response.get('multi_step_hint'):
            parts.append(f"\n\n🔄 {smart_response['multi_step_hint']}")
        
        # Add conversation flow
        if smart_response.get('conversation_flow'):
            parts.append(f"\n\n{smart_response['conversation_flow']}")
        
        return "\n".join(parts)
    
    def get_response_summary(self, smart_response: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of the smart response features used"""
        return {
            'used_acknowledgment': bool(smart_response.get('acknowledgment')),
            'suggestions_count': len(smart_response.get('proactive_suggestions', [])),
            'clarification_needed': bool(smart_response.get('clarifying_question')),
            'context_aware': smart_response.get('context_aware', False),
            'multi_step_suggested': bool(smart_response.get('multi_step_hint'))
        }


# Global instance
smart_agent = SmartAgentResponse()
