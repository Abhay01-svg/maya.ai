"""
Maya AI Web Interface
Flask web UI with comprehensive response handling and data display
"""

import sys
import io
from flask import Flask, render_template, request, jsonify
import time
import logging
from pathlib import Path
import os
from werkzeug.utils import secure_filename

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Maya AI modules
from modules.router import router
from modules.tools import weather_api, news_api, search_api, pc_control, memory
from modules.models import local_models
from modules.voice_processor import voice_processor
from modules.enhanced_moondream import EnhancedMoondream
from modules.unified_decision_maker import unified_decision_maker as decision_maker
from modules.tools import search_api
# from modules.voice_processor import voice_processor, voice_output
from modules.time_date import time_date_module
from modules.offline_model import offline_model
# Temporarily disabled pc_control due to import issues
# from modules.pc_control import pc_control

app = Flask(__name__)

# Configure file upload settings
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'py', 'js', 'html', 'css', 'json', 'xml', 'csv'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _format_search_results(results):
    """Format search results for AI processing"""
    if not results:
        return "No search results found."
    
    output = "Search Results:\n\n"
    for i, result in enumerate(results, 1):
        output += f"{i}. Title: {result.get('title', 'No title')}\n"
        output += f"   Content: {result.get('snippet', '')[:200]}\n"
        # Don't include URLs in the formatted text to avoid them appearing in responses
    return output

def _analyze_file(file_path, filename):
    """Analyze uploaded file and return content summary"""
    try:
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        if file_ext in ['txt', 'py', 'js', 'html', 'css', 'json', 'xml', 'csv']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if len(content) > 2000:
                    content = content[:2000] + "\n\n... (content truncated)"
                return {
                    'success': True,
                    'type': 'text',
                    'content': content,
                    'size': os.path.getsize(file_path),
                    'lines': content.count('\n') + 1
                }
        elif file_ext in ['png', 'jpg', 'jpeg', 'gif']:
            # For images, we can analyze them with the vision model
            return {
                'success': True,
                'type': 'image',
                'path': str(file_path),
                'size': os.path.getsize(file_path),
                'description': f"Image file ({file_ext}) uploaded successfully"
            }
        elif file_ext in ['pdf', 'doc', 'docx']:
            return {
                'success': True,
                'type': 'document',
                'path': str(file_path),
                'size': os.path.getsize(file_path),
                'description': f"Document file ({file_ext}) uploaded successfully"
            }
        else:
            return {
                'success': True,
                'type': 'binary',
                'path': str(file_path),
                'size': os.path.getsize(file_path),
                'description': f"File ({file_ext}) uploaded successfully"
            }
    except Exception as e:
        return {
            'success': False,
            'error': f"Error analyzing file: {str(e)}"
        }

