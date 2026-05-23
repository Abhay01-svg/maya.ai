"""
Maya AI Core Planner Module
Autonomous planning and workflow intelligence system
"""

import json
import os
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from config import PROJECT_ROOT, DEBUG_MODE

logger = logging.getLogger(__name__)

class PlanStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class PlanStep:
    """Individual step in a plan"""
    def __init__(self, step_id: int, description: str, action: str, 
                 parameters: Dict = None, priority: TaskPriority = TaskPriority.MEDIUM):
        self.step_id = step_id
        self.description = description
        self.action = action
        self.parameters = parameters or {}
        self.priority = priority
        self.status = PlanStatus.PENDING
        self.result = None
        self.started_at = None
        self.completed_at = None
        self.dependencies = []  # List of step_ids that must complete first
        
    def to_dict(self) -> Dict:
        return {
            'step_id': self.step_id,
            'description': self.description,
            'action': self.action,
            'parameters': self.parameters,
            'priority': self.priority.value,
            'status': self.status.value,
            'result': self.result,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'dependencies': self.dependencies
        }

class Plan:
    """A complete plan with multiple steps"""
    def __init__(self, plan_id: str, name: str, description: str, 
                 goal: str, created_by: str = "user"):
        self.plan_id = plan_id
        self.name = name
        self.description = description
        self.goal = goal
        self.created_by = created_by
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.status = PlanStatus.PENDING
        self.steps: List[PlanStep] = []
        self.progress = 0.0
        self.tags = []
        self.metadata = {}
        
    def add_step(self, description: str, action: str, 
                 parameters: Dict = None, priority: TaskPriority = TaskPriority.MEDIUM,
                 dependencies: List[int] = None) -> PlanStep:
        """Add a step to the plan"""
        step_id = len(self.steps) + 1
        step = PlanStep(step_id, description, action, parameters, priority)
        if dependencies:
            step.dependencies = dependencies
        self.steps.append(step)
        return step
    
    def update_progress(self):
        """Calculate plan progress percentage"""
        if not self.steps:
            self.progress = 0.0
            return
        completed = sum(1 for s in self.steps if s.status == PlanStatus.COMPLETED)
        self.progress = (completed / len(self.steps)) * 100
        
    def to_dict(self) -> Dict:
        return {
            'plan_id': self.plan_id,
            'name': self.name,
            'description': self.description,
            'goal': self.goal,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status.value,
            'progress': self.progress,
            'steps': [s.to_dict() for s in self.steps],
            'tags': self.tags,
            'metadata': self.metadata
        }

