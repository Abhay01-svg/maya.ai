"""
Maya Core Intelligence System
Autonomous coding engineer and workflow orchestrator
Main intelligence orchestrator that coordinates all Maya subsystems
"""

import os
import sys
import json
import logging
import sqlite3
import subprocess
import ast
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from enum import Enum

from config import PROJECT_ROOT, DEBUG_MODE
from modules.memory import memory
from modules.planner import planner, Plan, PlanStatus

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Task classification types"""
    CODING = "coding"
    DEBUGGING = "debugging"
    SIMULATION = "simulation"
    REPORT_GENERATION = "report_generation"
    AUTOMATION = "automation"
    PROJECT_ANALYSIS = "project_analysis"
    ARCHITECTURE_PLANNING = "architecture_planning"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    WORKFLOW_EXECUTION = "workflow_execution"
    GENERAL = "general"

class IntelligenceMode(Enum):
    """Intelligence operation modes"""
    RULE_BASED = "rule_based"      # Fast, deterministic
    NLP_HYBRID = "nlp_hybrid"      # NLP + rules
    DEEP_REASONING = "deep"        # Full AI reasoning (heavy)

class MayaCoreIntelligence:
    """
    Maya Core Intelligence System
    Coordinates: planning, analysis, execution, learning, validation
    """
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.memory_db = os.path.join(PROJECT_ROOT, "data", "maya_core.db")
        self.experience_dir = os.path.join(PROJECT_ROOT, "data", "experiences")
        self.current_mode = IntelligenceMode.RULE_BASED
        self.active_project = None
        self.learning_cache = {}
        
        self._init_database()
        self._init_experience_storage()
        
        logger.info("🧠 Maya Core Intelligence System initialized")
        
    def _init_database(self):
        """Initialize core intelligence database"""
        try:
            os.makedirs(os.path.dirname(self.memory_db), exist_ok=True)
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()
            
            # Experience storage
            c.execute('''CREATE TABLE IF NOT EXISTS experiences
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         task_type TEXT, query TEXT, solution TEXT,
                         reasoning TEXT, patterns TEXT, timestamp TIMESTAMP,
                         success BOOLEAN, project_context TEXT)''')
            
            # Coding patterns learned
            c.execute('''CREATE TABLE IF NOT EXISTS coding_patterns
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         pattern_name TEXT, pattern_code TEXT,
                         language TEXT, use_cases TEXT, context TEXT,
                         timestamp TIMESTAMP, usage_count INTEGER DEFAULT 0)''')
            
            # Project analysis cache
            c.execute('''CREATE TABLE IF NOT EXISTS project_analysis
                        (project_path TEXT PRIMARY KEY,
                         framework TEXT, dependencies TEXT,
                         file_structure TEXT, last_analyzed TIMESTAMP)''')
            
            # User behavior patterns
            c.execute('''CREATE TABLE IF NOT EXISTS user_patterns
                        (pattern_type TEXT PRIMARY KEY,
                         pattern_data TEXT, frequency INTEGER,
                         last_seen TIMESTAMP)''')
            
            conn.commit()
            conn.close()
            
            if DEBUG_MODE:
                logger.info("✅ Core intelligence database initialized")
                
        except Exception as e:
            logger.error(f"❌ Core database init error: {e}")
    
    def _init_experience_storage(self):
        """Initialize experience storage directory"""
        os.makedirs(self.experience_dir, exist_ok=True)
        
    def analyze_intent(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """
        Analyze user intent and classify task
        Returns: task type, complexity, required mode
        """
        query_lower = query.lower()
        context = context or {}
        
        # Rule-based intent classification
        task_indicators = {
            TaskType.CODING: [
                'code', 'write', 'implement', 'create', 'function', 'class',
                'module', 'script', 'program', 'develop', 'build'
            ],
            TaskType.DEBUGGING: [
                'debug', 'fix', 'error', 'bug', 'issue', 'problem',
                'traceback', 'exception', 'crash', 'not working'
            ],
            TaskType.SIMULATION: [
                'simulate', 'model', 'calculate', 'predict', 'analyze data',
                'computation', 'math', 'formula', 'algorithm'
            ],
            TaskType.REPORT_GENERATION: [
                'report', 'document', 'generate pdf', 'create word',
                'presentation', 'summary', 'analysis report'
            ],
            TaskType.AUTOMATION: [
                'automate', 'schedule', 'script', 'batch', 'cron',
                'pipeline', 'workflow', 'trigger', 'monitor'
            ],
            TaskType.PROJECT_ANALYSIS: [
                'analyze project', 'scan code', 'review', 'audit',
                'dependencies', 'structure', 'architecture review'
            ],
            TaskType.ARCHITECTURE_PLANNING: [
                'design', 'architecture', 'structure', 'plan system',
                'framework', 'pattern', 'organize code'
            ],
            TaskType.DEPLOYMENT: [
                'deploy', 'build', 'release', 'publish', 'install',
                'setup', 'configure', 'host'
            ],
            TaskType.DOCUMENTATION: [
                'document', 'readme', 'docstring', 'comment', 'explain',
                'tutorial', 'guide', 'manual'
            ],
            TaskType.WORKFLOW_EXECUTION: [
                'execute plan', 'run workflow', 'process', 'task',
                'orchestrate', 'coordinate'
            ]
        }
        
        # Score each task type
        scores = {task: 0 for task in TaskType}
        for task, indicators in task_indicators.items():
            for indicator in indicators:
                if indicator in query_lower:
                    scores[task] += 1
        
        # Determine primary task type
        max_score = max(scores.values())
        if max_score > 0:
            task_type = max(scores, key=scores.get)
        else:
            task_type = TaskType.GENERAL
        
        # Determine complexity
        complexity = self._assess_complexity(query, task_type)
        
        # Determine required intelligence mode
        required_mode = self._determine_intelligence_mode(query, complexity, task_type)
        
        return {
            'task_type': task_type,
            'complexity': complexity,
            'required_mode': required_mode,
            'confidence': max_score / max(len(task_indicators[task_type]), 1) if task_type != TaskType.GENERAL else 0.5,
            'context_needs': self._identify_context_needs(query, task_type)
        }
    
    def _assess_complexity(self, query: str, task_type: TaskType) -> str:
        """Assess task complexity"""
        complexity_score = 0
        
        # Length-based complexity
        if len(query) > 200:
            complexity_score += 2
        elif len(query) > 100:
            complexity_score += 1
        
        # Keyword-based complexity
        complex_indicators = [
            'multiple', 'complex', 'advanced', 'integrate', 'system',
            'architecture', 'framework', 'distributed', 'concurrent',
            'optimize', 'refactor', 'redesign'
        ]
        for indicator in complex_indicators:
            if indicator in query.lower():
                complexity_score += 1
        
        # Task type complexity baseline
        baseline_complexity = {
            TaskType.CODING: 1,
            TaskType.DEBUGGING: 2,
            TaskType.ARCHITECTURE_PLANNING: 3,
            TaskType.SIMULATION: 2,
            TaskType.AUTOMATION: 2
        }
        complexity_score += baseline_complexity.get(task_type, 1)
        
        if complexity_score >= 5:
            return "high"
        elif complexity_score >= 3:
            return "medium"
        return "low"
    
    def _determine_intelligence_mode(self, query: str, complexity: str, task_type: TaskType) -> IntelligenceMode:
        """Determine optimal intelligence mode"""
        if complexity == "high" or task_type in [TaskType.ARCHITECTURE_PLANNING, TaskType.DEBUGGING]:
            return IntelligenceMode.DEEP_REASONING
        elif complexity == "medium":
            return IntelligenceMode.NLP_HYBRID
        return IntelligenceMode.RULE_BASED
    
    def _identify_context_needs(self, query: str, task_type: TaskType) -> List[str]:
        """Identify what context is needed for the task"""
        needs = []
        
        if task_type == TaskType.CODING:
            needs.extend(['language', 'framework', 'existing_code'])
        elif task_type == TaskType.DEBUGGING:
            needs.extend(['error_logs', 'code_context', 'recent_changes'])
        elif task_type == TaskType.PROJECT_ANALYSIS:
            needs.extend(['project_structure', 'dependencies'])
        elif task_type == TaskType.AUTOMATION:
            needs.extend(['system_info', 'permissions', 'existing_scripts'])
        
        return needs
    
    def execute_workflow(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """
        Main execution workflow
        Follows: Analyze → Plan → Execute → Validate → Learn
        """
        # Step 1: Intent Analysis
        analysis = self.analyze_intent(query, context)
        logger.info(f"📊 Task classified: {analysis['task_type'].value} (complexity: {analysis['complexity']})")
        
        # Step 2: Context Understanding
        project_context = self._gather_context(analysis['context_needs'])
        
        # Step 3: Check Experience Memory
        similar_experience = self._find_similar_experience(query, analysis['task_type'])
        if similar_experience and similar_experience['success']:
            logger.info(f"💡 Found similar experience (ID: {similar_experience['id']})")
        
        # Step 4: Planning
        if analysis['task_type'] in [TaskType.CODING, TaskType.AUTOMATION, TaskType.WORKFLOW_EXECUTION]:
            plan = self._create_execution_plan(query, analysis, project_context)
        else:
            plan = None
        
        # Step 5: Independent Implementation
        result = self._execute_task(query, analysis, plan, project_context, similar_experience)
        
        # Step 6: Self-Validation
        validation = self._validate_result(result, analysis)
        
        # Step 7: Learn from experience
        self._store_experience(query, analysis, result, validation)
        
        return {
            'success': result.get('success', False),
            'analysis': analysis,
            'result': result,
            'validation': validation,
            'plan': plan.to_dict() if plan else None
        }
    
    def _gather_context(self, context_needs: List[str]) -> Dict:
        """Gather required context"""
        context = {}
        
        for need in context_needs:
            if need == 'project_structure':
                context['project_structure'] = self._scan_project_structure()
            elif need == 'language':
                context['detected_language'] = self._detect_primary_language()
            elif need == 'framework':
                context['detected_frameworks'] = self._detect_frameworks()
            elif need == 'existing_code':
                context['recent_files'] = self._get_recently_modified_files()
        
        return context
    
    def _scan_project_structure(self) -> Dict:
        """Scan current project structure"""
        structure = {
            'total_files': 0,
            'languages': {},
            'directories': [],
            'entry_points': []
        }
        
        try:
            for root, dirs, files in os.walk(self.project_root):
                # Skip __pycache__, node_modules, etc.
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]
                
                rel_root = os.path.relpath(root, self.project_root)
                if rel_root != '.':
                    structure['directories'].append(rel_root)
                
                for file in files:
                    if file.startswith('.'):
                        continue
                    
                    structure['total_files'] += 1
                    ext = os.path.splitext(file)[1]
                    if ext:
                        structure['languages'][ext] = structure['languages'].get(ext, 0) + 1
                    
                    # Detect entry points
                    if file in ['main.py', 'app.py', 'index.js', 'server.js', 'run.py']:
                        structure['entry_points'].append(os.path.join(rel_root, file))
        
        except Exception as e:
            logger.error(f"❌ Project scan error: {e}")
        
        return structure
    
    def _detect_primary_language(self) -> str:
        """Detect primary programming language"""
        structure = self._scan_project_structure()
        if not structure['languages']:
            return 'unknown'
        
        return max(structure['languages'], key=structure['languages'].get)
    
    def _detect_frameworks(self) -> List[str]:
        """Detect frameworks used in project"""
        frameworks = []
        
        # Check for framework indicators
        indicators = {
            'flask': ['flask', 'app.py'],
            'django': ['django', 'manage.py'],
            'fastapi': ['fastapi'],
            'react': ['react', 'src/App.js'],
            'vue': ['vue', 'vue.config.js'],
            'angular': ['angular', 'angular.json']
        }
        
        for framework, indicators_list in indicators.items():
            for indicator in indicators_list:
                if self._check_file_exists(indicator):
                    frameworks.append(framework)
                    break
        
        return frameworks
    
    def _check_file_exists(self, pattern: str) -> bool:
        """Check if file exists in project"""
        for root, dirs, files in os.walk(self.project_root):
            if pattern in files:
                return True
            if any(pattern in d for d in dirs):
                return True
        return False
    
    def _get_recently_modified_files(self, limit: int = 10) -> List[str]:
        """Get recently modified files"""
        files = []
        try:
            for root, dirs, filenames in os.walk(self.project_root):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    try:
                        mtime = os.path.getmtime(filepath)
                        files.append((filepath, mtime))
                    except:
                        pass
            
            # Sort by modification time
            files.sort(key=lambda x: x[1], reverse=True)
            return [f[0] for f in files[:limit]]
        
        except Exception as e:
            logger.error(f"❌ Recent files error: {e}")
            return []
    
    def _find_similar_experience(self, query: str, task_type: TaskType) -> Optional[Dict]:
        """Find similar past experience"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()
            
            c.execute('''SELECT id, query, solution, reasoning, success 
                        FROM experiences 
                        WHERE task_type = ? AND success = 1
                        ORDER BY timestamp DESC LIMIT 5''', (task_type.value,))
            
            rows = c.fetchall()
            conn.close()
            
            if rows:
                # Simple keyword matching
                query_words = set(query.lower().split())
                best_match = None
                best_score = 0
                
                for row in rows:
                    exp_words = set(row[1].lower().split())
                    score = len(query_words & exp_words)
                    if score > best_score:
                        best_score = score
                        best_match = {
                            'id': row[0],
                            'query': row[1],
                            'solution': row[2],
                            'reasoning': row[3],
                            'success': row[4]
                        }
                
                return best_match
            
        except Exception as e:
            logger.error(f"❌ Experience search error: {e}")
        
        return None
    
    def _create_execution_plan(self, query: str, analysis: Dict, context: Dict) -> Plan:
        """Create execution plan for task"""
        plan = planner.create_plan(
            name=f"Execute: {query[:50]}...",
            description=f"Automated plan for: {query}",
            goal=query,
            tags=[analysis['task_type'].value, analysis['complexity']]
        )
        
        # Add steps based on task type
        if analysis['task_type'] == TaskType.CODING:
            plan.add_step("Analyze requirements", "analyze_requirements")
            plan.add_step("Design solution", "design_solution")
            plan.add_step("Implement code", "implement_code")
            plan.add_step("Validate syntax", "validate_syntax")
            plan.add_step("Test execution", "test_execution")
        
        elif analysis['task_type'] == TaskType.DEBUGGING:
            plan.add_step("Analyze error", "analyze_error")
            plan.add_step("Locate issue", "locate_issue")
            plan.add_step("Implement fix", "implement_fix")
            plan.add_step("Verify solution", "verify_solution")
        
        planner._save_plan(plan)
        return plan
    
    def _execute_task(self, query: str, analysis: Dict, plan: Plan, 
                      context: Dict, experience: Dict = None) -> Dict:
        """Execute task based on analysis"""
        task_type = analysis['task_type']
        
        # Route to appropriate execution pipeline
        if task_type == TaskType.CODING:
            return self._execute_coding_pipeline(query, analysis, context, experience)
        elif task_type == TaskType.DEBUGGING:
            return self._execute_debugging_pipeline(query, analysis, context)
        elif task_type == TaskType.PROJECT_ANALYSIS:
            return self._execute_analysis_pipeline(query, analysis, context)
        elif task_type == TaskType.AUTOMATION:
            return self._execute_automation_pipeline(query, analysis, context)
        else:
            return self._execute_general_pipeline(query, analysis)
    
    def _execute_coding_pipeline(self, query: str, analysis: Dict, 
                                  context: Dict, experience: Dict) -> Dict:
        """Execute coding task pipeline"""
        from modules.autonomous_agent import autonomous_agent
        
        # Use experience if available
        if experience and experience.get('solution'):
            logger.info("💡 Applying learned pattern from previous experience")
        
        # Execute via autonomous agent
        result = autonomous_agent.execute_task("research_and_document", {
            'topic': query,
            'format': 'code'
        })
        
        return {
            'success': result is not None,
            'result': result,
            'pipeline': 'coding'
        }
    
    def _execute_debugging_pipeline(self, query: str, analysis: Dict, 
                                     context: Dict) -> Dict:
        """Execute debugging task pipeline"""
        # Analyze recent files for errors
        recent_files = context.get('recent_files', [])
        
        issues_found = []
        for filepath in recent_files[:5]:  # Check 5 most recent
            try:
                issues = self._analyze_code_for_issues(filepath)
                issues_found.extend(issues)
            except:
                pass
        
        return {
            'success': True,
            'issues_found': issues_found,
            'pipeline': 'debugging'
        }
    
    def _analyze_code_for_issues(self, filepath: str) -> List[Dict]:
        """Analyze Python code for common issues"""
        issues = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Syntax check
            try:
                ast.parse(code)
            except SyntaxError as e:
                issues.append({
                    'file': filepath,
                    'line': e.lineno,
                    'type': 'syntax_error',
                    'message': str(e)
                })
            
            # Check for common patterns
            if 'except:' in code and 'except Exception:' not in code:
                issues.append({
                    'file': filepath,
                    'type': 'style_warning',
                    'message': 'Bare except clause found'
                })
            
        except Exception as e:
            logger.error(f"❌ Code analysis error for {filepath}: {e}")
        
        return issues
    
    def _execute_analysis_pipeline(self, query: str, analysis: Dict, 
                                   context: Dict) -> Dict:
        """Execute project analysis pipeline"""
        project_structure = context.get('project_structure', {})
        
        return {
            'success': True,
            'analysis': {
                'total_files': project_structure.get('total_files', 0),
                'languages': project_structure.get('languages', {}),
                'entry_points': project_structure.get('entry_points', []),
                'frameworks': self._detect_frameworks()
            },
            'pipeline': 'analysis'
        }
    
    def _execute_automation_pipeline(self, query: str, analysis: Dict, 
                                    context: Dict) -> Dict:
        """Execute automation task pipeline"""
        # Create automation script
        return {
            'success': True,
            'message': 'Automation pipeline ready',
            'pipeline': 'automation'
        }
    
    def _execute_general_pipeline(self, query: str, analysis: Dict) -> Dict:
        """Execute general query via brain"""
        from modules.brain import brain
        
        result = brain.process_query(query)
        return result
    
    def _validate_result(self, result: Dict, analysis: Dict) -> Dict:
        """Validate execution result"""
        validation = {
            'syntax_valid': True,
            'imports_valid': True,
            'execution_feasible': True,
            'logical_issues': [],
            'overall_valid': True
        }
        
        # Validate based on task type
        if analysis['task_type'] == TaskType.CODING:
            if result.get('result'):
                # Check if result contains code
                code = str(result['result'])
                
                # Basic syntax validation for Python
                if 'def ' in code or 'class ' in code:
                    try:
                        ast.parse(code)
                    except SyntaxError as e:
                        validation['syntax_valid'] = False
                        validation['logical_issues'].append(f"Syntax error: {e}")
        
        # Overall validation
        validation['overall_valid'] = (
            validation['syntax_valid'] and 
            validation['imports_valid'] and 
            validation['execution_feasible'] and
            not validation['logical_issues']
        )
        
        return validation
    
    def _store_experience(self, query: str, analysis: Dict, result: Dict, 
                         validation: Dict):
        """Store experience for future learning"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()
            
            c.execute('''INSERT INTO experiences 
                        (task_type, query, solution, reasoning, patterns, 
                         timestamp, success, project_context)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (analysis['task_type'].value,
                      query,
                      json.dumps(result.get('result')),
                      f"Complexity: {analysis['complexity']}, Mode: {analysis['required_mode'].value}",
                      json.dumps(analysis),
                      datetime.now(),
                      validation.get('overall_valid', False),
                      json.dumps(self.active_project)))
            
            conn.commit()
            conn.close()
            
            if DEBUG_MODE:
                logger.info("💾 Experience stored for learning")
                
        except Exception as e:
            logger.error(f"❌ Experience storage error: {e}")
    
    def get_learning_stats(self) -> Dict:
        """Get learning statistics"""
        try:
            conn = sqlite3.connect(self.memory_db)
            c = conn.cursor()
            
            c.execute('SELECT COUNT(*) FROM experiences')
            total_experiences = c.fetchone()[0]
            
            c.execute('SELECT COUNT(*) FROM experiences WHERE success = 1')
            successful_experiences = c.fetchone()[0]
            
            c.execute('SELECT task_type, COUNT(*) FROM experiences GROUP BY task_type')
            task_distribution = dict(c.fetchall())
            
            conn.close()
            
            return {
                'total_experiences': total_experiences,
                'successful_experiences': successful_experiences,
                'success_rate': successful_experiences / max(total_experiences, 1),
                'task_distribution': task_distribution
            }
            
        except Exception as e:
            logger.error(f"❌ Stats error: {e}")
            return {}

# Singleton instance
core_intelligence = MayaCoreIntelligence()

if DEBUG_MODE:
    print("🧠 Maya Core Intelligence System ready")
    print("   Capabilities: Planning, Analysis, Execution, Learning, Validation")
