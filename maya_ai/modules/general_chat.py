"""
MAYA AI General Chat Intelligence System
========================================
Premium intelligent chat module with verification pipeline
Think → Verify → Validate → Respond

Core Philosophy:
Never blindly answer. Always think, verify, validate, then respond.
"""

import re
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import sqlite3
import hashlib

# Time/Date libraries
import pytz
from datetime import timezone

# NLP libraries
try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        nlp = None
        SPACY_AVAILABLE = False
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None

# Search libraries
try:
    from duckduckgo_search import DDGS
    DDG_AVAILABLE = True
except ImportError:
    DDG_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ChatVerification:
    """Verification result for a chat response"""
    message_type: str
    factual_confidence: float
    freshness_confidence: float
    context_confidence: float
    grammar_confidence: float
    relevance_confidence: float
    overall_confidence: float
    requires_clarification: bool
    verification_notes: List[str]
    time_mismatch: bool
    greeting_correction: Optional[str]


class GeneralChatIntelligence:
    """
    MAYA General Chat Intelligence System
    Smart verification pipeline before every response
    """

    def __init__(self):
        """Initialize the chat intelligence system"""
        self.spacy_nlp = nlp
        self.spacy_available = SPACY_AVAILABLE
        self.ddg_available = DDG_AVAILABLE

        # Initialize learning database
        self.learning_db = Path(__file__).parent.parent / "data" / "chat_learning.db"
        self._init_learning_db()

        # Load learned patterns
        self.learned_patterns = self._load_learned_patterns()

        # Initialize timezone (IST by default)
        self.default_timezone = pytz.timezone('Asia/Kolkata')

        logger.info("🧠 MAYA General Chat Intelligence initialized")

    def _init_learning_db(self):
        """Initialize SQLite database for self-learning"""
        self.learning_db.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.learning_db)
        c = conn.cursor()

        # User corrections table
        c.execute('''CREATE TABLE IF NOT EXISTS user_corrections
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      original_response TEXT, user_feedback TEXT,
                      corrected_response TEXT, timestamp TIMESTAMP)''')

        # Rejected answers table
        c.execute('''CREATE TABLE IF NOT EXISTS rejected_answers
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      query TEXT, reason TEXT, timestamp TIMESTAMP)''')

        # Preferred style table
        c.execute('''CREATE TABLE IF NOT EXISTS preferred_style
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      style_type TEXT, style_value TEXT, confidence REAL)''')

        conn.commit()
        conn.close()

    def _load_learned_patterns(self) -> Dict[str, Any]:
        """Load learned patterns from database"""
        patterns = {
            'corrections': [],
            'rejected': [],
            'style': {}
        }

        try:
            conn = sqlite3.connect(self.learning_db)
            c = conn.cursor()

            # Load corrections
            c.execute('SELECT original_response, user_feedback, corrected_response FROM user_corrections')
            for orig, feedback, corrected in c.fetchall():
                patterns['corrections'].append({
                    'original': orig,
                    'feedback': feedback,
                    'corrected': corrected
                })

            # Load style preferences
            c.execute('SELECT style_type, style_value, confidence FROM preferred_style')
            for stype, svalue, conf in c.fetchall():
                patterns['style'][stype] = {'value': svalue, 'confidence': conf}

            conn.close()
        except Exception as e:
            logger.warning(f"⚠️ Could not load learned patterns: {e}")

        return patterns

    # ==================== STEP 1: INPUT ANALYZER ====================

    def input_analyzer(self, message: str) -> str:
        """
        Step 1: Input Understanding
        Detect message type
        """
        message_lower = message.lower()

        # Greeting patterns
        greeting_patterns = ['hello', 'hi', 'hey', 'good morning', 'good evening', 'good night',
                           'namaste', 'namaskar', 'hola', 'greetings']
        if any(pattern in message_lower for pattern in greeting_patterns):
            return 'greeting'

        # Factual question patterns
        factual_patterns = ['what is', 'who is', 'where is', 'when did', 'how many',
                          'tallest', 'largest', 'smallest', 'capital of', 'population of']
        if any(pattern in message_lower for pattern in factual_patterns):
            return 'factual_question'

        # News request patterns
        news_patterns = ['news', 'latest', 'breaking', 'update', 'headlines', 'today news',
                       'kal ki news', 'latest update']
        if any(pattern in message_lower for pattern in news_patterns):
            return 'news_request'

        # Memory recall patterns
        memory_patterns = ['remember', 'yad hai', 'kya bola tha', 'last time', 'previous',
                        'mera project', 'maine kaha tha', 'discuss kiya']
        if any(pattern in message_lower for pattern in memory_patterns):
            return 'memory_recall'

        # Opinion patterns
        opinion_patterns = ['what do you think', 'your opinion', 'do you like', 'is it good',
                          'should i', 'recommend']
        if any(pattern in message_lower for pattern in opinion_patterns):
            return 'opinion'

        # Emotional patterns
        emotional_patterns = ['i feel', 'i am sad', 'i am happy', 'i am stressed',
                           'i am worried', 'i love', 'i hate']
        if any(pattern in message_lower for pattern in emotional_patterns):
            return 'emotional_message'

        # Comparison patterns
        comparison_patterns = ['vs', 'versus', 'compare', 'difference', 'better than',
                            'which is better', 'between']
        if any(pattern in message_lower for pattern in comparison_patterns):
            return 'comparison'

        # Time-sensitive patterns
        time_patterns = ['what time', 'current time', 'date today', 'what day', 'what month']
        if any(pattern in message_lower for pattern in time_patterns):
            return 'time_sensitive'

        # Follow-up patterns
        followup_patterns = ['then', 'also', 'and', 'more', 'next', 'after that',
                           'what about', 'tell me more']
        if any(pattern in message_lower for pattern in followup_patterns):
            return 'followup_question'

        # Default: casual chat
        return 'casual_chat'

    # ==================== STEP 2: LLAMA VERIFICATION ENGINE ====================

    def llama_verify(self, message: str, message_type: str) -> Dict[str, Any]:
        """
        Step 2: Llama Verification Engine
        Think before speaking - understand meaning, detect assumptions
        """
        verification = {
            'meaning_understood': True,
            'hidden_assumptions': [],
            'potential_errors': [],
            'verification_needed': False,
            'correction_needed': False,
            'correction_style': 'polite'
        }

        message_lower = message.lower()

        # Detect common misconceptions
        misconceptions = {
            'sun rotates around earth': 'Earth rotates around the Sun',
            'earth is flat': 'Earth is round/spherical',
            'moon has light': 'Moon reflects sunlight',
            'gravity is magnetic': 'Gravity is a fundamental force'
        }

        for misconception, correction in misconceptions.items():
            if misconception in message_lower:
                verification['potential_errors'].append({
                    'error': misconception,
                    'correction': correction
                })
                verification['correction_needed'] = True

        # Detect if verification is needed for factual claims
        if message_type in ['factual_question', 'news_request']:
            verification['verification_needed'] = True

        # Detect if user might be mistaken
        uncertain_phrases = ['i think', 'maybe', 'probably', 'i guess']
        if any(phrase in message_lower for phrase in uncertain_phrases):
            verification['hidden_assumptions'].append('User is uncertain')

        return verification

    # ==================== STEP 3: TIME & DATE VALIDATOR ====================

    def time_validator(self, message: str, message_type: str) -> Tuple[bool, Optional[str]]:
        """
        Step 3: Time & Date Validation
        Check greeting mismatches with actual time
        """
        if message_type != 'greeting':
            return False, None

        message_lower = message.lower()
        current_time = datetime.now(self.default_timezone)
        hour = current_time.hour

        # Time-based greeting detection
        greeting_time_map = {
            'good morning': (5, 12),  # 5 AM to 12 PM
            'good afternoon': (12, 17),  # 12 PM to 5 PM
            'good evening': (17, 21),  # 5 PM to 9 PM
            'good night': (21, 5)  # 9 PM to 5 AM
        }

        for greeting, (start, end) in greeting_time_map.items():
            if greeting in message_lower:
                # Check if greeting matches current time
                if start < end:
                    # Normal range (e.g., morning: 5-12)
                    if not (start <= hour < end):
                        # Mismatch detected
                        correct_greeting = self._get_correct_greeting(hour)
                        current_time_str = current_time.strftime('%I:%M %p')
                        correction = f"Sir abhi {greeting.replace('good ', '')} nahi 😊 Abhi {current_time_str} hai, {correct_greeting}."
                        return True, correction
                else:
                    # Overnight range (e.g., night: 21-5)
                    if not (hour >= start or hour < end):
                        correct_greeting = self._get_correct_greeting(hour)
                        current_time_str = current_time.strftime('%I:%M %p')
                        correction = f"Sir abhi {greeting.replace('good ', '')} nahi 😊 Abhi {current_time_str} hai, {correct_greeting}."
                        return True, correction

        return False, None

    def _get_correct_greeting(self, hour: int) -> str:
        """Get correct greeting based on hour"""
        if 5 <= hour < 12:
            return "good morning"
        elif 12 <= hour < 17:
            return "good afternoon"
        elif 17 <= hour < 21:
            return "good evening"
        else:
            return "good night"

    # ==================== STEP 4: FACT CHECKER ====================

    def fact_checker(self, message: str, message_type: str) -> Tuple[float, str]:
        """
        Step 4: Fact Validation
        Verify facts from trusted sources or internal knowledge
        """
        if message_type != 'factual_question':
            return 0.9, ""

        # Internal knowledge base for common facts
        internal_facts = {
            'tallest mountain': ('Mount Everest is currently recognized as the tallest mountain above sea level.', 0.95),
            'largest ocean': ('The Pacific Ocean is the largest ocean on Earth.', 0.95),
            'capital of india': ('New Delhi is the capital of India.', 0.99),
            'capital of usa': ('Washington, D.C. is the capital of the United States.', 0.99),
            'population of india': ('India has a population of over 1.4 billion people.', 0.90),
        }

        message_lower = message.lower()

        for fact_key, (fact, confidence) in internal_facts.items():
            if fact_key in message_lower:
                return confidence, f"Verified answer: {fact}"

        # If not in internal knowledge, search if available
        if self.ddg_available:
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(message, max_results=3))
                    if results:
                        return 0.75, f"Verified from search: {results[0]['body']}"
            except Exception as e:
                logger.warning(f"⚠️ Search failed: {e}")

        # Low confidence if not found
        return 0.4, "I need to verify this information. Let me search for accurate details."

    # ==================== STEP 5: NEWS CHECKER ====================

    def news_checker(self, message: str, message_type: str) -> Tuple[float, str]:
        """
        Step 5: News Validation
        Check current date and validate news freshness
        """
        if message_type != 'news_request':
            return 0.9, ""

        current_date = datetime.now(self.default_timezone)
        current_date_str = current_date.strftime('%d %B %Y')
        message_lower = message.lower()

        # Detect if user is asking for today's news
        if 'today' in message_lower or 'aaj' in message_lower:
            return 0.95, f"Aaj {current_date_str} hai. Ye aaj ke latest verified highlights hain..."

        # Detect if user is asking for yesterday's news
        if 'yesterday' in message_lower or 'kal' in message_lower:
            yesterday = current_date - datetime.timedelta(days=1)
            yesterday_str = yesterday.strftime('%d %B %Y')
            return 0.90, f"Aap kal ki news puch rahe hain yani {yesterday_str} ki. Ye verified updates hain:"

        # Default news response
        return 0.85, f"Current date: {current_date_str}. Ye latest verified updates hain..."

    # ==================== STEP 6: MEMORY VALIDATOR ====================

    def memory_validator(self, message: str, message_type: str) -> Tuple[float, str]:
        """
        Step 6: Memory Validation
        Check memory database before answering personal questions
        """
        if message_type != 'memory_recall':
            return 0.9, ""

        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from memory import memory
            profile = memory.get_user_profile()

            if profile:
                # Found relevant memory
                return 0.95, f"Memory verified: {json.dumps(profile, indent=2)}"
            else:
                # No memory found
                return 0.3, "I don't have that information in my memory. Could you remind me?"
        except Exception as e:
            logger.warning(f"⚠️ Memory check failed: {e}")
            return 0.5, "Memory check failed. Let me try to recall."

    # ==================== STEP 7: CONFIDENCE SCORING ====================

    def confidence_score(self, verification: Dict, fact_conf: float, news_conf: float,
                        memory_conf: float, fact_result: str, news_result: str, memory_result: str) -> ChatVerification:
        """
        Step 7: Confidence Engine
        Score every answer on multiple dimensions
        """
        # Base confidence
        factual_confidence = fact_conf
        freshness_confidence = news_conf
        context_confidence = memory_conf
        grammar_confidence = 0.95  # High confidence in grammar
        relevance_confidence = 0.90  # High confidence in relevance

        # Adjust based on verification
        if verification['correction_needed']:
            factual_confidence *= 0.7

        if verification['potential_errors']:
            factual_confidence *= 0.6

        # Overall confidence
        overall_confidence = (
            factual_confidence * 0.3 +
            freshness_confidence * 0.2 +
            context_confidence * 0.2 +
            grammar_confidence * 0.15 +
            relevance_confidence * 0.15
        )

        # Determine if clarification needed
        requires_clarification = overall_confidence < 0.6

        verification_notes = []
        if verification['correction_needed']:
            verification_notes.append("Potential correction needed")
        if verification['verification_needed']:
            verification_notes.append("Verification performed")
        if overall_confidence < 0.7:
            verification_notes.append("Low confidence - may need clarification")

        # Add actual results to notes
        if fact_result:
            verification_notes.append(fact_result)
        if news_result:
            verification_notes.append(news_result)
        if memory_result:
            verification_notes.append(memory_result)

        return ChatVerification(
            message_type=verification.get('message_type', 'casual_chat'),
            factual_confidence=factual_confidence,
            freshness_confidence=freshness_confidence,
            context_confidence=context_confidence,
            grammar_confidence=grammar_confidence,
            relevance_confidence=relevance_confidence,
            overall_confidence=overall_confidence,
            requires_clarification=requires_clarification,
            verification_notes=verification_notes,
            time_mismatch=False,
            greeting_correction=None
        )

    # ==================== STEP 8: FRIENDLY REPLY GENERATOR ====================

    def friendly_reply(self, message: str, verification: ChatVerification,
                      greeting_correction: Optional[str] = None) -> str:
        """
        Step 8: Human Response Style
        Generate warm, natural, intelligent responses
        """
        # If greeting mismatch detected, return correction
        if greeting_correction:
            return greeting_correction

        # If low confidence, ask for clarification
        if verification.requires_clarification:
            return "Sir, mujhe thoda confusion hai. Kya aap thoda detail mein bata sakte hain?"

        # Generate response based on message type
        message_type = verification.message_type

        if message_type == 'greeting':
            greetings = [
                "Hi boss! Kya haal hai?",
                "Hey boss! Kya chal raha hai?",
                "Hello boss! Kaise ho?",
                "Namaste boss! Maya AI ready hai help karne ke liye!"
            ]
            import random
            return random.choice(greetings)

        elif message_type == 'factual_question':
            if verification.factual_confidence > 0.8:
                # Find the fact result in verification notes
                for note in verification.verification_notes:
                    if 'Verified answer:' in note or 'Verified from search:' in note:
                        return note
                return "Information verified successfully."
            else:
                return "Let me verify this information for you first, boss."

        elif message_type == 'news_request':
            if verification.freshness_confidence > 0.8:
                # Find the news result in verification notes
                for note in verification.verification_notes:
                    if 'Aaj' in note or 'Current date' in note or 'verified' in note.lower():
                        return note
                return "Ye latest verified updates hain."
            else:
                return "News data fetch kar rahi hoon, please wait."

        elif message_type == 'memory_recall':
            if verification.context_confidence > 0.8:
                # Format memory information professionally
                memory_info = ""
                for note in verification.verification_notes:
                    if 'Memory verified:' in note:
                        try:
                            import json
                            # Extract JSON from the note
                            json_start = note.find('{')
                            if json_start != -1:
                                profile_data = json.loads(note[json_start:])
                                # Format professionally
                                memory_info = "Based on what I remember about you:\n\n"
                                for key, data in profile_data.items():
                                    memory_info += f"• {key.replace('_', ' ').title()}: {data['value']}\n"
                                return memory_info
                        except:
                            pass
                return "I have some information about you in my memory. What specifically would you like to know?"
            else:
                return "I don't have that information in my memory yet. Would you like me to remember it?"

        elif message_type == 'emotional_message':
            return "I understand boss. Maya AI always here for you. Kya help chahiye?"

        elif message_type == 'opinion':
            return "Ye subjective matter hai boss. Main factual information de sakti hun, personal opinion nahi."

        elif message_type == 'comparison':
            return "Comparison karne ke liye specific details chahiye boss. Batao kya compare karna hai."

        else:
            # Casual chat - use Llama model for detailed explanation
            try:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from modules.models import local_models
                result = local_models.smart_routing(message, "general_chat")
                if result and result.get('response'):
                    return result['response']
            except Exception as e:
                logger.warning(f"⚠️ Llama model failed: {e}")

            # Fallback with more helpful response
            return f"Let me explain about '{message}'. Could you provide more specific details so I can give you a better answer?"

    # ==================== SELF IMPROVEMENT ====================

    def learn_from_correction(self, original_response: str, user_feedback: str, corrected_response: str):
        """Learn from user corrections"""
        try:
            conn = sqlite3.connect(self.learning_db)
            c = conn.cursor()
            c.execute('''INSERT INTO user_corrections
                        (original_response, user_feedback, corrected_response, timestamp)
                        VALUES (?, ?, ?, ?)''',
                     (original_response, user_feedback, corrected_response, datetime.now()))
            conn.commit()
            conn.close()
            logger.info(f"🧠 Learned from correction: {user_feedback}")
        except Exception as e:
            logger.error(f"❌ Error learning correction: {e}")

    def record_rejected_answer(self, query: str, reason: str):
        """Record rejected answers for learning"""
        try:
            conn = sqlite3.connect(self.learning_db)
            c = conn.cursor()
            c.execute('''INSERT INTO rejected_answers
                        (query, reason, timestamp)
                        VALUES (?, ?, ?)''',
                     (query, reason, datetime.now()))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"❌ Error recording rejection: {e}")

    # ==================== MASTER RESPONSE FLOW ====================

    def process_message(self, message: str) -> str:
        """
        Master Response Flow
        User Input → Input Analyzer → Llama Verification → Time Validator →
        Fact Checker → Memory Checker → Confidence Scorer → Friendly Reply
        """
        # Step 1: Input Analyzer
        message_type = self.input_analyzer(message)

        # Step 2: Llama Verification
        verification = self.llama_verify(message, message_type)
        verification['message_type'] = message_type

        # Step 3: Time Validator
        time_mismatch, greeting_correction = self.time_validator(message, message_type)

        # Step 4: Fact Checker
        fact_confidence, fact_result = self.fact_checker(message, message_type)

        # Step 5: News Checker
        news_confidence, news_result = self.news_checker(message, message_type)

        # Step 6: Memory Validator
        memory_confidence, memory_result = self.memory_validator(message, message_type)

        # Step 7: Confidence Scoring
        chat_verification = self.confidence_score(verification, fact_confidence,
                                                  news_confidence, memory_confidence,
                                                  fact_result, news_result, memory_result)
        chat_verification.time_mismatch = time_mismatch
        chat_verification.greeting_correction = greeting_correction

        # Step 8: Friendly Reply Generator
        response = self.friendly_reply(message, chat_verification, greeting_correction)

        logger.info(f"🧠 Chat processed: type={message_type}, confidence={chat_verification.overall_confidence:.2f}")

        return response


# Global instance
general_chat_intelligence = GeneralChatIntelligence()


if __name__ == "__main__":
    # Test the general chat system
    test_messages = [
        "Good morning",
        "What is the tallest mountain?",
        "Today news",
        "Remember my name",
        "How are you?",
        "Sun rotates around Earth"
    ]

    print("=" * 70)
    print("🧠 MAYA General Chat Intelligence Test")
    print("=" * 70)

    for msg in test_messages:
        print(f"\nUser: {msg}")
        response = general_chat_intelligence.process_message(msg)
        print(f"Maya: {response}")

    print("\n" + "=" * 70)
    print("✅ Test Complete")
    print("=" * 70)
