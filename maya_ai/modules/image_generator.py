"""
Maya AI Image Generation Module
Advanced AI image creation with multiple styles and techniques
"""

import logging
import time
import os
import json
import base64
from typing import Dict, List, Optional, Union
from pathlib import Path
import uuid
import subprocess
from io import BytesIO

# Image processing
try:
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    IMAGE_AVAILABLE = True
except ImportError:
    IMAGE_AVAILABLE = False
    logging.warning("⚠️  Image processing libraries not available")

from config import DEBUG_MODE

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Advanced AI image generation system"""
    
    def __init__(self):
        self.output_dir = Path("generated_images")
        self.output_dir.mkdir(exist_ok=True)
        
        # Generation styles
        self.styles = {
            'realistic': 'photorealistic, high detail, professional photography',
            'artistic': 'digital art, artistic, creative, masterpiece',
            'logo': 'minimalist logo, vector design, clean lines, professional',
            'poster': 'movie poster style, dramatic lighting, cinematic',
            'cartoon': 'cartoon style, animated, colorful, fun',
            'abstract': 'abstract art, geometric patterns, modern art',
            'portrait': 'portrait photography, realistic face, detailed features',
            'landscape': 'landscape photography, nature, scenic, beautiful',
            'ui': 'UI design, modern interface, clean design, user interface',
            'concept': 'concept art, futuristic, sci-fi, detailed concept'
        }
        
        # Quality presets
        self.quality_presets = {
            'fast': {'steps': 20, 'size': (512, 512)},
            'medium': {'steps': 30, 'size': (768, 768)},
            'high': {'steps': 50, 'size': (1024, 1024)},
            'ultra': {'steps': 100, 'size': (1024, 1024)}
        }
        
        # Available models (check what's installed)
        self.available_models = self._check_available_models()
        
        if DEBUG_MODE:
            logger.info("🎨 Image Generator initialized")
            logger.info(f"📁 Output directory: {self.output_dir}")
            logger.info(f"🤖 Available models: {list(self.available_models.keys())}")
    
    def _check_available_models(self) -> Dict:
        """Check which image generation models are available"""
        models = {}
        
        # Check for Stable Diffusion (most common)
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
            if 'stability' in result.stdout.lower() or 'diffusion' in result.stdout.lower():
                models['stable_diffusion'] = 'ollama'
        except:
            pass
        
        # Check for other common models
        common_models = ['stability-ai/sdxl', 'runwayml/stable-diffusion-v1-5']
        for model in common_models:
            try:
                result = subprocess.run(['ollama', 'show', model], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    models[model] = 'ollama'
            except:
                continue
        
        # Fallback to placeholder if no models found
        if not models:
            models['placeholder'] = 'mock'
            logger.warning("⚠️  No image generation models found, using placeholder")
        
        return models
    
    def generate_image(self, prompt: str, style: str = 'realistic', 
                      quality: str = 'medium', model: str = None) -> Dict:
        """Generate AI image from prompt"""
        start_time = time.time()
        
        try:
            # Validate inputs
            if not prompt or len(prompt.strip()) < 3:
                return {
                    'success': False,
                    'error': 'Prompt too short',
                    'response': '❌ Prompt kam se kam 3 characters ka hona chahiye'
                }
            
            # Get model
            if not model:
                model = list(self.available_models.keys())[0]
            
            if model not in self.available_models:
                return {
                    'success': False,
                    'error': f'Model {model} not available',
                    'response': f"❌ Model '{model}' available nahi hai"
                }
            
            # Enhance prompt with style
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            # Get quality settings
            quality_settings = self.quality_presets.get(quality, self.quality_presets['medium'])
            
            # Generate image
            generation_result = self._generate_with_model(enhanced_prompt, model, quality_settings)
            
            if not generation_result['success']:
                return generation_result
            
            # Save image
            saved_image = self._save_generated_image(generation_result['image'], prompt, style)
            
            generation_time = time.time() - start_time
            
            return {
                'success': True,
                'prompt': prompt,
                'enhanced_prompt': enhanced_prompt,
                'style': style,
                'quality': quality,
                'model': model,
                'model_backend': self.available_models[model],
                'image_path': saved_image['path'],
                'image_filename': saved_image['filename'],
                'image_size': saved_image['size'],
                'generation_time': generation_time,
                'response': f"🎨 Image generated successfully!\n📁 Saved as: {saved_image['filename']}\n⏱️  Time: {generation_time:.2f}s"
            }
            
        except Exception as e:
            logger.error(f"❌ Image generation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ Image generation mein error: {str(e)}"
            }
    
    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt with style and quality keywords"""
        style_keywords = self.styles.get(style, self.styles['realistic'])
        
        # Build enhanced prompt
        enhanced_parts = [
            prompt.strip(),
            style_keywords,
            'high quality',
            'detailed',
            'professional'
        ]
        
        # Add specific style enhancements
        if style == 'logo':
            enhanced_parts.extend(['vector design', 'scalable', 'clean'])
        elif style == 'portrait':
            enhanced_parts.extend(['realistic face', 'detailed features', 'natural lighting'])
        elif style == 'landscape':
            enhanced_parts.extend(['scenic', 'beautiful', 'nature'])
        elif style == 'ui':
            enhanced_parts.extend(['modern interface', 'clean design', 'user-friendly'])
        
        return ', '.join(enhanced_parts)
    
    def _generate_with_model(self, prompt: str, model: str, quality_settings: Dict) -> Dict:
        """Generate image using specified model"""
        try:
            if self.available_models[model] == 'mock':
                return self._generate_mock_image(prompt, quality_settings)
            elif self.available_models[model] == 'ollama':
                return self._generate_with_ollama(prompt, model, quality_settings)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported model backend: {self.available_models[model]}'
                }
        
        except Exception as e:
            logger.error(f"❌ Model generation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_mock_image(self, prompt: str, quality_settings: Dict) -> Dict:
        """Generate mock image for testing"""
        try:
            if not IMAGE_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Image processing libraries not available'
                }
            
            # Create a simple placeholder image
            size = quality_settings['size']
            image = Image.new('RGB', size, color=(100, 150, 200))
            
            # Add text
            draw = ImageDraw.Draw(image)
            
            # Try to load font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Add prompt text
            text_lines = self._wrap_text(prompt, 40)
            y_position = 50
            
            for line in text_lines[:5]:  # Limit to 5 lines
                draw.text((50, y_position), line, fill=(255, 255, 255), font=font)
                y_position += 30
            
            return {
                'success': True,
                'image': image,
                'method': 'mock'
            }
            
        except Exception as e:
            logger.error(f"❌ Mock image generation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_with_ollama(self, prompt: str, model: str, quality_settings: Dict) -> Dict:
        """Generate image using Ollama model"""
        try:
            # This would integrate with actual image generation model
            # For now, return mock as placeholder
            logger.warning("⚠️  Ollama image generation not fully implemented, using mock")
            return self._generate_mock_image(prompt, quality_settings)
            
        except Exception as e:
            logger.error(f"❌ Ollama generation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _wrap_text(self, text: str, max_length: int) -> List[str]:
        """Wrap text to fit within max length"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_length:
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _save_generated_image(self, image, prompt: str, style: str) -> Dict:
        """Save generated image to file"""
        try:
            # Generate unique filename
            timestamp = int(time.time())
            safe_prompt = "".join(c for c in prompt[:20] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"img_{timestamp}_{safe_prompt}_{style}.png"
            
            # Ensure filename is safe
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
            
            filepath = self.output_dir / filename
            
            # Save image
            image.save(filepath, 'PNG', quality=95)
            
            # Get image info
            if hasattr(image, 'size'):
                size = image.size
            else:
                size = (0, 0)
            
            return {
                'path': str(filepath),
                'filename': filename,
                'size': size,
                'file_size': os.path.getsize(filepath)
            }
            
        except Exception as e:
            logger.error(f"❌ Image save error: {e}")
            return {
                'path': '',
                'filename': '',
                'size': (0, 0)
            }
    
    def batch_generate(self, prompts: List[str], style: str = 'realistic', 
                      quality: str = 'medium') -> Dict:
        """Generate multiple images in batch"""
        try:
            batch_results = []
            total_time = 0
            
            for i, prompt in enumerate(prompts):
                if i >= 5:  # Limit batch size
                    break
                
                result = self.generate_image(prompt, style, quality)
                batch_results.append(result)
                total_time += result.get('generation_time', 0)
            
            # Generate batch summary
            successful = [r for r in batch_results if r['success']]
            failed = [r for r in batch_results if not r['success']]
            
            summary = f"🎨 Batch Generation Summary:\n"
            summary += f"• Total prompts: {len(prompts)}\n"
            summary += f"• Successful: {len(successful)}\n"
            summary += f"• Failed: {len(failed)}\n"
            summary += f"• Total time: {total_time:.2f}s\n"
            
            if successful:
                summary += f"• Average time: {total_time/len(successful):.2f}s per image\n"
            
            return {
                'success': True,
                'batch_results': batch_results,
                'summary': summary,
                'total_prompts': len(prompts),
                'successful': len(successful),
                'failed': len(failed),
                'total_time': total_time,
                'response': summary
            }
            
        except Exception as e:
            logger.error(f"❌ Batch generation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ Batch generation failed: {str(e)}"
            }
    
    def create_logo(self, company_name: str, industry: str = 'technology', 
                   colors: List[str] = None) -> Dict:
        """Generate professional logo"""
        try:
            # Build logo-specific prompt
            logo_prompt = f"minimalist logo for {company_name}"
            
            if industry:
                logo_prompt += f" {industry} company"
            
            logo_prompt += " clean design professional vector logo"
            
            if colors:
                logo_prompt += f" colors: {', '.join(colors)}"
            
            return self.generate_image(logo_prompt, style='logo', quality='high')
            
        except Exception as e:
            logger.error(f"❌ Logo generation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ Logo generation failed: {str(e)}"
            }
    
    def create_poster(self, title: str, theme: str = 'movie', style: str = 'dramatic') -> Dict:
        """Generate poster design"""
        try:
            # Build poster-specific prompt
            poster_prompt = f"{title} poster"
            
            if theme:
                poster_prompt += f" {theme} theme"
            
            poster_prompt += f" {style} lighting cinematic professional poster design"
            
            return self.generate_image(poster_prompt, style='poster', quality='high')
            
        except Exception as e:
            logger.error(f"❌ Poster generation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ Poster generation failed: {str(e)}"
            }
    
    def create_ui_mockup(self, app_name: str, app_type: str = 'mobile') -> Dict:
        """Generate UI design mockup"""
        try:
            # Build UI-specific prompt
            ui_prompt = f"modern UI design for {app_name}"
            
            if app_type:
                ui_prompt += f" {app_type} application"
            
            ui_prompt += " clean interface user-friendly modern design professional UI"
            
            return self.generate_image(ui_prompt, style='ui', quality='high')
            
        except Exception as e:
            logger.error(f"❌ UI mockup generation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ UI mockup generation failed: {str(e)}"
            }
    
    def get_generation_info(self) -> Dict:
        """Get information about available generation options"""
        return {
            'available_styles': list(self.styles.keys()),
            'available_qualities': list(self.quality_presets.keys()),
            'available_models': list(self.available_models.keys()),
            'output_directory': str(self.output_dir),
            'image_processing_available': IMAGE_AVAILABLE,
            'model_details': {
                model: {'backend': backend} for model, backend in self.available_models.items()
            }
        }
    
    def list_generated_images(self) -> Dict:
        """List all previously generated images"""
        try:
            if not self.output_dir.exists():
                return {
                    'success': True,
                    'images': [],
                    'total_count': 0,
                    'response': '📁 No generated images found'
                }
            
            images = []
            for file_path in self.output_dir.glob('*.png'):
                stat = file_path.stat()
                images.append({
                    'filename': file_path.name,
                    'path': str(file_path),
                    'size': stat.st_size,
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime
                })
            
            # Sort by creation time (newest first)
            images.sort(key=lambda x: x['created'], reverse=True)
            
            response = f"📁 Generated Images ({len(images)} total):\n"
            for i, img in enumerate(images[:10], 1):  # Show last 10
                response += f"{i}. {img['filename']} ({img['size']/1024:.1f} KB)\n"
            
            return {
                'success': True,
                'images': images,
                'total_count': len(images),
                'response': response
            }
            
        except Exception as e:
            logger.error(f"❌ List images error: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ Failed to list images: {str(e)}"
            }

# Global image generator instance
image_generator = ImageGenerator()
