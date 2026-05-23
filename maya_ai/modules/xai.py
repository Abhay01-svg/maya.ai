"""
Maya AI XAI (Explainable AI) Module
===================================
Provides reasoning tracing, attention mapping, decision visualization,
and code explanation for transparent AI behavior.
"""

import logging
import json
import re
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class DecisionStep:
    """A single step in the AI's decision process"""
    step_name: str
    action: str
    result: Any
    reasoning: str
    timestamp: float = time.time()

@dataclass
class XAIReport:
    """Full XAI report for a query"""
    query: str
    intent: str
    confidence: float
    decision_path: List[DecisionStep]
    attention_map: Dict[str, float]
    knowledge_sources: List[str]
    logic_type: str # Deductive, Inductive, etc.
    memory_references: List[str]

class XAIEngine:
    """Engine for generating explainability and reasoning reports"""
    
    def __init__(self):
        self.current_report: Optional[XAIReport] = None
        self._trace: List[DecisionStep] = []
        logger.info("🧠 XAI Engine initialized")

    def start_trace(self, query: str):
        """Start a new decision trace"""
        self._trace = []
        self.current_report = XAIReport(
            query=query,
            intent="unknown",
            confidence=0.0,
            decision_path=[],
            attention_map={},
            knowledge_sources=[],
            logic_type="Heuristic",
            memory_references=[]
        )
        self.add_step("Input Received", "Capture", query, "User input received and normalization started")

    def add_step(self, name: str, action: str, result: Any, reasoning: str):
        """Add a step to the current decision trace"""
        step = DecisionStep(name, action, result, reasoning)
        self._trace.append(step)
        if self.current_report:
            self.current_report.decision_path.append(step)
        logger.debug(f"XAI Step: {name} -> {reasoning}")

    def generate_attention_map(self, text: str, elite_nlp_data: Any) -> Dict[str, float]:
        """Generate a simulated attention map based on token importance"""
        tokens = text.lower().split()
        weights = {token: 0.1 for token in tokens}
        
        # Keywords from Elite NLP parsed data get higher weights
        important_tokens = getattr(elite_nlp_data, 'tokens', [])
        for token in important_tokens:
            t = token.lower()
            if t in weights:
                weights[t] += 0.4
        
        # Entities get highest weights
        entities = getattr(elite_nlp_data, 'entities', [])
        for ent in entities:
            # ent can be a dict or a spacy Span
            ent_text = ent.get('text', '') if isinstance(ent, dict) else str(ent)
            ent_tokens = ent_text.lower().split()
            for et in ent_tokens:
                if et in weights:
                    weights[et] += 0.5
        
        # Normalize weights to 0.0 - 1.0
        max_w = max(weights.values()) if weights else 1.0
        return {k: round(v/max_w, 2) for k, v in weights.items()}

    def explain_code(self, code: str, language: str = "python") -> str:
        """Generate a detailed explanation for code snippets"""
        # This will be used by brain.py calling specialized models
        self.add_step("Code Explanation", "Analyze", language, "Identifying logic structures and patterns in code")
        return f"This {language} snippet implements logic for..." # Placeholder

    def finalize_report(self, final_intent: str, confidence: float, sources: List[str]) -> Dict[str, Any]:
        """Finalize and return the XAI report as a dictionary"""
        if self.current_report:
            self.current_report.intent = final_intent
            self.current_report.confidence = confidence
            self.current_report.knowledge_sources = sources
            
            # Decide logic type based on intent
            if final_intent in ["calculation", "wolfram"]:
                self.current_report.logic_type = "Deductive / Mathematical"
            elif final_intent in ["rag", "search"]:
                self.current_report.logic_type = "Inductive / Evidence-based"
            else:
                self.current_report.logic_type = "Associative / Heuristic"

            return asdict(self.current_report)
        return {}

    def get_visual_trace(self) -> str:
        """Return a markdown-formatted string of the decision trace"""
        if not self._trace:
            return "No trace available."
            
        trace_str = "### 🧠 Maya Decision Trace\n"
        for i, step in enumerate(self._trace, 1):
            trace_str += f"{i}. **{step.step_name}**: {step.reasoning}\n"
        return trace_str

# Singleton
xai_engine = XAIEngine()
