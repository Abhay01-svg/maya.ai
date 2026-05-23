"""
Maya AI Models Module
Local model inference: Llama 3.2 3B, Qwen Coder, etc.
"""

import subprocess
import logging
import json
import time
from typing import Dict, List
from config import LLAMA_PATH, QWEN_PATH, BLACKBOX_PATH, DEBUG_MODE, MAYA_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class LocalModels:
    """Wrapper for local AI models"""
    
    def __init__(self):
        self.llama_path = LLAMA_PATH
        self.qwen_path = QWEN_PATH
        self.blackbox_path = BLACKBOX_PATH
        self.system_prompt = MAYA_SYSTEM_PROMPT
    
    # ==================== LLAMA 3.2 ====================
    
    def llama_inference(self, prompt: str, max_tokens: int = 256) -> str:
        """Run inference on Llama 3.2 3B"""
        try:
            # Prepend system prompt to guide identity and style
            full_prompt = f"{self.system_prompt}\n\nUser: {prompt}\nMaya AI:"
            
            # Try via Ollama (common local setup)
            cmd = [
                "ollama", "run", "llama3.2:3b",
                full_prompt
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                # Fallback: try direct model path
                return self._inference_direct(self.llama_path, prompt, max_tokens)
        
        except Exception as e:
            logger.error(f"❌ Llama inference error: {e}")
            return f"⚠️  Llama model error: {str(e)}"
    
    def llama_chat(self, messages: list) -> str:
        """Chat with Llama model"""
        try:
            # Format messages for chat
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            
            return self.llama_inference(prompt)
        except Exception as e:
            logger.error(f"❌ Llama chat error: {e}")
            return f"❌ Chat error: {str(e)}"
    
    # ==================== QWEN CODER ====================
    
    def qwen_code_generation(self, prompt: str, language: str = "python") -> str:
        """Generate code using Qwen Coder"""
        try:
            # Enhance prompt for coding
            full_prompt = f"""Generate only the code for this task. No explanations, no comments, no markdown formatting.

Task: {prompt}

Code only:"""
            
            cmd = [
                "ollama", "run", "qwen2.5-coder:3b",
                full_prompt
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                response = result.stdout.strip()
                # Remove markdown code blocks
                if response.startswith('```'):
                    lines = response.split('\n')
                    if len(lines) > 1:
                        # Remove first line (```python) and last line (```)
                        response = '\n'.join(lines[1:-1])
                return response.strip()
            else:
                return self._inference_direct(self.qwen_path, full_prompt)
        
        except Exception as e:
            logger.error(f"❌ Qwen code generation error: {e}")
            return f"❌ Code generation error: {str(e)}"
    
    def qwen_code_review(self, code: str) -> str:
        """Review code using Qwen"""
        try:
            prompt = f"""Review this code for issues, optimization, and best practices:

```
{code}
```

Provide constructive feedback."""
            
            return self.qwen_code_generation(prompt)
        except Exception as e:
            logger.error(f"❌ Qwen review error: {e}")
            return f"❌ Review error: {str(e)}"
    
    # ==================== MOONDREAM VISION ====================
    
    def vision_analysis(self, image_path: str, prompt: str = "Describe this image") -> str:
        """Analyze images using Moondream vision model"""
        try:
            full_prompt = f"Analyze this image: {prompt}"
            
            cmd = [
                "ollama", "run", "moondream:latest",
                full_prompt
            ]
            
            # For vision models, we need to handle image input differently
            # This is a simplified version - in production, you'd need proper image encoding
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"Moondream error: {result.stderr}")
                return "❌ Vision analysis failed"
        
        except Exception as e:
            logger.error(f"❌ Moondream error: {e}")
            return f"❌ Vision analysis error: {str(e)}"
    
    # ==================== BLACKBOX CLI ====================
    
    def blackbox_code_gen(self, prompt: str) -> str:
        """Generate code using Blackbox CLI"""
        try:
            # Using blackbox command line
            cmd = [self.blackbox_path, "generate"]
            
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"Blackbox error: {result.stderr}")
                return "❌ Blackbox generation failed"
        
        except Exception as e:
            logger.error(f"❌ Blackbox error: {e}")
            return f"❌ Blackbox error: {str(e)}"
    
    # ==================== GENERAL INFERENCE ====================
    
    def _inference_direct(self, model_path: str, prompt: str, max_tokens: int = 256) -> str:
        """Direct inference using model path"""
        try:
            # This is a placeholder for direct model loading
            # In production, use llama-cpp-python or similar
            logger.warning(f"⚠️  Using fallback inference for {model_path}")
            return f"[Model output would be generated by {model_path}]"
        except Exception as e:
            logger.error(f"❌ Direct inference error: {e}")
            return str(e)
    
    def smart_routing(self, prompt: str, task_type: str) -> str:
        """Route to appropriate model based on task"""
        result = {
            "model_used": None,
            "response": None,
            "tokens_used": 0,
            "time_taken": 0
        }
        
        try:
            start_time = time.time()
            
            if task_type == "coding":
                result["model_used"] = "Qwen Coder"
                result["response"] = self.qwen_code_generation(prompt)
            
            elif task_type == "code_review":
                result["model_used"] = "Qwen Coder"
                result["response"] = self.qwen_code_review(prompt)
            
            elif task_type == "vision":
                result["model_used"] = "Moondream"
                # Extract image path from prompt if provided
                try:
                    parts = prompt.split("|", 1)
                    if len(parts) == 2:
                        image_path, vision_prompt = parts
                        result["response"] = self.vision_analysis(image_path.strip(), vision_prompt.strip())
                    else:
                        result["response"] = self.vision_analysis(prompt)
                except:
                    result["response"] = self.vision_analysis(prompt)
            
            elif task_type == "general_chat":
                result["model_used"] = "Llama 3.2 3B"
                result["response"] = self.llama_inference(prompt)
            
            elif task_type == "chat":
                result["model_used"] = "Llama 3.2 3B"
                # Parse as messages if in chat format
                try:
                    messages = json.loads(prompt)
                    result["response"] = self.llama_chat(messages)
                except:
                    result["response"] = self.llama_inference(prompt)
            
            else:
                # Always use Llama for any general queries
                result["model_used"] = "Llama 3.2 3B"
                result["response"] = self.llama_inference(prompt)
            
            result["time_taken"] = time.time() - start_time
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Routing error: {e}")
            return {
                "model_used": None,
                "response": f"❌ Error: {str(e)}",
                "tokens_used": 0,
                "time_taken": 0
            }


class ModelCache:
    """Cache for model responses to reduce load"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
    
    def get(self, key: str):
        """Get cached response"""
        return self.cache.get(key)
    
    def set(self, key: str, value: str):
        """Cache response"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            self.cache.pop(next(iter(self.cache)))
        
        self.cache[key] = {
            "value": value,
            "timestamp": time.time()
        }
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()


# Initialize
local_models = LocalModels()
model_cache = ModelCache()

if DEBUG_MODE:
    print("🤖 Maya Local Models initialized")
