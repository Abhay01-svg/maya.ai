"""
Maya AI Memory System
Stores user preferences, chat history, habits, and learning data
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from config import MEMORY_DB, HABITS_DB, DEBUG_MODE
import logging
import re

logger = logging.getLogger(__name__)

class MayaMemory:
    """Main memory system for Maya AI"""
    
    def __init__(self):
        self.memory_db = MEMORY_DB
        self.habits_db = HABITS_DB
        self._init_databases()
    
    def _init_databases(self):
        """Initialize SQLite databases"""
        # User Memory Database
        conn = sqlite3.connect(self.memory_db)
        c = conn.cursor()

        # User preferences table
        c.execute('''CREATE TABLE IF NOT EXISTS user_preferences
                     (key TEXT PRIMARY KEY, value TEXT, updated_at TIMESTAMP)''')

        # Chat history table
        c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      query TEXT, response TEXT, timestamp TIMESTAMP,
                      intent TEXT, tokens_used INTEGER)''')

        # Custom commands table
        c.execute('''CREATE TABLE IF NOT EXISTS custom_commands
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      command_name TEXT, command_action TEXT, created_at TIMESTAMP)''')

        # User facts/learnings table (NLP-based learning)
        c.execute('''CREATE TABLE IF NOT EXISTS user_facts
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      fact_type TEXT, fact_value TEXT, confidence REAL,
                      source_message TEXT, learned_at TIMESTAMP, last_used TIMESTAMP)''')

        # Maya identity table (system facts about Maya)
        c.execute('''CREATE TABLE IF NOT EXISTS maya_identity
                     (key TEXT PRIMARY KEY, value TEXT, updated_at TIMESTAMP)''')

        conn.commit()
        conn.close()

        # Initialize Maya's identity
        self._init_maya_identity()

        # Habits Database
        conn = sqlite3.connect(self.habits_db)
        c = conn.cursor()

        # User habits table
        c.execute('''CREATE TABLE IF NOT EXISTS habits
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      app_name TEXT, open_time TIME, frequency INTEGER,
                      last_opened TIMESTAMP)''')

        # Routine table
        c.execute('''CREATE TABLE IF NOT EXISTS routines
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      routine_name TEXT, trigger_time TIME, action TEXT,
                      enabled INTEGER)''')

        conn.commit()
        conn.close()

        if DEBUG_MODE:
            logger.info("✅ Memory databases initialized")

    def _init_maya_identity(self):
        """Initialize Maya's identity in the database"""
        maya_facts = {
            'name': 'Maya',
            'full_name': 'Maya AI',
            'type': 'AI Assistant',
            'purpose': 'To help you with tasks, calculations, coding, research, and more',
            'creator': 'Your AI Assistant',
            'capabilities': 'General chat, coding, research (RAG), calculations, weather, news, time/date, memory, PC control, vision, document processing',
            'models_used': 'Llama, Qwen Coder for specialized tasks',
            'personality': 'Helpful, intelligent, and friendly'
        }

        conn = sqlite3.connect(self.memory_db)
        c = conn.cursor()

        for key, value in maya_facts.items():
            c.execute('''INSERT OR REPLACE INTO maya_identity
                        (key, value, updated_at) VALUES (?, ?, ?)''',
                     (key, value, datetime.now()))

        conn.commit()
        conn.close()

        if DEBUG_MODE:
            logger.info("✅ Maya identity initialized")
    
    # ==================== PREFERENCES ====================
    
    def set_preference(self, key: str, value: str) -> bool:
        """Store user preference"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()
            c.execute('''INSERT OR REPLACE INTO user_preferences 
                        (key, value, updated_at) VALUES (?, ?, ?)''',
                     (key, value, datetime.now()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ Error setting preference: {e}")
            return False
    
    def get_preference(self, key: str, default=None):
        """Retrieve user preference"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()
            c.execute('SELECT value FROM user_preferences WHERE key = ?', (key,))
            result = c.fetchone()
            conn.close()
            return result[0] if result else default
        except Exception as e:
            logger.error(f"❌ Error getting preference: {e}")
            return default
    
    def get_all_preferences(self) -> dict:
        """Get all preferences"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()
            c.execute('SELECT key, value FROM user_preferences')
            prefs = dict(c.fetchall())
            conn.close()
            return prefs
        except Exception as e:
            logger.error(f"❌ Error getting preferences: {e}")
            return {}
    
    # ==================== CHAT HISTORY ====================
    
    def save_chat(self, query: str, response: str, intent: str = "", tokens: int = 0) -> bool:
        """Save chat interaction"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()
            c.execute('''INSERT INTO chat_history 
                        (query, response, intent, tokens_used, timestamp)
                        VALUES (?, ?, ?, ?, ?)''',
                     (query, response, intent, tokens, datetime.now()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ Error saving chat: {e}")
            return False
    
    def get_chat_history(self, limit: int = 50) -> list:
        """Get recent chat history"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()
            c.execute('''SELECT query, response, intent, timestamp FROM chat_history 
                        ORDER BY timestamp DESC LIMIT ?''', (limit,))
            history = c.fetchall()
            conn.close()
            return history
        except Exception as e:
            logger.error(f"❌ Error getting chat history: {e}")
            return []
    
    def search_chat_history(self, keyword: str, limit: int = 20) -> list:
        """Search chat history by keyword"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()
            c.execute('''SELECT query, response, intent FROM chat_history 
                        WHERE query LIKE ? ORDER BY timestamp DESC LIMIT ?''',
                     (f"%{keyword}%", limit))
            results = c.fetchall()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"❌ Error searching chat history: {e}")
            return []
    
    # ==================== CUSTOM COMMANDS ====================
    
    def add_custom_command(self, name: str, action: str) -> bool:
        """Add custom command"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()
            c.execute('''INSERT INTO custom_commands (command_name, command_action, created_at)
                        VALUES (?, ?, ?)''',
                     (name, action, datetime.now()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ Error adding command: {e}")
            return False
    
    def get_custom_command(self, name: str) -> str:
        """Get custom command action"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()
            c.execute('SELECT command_action FROM custom_commands WHERE command_name = ?', (name,))
            result = c.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"❌ Error getting command: {e}")
            return None
    
    # ==================== HABITS ====================
    
    def log_app_usage(self, app_name: str) -> bool:
        """Log app usage for habit learning"""
        try:
            conn = sqlite3.connect(self.habits_db)
            c = conn.cursor()
            
            # Check if habit exists
            c.execute('SELECT frequency FROM habits WHERE app_name = ?', (app_name,))
            result = c.fetchone()
            
            if result:
                new_frequency = result[0] + 1
                c.execute('''UPDATE habits SET frequency = ?, last_opened = ? 
                           WHERE app_name = ?''',
                         (new_frequency, datetime.now(), app_name))
            else:
                c.execute('''INSERT INTO habits (app_name, frequency, last_opened)
                           VALUES (?, ?, ?)''',
                         (app_name, 1, datetime.now()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ Error logging app usage: {e}")
            return False
    
    def get_top_apps(self, limit: int = 5) -> list:
        """Get most frequently used apps"""
        try:
            conn = sqlite3.connect(self.habits_db)
            c = conn.cursor()
            c.execute('''SELECT app_name, frequency, last_opened FROM habits 
                        ORDER BY frequency DESC LIMIT ?''', (limit,))
            apps = c.fetchall()
            conn.close()
            return apps
        except Exception as e:
            logger.error(f"❌ Error getting top apps: {e}")
            return []
    
    def add_routine(self, routine_name: str, trigger_time: str, action: str) -> bool:
        """Add automation routine"""
        try:
            conn = sqlite3.connect(self.habits_db)
            c = conn.cursor()
            c.execute('''INSERT INTO routines (routine_name, trigger_time, action, enabled)
                        VALUES (?, ?, ?, ?)''',
                     (routine_name, trigger_time, action, 1))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ Error adding routine: {e}")
            return False
    
    def get_routines(self) -> list:
        """Get all active routines"""
        try:
            conn = sqlite3.connect(self.habits_db)
            c = conn.cursor()
            c.execute('SELECT routine_name, trigger_time, action FROM routines WHERE enabled = 1')
            routines = c.fetchall()
            conn.close()
            return routines
        except Exception as e:
            logger.error(f"❌ Error getting routines: {e}")
            return []
    
    # ==================== NLP-BASED LEARNING ====================

    def extract_and_learn_facts(self, message: str) -> int:
        """
        Extract facts from user message using NLP patterns
        Returns number of facts learned
        """
        facts_learned = 0
        message_lower = message.lower()

        # Pattern: "I am a [profession/role]"
        profession_match = re.search(r'i am (?:a|an) (.+?)(?:\.|$)', message_lower)
        if profession_match:
            self._store_fact('profession', profession_match.group(1).strip(), message, 0.9)
            facts_learned += 1

        # Pattern: "I like to [activity]"
        like_match = re.search(r'i like (?:to )?(.+?)(?:\.|$)', message_lower)
        if like_match:
            self._store_fact('preference', like_match.group(1).strip(), message, 0.85)
            facts_learned += 1

        # Pattern: "My name is [name]"
        name_match = re.search(r'(?:my name is|i am|i\'m) (.+?)(?:\.|$)', message_lower)
        if name_match:
            self._store_fact('name', name_match.group(1).strip(), message, 0.95)
            facts_learned += 1

        # Pattern: "I live in [location]"
        location_match = re.search(r'i live (?:in|at) (.+?)(?:\.|$)', message_lower)
        if location_match:
            self._store_fact('location', location_match.group(1).strip(), message, 0.85)
            facts_learned += 1

        # Pattern: "I am a student"
        if 'student' in message_lower:
            self._store_fact('occupation', 'student', message, 0.9)
            facts_learned += 1

        # Pattern: "I work at [company]"
        work_match = re.search(r'i work (?:at|for) (.+?)(?:\.|$)', message_lower)
        if work_match:
            self._store_fact('workplace', work_match.group(1).strip(), message, 0.85)
            facts_learned += 1

        if facts_learned > 0:
            logger.info(f"🧠 Learned {facts_learned} new facts from user input")

        return facts_learned

    def _store_fact(self, fact_type: str, fact_value: str, source_message: str, confidence: float):
        """Store a learned fact in the database"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()

            # Check if fact already exists
            c.execute('''SELECT id FROM user_facts
                        WHERE fact_type = ? AND fact_value = ?''',
                     (fact_type, fact_value))
            existing = c.fetchone()

            if existing:
                # Update confidence and last_used
                c.execute('''UPDATE user_facts
                           SET confidence = ?, last_used = ?
                           WHERE id = ?''',
                         (confidence, datetime.now(), existing[0]))
            else:
                # Insert new fact
                c.execute('''INSERT INTO user_facts
                           (fact_type, fact_value, confidence, source_message, learned_at, last_used)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                         (fact_type, fact_value, confidence, source_message, datetime.now(), datetime.now()))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"❌ Error storing fact: {e}")

    def get_relevant_facts(self, query: str, limit: int = 5) -> list:
        """Retrieve relevant facts based on query keywords"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()

            # Get all facts
            c.execute('''SELECT fact_type, fact_value, confidence FROM user_facts
                        ORDER BY confidence DESC, last_used DESC''')
            all_facts = c.fetchall()
            conn.close()

            # Simple keyword matching for relevance
            query_lower = query.lower()
            relevant_facts = []

            for fact_type, fact_value, confidence in all_facts:
                # Check if fact type or value relates to query
                if (fact_type in query_lower or
                    any(word in query_lower for word in fact_value.lower().split())):
                    relevant_facts.append({
                        'type': fact_type,
                        'value': fact_value,
                        'confidence': confidence
                    })

            return relevant_facts[:limit]
        except Exception as e:
            logger.error(f"❌ Error retrieving facts: {e}")
            return []

    def get_user_profile(self) -> dict:
        """Get complete user profile from learned facts"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()

            c.execute('''SELECT fact_type, fact_value, confidence FROM user_facts
                        ORDER BY confidence DESC''')
            facts = c.fetchall()
            conn.close()

            profile = {}
            for fact_type, fact_value, confidence in facts:
                if fact_type not in profile or confidence > profile[fact_type].get('confidence', 0):
                    profile[fact_type] = {
                        'value': fact_value,
                        'confidence': confidence
                    }

            return profile
        except Exception as e:
            logger.error(f"❌ Error getting user profile: {e}")
            return {}

    def get_maya_identity(self) -> dict:
        """Get Maya's identity information"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()

            c.execute('''SELECT key, value FROM maya_identity''')
            facts = c.fetchall()
            conn.close()

            identity = {}
            for key, value in facts:
                identity[key] = value

            return identity
        except Exception as e:
            logger.error(f"❌ Error getting Maya identity: {e}")
            return {}

    def is_identity_query(self, query: str) -> bool:
        """Check if query is asking about Maya's identity"""
        identity_keywords = [
            'who are you', 'what are you', 'what is your name',
            'what is your purpose', 'what can you do', 'your capabilities',
            'introduce yourself', 'tell me about yourself', 'what model are you',
            'are you llama', 'are you qwen', 'are you ai', 'are you a bot'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in identity_keywords)

    # ==================== EXPORT/IMPORT ====================

    def export_memory(self, filepath: str) -> bool:
        """Export all memory data to JSON"""
        try:
            data = {
                "preferences": self.get_all_preferences(),
                "chat_history": self.get_chat_history(limit=100),
                "routines": self.get_routines(),
                "top_apps": self.get_top_apps(),
                "export_time": datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"✅ Memory exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Error exporting memory: {e}")
            return False

# Singleton instance
memory = MayaMemory()

if DEBUG_MODE:
    print("🧠 Maya Memory System initialized")
