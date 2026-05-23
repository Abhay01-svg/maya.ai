"""
Maya AI Autonomous Brain System
Advanced multi-agent decision-making engine that intelligently routes tasks to best modules
"""

import logging
import time
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from config import DEBUG_MODE
from .tools import search_api, weather_api, news_api
from .brain import brain
from .memory import memory

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Task types for intelligent routing"""
    WEB_SEARCH = "web_search"
    DOCUMENT_ANALYSIS = "document_analysis"
    IMAGE_ANALYSIS = "image_analysis"
    NEWS_SEARCH = "news_search"
    IMAGE_GENERATION = "image_generation"
    CODE_EXECUTION = "code_execution"
    GENERAL_CHAT = "general_chat"
    CALCULATION = "calculation"
    WEATHER = "weather"
    MULTI_TOOL = "multi_tool"

@dataclass
class TaskAnalysis:
    """Task analysis result"""
    task_type: TaskType
    confidence: float
    modules_needed: List[str]
    priority: int
    estimated_time: float
    reasoning: str

class AutonomousDecisionEngine:
    """Central decision-making engine for intelligent task routing"""
    
    def __init__(self):
        self.start_time = time.time()
        self.task_count = 0
        self.active_modules = {
            'rag_search': True,
            'moondream': True,
            'image_generator': True,
            'brain_executor': True,
            'news_engine': True,
            'llama_verifier': True
        }
        
        # Task detection patterns
        self.task_patterns = {
            TaskType.WEB_SEARCH: [
                r'search for (.+)',
                r'find information about (.+)',
                r'what is (.+)',
                r'latest (.+)',
                r'current (.+)',
                r'research (.+)',
                r'look up (.+)',
                r'google (.+)'
            ],
            TaskType.DOCUMENT_ANALYSIS: [
                r'read (?:pdf|document|file) (.+)',
                r'summarize (?:pdf|document|file) (.+)',
                r'analyze (?:pdf|document|file) (.+)',
                r'extract from (.+)',
                r'interpret (.+)',
                r'uploaded (?:pdf|doc|txt) (.+)'
            ],
            TaskType.IMAGE_ANALYSIS: [
                r'analyze (?:image|picture|photo) (.+)',
                r'read (?:image|picture|photo) (.+)',
                r'ocr (?:image|picture|photo) (.+)',
                r'extract text from (?:image|picture|photo) (.+)',
                r'what do you see in (?:image|picture|photo) (.+)',
                r'describe (?:image|picture|photo) (.+)'
            ],
            TaskType.NEWS_SEARCH: [
                r'(?:today|latest|current) news',
                r'(?:news|headlines|updates)',
                r'(?:market|sports|politics) news',
                r'breaking news',
                r'current affairs',
                r'latest update',
                r'live market'
            ],
            TaskType.IMAGE_GENERATION: [
                r'generate (?:image|picture|photo) (.+)',
                r'create (?:logo|poster|art) (.+)',
                r'design (?:ui|mockup|concept) (.+)',
                r'make (?:image|picture|photo) (.+)',
                r'draw (.+)',
                r'visualize (.+)'
            ],
            TaskType.CODE_EXECUTION: [
                r'create (?:app|program|script|code) (.+)',
                r'build (?:app|program|script|code) (.+)',
                r'develop (?:app|program|script|code) (.+)',
                r'write (?:code|python|javascript) (.+)',
                r'automate (.+)',
                r'script (.+)',
                r'calculate (.+)',
                r'math (.+)'
            ]
        }
        
        if DEBUG_MODE:
            logger.info("🧠 Autonomous Decision Engine initialized")
    
    def analyze_task(self, user_input: str, context: Dict = None) -> TaskAnalysis:
        """Analyze user input and determine best routing strategy"""
        self.task_count += 1
        start_time = time.time()
        
        user_input_lower = user_input.lower().strip()
        
        # Check for multi-tool tasks
        multi_tool_score = self._detect_multi_tool_task(user_input_lower)
        
        # Analyze each task type
        task_scores = {}
        for task_type, patterns in self.task_patterns.items():
            score = 0
            matched_patterns = []
            
            for pattern in patterns:
                if re.search(pattern, user_input_lower, re.IGNORECASE):
                    score += 1
                    matched_patterns.append(pattern)
            
            if score > 0:
                task_scores[task_type] = {
                    'score': score,
                    'patterns': matched_patterns,
                    'confidence': min(score / len(patterns), 1.0)
                }
        
        # Determine primary task type
        if multi_tool_score > 0.7:
            primary_task = TaskType.MULTI_TOOL
            confidence = multi_tool_score
            modules_needed = self._get_modules_for_multi_tool(user_input_lower)
        elif task_scores:
            primary_task = max(task_scores.keys(), key=lambda k: task_scores[k]['score'])
            confidence = task_scores[primary_task]['confidence']
            modules_needed = self._get_modules_for_task(primary_task)
        else:
            primary_task = TaskType.GENERAL_CHAT
            confidence = 0.5
            modules_needed = ['llama_verifier']
        
        # Calculate priority and estimated time
        priority = self._calculate_priority(primary_task, user_input_lower)
        estimated_time = self._estimate_time(primary_task, user_input_lower)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(primary_task, task_scores, user_input_lower)
        
        analysis_time = time.time() - start_time
        
        if DEBUG_MODE:
            logger.info(f"🎯 Task analyzed: {primary_task.value} (confidence: {confidence:.2f})")
            logger.info(f"⏱️  Analysis time: {analysis_time:.3f}s")
        
        return TaskAnalysis(
            task_type=primary_task,
            confidence=confidence,
            modules_needed=modules_needed,
            priority=priority,
            estimated_time=estimated_time,
            reasoning=reasoning
        )
    
    def _detect_multi_tool_task(self, user_input: str) -> float:
        """Detect if task requires multiple tools"""
        multi_tool_indicators = [
            r'compare (.+) with (.+)',
            r'analyze (.+) and (.+)',
            r'combine (.+) with (.+)',
            r'integrate (.+) and (.+)',
            r'summarize (.+) and research (.+)',
            r'create (.+) using (.+)'
        ]
        
        score = 0
        for indicator in multi_tool_indicators:
            if re.search(indicator, user_input, re.IGNORECASE):
                score += 0.3
        
        # Check for complex keywords
        complex_keywords = ['compare', 'combine', 'integrate', 'analyze and', 'research and']
        for keyword in complex_keywords:
            if keyword in user_input:
                score += 0.2
        
        return min(score, 1.0)
    
    def _get_modules_for_task(self, task_type: TaskType) -> List[str]:
        """Get required modules for task type"""
        module_mapping = {
            TaskType.WEB_SEARCH: ['rag_search', 'llama_verifier'],
            TaskType.DOCUMENT_ANALYSIS: ['moondream', 'llama_verifier'],
            TaskType.IMAGE_ANALYSIS: ['moondream', 'llama_verifier'],
            TaskType.NEWS_SEARCH: ['news_engine', 'rag_search', 'llama_verifier'],
            TaskType.IMAGE_GENERATION: ['image_generator', 'llama_verifier'],
            TaskType.CODE_EXECUTION: ['brain_executor', 'llama_verifier'],
            TaskType.GENERAL_CHAT: ['llama_verifier'],
            TaskType.CALCULATION: ['brain_executor'],
            TaskType.WEATHER: ['brain_executor'],
            TaskType.MULTI_TOOL: []  # Will be determined separately
        }
        return module_mapping.get(task_type, ['llama_verifier'])
    
    def _get_modules_for_multi_tool(self, user_input: str) -> List[str]:
        """Determine modules needed for multi-tool tasks"""
        modules = set()
        
        # Check for document + web search combination
        if any(word in user_input for word in ['pdf', 'document', 'file']):
            modules.add('moondream')
        if any(word in user_input for word in ['search', 'research', 'latest', 'compare']):
            modules.add('rag_search')
        
        # Check for image + analysis
        if any(word in user_input for word in ['image', 'picture', 'photo']):
            modules.add('moondream')
        
        # Always include verifier
        modules.add('llama_verifier')
        
        return list(modules)
    
    def _calculate_priority(self, task_type: TaskType, user_input: str) -> int:
        """Calculate task priority (1=highest, 5=lowest)"""
        urgent_keywords = ['urgent', 'emergency', 'asap', 'immediately']
        if any(keyword in user_input.lower() for keyword in urgent_keywords):
            return 1
        
        priority_mapping = {
            TaskType.CODE_EXECUTION: 2,
            TaskType.WEB_SEARCH: 2,
            TaskType.NEWS_SEARCH: 2,
            TaskType.DOCUMENT_ANALYSIS: 3,
            TaskType.IMAGE_ANALYSIS: 3,
            TaskType.IMAGE_GENERATION: 4,
            TaskType.MULTI_TOOL: 2,
            TaskType.GENERAL_CHAT: 5
        }
        
        return priority_mapping.get(task_type, 5)
    
    def _estimate_time(self, task_type: TaskType, user_input: str) -> float:
        """Estimate task completion time in seconds"""
        time_mapping = {
            TaskType.WEB_SEARCH: 5.0,
            TaskType.DOCUMENT_ANALYSIS: 10.0,
            TaskType.IMAGE_ANALYSIS: 8.0,
            TaskType.NEWS_SEARCH: 6.0,
            TaskType.IMAGE_GENERATION: 15.0,
            TaskType.CODE_EXECUTION: 12.0,
            TaskType.GENERAL_CHAT: 3.0,
            TaskType.CALCULATION: 2.0,
            TaskType.WEATHER: 3.0,
            TaskType.MULTI_TOOL: 20.0
        }
        
        base_time = time_mapping.get(task_type, 5.0)
        
        # Adjust based on complexity
        if len(user_input) > 100:
            base_time *= 1.5
        if 'detailed' in user_input.lower() or 'comprehensive' in user_input.lower():
            base_time *= 1.3
        
        return base_time
    
    def _generate_reasoning(self, primary_task: TaskType, task_scores: Dict, user_input: str) -> str:
        """Generate reasoning for task selection"""
        reasoning_parts = []
        
        # Primary task reasoning
        if primary_task == TaskType.MULTI_TOOL:
            reasoning_parts.append("Multi-tool task detected requiring multiple modules")
        elif task_scores.get(primary_task):
            patterns = task_scores[primary_task]['patterns']
            reasoning_parts.append(f"Detected patterns: {', '.join(patterns[:2])}")
        
        # Context reasoning
        if any(word in user_input.lower() for word in ['urgent', 'quickly']):
            reasoning_parts.append("High priority task detected")
        
        if len(user_input) > 50:
            reasoning_parts.append("Complex query requiring detailed processing")
        
        return "; ".join(reasoning_parts) if reasoning_parts else "General chat request"

class AutonomousTaskExecutor:
    """Execute tasks using appropriate modules"""
    
    def __init__(self):
        self.decision_engine = AutonomousDecisionEngine()
        self.execution_history = []
        
        if DEBUG_MODE:
            logger.info("🚀 Autonomous Task Executor initialized")
    
    def execute_task(self, user_input: str, context: Dict = None) -> Dict:
        """Execute task using intelligent routing"""
        start_time = time.time()
        
        # Analyze task
        analysis = self.decision_engine.analyze_task(user_input, context)
        
        # Execute based on task type
        result = self._execute_by_task_type(analysis, user_input, context)
        
        # Verify with Llama
        if 'llama_verifier' in analysis.modules_needed:
            result = self._verify_with_llama(result, user_input)
        
        # Record execution
        execution_time = time.time() - start_time
        self.execution_history.append({
            'task': user_input,
            'analysis': analysis,
            'result': result,
            'execution_time': execution_time,
            'timestamp': time.time()
        })
        
        return result
    
    def _execute_by_task_type(self, analysis: TaskAnalysis, user_input: str, context: Dict) -> Dict:
        """Execute task based on determined type"""
        task_type = analysis.task_type
        
        try:
            if task_type == TaskType.WEB_SEARCH:
                return self._execute_web_search(user_input, analysis)
            elif task_type == TaskType.DOCUMENT_ANALYSIS:
                return self._execute_document_analysis(user_input, analysis, context)
            elif task_type == TaskType.IMAGE_ANALYSIS:
                return self._execute_image_analysis(user_input, analysis, context)
            elif task_type == TaskType.NEWS_SEARCH:
                return self._execute_news_search(user_input, analysis)
            elif task_type == TaskType.IMAGE_GENERATION:
                return self._execute_image_generation(user_input, analysis)
            elif task_type == TaskType.CODE_EXECUTION:
                return self._execute_code_execution(user_input, analysis)
            elif task_type == TaskType.MULTI_TOOL:
                return self._execute_multi_tool(user_input, analysis, context)
            else:
                return self._execute_general_chat(user_input, analysis)
        
        except Exception as e:
            logger.error(f"❌ Task execution error: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_type': task_type.value,
                'response': f"❌ Error executing {task_type.value}: {str(e)}"
            }
    
    def _execute_web_search(self, user_input: str, analysis: TaskAnalysis) -> Dict:
        """Execute web search with RAG"""
        try:
            # Extract search query
            search_query = self._extract_search_query(user_input)
            
            # Perform search
            search_results = search_api.get_hinglish_search(search_query, limit=5)
            
            # Process and summarize
            summary = self._summarize_search_results(search_results, search_query)
            
            return {
                'success': True,
                'task_type': TaskType.WEB_SEARCH.value,
                'modules_used': ['rag_search'],
                'search_query': search_query,
                'results': search_results,
                'summary': summary,
                'response': summary
            }
        
        except Exception as e:
            return {
                'success': False,
                'task_type': TaskType.WEB_SEARCH.value,
                'error': str(e),
                'response': f"❌ Web search failed: {str(e)}"
            }
    
    def _execute_document_analysis(self, user_input: str, analysis: TaskAnalysis, context: Dict) -> Dict:
        """Execute document analysis using Moondream"""
        try:
            # Get file path from context or upload
            file_path = context.get('file_path') if context else None
            
            if not file_path:
                return {
                    'success': False,
                    'task_type': TaskType.DOCUMENT_ANALYSIS.value,
                    'error': 'No file provided',
                    'response': '❌ Please upload a PDF or document to analyze'
                }
            
            # Use Moondream for analysis
            analysis_prompt = f"Analyze this document: {user_input}"
            
            # This would integrate with Moondream
            # For now, return placeholder
            return {
                'success': True,
                'task_type': TaskType.DOCUMENT_ANALYSIS.value,
                'modules_used': ['moondream'],
                'file_path': file_path,
                'analysis': analysis_prompt,
                'response': f"📄 Document analysis for '{file_path}' - {analysis_prompt}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'task_type': TaskType.DOCUMENT_ANALYSIS.value,
                'error': str(e),
                'response': f"❌ Document analysis failed: {str(e)}"
            }
    
    def _execute_image_analysis(self, user_input: str, analysis: TaskAnalysis, context: Dict) -> Dict:
        """Execute image analysis using Moondream"""
        try:
            # Get image path from context or upload
            image_path = context.get('image_path') if context else None
            
            if not image_path:
                return {
                    'success': False,
                    'task_type': TaskType.IMAGE_ANALYSIS.value,
                    'error': 'No image provided',
                    'response': '❌ Please upload an image to analyze'
                }
            
            # Use Moondream for image analysis
            analysis_prompt = f"Analyze this image: {user_input}"
            
            # This would integrate with Moondream
            return {
                'success': True,
                'task_type': TaskType.IMAGE_ANALYSIS.value,
                'modules_used': ['moondream'],
                'image_path': image_path,
                'analysis': analysis_prompt,
                'response': f"🖼️ Image analysis for '{image_path}' - {analysis_prompt}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'task_type': TaskType.IMAGE_ANALYSIS.value,
                'error': str(e),
                'response': f"❌ Image analysis failed: {str(e)}"
            }
    
    def _execute_news_search(self, user_input: str, analysis: TaskAnalysis) -> Dict:
        """Execute latest news search"""
        try:
            # Extract news topic
            news_topic = self._extract_news_topic(user_input)
            
            # Get latest news
            news_results = news_api.get_hinglish_news(news_topic, limit=5)
            
            # Process and summarize
            summary = self._summarize_news_results(news_results, news_topic)
            
            return {
                'success': True,
                'task_type': TaskType.NEWS_SEARCH.value,
                'modules_used': ['news_engine', 'rag_search'],
                'news_topic': news_topic,
                'results': news_results,
                'summary': summary,
                'response': summary
            }
        
        except Exception as e:
            return {
                'success': False,
                'task_type': TaskType.NEWS_SEARCH.value,
                'error': str(e),
                'response': f"❌ News search failed: {str(e)}"
            }
    
    def _execute_image_generation(self, user_input: str, analysis: TaskAnalysis) -> Dict:
        """Execute image generation"""
        try:
            # Extract image generation prompt
            generation_prompt = self._extract_generation_prompt(user_input)
            
            # This would integrate with image generation model
            # For now, return placeholder
            return {
                'success': True,
                'task_type': TaskType.IMAGE_GENERATION.value,
                'modules_used': ['image_generator'],
                'prompt': generation_prompt,
                'response': f"🎨 Image generation prompt: '{generation_prompt}'"
            }
        
        except Exception as e:
            return {
                'success': False,
                'task_type': TaskType.IMAGE_GENERATION.value,
                'error': str(e),
                'response': f"❌ Image generation failed: {str(e)}"
            }
    
    def _execute_code_execution(self, user_input: str, analysis: TaskAnalysis) -> Dict:
        """Execute code/automation tasks using brain.py"""
        try:
            # Use existing brain system
            result = brain.process_query(user_input)
            
            return {
                'success': result.get('success', False),
                'task_type': TaskType.CODE_EXECUTION.value,
                'modules_used': ['brain_executor'],
                'brain_result': result,
                'response': result.get('hinglish_response', result.get('response', '❌ No response'))
            }
        
        except Exception as e:
            return {
                'success': False,
                'task_type': TaskType.CODE_EXECUTION.value,
                'error': str(e),
                'response': f"❌ Code execution failed: {str(e)}"
            }
    
    def _execute_multi_tool(self, user_input: str, analysis: TaskAnalysis, context: Dict) -> Dict:
        """Execute multi-tool tasks"""
        try:
            results = []
            modules_used = []
            
            # Execute each required module
            for module in analysis.modules_needed:
                if module == 'rag_search':
                    search_result = self._execute_web_search(user_input, analysis)
                    results.append(search_result)
                    modules_used.append('rag_search')
                
                elif module == 'moondream':
                    if context and context.get('file_path'):
                        doc_result = self._execute_document_analysis(user_input, analysis, context)
                        results.append(doc_result)
                    elif context and context.get('image_path'):
                        img_result = self._execute_image_analysis(user_input, analysis, context)
                        results.append(img_result)
                    modules_used.append('moondream')
                
                elif module == 'news_engine':
                    news_result = self._execute_news_search(user_input, analysis)
                    results.append(news_result)
                    modules_used.append('news_engine')
            
            # Combine results
            combined_response = self._combine_multi_tool_results(results, user_input)
            
            return {
                'success': True,
                'task_type': TaskType.MULTI_TOOL.value,
                'modules_used': modules_used,
                'individual_results': results,
                'combined_response': combined_response,
                'response': combined_response
            }
        
        except Exception as e:
            return {
                'success': False,
                'task_type': TaskType.MULTI_TOOL.value,
                'error': str(e),
                'response': f"❌ Multi-tool execution failed: {str(e)}"
            }
    
    def _execute_general_chat(self, user_input: str, analysis: TaskAnalysis) -> Dict:
        """Execute general chat using Llama"""
        try:
            # Use existing brain system for general chat
            result = brain.process_query(user_input)
            
            return {
                'success': result.get('success', False),
                'task_type': TaskType.GENERAL_CHAT.value,
                'modules_used': ['llama_verifier'],
                'brain_result': result,
                'response': result.get('hinglish_response', result.get('response', '❌ No response'))
            }
        
        except Exception as e:
            return {
                'success': False,
                'task_type': TaskType.GENERAL_CHAT.value,
                'error': str(e),
                'response': f"❌ General chat failed: {str(e)}"
            }
    
    def _verify_with_llama(self, result: Dict, original_input: str) -> Dict:
        """Verify and enhance response with Llama"""
        try:
            verification_prompt = f"""
            Original request: {original_input}
            Generated response: {result.get('response', '')}
            
            Please verify this response is accurate, complete, and helpful. 
            If it needs improvement, provide a better version.
            Keep responses in Hinglish style.
            """
            
            # Use Llama for verification
            verification_result = brain.process_query(verification_prompt)
            
            if verification_result.get('success'):
                verified_response = verification_result.get('hinglish_response', verification_result.get('response', ''))
                result['verified_response'] = verified_response
                result['llama_verified'] = True
                result['response'] = verified_response  # Use verified response as primary
            else:
                result['llama_verified'] = False
                result['verified_response'] = result.get('response')
        
        except Exception as e:
            logger.error(f"❌ Llama verification error: {e}")
            result['llama_verified'] = False
            result['verified_response'] = result.get('response')
        
        return result
    
    def _extract_search_query(self, user_input: str) -> str:
        """Extract search query from user input"""
        patterns = [
            r'search for (.+)',
            r'find information about (.+)',
            r'what is (.+)',
            r'latest (.+)',
            r'current (.+)',
            r'research (.+)',
            r'look up (.+)',
            r'google (.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return user_input
    
    def _extract_news_topic(self, user_input: str) -> str:
        """Extract news topic from user input"""
        if any(word in user_input.lower() for word in ['today news', 'latest news', 'current news']):
            return 'latest'
        
        patterns = [
            r'(?:market|sports|politics|tech|science) news',
            r'news about (.+)',
            r'latest (.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                return match.group(1).strip() if match.groups() else match.group(0).strip()
        
        return 'latest'
    
    def _extract_generation_prompt(self, user_input: str) -> str:
        """Extract image generation prompt from user input"""
        patterns = [
            r'generate (?:image|picture|photo) (.+)',
            r'create (?:logo|poster|art) (.+)',
            r'design (?:ui|mockup|concept) (.+)',
            r'make (?:image|picture|photo) (.+)',
            r'draw (.+)',
            r'visualize (.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return user_input
    
    def _summarize_search_results(self, results: str, query: str) -> str:
        """Summarize search results"""
        if not results or results.startswith('❌'):
            return f"❌ '{query}' ke search results nahi mile"
        
        return results  # Already formatted in Hinglish
    
    def _summarize_news_results(self, results: str, topic: str) -> str:
        """Summarize news results"""
        if not results or results.startswith('❌'):
            return f"❌ '{topic}' ki news nahi mili"
        
        return results  # Already formatted in Hinglish
    
    def _combine_multi_tool_results(self, results: List[Dict], user_input: str) -> str:
        """Combine results from multiple tools"""
        combined_parts = []
        
        for result in results:
            if result.get('success'):
                response = result.get('response', '')
                if response and not response.startswith('❌'):
                    combined_parts.append(response)
        
        if combined_parts:
            return '\n\n'.join(combined_parts)
        else:
            return f"❌ Multi-tool task failed: {user_input}"

# Global autonomous brain instance
autonomous_brain = AutonomousTaskExecutor()
