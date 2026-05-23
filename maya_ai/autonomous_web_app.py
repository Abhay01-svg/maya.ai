"""
Maya AI Autonomous Web Application
Advanced futuristic UI with drag & drop, multi-tool workflows, and AGI-like capabilities
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import time
import uuid
from pathlib import Path
import logging
from werkzeug.utils import secure_filename
import base64

# Import Maya AI modules
from modules.autonomous_brain import autonomous_brain
from modules.enhanced_moondream import enhanced_moondream
from modules.rag_search import rag_engine
from modules.news_engine import news_engine
from modules.image_generator import image_generator
from modules.enhanced_brain import enhanced_brain
from modules.memory import memory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'maya-ai-autonomous-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Upload directories
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
GENERATED_FOLDER = Path('generated_images')
GENERATED_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['GENERATED_FOLDER'] = str(GENERATED_FOLDER)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'bmp', 'tiff'
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionManager:
    """Manage user sessions and context"""
    
    def __init__(self):
        self.sessions = {}
    
    def get_session(self, session_id):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'id': session_id,
                'created_at': time.time(),
                'chat_history': [],
                'uploaded_files': [],
                'active_tools': [],
                'context': {},
                'workflow_state': None
            }
        return self.sessions[session_id]
    
    def add_message(self, session_id, role, content, metadata=None):
        session = self.get_session(session_id)
        message = {
            'role': role,
            'content': content,
            'timestamp': time.time(),
            'metadata': metadata or {}
        }
        session['chat_history'].append(message)
        
        # Keep only last 50 messages
        if len(session['chat_history']) > 50:
            session['chat_history'] = session['chat_history'][-50:]
    
    def add_uploaded_file(self, session_id, file_info):
        session = self.get_session(session_id)
        session['uploaded_files'].append(file_info)
    
    def set_active_tool(self, session_id, tool_name):
        session = self.get_session(session_id)
        if tool_name not in session['active_tools']:
            session['active_tools'].append(tool_name)
    
    def clear_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

session_manager = SessionManager()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page"""
    session_id = str(uuid.uuid4())
    return render_template('autonomous_index.html', session_id=session_id)