class MayaPlanner:
    """
    Core Planner for Maya AI
    Provides autonomous planning, workflow orchestration, and task management
    """
    
    def __init__(self):
        self.plans_db = os.path.join(PROJECT_ROOT, "data", "plans.db")
        self._init_database()
        self.active_plan = None
        logger.info("🎯 Maya Planner Core initialized")
        
    def _init_database(self):
        """Initialize plans database"""
        try:
            os.makedirs(os.path.dirname(self.plans_db), exist_ok=True)
            conn = sqlite3.connect(self.plans_db)
            c = conn.cursor()
            
            # Plans table
            c.execute('''CREATE TABLE IF NOT EXISTS plans
                        (plan_id TEXT PRIMARY KEY, name TEXT, description TEXT,
                         goal TEXT, created_by TEXT, created_at TIMESTAMP,
                         updated_at TIMESTAMP, status TEXT, progress REAL,
                         tags TEXT, metadata TEXT)''')
            
            # Plan steps table
            c.execute('''CREATE TABLE IF NOT EXISTS plan_steps
                        (step_id INTEGER, plan_id TEXT, description TEXT,
                         action TEXT, parameters TEXT, priority INTEGER,
                         status TEXT, result TEXT, started_at TIMESTAMP,
                         completed_at TIMESTAMP, dependencies TEXT,
                         PRIMARY KEY (step_id, plan_id),
                         FOREIGN KEY (plan_id) REFERENCES plans(plan_id))''')
            
            # Plan execution history
            c.execute('''CREATE TABLE IF NOT EXISTS execution_history
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         plan_id TEXT, step_id INTEGER, action TEXT,
                         status TEXT, result TEXT, executed_at TIMESTAMP)''')
            
            conn.commit()
            conn.close()
            
            if DEBUG_MODE:
                logger.info("✅ Planner database initialized")
                
        except Exception as e:
            logger.error(f"❌ Planner database init error: {e}")
    
    def create_plan(self, name: str, description: str, goal: str,
                    tags: List[str] = None, created_by: str = "user") -> Plan:
        """Create a new plan"""
        import uuid
        plan_id = str(uuid.uuid4())[:8]
        
        plan = Plan(plan_id, name, description, goal, created_by)
        if tags:
            plan.tags = tags
            
        # Save to database
        self._save_plan(plan)
        
        logger.info(f"📝 Created plan: {name} (ID: {plan_id})")
        return plan
    
    def _save_plan(self, plan: Plan):
        """Save plan to database"""
        try:
            conn = sqlite3.connect(self.plans_db)
            c = conn.cursor()
            
            c.execute('''INSERT OR REPLACE INTO plans 
                        (plan_id, name, description, goal, created_by,
                         created_at, updated_at, status, progress, tags, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (plan.plan_id, plan.name, plan.description, plan.goal,
                      plan.created_by, plan.created_at, plan.updated_at,
                      plan.status.value, plan.progress, 
                      json.dumps(plan.tags), json.dumps(plan.metadata)))
            
            # Save steps
            for step in plan.steps:
                c.execute('''INSERT OR REPLACE INTO plan_steps
                            (step_id, plan_id, description, action, parameters,
                             priority, status, result, started_at, completed_at, dependencies)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (step.step_id, plan.plan_id, step.description, step.action,
                          json.dumps(step.parameters), step.priority.value,
                          step.status.value, json.dumps(step.result) if step.result else None,
                          step.started_at, step.completed_at,
                          json.dumps(step.dependencies)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error saving plan: {e}")
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Retrieve a plan by ID"""
        try:
            conn = sqlite3.connect(self.plans_db)
            c = conn.cursor()
            
            c.execute('SELECT * FROM plans WHERE plan_id = ?', (plan_id,))
            row = c.fetchone()
            
            if not row:
                conn.close()
                return None
            
            plan = Plan(row[0], row[1], row[2], row[3], row[4])
            plan.created_at = datetime.fromisoformat(row[5])
            plan.updated_at = datetime.fromisoformat(row[6])
            plan.status = PlanStatus(row[7])
            plan.progress = row[8]
            plan.tags = json.loads(row[9]) if row[9] else []
            plan.metadata = json.loads(row[10]) if row[10] else {}
            
            # Load steps
            c.execute('SELECT * FROM plan_steps WHERE plan_id = ? ORDER BY step_id', (plan_id,))
            step_rows = c.fetchall()
            
            for row in step_rows:
                step = PlanStep(row[0], row[2], row[3], 
                               json.loads(row[4]) if row[4] else {},
                               TaskPriority(row[5]))
                step.status = PlanStatus(row[6])
                step.result = json.loads(row[7]) if row[7] else None
                step.started_at = datetime.fromisoformat(row[8]) if row[8] else None
                step.completed_at = datetime.fromisoformat(row[9]) if row[9] else None
                step.dependencies = json.loads(row[10]) if row[10] else []
                plan.steps.append(step)
            
            conn.close()
            return plan
            
        except Exception as e:
            logger.error(f"❌ Error loading plan: {e}")
            return None
    
    def list_plans(self, status: PlanStatus = None, limit: int = 20) -> List[Dict]:
        """List all plans, optionally filtered by status"""
        try:
            conn = sqlite3.connect(self.plans_db)
            c = conn.cursor()
            
            if status:
                c.execute('''SELECT plan_id, name, description, goal, status, progress, created_at 
                            FROM plans WHERE status = ? ORDER BY created_at DESC LIMIT ?''',
                         (status.value, limit))
            else:
                c.execute('''SELECT plan_id, name, description, goal, status, progress, created_at 
                            FROM plans ORDER BY created_at DESC LIMIT ?''', (limit,))
            
            rows = c.fetchall()
            conn.close()
            
            return [{
                'plan_id': r[0],
                'name': r[1],
                'description': r[2],
                'goal': r[3],
                'status': r[4],
                'progress': r[5],
                'created_at': r[6]
            } for r in rows]
            
        except Exception as e:
            logger.error(f"❌ Error listing plans: {e}")
            return []
    
    def execute_step(self, plan_id: str, step_id: int, 
                     executor_func=None) -> Dict[str, Any]:
        """Execute a single plan step"""
        plan = self.get_plan(plan_id)
        if not plan:
            return {'success': False, 'error': 'Plan not found'}
        
        step = next((s for s in plan.steps if s.step_id == step_id), None)
        if not step:
            return {'success': False, 'error': 'Step not found'}
        
        # Check dependencies
        for dep_id in step.dependencies:
            dep_step = next((s for s in plan.steps if s.step_id == dep_id), None)
            if not dep_step or dep_step.status != PlanStatus.COMPLETED:
                return {'success': False, 'error': f'Dependency step {dep_id} not completed'}
        
        # Execute
        step.status = PlanStatus.IN_PROGRESS
        step.started_at = datetime.now()
        
        try:
            result = None
            if executor_func:
                result = executor_func(step.action, step.parameters)
            else:
                # Default execution via autonomous agent
                from modules.autonomous_agent import autonomous_agent
                result = autonomous_agent.execute_task(step.action, step.parameters)
            
            step.status = PlanStatus.COMPLETED
            step.completed_at = datetime.now()
            step.result = result
            
            # Update plan progress
            plan.update_progress()
            plan.updated_at = datetime.now()
            if plan.progress == 100:
                plan.status = PlanStatus.COMPLETED
            
            self._save_plan(plan)
            
            # Log execution
            self._log_execution(plan_id, step_id, step.action, 'completed', result)
            
            return {'success': True, 'result': result, 'step': step.to_dict()}
            
        except Exception as e:
            step.status = PlanStatus.FAILED
            plan.status = PlanStatus.FAILED
            self._save_plan(plan)
            self._log_execution(plan_id, step_id, step.action, 'failed', str(e))
            
            logger.error(f"❌ Step execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _log_execution(self, plan_id: str, step_id: int, action: str, 
                       status: str, result: Any):
        """Log execution history"""
        try:
            conn = sqlite3.connect(self.plans_db)
            c = conn.cursor()
            
            c.execute('''INSERT INTO execution_history 
                        (plan_id, step_id, action, status, result, executed_at)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (plan_id, step_id, action, status, 
                      json.dumps(result) if result else None, datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error logging execution: {e}")
    
    def execute_plan(self, plan_id: str, executor_func=None) -> Dict[str, Any]:
        """Execute entire plan step by step"""
        plan = self.get_plan(plan_id)
        if not plan:
            return {'success': False, 'error': 'Plan not found'}
        
        plan.status = PlanStatus.IN_PROGRESS
        self._save_plan(plan)
        
        results = []
        for step in plan.steps:
            if step.status == PlanStatus.PENDING:
                result = self.execute_step(plan_id, step.step_id, executor_func)
                results.append(result)
                
                if not result['success']:
                    return {
                        'success': False,
                        'error': f'Step {step.step_id} failed',
                        'step_results': results
                    }
        
        return {
            'success': True,
            'plan_id': plan_id,
            'total_steps': len(plan.steps),
            'completed_steps': len([r for r in results if r['success']]),
            'results': results
        }
    
    def delete_plan(self, plan_id: str) -> bool:
        """Delete a plan"""
        try:
            conn = sqlite3.connect(self.plans_db)
            c = conn.cursor()
            
            c.execute('DELETE FROM plan_steps WHERE plan_id = ?', (plan_id,))
            c.execute('DELETE FROM execution_history WHERE plan_id = ?', (plan_id,))
            c.execute('DELETE FROM plans WHERE plan_id = ?', (plan_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"🗑️ Deleted plan: {plan_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting plan: {e}")
            return False
    
    def get_execution_history(self, plan_id: str = None, limit: int = 50) -> List[Dict]:
        """Get execution history"""
        try:
            conn = sqlite3.connect(self.plans_db)
            c = conn.cursor()
            
            if plan_id:
                c.execute('''SELECT * FROM execution_history 
                            WHERE plan_id = ? ORDER BY executed_at DESC LIMIT ?''',
                         (plan_id, limit))
            else:
                c.execute('''SELECT * FROM execution_history 
                            ORDER BY executed_at DESC LIMIT ?''', (limit,))
            
            rows = c.fetchall()
            conn.close()
            
            return [{
                'id': r[0],
                'plan_id': r[1],
                'step_id': r[2],
                'action': r[3],
                'status': r[4],
                'result': json.loads(r[5]) if r[5] else None,
                'executed_at': r[6]
            } for r in rows]
            
        except Exception as e:
            logger.error(f"❌ Error getting history: {e}")
            return []

# Singleton instance
planner = MayaPlanner()

if DEBUG_MODE:
    print("🎯 Maya Planner Core initialized")
