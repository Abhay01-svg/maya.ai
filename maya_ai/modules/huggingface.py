"""
Maya AI HuggingFace Integration
Connect to HuggingFace models for additional AI capabilities
"""

import requests
import json
import logging
from typing import Dict, List, Optional
from config import HF_API_KEY, DEBUG_MODE

logger = logging.getLogger(__name__)

class HuggingFaceAPI:
    """HuggingFace API integration for Maya AI"""
    
    def __init__(self):
        self.api_key = HF_API_KEY
        self.base_url = "https://api-inference.huggingface.co/models"
        self.hub_url = "https://huggingface.co/api"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Available models that should work
        self.available_models = {
            "text_generation": [
                "gpt2",
                "gpt2-medium", 
                "EleutherAI/gpt-neo-125M",
                "bigscience/bloom-560m"
            ],
            "text_classification": [
                "distilbert-base-uncased",
                "cardiffnlp/twitter-roberta-base-sentiment"
            ],
            "summarization": [
                "facebook/bart-large-cnn",
                "t5-small"
            ],
            "translation": [
                "Helsinki-NLP/opus-mt-en-fr",
                "Helsinki-NLP/opus-mt-en-es"
            ]
        }
        
        # Check if key is read-only
        self.is_read_only = self._check_key_permissions()
    
    def _check_key_permissions(self) -> bool:
        """Check if the API key is read-only"""
        try:
            # Try to access user info - this works with read keys
            response = requests.get(
                f"{self.hub_url}/whoami",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                user_data = response.json()
                # Check if user has inference permissions
                return not user_data.get("canPayForInference", False)
            return True
        except:
            return True
    
    def test_connection(self) -> Dict[str, any]:
        """Test if HuggingFace API is accessible and return capabilities"""
        try:
            result = {
                "connected": False,
                "can_inference": False,
                "can_read": False,
                "message": ""
            }
            
            # Test Hub API (works with read keys)
            response = requests.get(
                f"{self.hub_url}/whoami",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                result["connected"] = True
                result["can_read"] = True
                user_data = response.json()
                result["can_inference"] = user_data.get("canPayForInference", False)
                
                if self.is_read_only:
                    result["message"] = "Read-only key - limited to model information"
                else:
                    result["message"] = "Full access - inference available"
            else:
                result["message"] = "Invalid API key"
                
            return result
        except Exception as e:
            logger.error(f"❌ HuggingFace connection test failed: {e}")
            return {
                "connected": False,
                "can_inference": False,
                "can_read": False,
                "message": f"Connection failed: {str(e)}"
            }
    
    def generate_text(self, prompt: str, model: str = "gpt2", max_length: int = 100) -> str:
        """Generate text using HuggingFace models"""
        if self.is_read_only:
            return "❌ Text generation requires full access key (not read-only)"
        
        try:
            url = f"{self.base_url}/{model}"
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": max_length,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    return generated_text.replace(prompt, "").strip()
                else:
                    return str(result)
            else:
                logger.error(f"❌ HuggingFace API error: {response.status_code}")
                return f"❌ Model {model} not available or API error"
                
        except Exception as e:
            logger.error(f"❌ HuggingFace text generation error: {e}")
            return f"❌ Text generation failed: {str(e)}"
    
    def classify_text(self, text: str, model: str = "distilbert-base-uncased") -> Dict:
        """Classify text sentiment or categories"""
        try:
            url = f"{self.base_url}/{model}"
            payload = {"inputs": text}
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                logger.error(f"❌ HuggingFace classification error: {response.status_code}")
                return {"error": f"Model {model} not available"}
                
        except Exception as e:
            logger.error(f"❌ HuggingFace classification error: {e}")
            return {"error": str(e)}
    
    def summarize_text(self, text: str, model: str = "facebook/bart-large-cnn") -> str:
        """Summarize text using HuggingFace models"""
        try:
            url = f"{self.base_url}/{model}"
            payload = {"inputs": text, "parameters": {"max_length": 150}}
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("summary_text", text)
                else:
                    return str(result)
            else:
                logger.error(f"❌ HuggingFace summarization error: {response.status_code}")
                return f"❌ Summarization failed for model {model}"
                
        except Exception as e:
            logger.error(f"❌ HuggingFace summarization error: {e}")
            return f"❌ Summarization failed: {str(e)}"
    
    def translate_text(self, text: str, target_lang: str = "fr") -> str:
        """Translate text using HuggingFace models"""
        try:
            # Map language codes to models
            model_map = {
                "fr": "Helsinki-NLP/opus-mt-en-fr",
                "es": "Helsinki-NLP/opus-mt-en-es",
                "de": "Helsinki-NLP/opus-mt-en-de",
                "it": "Helsinki-NLP/opus-mt-en-it"
            }
            
            model = model_map.get(target_lang, "Helsinki-NLP/opus-mt-en-fr")
            url = f"{self.base_url}/{model}"
            payload = {"inputs": text}
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("translation_text", text)
                else:
                    return str(result)
            else:
                logger.error(f"❌ HuggingFace translation error: {response.status_code}")
                return f"❌ Translation failed for {target_lang}"
                
        except Exception as e:
            logger.error(f"❌ HuggingFace translation error: {e}")
            return f"❌ Translation failed: {str(e)}"
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models by category"""
        return self.available_models
    
    def get_model_info(self, model_id: str) -> Dict:
        """Get model information (works with read-only keys)"""
        try:
            url = f"{self.hub_url}/models/{model_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Model {model_id} not found"}
                
        except Exception as e:
            logger.error(f"❌ Model info error: {e}")
            return {"error": str(e)}
    
    def search_models(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for models (works with read-only keys)"""
        try:
            url = f"{self.hub_url}/models"
            params = {
                "search": query,
                "limit": limit,
                "sort": "downloads",
                "direction": "-1"
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ Model search error: {e}")
            return []
    
    def get_popular_models(self, category: str = "text-generation", limit: int = 10) -> List[Dict]:
        """Get popular models by category (works with read-only keys)"""
        try:
            url = f"{self.hub_url}/models"
            params = {
                "filter": category,
                "limit": limit,
                "sort": "downloads",
                "direction": "-1"
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ Popular models error: {e}")
            return []
    
    def smart_generate(self, prompt: str, task_type: str = "general") -> str:
        """Smart text generation based on task type"""
        if self.is_read_only:
            return f"❌ Text generation requires full access key. Current key is read-only. Get a full access key from HuggingFace to enable model inference."
        
        if task_type == "creative":
            return self.generate_text(prompt, "gpt2", max_length=150)
        elif task_type == "technical":
            return self.generate_text(prompt, "EleutherAI/gpt-neo-125M", max_length=200)
        elif task_type == "summary":
            return self.summarize_text(prompt)
        else:
            return self.generate_text(prompt, "gpt2", max_length=100)
    
    def get_status_info(self) -> Dict:
        """Get comprehensive status information"""
        connection_status = self.test_connection()
        
        return {
            "connection": connection_status,
            "key_type": "Read-only" if self.is_read_only else "Full access",
            "available_categories": list(self.available_models.keys()),
            "recommendations": self._get_recommendations()
        }
    
    def _get_recommendations(self) -> List[str]:
        """Get recommendations based on key type"""
        if self.is_read_only:
            return [
                "Get a full access HuggingFace key for model inference",
                "Current key allows model information and search",
                "Consider upgrading to unlock AI capabilities"
            ]
        else:
            return [
                "Full access available - can use model inference",
                "Try text generation with GPT-2 models",
                "Use classification and summarization features"
            ]


# Initialize HuggingFace API
huggingface_api = HuggingFaceAPI()

if DEBUG_MODE:
    print("🤗 HuggingFace API initialized")
    status = huggingface_api.get_status_info()
    print(f"📋 Status: {status['key_type']}")
    print(f"🔗 Connection: {status['connection']['message']}")
    if status['connection']['connected']:
        print("✅ HuggingFace API connection successful")
    else:
        print("⚠️  HuggingFace API connection failed")