@app.route('/status')
def status():
    """System status endpoint"""
    try:
        # Get system status
        status_info = {
            'maya_ai': {
                'status': 'operational',
                'uptime': time.time() - app.start_time if hasattr(app, 'start_time') else 0,
                'active_sessions': len(session_manager.sessions),
                'modules': {
                    'autonomous_brain': 'active',
                    'rag_search': 'active',
                    'enhanced_moondream': 'active',
                    'news_engine': 'active',
                    'image_generator': 'active',
                    'enhanced_brain': 'active'
                }
            },
            'models': {
                'llama_3.2_3b': 'available',
                'qwen_2.5_coder_3b': 'available',
                'moondream': 'available'
            },
            'tools': {
                'web_search': 'active',
                'news_search': 'active',
                'weather_api': 'active',
                'calculator': 'active',
                'pc_control': 'active'
            }
        }
        
        return jsonify({
            'success': True,
            'data': status_info,
            'timestamp': time.time()
        })
    
    except Exception as e:
        logger.error(f"❌ Status endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint with autonomous routing"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message', '')
        context = data.get('context', {})
        
        if not session_id or not message:
            return jsonify({
                'success': False,
                'error': 'Missing session_id or message'
            })
        
        # Add user message to session
        session_manager.add_message(session_id, 'user', message)
        
        # Process with autonomous brain
        start_time = time.time()
        result = autonomous_brain.execute_task(message, context)
        processing_time = time.time() - start_time
        
        # Add AI response to session
        session_manager.add_message(session_id, 'assistant', result.get('response', ''), {
            'task_type': result.get('task_type'),
            'modules_used': result.get('modules_used', []),
            'processing_time': processing_time
        })
        
        # Update active tools
        for module in result.get('modules_used', []):
            session_manager.set_active_tool(session_id, module)
        
        return jsonify({
            'success': True,
            'data': {
                'response': result.get('response'),
                'task_type': result.get('task_type'),
                'modules_used': result.get('modules_used', []),
                'processing_time': processing_time,
                'confidence': result.get('confidence', 0.0),
                'active_tools': session_manager.get_session(session_id)['active_tools']
            },
            'timestamp': time.time()
        })
    
    except Exception as e:
        logger.error(f"❌ Chat endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        })

@app.route('/upload', methods=['POST'])
def upload_file():
    """File upload endpoint"""
    try:
        session_id = request.form.get('session_id')
        analysis_type = request.form.get('analysis_type', 'summary')
        query = request.form.get('query', '')
        
        if not session_id or 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Missing session_id or file'
            })
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            })
        
        if file and allowed_file(file.filename):
            # Secure filename and save
            filename = secure_filename(file.filename)
            timestamp = int(time.time())
            safe_filename = f"{timestamp}_{filename}"
            file_path = UPLOAD_FOLDER / safe_filename
            file.save(str(file_path))
            
            # Add to session
            file_info = {
                'original_name': filename,
                'safe_name': safe_filename,
                'path': str(file_path),
                'size': file_path.stat().st_size,
                'uploaded_at': time.time(),
                'analysis_type': analysis_type
            }
            session_manager.add_uploaded_file(session_id, file_info)
            
            # Process with enhanced Moondream
            result = enhanced_moondream.process_file(
                str(file_path), 
                analysis_type, 
                query,
                {'session_id': session_id}
            )
            
            # Add processing message to session
            session_manager.add_message(session_id, 'assistant', result.get('response', ''), {
                'action': 'file_analysis',
                'file_info': file_info,
                'analysis_type': analysis_type
            })
            
            return jsonify({
                'success': True,
                'data': {
                    'file_info': file_info,
                    'analysis_result': result,
                    'response': result.get('response')
                },
                'timestamp': time.time()
            })
        
        else:
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            })
    
    except Exception as e:
        logger.error(f"❌ Upload endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        })

@app.route('/search', methods=['POST'])
def deep_search():
    """Deep web search endpoint"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        query = data.get('query', '')
        max_results = data.get('max_results', 10)
        depth = data.get('depth', 2)
        
        if not session_id or not query:
            return jsonify({
                'success': False,
                'error': 'Missing session_id or query'
            })
        
        # Perform deep search
        result = rag_engine.deep_search(query, max_results, depth)
        
        # Add to session
        session_manager.add_message(session_id, 'assistant', result.get('response', ''), {
            'action': 'deep_search',
            'query': query,
            'sources_count': result.get('sources_count', 0)
        })
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': time.time()
        })
    
    except Exception as e:
        logger.error(f"❌ Search endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        })

@app.route('/news', methods=['POST'])
def get_news():
    """Latest news endpoint"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        query = data.get('query', '')
        category = data.get('category', None)
        max_articles = data.get('max_articles', 10)
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Missing session_id'
            })
        
        # Get news
        result = news_engine.get_latest_news(query, category, max_articles)
        
        # Add to session
        session_manager.add_message(session_id, 'assistant', result.get('response', ''), {
            'action': 'news_search',
            'category': category,
            'articles_found': result.get('articles_found', 0)
        })
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': time.time()
        })
    
    except Exception as e:
        logger.error(f"❌ News endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        })

@app.route('/generate_image', methods=['POST'])
def generate_image():
    """Image generation endpoint"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        prompt = data.get('prompt', '')
        style = data.get('style', 'realistic')
        quality = data.get('quality', 'medium')
        
        if not session_id or not prompt:
            return jsonify({
                'success': False,
                'error': 'Missing session_id or prompt'
            })
        
        # Generate image
        result = image_generator.generate_image(prompt, style, quality)
        
        if result['success']:
            # Add to session
            session_manager.add_message(session_id, 'assistant', result.get('response', ''), {
                'action': 'image_generation',
                'prompt': prompt,
                'style': style,
                'image_path': result.get('image_path')
            })
        
        return jsonify({
            'success': result['success'],
            'data': result,
            'timestamp': time.time()
        })
    
    except Exception as e:
        logger.error(f"❌ Image generation endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        })

@app.route('/execute', methods=['POST'])
def execute_command():
    """Command execution endpoint"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        command = data.get('command', '')
        context = data.get('context', {})
        
        if not session_id or not command:
            return jsonify({
                'success': False,
                'error': 'Missing session_id or command'
            })
        
        # Execute command
        result = enhanced_brain.execute_command(command, context)
        
        # Add to session
        session_manager.add_message(session_id, 'assistant', result.get('response', ''), {
            'action': 'command_execution',
            'command': command,
            'category': result.get('category'),
            'success': result.get('success')
        })
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': time.time()
        })
    
    except Exception as e:
        logger.error(f"❌ Command execution endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        })

@app.route('/workflow', methods=['POST'])
def workflow():
    """Multi-tool workflow endpoint"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        workflow_type = data.get('type', '')
        inputs = data.get('inputs', {})
        
        if not session_id or not workflow_type:
            return jsonify({
                'success': False,
                'error': 'Missing session_id or workflow_type'
            })
        
        # Execute workflow based on type
        if workflow_type == 'research_and_summarize':
            result = execute_research_workflow(inputs)
        elif workflow_type == 'document_analysis':
            result = execute_document_workflow(inputs, session_id)
        elif workflow_type == 'creative_project':
            result = execute_creative_workflow(inputs)
        else:
            result = {
                'success': False,
                'error': f'Unknown workflow type: {workflow_type}'
            }
        
        # Add to session
        session_manager.add_message(session_id, 'assistant', result.get('response', ''), {
            'action': 'workflow',
            'workflow_type': workflow_type,
            'success': result.get('success')
        })
        
        return jsonify({
            'success': result['success'],
            'data': result,
            'timestamp': time.time()
        })
    
    except Exception as e:
        logger.error(f"❌ Workflow endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        })

def execute_research_workflow(inputs):
    """Execute research and summarize workflow"""
    try:
        query = inputs.get('query', '')
        if not query:
            return {'success': False, 'error': 'No query provided'}
        
        # Step 1: Deep search
        search_result = rag_engine.deep_search(query, max_results=8, depth=2)
        
        if not search_result['success']:
            return search_result
        
        # Step 2: Extract key information
        summary = search_result.get('summary', {})
        
        # Step 3: Generate comprehensive response
        response = f"🔍 Research Workflow Results:\n\n"
        response += f"📝 Query: {query}\n\n"
        response += f"📊 Sources Analyzed: {search_result.get('sources_count', 0)}\n"
        response += f"⏱️  Research Time: {search_result.get('search_time', 0):.2f}s\n\n"
        response += search_result.get('response', '')
        
        return {
            'success': True,
            'workflow_type': 'research_and_summarize',
            'search_result': search_result,
            'response': response
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def execute_document_workflow(inputs, session_id):
    """Execute document analysis workflow"""
    try:
        session = session_manager.get_session(session_id)
        uploaded_files = session.get('uploaded_files', [])
        
        if not uploaded_files:
            return {'success': False, 'error': 'No files uploaded'}
        
        # Process latest uploaded file
        latest_file = uploaded_files[-1]
        file_path = latest_file['path']
        analysis_type = inputs.get('analysis_type', 'summary')
        query = inputs.get('query', '')
        
        # Analyze document
        result = enhanced_moondream.process_file(file_path, analysis_type, query)
        
        response = f"📄 Document Analysis Workflow:\n\n"
        response += f"📁 File: {latest_file['original_name']}\n"
        response += f"📏 Size: {latest_file['size']} bytes\n"
        response += f"🔍 Analysis Type: {analysis_type}\n\n"
        response += result.get('response', '')
        
        return {
            'success': result['success'],
            'workflow_type': 'document_analysis',
            'file_result': result,
            'response': response
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def execute_creative_workflow(inputs):
    """Execute creative project workflow"""
    try:
        project_type = inputs.get('project_type', 'logo')
        description = inputs.get('description', '')
        
        if not description:
            return {'success': False, 'error': 'No description provided'}
        
        # Step 1: Generate image
        if project_type == 'logo':
            image_result = image_generator.create_logo(description)
        elif project_type == 'poster':
            image_result = image_generator.create_poster(description)
        elif project_type == 'ui':
            image_result = image_generator.create_ui_mockup(description)
        else:
            image_result = image_generator.generate_image(description, 'artistic', 'high')
        
        # Step 2: Generate creative response
        response = f"🎨 Creative Workflow Results:\n\n"
        response += f"🎭 Project Type: {project_type}\n"
        response += f"💭 Description: {description}\n\n"
        response += image_result.get('response', '')
        
        return {
            'success': image_result['success'],
            'workflow_type': 'creative_project',
            'image_result': image_result,
            'response': response
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/session/<session_id>')
def get_session(session_id):
    """Get session information"""
    try:
        session = session_manager.get_session(session_id)
        return jsonify({
            'success': True,
            'data': {
                'session_id': session_id,
                'chat_history': session['chat_history'],
                'uploaded_files': session['uploaded_files'],
                'active_tools': session['active_tools'],
                'created_at': session['created_at']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/session/<session_id>/clear', methods=['POST'])
def clear_session(session_id):
    """Clear session data"""
    try:
        session_manager.clear_session(session_id)
        return jsonify({
            'success': True,
            'message': f'Session {session_id} cleared'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated files"""
    try:
        # Check in generated images folder first
        image_path = GENERATED_FOLDER / filename
        if image_path.exists():
            return send_file(str(image_path))
        
        # Check in uploads folder
        upload_path = UPLOAD_FOLDER / filename
        if upload_path.exists():
            return send_file(str(upload_path))
        
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/system/stats')
def system_stats():
    """Get system statistics"""
    try:
        # Get brain execution stats
        brain_stats = enhanced_brain.get_execution_stats()
        
        # Get image generation info
        image_info = image_generator.get_generation_info()
        
        # Get memory stats
        memory_stats = {
            'total_sessions': len(session_manager.sessions),
            'active_sessions': len([s for s in session_manager.sessions.values() if time.time() - s['created_at'] < 3600])
        }
        
        return jsonify({
            'success': True,
            'data': {
                'brain_stats': brain_stats,
                'image_info': image_info,
                'memory_stats': memory_stats,
                'uptime': time.time() - app.start_time if hasattr(app, 'start_time') else 0
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.start_time = time.time()
    logger.info("🚀 Starting Maya AI Autonomous Web Application")
    logger.info("🌐 Available at: http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
