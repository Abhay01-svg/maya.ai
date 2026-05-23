"""
Groq API Integration Module
Cloud-based LLM fallback when local models fail
Uses Groq for ultra-fast inference as ultimate fallback
"""

import logging
from typing import Optional, List, Dict, Any
import time

logger = logging.getLogger(__name__)

class GroqAPI:
    """Groq Cloud API Integration for fallback inference"""
    
    def __init__(self, api_key: str):
        """
        Initialize Groq API client
        
        Args:
            api_key: Groq API key
        """
        self.api_key = api_key
        self.is_available = False
        self.client = None
        self.model = "llama-3.3-70b-versatile"  # Fast and capable model
        self.timeout = 30
        
        if not api_key:
            logger.warning("⚠️ Groq API key not configured, Groq fallback disabled")
            return
        
        try:
            from groq import Groq
            self.client = Groq(api_key=api_key)
            self.is_available = True
            logger.info("✅ Groq API client initialized and ready as fallback")
        except ImportError:
            logger.warning("⚠️ groq library not installed. Install with: pip install groq")
            self.is_available = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize Groq: {e}")
            self.is_available = False
    
    def is_ready(self) -> bool:
        """Check if Groq API is ready to use"""
        return self.is_available and self.client is not None and bool(self.api_key)
    
    def infer(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Run inference on Groq (fallback for general text generation)
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
        
        Returns:
            Generated text or error message
        """
        if not self.is_ready():
            return "❌ Groq API not available"
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=self.timeout
            )
            
            elapsed_time = time.time() - start_time
            result = response.choices[0].message.content
            
            logger.info(f"✅ Groq inference successful ({elapsed_time:.2f}s): {len(result)} chars")
            return result
            
        except Exception as e:
            logger.error(f"❌ Groq inference error: {e}")
            return f"❌ Groq API error: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 512, 
             temperature: float = 0.7) -> str:
        """
        Chat interface for Groq
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Chat response or error message
        """
        if not self.is_ready():
            return "❌ Groq API not available"
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=self.timeout
            )
            
            elapsed_time = time.time() - start_time
            result = response.choices[0].message.content
            
            logger.info(f"✅ Groq chat successful ({elapsed_time:.2f}s)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Groq chat error: {e}")
            return f"❌ Groq chat error: {str(e)}"
    
    def code_generation(self, prompt: str, language: str = "python") -> str:
        """
        Generate code using Groq (fallback for Qwen)
        
        Args:
            prompt: Code generation prompt
            language: Programming language
        
        Returns:
            Generated code or error message
        """
        if not self.is_ready():
            return "❌ Groq API not available"
        
        try:
            enhanced_prompt = f"""Generate only {language} code for this task. No explanations, no comments, no markdown.

Task: {prompt}

Code:"""
            
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                model=self.model,
                max_tokens=1024,
                temperature=0.3,  # Lower temperature for code
                timeout=self.timeout
            )
            
            elapsed_time = time.time() - start_time
            code = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if code.startswith('```'):
                lines = code.split('\n')
                if len(lines) > 1:
                    code = '\n'.join(lines[1:-1]) if lines[-1].strip() == '```' else '\n'.join(lines[1:])
            
            logger.info(f"✅ Groq code generation successful ({elapsed_time:.2f}s)")
            return code
            
        except Exception as e:
            logger.error(f"❌ Groq code generation error: {e}")
            return f"❌ Code generation error: {str(e)}"
    
    def analysis(self, text: str, analysis_type: str = "general") -> str:
        """
        Analyze text using Groq (fallback for vision/document analysis)
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis (general, summary, sentiment, etc.)
        
        Returns:
            Analysis result or error message
        """
        if not self.is_ready():
            return "❌ Groq API not available"
        
        try:
            prompt = f"""Perform a {analysis_type} analysis of the following text:

{text}

Provide concise, actionable analysis:"""
            
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                max_tokens=1024,
                temperature=0.5,
                timeout=self.timeout
            )
            
            elapsed_time = time.time() - start_time
            result = response.choices[0].message.content
            
            logger.info(f"✅ Groq analysis successful ({elapsed_time:.2f}s)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Groq analysis error: {e}")
            return f"❌ Analysis error: {str(e)}"
    
    def qa(self, question: str, context: Optional[str] = None) -> str:
        """
        Question-answering using Groq
        
        Args:
            question: The question to answer
            context: Optional context for better answers
        
        Returns:
            Answer or error message
        """
        if not self.is_ready():
            return "❌ Groq API not available"
        
        try:
            if context:
                prompt = f"""Based on the following context, answer the question:

Context:
{context}

Question: {question}

Answer:"""
            else:
                prompt = f"Answer this question: {question}"
            
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                max_tokens=512,
                temperature=0.5,
                timeout=self.timeout
            )
            
            elapsed_time = time.time() - start_time
            answer = response.choices[0].message.content
            
            logger.info(f"✅ Groq Q&A successful ({elapsed_time:.2f}s)")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Groq Q&A error: {e}")
            return f"❌ Q&A error: {str(e)}"
    
    def set_model(self, model_name: str) -> None:
        """
        Change the Groq model being used
        
        Available models:
        - mixtral-8x7b-32768 (default, balanced)
        - gemma-7b-it (lighter, faster)
        - llama2-70b-4096 (larger, more capable)
        
        Args:
            model_name: Name of the model to use
        """
        self.model = model_name
        logger.info(f"🔄 Switched Groq model to: {model_name}")


# Global Groq instance
def get_groq_client(api_key: str) -> Optional[GroqAPI]:
    """Factory function to create and return Groq client"""
    if not api_key:
        return None
    return GroqAPI(api_key)