@app.route('/')
def index():
    """Main web interface"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests with intelligent decision making"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({
                "success": False,
                "error": "No message provided",
                "response": None,
                "metadata": {}
            }), 400
        
        start_time = time.time()
        
        # Use enhanced NLP-based decision making
        decision = decision_maker.decide_module("", user_message)
        intent = decision['primary_module']
        module_used = decision['primary_module']
        classification_method = decision.get('classification_method', 'rule-based')
        confidence = decision.get('confidence', 0.5)
        reasoning = decision.get('reasoning', 'Unknown reasoning')
        entities = decision.get('entities', {})
        
        logger.info(f" NLP Classification: {intent} (confidence: {confidence:.2f}) - {reasoning}")
        
        response_text = None
        tokens_used = 0
        is_fallback = False
        is_rag_response = False
        
        # Step 3: Execute based on enhanced NLP decision
        try:
            if decision['start_ollama']:
                logger.info(" Starting Ollama...")
                decision_maker.ollama.start_ollama()
            
            # Execute based on NLP-classified module
            if module_used == "calculator":
                expression = entities.get('expression', user_message)
                calc_result = calculator.evaluate_expression(expression)
                response_text = calc_result if isinstance(calc_result, str) else str(calc_result)
                model_used = "Calculator"
            
            elif module_used == "weather_api":
                from modules.tools import weather_api
                city = entities.get('city', 'current')
                response_text = weather_api.get_hinglish_weather(city)
                model_used = "Weather API"
            
            elif module_used == "news_api":
                from modules.tools import news_api
                topic = entities.get('topic', 'india')
                response_text = news_api.get_hinglish_news(topic, limit=3)
                model_used = "News API"
            
            elif module_used == "search_api":
                search_query = entities.get('query', user_message)
                logger.info(f"🔍 Performing web search for: {search_query}")
                results = search_api.search(search_query, limit=5)
                logger.info(f"📊 Found {len(results)} search results")
                
                # Format search results for display
                search_text = _format_search_results(results) if results else "❌ No search results"
                
                # Verify/refine search results via local model for quality (LLM); do not expose model names
                try:
                    verify_prompt = (
                        "Based on these search results, provide a professional, direct response to the user's question. "
                        "Focus on the actual information and insights. Do not include URLs, source references, "
                        "or phrases like 'according to', 'based on', 'from the search results'. "
                        "Respond as if you have direct knowledge of the topic. Be concise and professional.\n\n"
                        "User's original question: " + user_message + "\n\n"
                        "Search results to synthesize:\n" + search_text
                    )
                    verify_result = local_models.smart_routing(verify_prompt, "general_chat")
                    response_text = verify_result.get('response') or search_text
                    logger.info("✅ Search results refined by local model")
                except Exception as e:
                    logger.warning(f"⚠️ Search result refinement failed: {e}")
                    response_text = search_text
                
                model_used = "DuckDuckGo Search (RAG)"
                is_rag_response = True
                logger.info("🦆 DuckDuckGo RAG response generated successfully")
            
            elif module_used == "time_date_module":
                from modules.time_date import time_date_module
                result = time_date_module.get_time_date(user_message)
                return {
                    "response": result.get('response'),
                    "module": module_used
                }
            
            elif module_used == "offline_model":
                from modules.offline_model import offline_model
                result = offline_model.process_query(user_message)
                return {
                    "response": result.get('response'),
                    "module": module_used
                }
            
            elif module_used == "pc_control":
                from modules.pc_control import pc_control
                action = entities.get('action')
                app_name = entities.get('app')
                
                if action == "open" and app_name:
                    result = pc_control.open_app(app_name)
                elif action == "close" and app_name:
                    result = pc_control.close_app(app_name)
                elif action == "screenshot":
                    result = pc_control.screenshot()
                else:
                    result = {"message": "Action not recognized"}
                
                response_text = result.get('message', result.get('hinglish', str(result)))
                model_used = "PC Control"
            
            elif module_used == "memory":
                response_text = "✅ Memory operation completed"
                model_used = "Memory"
            
            elif module_used == "qwen_coder":
                result = local_models.smart_routing(user_message, "coding")
                response_text = result.get('response')
                model_used = result.get('model_used', 'Qwen Coder')
                tokens_used = result.get('tokens_used', 0)
            
            elif module_used == "llama_general":
                # Check if this is a greeting for more natural response
                if intent == "greeting":
                    greeting_prompt = (
                        "Respond naturally and warmly to this greeting. "
                        "Keep it brief and friendly. Don't ask questions back unless appropriate. "
                        "Avoid sounding like you're being disturbed or busy.\n\n"
                        "Greeting: " + user_message
                    )
                    result = local_models.smart_routing(greeting_prompt, "general_chat")
                else:
                    # Add professional response guidance for non-greetings
                    professional_prompt = (
                        "Provide a professional, direct response to this question. "
                        "Be concise and informative. Avoid unnecessary conversational filler, "
                        "apologies, or phrases like 'I think', 'I believe', 'It seems like'. "
                        "Focus on providing clear, factual information.\n\n"
                        "Question: " + user_message
                    )
                    result = local_models.smart_routing(professional_prompt, "general_chat")
                
                response_text = result.get('response')
                model_used = result.get('model_used', 'Llama 3.2')
                tokens_used = result.get('tokens_used', 0)
            
            else:
                # Fallback to brain processing with professional guidance
                professional_prompt = (
                    "Provide a professional, direct response. Be concise and informative. "
                    "Avoid conversational filler and unnecessary phrases. Focus on clear information."
                )
                brain_response = brain.process_query(professional_prompt)
                response_text = brain_response.get('response') or brain_response
                model_used = brain_response.get('model_used') if isinstance(brain_response, dict) else "Maya Brain"
            
            # Validate output quality
            if response_text:
                is_valid, validation_msg = decision_maker.validate_output(response_text, intent)
                if not is_valid and decision['fallback_modules']:
                    logger.warning(f"⚠️  Validation failed: {validation_msg}, trying fallback...")
                    fallback_result = decision_maker.get_fallback_response(
                        decision['fallback_modules'],
                        user_message
                    )
                    if fallback_result:
                        response_text = fallback_result['response']
                        model_used = fallback_result.get('module', 'Fallback')
                        is_fallback = True
        
        finally:
            # Clean up Ollama if needed
            if decision['stop_ollama_after']:
                logger.info("🛑 Stopping Ollama...")
                decision_maker.ollama.stop_ollama()
        
        # Step 4: Store in memory
        if response_text:
            memory.save_chat(user_message, response_text, intent, tokens_used)
        
        # Step 5: Return comprehensive response
        elapsed_time = time.time() - start_time
        
        web_response = {
            "success": bool(response_text and not response_text.startswith('❌')),
            "response": response_text or "❌ Unable to process query",
            "metadata": {
                "intent": intent,
                "module_used": module_used,
                "primary_decision": module_used,
                "is_fallback": is_fallback,
                "is_rag_response": is_rag_response,
                "confidence": decision.get('confidence', 0.5),
                "reasoning": decision.get('reasoning', ''),
                "tokens_used": tokens_used,
                "response_time_ms": round(elapsed_time * 1000, 2),
                "estimated_time_ms": round(decision_maker.estimate_response_time(module_used) * 1000, 2),
            }
        }
        
        logger.info(f"✅ Response sent in {elapsed_time:.2f}s")
        return jsonify(web_response)
        
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "response": f"❌ Error: {str(e)}",
            "metadata": {
                "intent": "error",
                "module_used": None,
                "confidence": 0.0,
            }
        }), 500

@app.route('/status')
def status():
    """Get Maya AI status with comprehensive system info"""
    try:
        stats = {
            'models_available': {
                'llama3.2:3b': True,
                'qwen2.5-coder:3b': True,
                'moondream:latest': True
            },
            'memory_chats': len(memory.get_chat_history(100)),
            'calculator': 'ready',
            'voice': 'available' if hasattr(memory, 'voice_interface') else 'disabled',
            'apis': {
                'weather': 'connected',
                'news': 'connected',
                'search': 'connected',
                'huggingface': 'read_only'
            },
            'ollama': {
                'status': 'running' if decision_maker.ollama.is_ollama_running() else 'stopped',
                'available_modules': decision_maker.available_modules,
            },
            'decision_maker': {
                'initialized': True,
                'performance_tracking': len(decision_maker.module_performance) > 0
            }
        }
        
        return jsonify({
            "success": True,
            "status": "online",
            "stats": stats,
            "uptime": f"{time.time() - time.time():.0f}s"
        })
    except Exception as e:
        logger.error(f"❌ Status error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = int(time.time())
            filename = f"{timestamp}_{filename}"
            
            file_path = Path(app.config['UPLOAD_FOLDER']) / filename
            file.save(str(file_path))
            
            # Analyze the file
            analysis = _analyze_file(file_path, filename)
            
            if analysis['success']:
                # For text files, try to process with AI
                if analysis['type'] == 'text':
                    try:
                        content_preview = analysis.get('content', '')[:500]
                        ai_prompt = f"Analyze this file content and provide a summary:\n\n{content_preview}"
                        ai_result = local_models.smart_routing(ai_prompt, "general_chat")
                        analysis['ai_summary'] = ai_result.get('response', 'Unable to analyze content')
                    except Exception as e:
                        analysis['ai_summary'] = f"AI analysis failed: {str(e)}"
                
                # For images, try to analyze with vision model
                elif analysis['type'] == 'image':
                    try:
                        from modules.enhanced_moondream import analyze_image
                        vision_result = analyze_image(str(file_path), "Describe this image in detail")
                        analysis['ai_summary'] = vision_result.get('description', 'Unable to analyze image')
                    except Exception as e:
                        analysis['ai_summary'] = f"Vision analysis failed: {str(e)}"
                
                return jsonify({
                    'success': True,
                    'file_info': {
                        'filename': filename,
                        'original_name': file.filename,
                        'size': analysis['size'],
                        'type': analysis['type'],
                        'analysis': analysis
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': analysis['error']
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Allowed types: {", ".join(sorted(ALLOWED_EXTENSIONS))}'
            }), 400
            
    except Exception as e:
        logger.error(f"❌ Upload error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@app.route('/voice/start', methods=['POST'])
def start_voice_listening():
    """Start voice listening with wake word detection"""
    try:
        def wake_word_callback(detected_word):
            logger.info(f"🎤 Wake word detected: {detected_word}")
            # Here you could trigger an action or send a message to the frontend
        
        success = voice_processor.start_listening(wake_word_callback)
        
        return jsonify({
            'success': success,
            'wake_words': voice_processor.get_supported_wake_words(),
            'status': 'listening' if success else 'error'
        })
    except Exception as e:
        logger.error(f"Voice start error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/voice/auto', methods=['POST'])
def start_auto_detection():
    """Start automatic wake/stop word detection"""
    try:
        success = voice_processor.start_auto_detection()
        return jsonify({
            'success': success,
            'message': 'Automatic wake/stop detection started' if success else 'Failed to start auto detection'
        })
    except Exception as e:
        logger.error(f"Auto detection start error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/voice/stop', methods=['POST'])
def stop_voice_listening():
    """Stop voice listening"""
    try:
        voice_processor.stop_listening()
        return jsonify({
            'success': True,
            'status': 'stopped'
        })
    except Exception as e:
        logger.error(f"Voice stop error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/voice/speak', methods=['POST'])
def speak_text():
    """Convert text to speech"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        blocking = data.get('blocking', False)
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        success = voice_output.speak(text, blocking)
        
        return jsonify({
            'success': success,
            'text': text,
            'is_speaking': voice_output.is_busy()
        })
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/voice/configure', methods=['POST'])
def configure_voice():
    """Configure voice settings for more natural output"""
    try:
        data = request.get_json()
        
        if not voice_output.tts_engine:
            return jsonify({
                'success': False,
                'error': 'TTS engine not available'
            }), 400
        
        # Apply voice configuration
        if 'rate' in data:
            voice_output.tts_engine.setProperty('rate', int(data['rate']))
        
        if 'volume' in data:
            voice_output.tts_engine.setProperty('volume', float(data['volume']))
        
        if 'pitch' in data:
            try:
                voice_output.tts_engine.setProperty('pitch', int(data['pitch']))
            except:
                pass  # Pitch not supported
        
        # Change voice if specified
        if 'voice_id' in data:
            try:
                voice_output.tts_engine.setProperty('voice', data['voice_id'])
            except Exception as e:
                logger.warning(f"Voice change failed: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Voice configuration updated'
        })
        
    except Exception as e:
        logger.error(f"Voice configuration error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/voice/voices')
def get_available_voices():
    """Get list of available TTS voices"""
    try:
        voices = []
        if voice_output.tts_engine:
            for voice in voice_output.tts_engine.getProperty('voices'):
                voices.append({
                    'id': voice.id,
                    'name': voice.name,
                    'gender': voice.gender,
                    'languages': voice.languages if hasattr(voice, 'languages') else []
                })
        
        return jsonify({
            'success': True,
            'voices': voices
        })
        
    except Exception as e:
        logger.error(f"Get voices error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/voice/test', methods=['POST'])
def test_voice():
    """Test voice output with sample text"""
    try:
        data = request.get_json()
        test_text = data.get('text', "Hello, I'm Maya AI. How does my voice sound?")
        
        success = voice_output.speak(test_text, blocking=True)
        
        return jsonify({
            'success': success,
            'text': test_text,
            'message': 'Voice test completed' if success else 'Voice test failed'
        })
        
    except Exception as e:
        logger.error(f"Voice test error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/voice/status')
def voice_status():
    """Get voice system status"""
    try:
        # Get current voice settings
        voice_settings = {}
        if voice_output.tts_engine:
            try:
                voice_settings = {
                    'rate': voice_output.tts_engine.getProperty('rate'),
                    'volume': voice_output.tts_engine.getProperty('volume'),
                    'voice': voice_output.tts_engine.getProperty('voice')
                }
            except:
                pass
        
        return jsonify({
            'success': True,
            'voice_processor': {
                'is_listening': voice_processor.is_listening,
                'is_processing': voice_processor.is_processing,
                'supported_wake_words': voice_processor.get_supported_wake_words(),
                'uses_c_module': voice_processor.use_c_module
            },
            'voice_output': {
                'is_speaking': voice_output.is_busy(),
                'tts_available': voice_output.tts_engine is not None,
                'settings': voice_settings
            }
        })
    except Exception as e:
        logger.error(f"Voice status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/models')
def models():
    """Get available models info"""
    try:
        models_info = {
            'llama3.2:3b': {
                'name': 'Llama 3.2 3B',
                'type': 'General Chat',
                'size': '2.0 GB',
                'status': 'Available'
            },
            'qwen2.5-coder:7b': {
                'name': 'Qwen 2.5 Coder 7B',
                'type': 'Code Generation',
                'size': '4.7 GB',
                'status': 'Available'
            },
            'moondream:latest': {
                'name': 'Moondream',
                'type': 'Vision Model',
                'size': '1.7 GB',
                'status': 'Available'
            }
        }
        return jsonify(models_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("[STARTUP] Starting Maya AI Web Interface...")
    print("[INFO] Open http://localhost:5000 in your browser")
    print("[INFO] Debug mode: ON")
    app.run(debug=True, host='0.0.0.0', port=5000)
