"""
Maya Experience Engine
Advanced learning and pattern recognition system
"""

import os
import json
import sqlite3
import pickle
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

from config import PROJECT_ROOT, DEBUG_MODE

logger = logging.getLogger(__name__)

class ExperiencePattern:
    """Represents a learned pattern"""
    def __init__(self, pattern_id: str, pattern_type: str, data: Dict,
                 context: str, success_rate: float = 0.0):
        self.pattern_id = pattern_id
        self.pattern_type = pattern_type
        self.data = data
        self.context = context
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        self.usage_count = 0
        self.success_rate = success_rate
        
    def to_dict(self) -> Dict:
        return {
            'pattern_id': self.pattern_id,
            'pattern_type': self.pattern_type,
            'data': self.data,
            'context': self.context,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat(),
            'usage_count': self.usage_count,
            'success_rate': self.success_rate
        }

class MayaExperienceEngine:
    """
    Experience Engine for Maya AI
    Handles: pattern learning, experience retention, knowledge reuse
    """
    
    def __init__(self):
        self.experience_db = os.path.join(PROJECT_ROOT, "data", "experience_engine.db")
        self.patterns_dir = os.path.join(PROJECT_ROOT, "data", "patterns")
        self.vector_store = {}  # Simple in-memory vector store
        
        self._init_database()
        os.makedirs(self.patterns_dir, exist_ok=True)
        
        logger.info("🎓 Maya Experience Engine initialized")
        
    def _init_database(self):
        """Initialize experience database"""
        try:
            os.makedirs(os.path.dirname(self.experience_db), exist_ok=True)
            conn = sqlite3.connect(self.experience_db)
            c = conn.cursor()
            
            # Detailed experiences
            c.execute('''CREATE TABLE IF NOT EXISTS detailed_experiences
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         experience_hash TEXT UNIQUE,
                         task_type TEXT, query TEXT,
                         solution TEXT, reasoning TEXT,
                         failure_reason TEXT, fix_applied TEXT,
                         patterns_extracted TEXT, context TEXT,
                         created_at TIMESTAMP, updated_at TIMESTAMP,
                         usage_count INTEGER DEFAULT 0,
                         success_count INTEGER DEFAULT 0,
                         failure_count INTEGER DEFAULT 0)''')
            
            # Code patterns
            c.execute('''CREATE TABLE IF NOT EXISTS code_patterns
                        (pattern_id TEXT PRIMARY KEY,
                         pattern_hash TEXT,
                         language TEXT,
                         pattern_type TEXT,
                         code_template TEXT,
                         variables TEXT,
                         use_cases TEXT,
                         success_rate REAL,
                         usage_count INTEGER,
                         created_at TIMESTAMP)''')
            
            # Architecture patterns
            c.execute('''CREATE TABLE IF NOT EXISTS architecture_patterns
                        (pattern_id TEXT PRIMARY KEY,
                         pattern_name TEXT,
                         description TEXT,
                         components TEXT,
                         relationships TEXT,
                         use_cases TEXT,
                         projects_used TEXT,
                         created_at TIMESTAMP)''')
            
            # Debugging knowledge
            c.execute('''CREATE TABLE IF NOT EXISTS debugging_knowledge
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         error_type TEXT,
                         error_message TEXT,
                         error_hash TEXT,
                         solution TEXT,
                         root_cause TEXT,
                         prevention TEXT,
                         times_encountered INTEGER DEFAULT 0,
                         times_solved INTEGER DEFAULT 0)''')
            
            # User preferences (learned)
            c.execute('''CREATE TABLE IF NOT EXISTS learned_preferences
                        (preference_type TEXT PRIMARY KEY,
                         preference_data TEXT,
                         confidence REAL,
                         sample_count INTEGER,
                         first_observed TIMESTAMP,
                         last_observed TIMESTAMP)''')
            
            conn.commit()
            conn.close()
            
            if DEBUG_MODE:
                logger.info("✅ Experience database initialized")
                
        except Exception as e:
            logger.error(f"❌ Experience DB init error: {e}")
    
    def learn_from_execution(self, task_type: str, query: str, 
                             solution: Any, reasoning: str,
                             success: bool, failure_reason: str = None,
                             fix_applied: str = None, context: Dict = None):
        """
        Learn from task execution
        Extracts patterns and stores knowledge
        """
        experience_hash = self._generate_hash(query + str(solution))
        
        # Extract patterns
        patterns = self._extract_patterns(solution, task_type)
        
        # Store experience
        self._store_experience(
            experience_hash=experience_hash,
            task_type=task_type,
            query=query,
            solution=solution,
            reasoning=reasoning,
            failure_reason=failure_reason,
            fix_applied=fix_applied,
            patterns=patterns,
            context=context or {},
            success=success
        )
        
        # Learn from failure if applicable
        if not success and failure_reason:
            self._learn_from_failure(failure_reason, fix_applied, task_type)
        
        # Update code patterns if coding task
        if task_type == 'coding' and isinstance(solution, str):
            self._learn_code_pattern(solution, context or {})
        
        logger.info(f"🎓 Learned from execution: {task_type} (success={success})")
    
    def _generate_hash(self, content: str) -> str:
        """Generate hash for content"""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _extract_patterns(self, solution: Any, task_type: str) -> List[Dict]:
        """Extract reusable patterns from solution"""
        patterns = []
        
        if task_type == 'coding' and isinstance(solution, str):
            # Extract function definitions
            import re
            func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
            functions = re.findall(func_pattern, solution)
            if functions:
                patterns.append({
                    'type': 'functions',
                    'names': functions,
                    'count': len(functions)
                })
            
            # Extract class definitions
            class_pattern = r'class\s+(\w+)(?:\([^)]*\))?:'
            classes = re.findall(class_pattern, solution)
            if classes:
                patterns.append({
                    'type': 'classes',
                    'names': classes,
                    'count': len(classes)
                })
        
        return patterns
    
    def _store_experience(self, **kwargs):
        """Store experience in database"""
        try:
            conn = sqlite3.connect(self.experience_db)
            c = conn.cursor()
            
            c.execute('''INSERT OR REPLACE INTO detailed_experiences
                        (experience_hash, task_type, query, solution, reasoning,
                         failure_reason, fix_applied, patterns_extracted, context,
                         created_at, updated_at, usage_count, success_count, failure_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (kwargs['experience_hash'],
                      kwargs['task_type'],
                      kwargs['query'],
                      json.dumps(kwargs['solution']),
                      kwargs['reasoning'],
                      kwargs.get('failure_reason'),
                      kwargs.get('fix_applied'),
                      json.dumps(kwargs['patterns']),
                      json.dumps(kwargs.get('context')),
                      datetime.now(),
                      datetime.now(),
                      0,
                      1 if kwargs['success'] else 0,
                      0 if kwargs['success'] else 1))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Store experience error: {e}")
    
    def _learn_from_failure(self, failure_reason: str, fix_applied: str, task_type: str):
        """Learn from failure to prevent future occurrences"""
        try:
            conn = sqlite3.connect(self.experience_db)
            c = conn.cursor()
            
            # Extract error type
            error_type = self._classify_error(failure_reason)
            error_hash = self._generate_hash(failure_reason)
            
            # Check if similar error exists
            c.execute('SELECT id, times_encountered FROM debugging_knowledge WHERE error_hash = ?',
                     (error_hash,))
            row = c.fetchone()
            
            if row:
                # Update existing
                c.execute('''UPDATE debugging_knowledge 
                            SET times_encountered = times_encountered + 1,
                                times_solved = times_solved + 1,
                                solution = ?
                            WHERE id = ?''',
                         (fix_applied, row[0]))
            else:
                # Insert new
                c.execute('''INSERT INTO debugging_knowledge
                            (error_type, error_message, error_hash, solution,
                             root_cause, times_encountered, times_solved)
                            VALUES (?, ?, ?, ?, ?, 1, 1)''',
                         (error_type, failure_reason, error_hash, 
                          fix_applied, self._extract_root_cause(failure_reason)))
            
            conn.commit()
            conn.close()
            
            logger.info(f"🐛 Learned from failure: {error_type}")
            
        except Exception as e:
            logger.error(f"❌ Learn from failure error: {e}")
    
    def _classify_error(self, error_message: str) -> str:
        """Classify error type from message"""
        error_lower = error_message.lower()
        
        if 'syntax' in error_lower or 'parse' in error_lower:
            return 'syntax_error'
        elif 'import' in error_lower or 'module' in error_lower:
            return 'import_error'
        elif 'attribute' in error_lower or 'has no' in error_lower:
            return 'attribute_error'
        elif 'type' in error_lower and 'error' in error_lower:
            return 'type_error'
        elif 'key' in error_lower:
            return 'key_error'
        elif 'index' in error_lower:
            return 'index_error'
        elif 'file' in error_lower or 'not found' in error_lower:
            return 'file_error'
        elif 'permission' in error_lower or 'access' in error_lower:
            return 'permission_error'
        elif 'memory' in error_lower:
            return 'memory_error'
        elif 'timeout' in error_lower or 'timed out' in error_lower:
            return 'timeout_error'
        elif 'connection' in error_lower or 'network' in error_lower:
            return 'connection_error'
        else:
            return 'runtime_error'
    
    def _extract_root_cause(self, error_message: str) -> str:
        """Extract root cause from error"""
        # Simple heuristic extraction
        if 'NoneType' in error_message:
            return 'null_reference'
        elif 'not defined' in error_message or 'not found' in error_message:
            return 'missing_reference'
        elif 'expected' in error_message and 'got' in error_message:
            return 'type_mismatch'
        return 'unknown'
    
    def _learn_code_pattern(self, code: str, context: Dict):
        """Extract and store code patterns"""
        try:
            import re
            
            # Extract function templates
            func_matches = re.finditer(
                r'def\s+(\w+)\s*\(([^)]*)\):\s*(?:->\s*(\w+))?\s*\n?\s*(?:"""([^"]*)""")?',
                code, re.DOTALL
            )
            
            for match in func_matches:
                func_name = match.group(1)
                params = match.group(2)
                return_type = match.group(3) or 'Any'
                docstring = match.group(4) or ''
                
                # Create pattern
                pattern_id = f"func_{func_name}_{self._generate_hash(code[:100])}"
                pattern_hash = self._generate_hash(f"def {func_name}({params})")
                
                # Check if pattern exists
                conn = sqlite3.connect(self.experience_db)
                c = conn.cursor()
                
                c.execute('SELECT usage_count FROM code_patterns WHERE pattern_hash = ?',
                         (pattern_hash,))
                row = c.fetchone()
                
                if row:
                    # Update usage
                    c.execute('''UPDATE code_patterns 
                                SET usage_count = usage_count + 1,
                                    success_rate = (success_rate * usage_count + 1.0) / (usage_count + 1)
                                WHERE pattern_hash = ?''',
                             (pattern_hash,))
                else:
                    # Store new pattern
                    c.execute('''INSERT INTO code_patterns
                                (pattern_id, pattern_hash, language, pattern_type,
                                 code_template, variables, use_cases, success_rate, usage_count, created_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                             (pattern_id, pattern_hash, 'python', 'function',
                              f'def {func_name}({params}):\n    """{docstring}"""\n    # Implementation',
                              json.dumps({'params': params, 'return': return_type}),
                              json.dumps([context.get('task', 'general')]),
                              1.0, 1, datetime.now()))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            logger.error(f"❌ Learn code pattern error: {e}")
    
    def find_relevant_experience(self, query: str, task_type: str = None, 
                                 limit: int = 3) -> List[Dict]:
        """Find relevant past experiences"""
        try:
            conn = sqlite3.connect(self.experience_db)
            c = conn.cursor()
            
            if task_type:
                c.execute('''SELECT id, task_type, query, solution, reasoning,
                            success_count, failure_count
                            FROM detailed_experiences 
                            WHERE task_type = ? AND success_count > 0
                            ORDER BY success_count DESC, updated_at DESC
                            LIMIT ?''', (task_type, limit))
            else:
                c.execute('''SELECT id, task_type, query, solution, reasoning,
                            success_count, failure_count
                            FROM detailed_experiences 
                            WHERE success_count > 0
                            ORDER BY updated_at DESC
                            LIMIT ?''', (limit,))
            
            rows = c.fetchall()
            conn.close()
            
            # Score by relevance
            query_words = set(query.lower().split())
            scored_experiences = []
            
            for row in rows:
                exp_query = row[2].lower()
                exp_words = set(exp_query.split())
                score = len(query_words & exp_words)
                
                success_count = int(row[5])
                failure_count = int(row[6])
                total = success_count + failure_count
                success_rate = success_count / max(total, 1)
                
                exp = {
                    'id': row[0],
                    'task_type': row[1],
                    'query': row[2],
                    'solution': json.loads(row[3]) if row[3] else None,
                    'reasoning': row[4],
                    'success_rate': success_rate,
                    'relevance_score': score
                }
                scored_experiences.append((score, exp))
            
            # Sort by relevance
            scored_experiences.sort(key=lambda x: x[0], reverse=True)
            return [exp for _, exp in scored_experiences[:limit]]
            
        except Exception as e:
            logger.error(f"❌ Find experience error: {e}")
            return []
    
    def get_code_pattern(self, pattern_type: str, language: str = 'python') -> Optional[Dict]:
        """Get a code pattern by type"""
        try:
            conn = sqlite3.connect(self.experience_db)
            c = conn.cursor()
            
            c.execute('''SELECT * FROM code_patterns 
                        WHERE pattern_type = ? AND language = ?
                        ORDER BY success_rate DESC, usage_count DESC
                        LIMIT 1''',
                     (pattern_type, language))
            
            row = c.fetchone()
            conn.close()
            
            if row:
                return {
                    'pattern_id': row[0],
                    'language': row[2],
                    'type': row[3],
                    'template': row[4],
                    'variables': json.loads(row[5]) if row[5] else {},
                    'use_cases': json.loads(row[6]) if row[6] else [],
                    'success_rate': row[7]
                }
            
        except Exception as e:
            logger.error(f"❌ Get pattern error: {e}")
        
        return None
    
    def suggest_fix(self, error_message: str) -> Optional[Dict]:
        """Suggest fix based on known errors"""
        try:
            error_type = self._classify_error(error_message)
            error_hash = self._generate_hash(error_message)
            
            conn = sqlite3.connect(self.experience_db)
            c = conn.cursor()
            
            # Try exact hash match first
            c.execute('''SELECT solution, root_cause, times_solved
                        FROM debugging_knowledge
                        WHERE error_hash = ? AND times_solved > 0''',
                     (error_hash,))
            
            row = c.fetchone()
            
            if not row:
                # Try error type match
                c.execute('''SELECT solution, root_cause, times_solved
                            FROM debugging_knowledge
                            WHERE error_type = ? AND times_solved > 0
                            ORDER BY times_solved DESC
                            LIMIT 1''',
                         (error_type,))
                row = c.fetchone()
            
            conn.close()
            
            if row:
                return {
                    'solution': row[0],
                    'root_cause': row[1],
                    'confidence': min(row[2] / 10, 1.0),  # Cap at 1.0
                    'match_type': 'exact' if row else 'type'
                }
            
        except Exception as e:
            logger.error(f"❌ Suggest fix error: {e}")
        
        return None
    
    def learn_user_preference(self, preference_type: str, observation: Any):
        """Learn user preference from observation"""
        try:
            conn = sqlite3.connect(self.experience_db)
            c = conn.cursor()
            
            c.execute('SELECT * FROM learned_preferences WHERE preference_type = ?',
                     (preference_type,))
            row = c.fetchone()
            
            if row:
                # Update with new observation
                existing_data = json.loads(row[1])
                existing_data['observations'].append(observation)
                
                # Simple majority voting for preferences
                from collections import Counter
                if isinstance(observation, str):
                    counts = Counter(existing_data['observations'])
                    most_common = counts.most_common(1)[0]
                    confidence = most_common[1] / len(existing_data['observations'])
                else:
                    confidence = 0.5
                
                c.execute('''UPDATE learned_preferences
                            SET preference_data = ?,
                                confidence = ?,
                                sample_count = sample_count + 1,
                                last_observed = ?
                            WHERE preference_type = ?''',
                         (json.dumps(existing_data), confidence, datetime.now(), preference_type))
            else:
                # New preference
                data = {'observations': [observation]}
                c.execute('''INSERT INTO learned_preferences
                            (preference_type, preference_data, confidence, sample_count,
                             first_observed, last_observed)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                         (preference_type, json.dumps(data), 0.5, 1, datetime.now(), datetime.now()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"👤 Learned preference: {preference_type}")
            
        except Exception as e:
            logger.error(f"❌ Learn preference error: {e}")
    
    def get_learning_summary(self) -> Dict:
        """Get comprehensive learning summary"""
        try:
            conn = sqlite3.connect(self.experience_db)
            c = conn.cursor()
            
            # Total experiences
            c.execute('SELECT COUNT(*) FROM detailed_experiences')
            total_exp = c.fetchone()[0]
            
            # Success rate
            c.execute('SELECT SUM(success_count), SUM(failure_count) FROM detailed_experiences')
            success, failure = c.fetchone()
            success_rate = success / max(success + failure, 1)
            
            # Patterns learned
            c.execute('SELECT COUNT(*) FROM code_patterns')
            code_patterns = c.fetchone()[0]
            
            # Debugging knowledge
            c.execute('SELECT COUNT(*) FROM debugging_knowledge')
            debug_knowledge = c.fetchone()[0]
            
            # User preferences learned
            c.execute('SELECT COUNT(*) FROM learned_preferences')
            preferences = c.fetchone()[0]
            
            # Task type distribution
            c.execute('SELECT task_type, COUNT(*) FROM detailed_experiences GROUP BY task_type')
            task_dist = dict(c.fetchall())
            
            conn.close()
            
            return {
                'total_experiences': total_exp,
                'success_rate': success_rate,
                'code_patterns_learned': code_patterns,
                'debugging_knowledge': debug_knowledge,
                'user_preferences_learned': preferences,
                'task_type_distribution': task_dist
            }
            
        except Exception as e:
            logger.error(f"❌ Learning summary error: {e}")
            return {}

# Singleton instance
experience_engine = MayaExperienceEngine()

if DEBUG_MODE:
    print("🎓 Maya Experience Engine ready")
    print("   Capabilities: Pattern learning, Experience retention, Knowledge reuse")
