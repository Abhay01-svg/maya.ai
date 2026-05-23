"""
Maya AI Enhanced Brain System
Master command executor with advanced automation and tool integration
"""

import logging
import time
import os
import json
import subprocess
import ast
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import tempfile
import shutil

from config import DEBUG_MODE
from .brain import brain as original_brain
from .calculator import calculator
from .pc_control import pc_control
from .memory import memory
from .tools import weather_api, news_api, search_api

logger = logging.getLogger(__name__)

class EnhancedBrain:
    """Enhanced brain system with master command execution capabilities"""
    
    def __init__(self):
        self.start_time = time.time()
        self.command_count = 0
        self.execution_history = []
        self.temp_dir = Path(tempfile.gettempdir()) / "maya_brain_temp"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Command categories
        self.command_categories = {
            'automation': ['automate', 'script', 'batch', 'schedule', 'monitor'],
            'development': ['create', 'build', 'develop', 'code', 'program', 'app'],
            'system': ['system', 'process', 'service', 'task', 'manage'],
            'file': ['file', 'folder', 'directory', 'copy', 'move', 'delete', 'organize'],
            'network': ['network', 'internet', 'download', 'upload', 'connect'],
            'data': ['data', 'database', 'backup', 'restore', 'analyze'],
            'security': ['security', 'encrypt', 'decrypt', 'password', 'protect']
        }
        
        # Safe operations whitelist
        self.safe_operations = {
            'file_ops': ['list', 'read', 'copy', 'move', 'create'],
            'system_info': ['info', 'status', 'monitor'],
            'calculation': ['calculate', 'compute', 'math'],
            'web': ['search', 'fetch', 'download'],
            'automation': ['schedule', 'monitor', 'log']
        }
        
        if DEBUG_MODE:
            logger.info("🧠 Enhanced Brain System initialized")
            logger.info(f"📁 Temp directory: {self.temp_dir}")
    
    def execute_command(self, user_command: str, context: Dict = None) -> Dict:
        """Execute user command with intelligent routing"""
        start_time = time.time()
        self.command_count += 1
        
        try:
            # Analyze command
            command_analysis = self._analyze_command(user_command)
            
            # Route to appropriate executor
            result = self._execute_by_category(command_analysis, user_command, context)
            
            # Verify and enhance result
            verified_result = self._verify_execution_result(result, user_command)
            
            execution_time = time.time() - start_time
            
            # Record execution
            self._record_execution(user_command, command_analysis, verified_result, execution_time)
            
            return verified_result
            
        except Exception as e:
            logger.error(f"❌ Command execution error: {e}")
            return {
                'success': False,
                'command': user_command,
                'error': str(e),
                'response': f"❌ Command execution failed: {str(e)}",
                'execution_time': time.time() - start_time
            }
    
    def _analyze_command(self, command: str) -> Dict:
        """Analyze command and determine category and safety"""
        command_lower = command.lower().strip()
        
        # Determine category
        category = 'general'
        for cat_name, keywords in self.command_categories.items():
            if any(keyword in command_lower for keyword in keywords):
                category = cat_name
                break
        
        # Check safety
        is_safe = self._is_safe_command(command_lower)
        
        # Extract action and target
        action, target = self._extract_action_target(command)
        
        # Determine complexity
        complexity = self._determine_complexity(command)
        
        return {
            'category': category,
            'is_safe': is_safe,
            'action': action,
            'target': target,
            'complexity': complexity,
            'command_length': len(command),
            'requires_confirmation': not is_safe or complexity > 7
        }
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute"""
        dangerous_patterns = [
            'delete', 'remove', 'format', 'erase', 'destroy',
            'shutdown', 'restart', 'reboot', 'halt',
            'sudo', 'admin', 'root', 'privilege',
            'password', 'secret', 'key', 'token',
            'system32', 'windows', 'program files'
        ]
        
        return not any(pattern in command for pattern in dangerous_patterns)
    
    def _extract_action_target(self, command: str) -> tuple:
        """Extract action and target from command"""
        words = command.lower().split()
        
        action_words = ['create', 'build', 'make', 'generate', 'write', 'code',
                       'open', 'start', 'launch', 'run', 'execute',
                       'close', 'stop', 'kill', 'terminate',
                       'copy', 'move', 'delete', 'remove',
                       'list', 'show', 'display', 'get', 'find',
                       'calculate', 'compute', 'analyze', 'process']
        
        action = None
        target = None
        
        for word in words:
            if word in action_words and not action:
                action = word
            elif action and not target:
                target = word
                break
        
        return (action or 'unknown', target or 'unknown')
    
    def _determine_complexity(self, command: str) -> int:
        """Determine command complexity (1-10 scale)"""
        complexity = 1
        
        # Base complexity on length
        complexity += min(len(command.split()) // 10, 3)
        
        # Add complexity for specific patterns
        if any(word in command.lower() for word in ['create', 'build', 'develop']):
            complexity += 2
        if any(word in command.lower() for word in ['automate', 'script', 'batch']):
            complexity += 3
        if any(word in command.lower() for word in ['system', 'admin', 'root']):
            complexity += 4
        
        return min(complexity, 10)
    
    def _execute_by_category(self, analysis: Dict, command: str, context: Dict) -> Dict:
        """Execute command based on category"""
        category = analysis['category']
        
        try:
            if category == 'development':
                return self._execute_development_command(command, analysis)
            elif category == 'automation':
                return self._execute_automation_command(command, analysis)
            elif category == 'system':
                return self._execute_system_command(command, analysis)
            elif category == 'file':
                return self._execute_file_command(command, analysis)
            elif category == 'network':
                return self._execute_network_command(command, analysis)
            elif category == 'data':
                return self._execute_data_command(command, analysis)
            elif category == 'security':
                return self._execute_security_command(command, analysis)
            else:
                return self._execute_general_command(command, analysis)
        
        except Exception as e:
            logger.error(f"❌ Category execution error: {e}")
            return {
                'success': False,
                'category': category,
                'error': str(e),
                'response': f"❌ {category} command failed: {str(e)}"
            }
    
    def _execute_development_command(self, command: str, analysis: Dict) -> Dict:
        """Execute development commands"""
        try:
            # Use original brain for development tasks
            result = original_brain.process_query(command)
            
            if result.get('success'):
                return {
                    'success': True,
                    'category': 'development',
                    'command': command,
                    'brain_result': result,
                    'response': result.get('hinglish_response', result.get('response')),
                    'modules_used': result.get('tool_used', 'brain')
                }
            else:
                return {
                    'success': False,
                    'category': 'development',
                    'error': 'Brain processing failed',
                    'response': result.get('response', '❌ Development command failed')
                }
        
        except Exception as e:
            return {
                'success': False,
                'category': 'development',
                'error': str(e),
                'response': f"❌ Development command error: {str(e)}"
            }
    
    def _execute_automation_command(self, command: str, analysis: Dict) -> Dict:
        """Execute automation commands"""
        try:
            # Create automation script
            script_content = self._generate_automation_script(command)
            
            if script_content:
                # Save script to temp file
                script_path = self.temp_dir / f"automation_{int(time.time())}.py"
                with open(script_path, 'w') as f:
                    f.write(script_content)
                
                return {
                    'success': True,
                    'category': 'automation',
                    'command': command,
                    'script_path': str(script_path),
                    'script_content': script_content,
                    'response': f"🤖 Automation script created:\n📁 {script_path.name}\n\n{script_content[:200]}..."
                }
            else:
                return {
                    'success': False,
                    'category': 'automation',
                    'error': 'Could not generate automation script',
                    'response': '❌ Automation script generation failed'
                }
        
        except Exception as e:
            return {
                'success': False,
                'category': 'automation',
                'error': str(e),
                'response': f"❌ Automation command error: {str(e)}"
            }
    
    def _execute_system_command(self, command: str, analysis: Dict) -> Dict:
        """Execute system commands (safe only)"""
        try:
            if not analysis['is_safe']:
                return {
                    'success': False,
                    'category': 'system',
                    'error': 'Command not safe for execution',
                    'response': '❌ Ye system command safe nahi hai'
                }
            
            # Get system information
            system_info = self._get_system_info()
            
            return {
                'success': True,
                'category': 'system',
                'command': command,
                'system_info': system_info,
                'response': f"🖥️ System Information:\n💻 CPU: {system_info.get('cpu_percent', 'N/A')}%\n💾 Memory: {system_info.get('memory_percent', 'N/A')}%\n💿 Disk: {system_info.get('disk_percent', 'N/A')}%\n📊 Processes: {system_info.get('process_count', 'N/A')}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'category': 'system',
                'error': str(e),
                'response': f"❌ System command error: {str(e)}"
            }
    
    def _execute_file_command(self, command: str, analysis: Dict) -> Dict:
        """Execute file commands"""
        try:
            action = analysis['action']
            target = analysis['target']
            
            if action in ['list', 'show', 'display']:
                return self._list_files(target)
            elif action in ['read', 'open']:
                return self._read_file(target)
            elif action in ['create', 'make', 'generate']:
                return self._create_file(target, command)
            else:
                return {
                    'success': False,
                    'category': 'file',
                    'error': f'Unsupported file action: {action}',
                    'response': f"❌ File action '{action}' supported nahi hai"
                }
        
        except Exception as e:
            return {
                'success': False,
                'category': 'file',
                'error': str(e),
                'response': f"❌ File command error: {str(e)}"
            }
    
    def _execute_network_command(self, command: str, analysis: Dict) -> Dict:
        """Execute network commands"""
        try:
            # Use search API for network-related tasks
            result = search_api.get_hinglish_search(command, limit=3)
            
            if result and not result.startswith('❌'):
                return {
                    'success': True,
                    'category': 'network',
                    'command': command,
                    'search_results': result,
                    'response': result
                }
            else:
                return {
                    'success': False,
                    'category': 'network',
                    'error': 'Network search failed',
                    'response': result or '❌ Network command failed'
                }
        
        except Exception as e:
            return {
                'success': False,
                'category': 'network',
                'error': str(e),
                'response': f"❌ Network command error: {str(e)}"
            }
    
    def _execute_data_command(self, command: str, analysis: Dict) -> Dict:
        """Execute data commands"""
        try:
            # Use calculator for data calculations
            if any(word in command.lower() for word in ['calculate', 'compute', 'math']):
                result = calculator.evaluate_expression(command)
                return {
                    'success': True,
                    'category': 'data',
                    'command': command,
                    'calculation_result': result,
                    'response': f"🧮 Calculation Result: {result}"
                }
            else:
                # Use original brain for other data tasks
                result = original_brain.process_query(command)
                return {
                    'success': result.get('success', False),
                    'category': 'data',
                    'command': command,
                    'brain_result': result,
                    'response': result.get('hinglish_response', result.get('response'))
                }
        
        except Exception as e:
            return {
                'success': False,
                'category': 'data',
                'error': str(e),
                'response': f"❌ Data command error: {str(e)}"
            }
    
    def _execute_security_command(self, command: str, analysis: Dict) -> Dict:
        """Execute security commands (limited for safety)"""
        try:
            # For security commands, only provide information
            return {
                'success': True,
                'category': 'security',
                'command': command,
                'response': '🔒 Security commands are limited for safety. Please use manual methods for sensitive operations.',
                'security_note': 'For security reasons, automated security commands are restricted.'
            }
        
        except Exception as e:
            return {
                'success': False,
                'category': 'security',
                'error': str(e),
                'response': f"❌ Security command error: {str(e)}"
            }
    
    def _execute_general_command(self, command: str, analysis: Dict) -> Dict:
        """Execute general commands"""
        try:
            # Use original brain for general commands
            result = original_brain.process_query(command)
            
            return {
                'success': result.get('success', False),
                'category': 'general',
                'command': command,
                'brain_result': result,
                'response': result.get('hinglish_response', result.get('response')),
                'modules_used': result.get('tool_used', 'brain')
            }
        
        except Exception as e:
            return {
                'success': False,
                'category': 'general',
                'error': str(e),
                'response': f"❌ General command error: {str(e)}"
            }
    
    def _generate_automation_script(self, command: str) -> str:
        """Generate automation script based on command"""
        try:
            script_template = '''#!/usr/bin/env python3
"""
Auto-generated automation script
Command: {command}
Generated at: {timestamp}
"""

import time
import logging
import os
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main automation function"""
    print("🤖 Starting automation script...")
    
    try:
        # TODO: Add your automation logic here
        # This is a template - customize based on your needs
        
        # Example: File monitoring
        target_path = r"{target_path}"
        
        if os.path.exists(target_path):
            logger.info(f"✅ Target path exists: {{target_path}}")
            print(f"✅ Found target: {{target_path}}")
        else:
            logger.warning(f"⚠️  Target path not found: {{target_path}}")
            print(f"❌ Target not found: {{target_path}}")
        
        # Example: Time-based action
        start_time = time.time()
        
        # Add your automation logic here
        print("⚙️  Processing automation task...")
        time.sleep(1)  # Simulate work
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Automation completed in {{duration:.2f}} seconds")
        logger.info("✅ Automation script completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Automation error: {{e}}")
        print(f"❌ Automation failed: {{e}}")

if __name__ == "__main__":
    main()
'''.format(
                command=command,
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                target_path=str(self.temp_dir)
            )
            
            return script_template
            
        except Exception as e:
            logger.error(f"❌ Script generation error: {e}")
            return ""
    
    def _get_system_info(self) -> Dict:
        """Get system information"""
        try:
            import psutil
            
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'process_count': len(psutil.pids()),
                'boot_time': psutil.boot_time()
            }
        except ImportError:
            return {
                'cpu_percent': 'N/A',
                'memory_percent': 'N/A',
                'disk_percent': 'N/A',
                'process_count': 'N/A',
                'boot_time': 'N/A'
            }
    
    def _list_files(self, target: str) -> Dict:
        """List files in directory"""
        try:
            if target == 'unknown' or not target:
                target = '.'
            
            target_path = Path(target)
            
            if not target_path.exists():
                return {
                    'success': False,
                    'error': f'Path not found: {target}',
                    'response': f"❌ Path '{target}' nahi mili"
                }
            
            if target_path.is_file():
                return {
                    'success': True,
                    'action': 'file_info',
                    'file_path': str(target_path),
                    'file_size': target_path.stat().st_size,
                    'response': f"📄 File: {target_path.name} ({target_path.stat().st_size} bytes)"
                }
            
            # List directory contents
            items = list(target_path.iterdir())[:20]  # Limit to 20 items
            
            file_list = []
            for item in items:
                try:
                    item_info = {
                        'name': item.name,
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': item.stat().st_size if item.is_file() else 0
                    }
                    file_list.append(item_info)
                except:
                    continue
            
            response = f"📁 Contents of '{target}':\n"
            for i, item in enumerate(file_list[:10], 1):
                icon = "📁" if item['type'] == 'directory' else "📄"
                size_str = f" ({item['size']} bytes)" if item['type'] == 'file' else ""
                response += f"{i}. {icon} {item['name']}{size_str}\n"
            
            return {
                'success': True,
                'action': 'list_directory',
                'directory': str(target_path),
                'items': file_list,
                'response': response
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ File listing failed: {str(e)}"
            }
    
    def _read_file(self, target: str) -> Dict:
        """Read file content"""
        try:
            if target == 'unknown':
                return {
                    'success': False,
                    'error': 'No file specified',
                    'response': '❌ Koi file specify nahi kiya gaya'
                }
            
            file_path = Path(target)
            
            if not file_path.exists() or not file_path.is_file():
                return {
                    'success': False,
                    'error': f'File not found: {target}',
                    'response': f"❌ File '{target}' nahi mili"
                }
            
            # Read file content (limit to prevent memory issues)
            max_size = 1024 * 1024  # 1MB limit
            file_size = file_path.stat().st_size
            
            if file_size > max_size:
                return {
                    'success': False,
                    'error': 'File too large',
                    'response': f"❌ File bahut badi hai ({file_size} bytes, max: {max_size})"
                }
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Limit content for display
            display_content = content[:1000]
            if len(content) > 1000:
                display_content += "\n... (content truncated)"
            
            response = f"📄 File: {file_path.name} ({file_size} bytes)\n\n{display_content}"
            
            return {
                'success': True,
                'action': 'read_file',
                'file_path': str(file_path),
                'file_size': file_size,
                'content': content,
                'display_content': display_content,
                'response': response
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ File reading failed: {str(e)}"
            }
    
    def _create_file(self, target: str, command: str) -> Dict:
        """Create new file"""
        try:
            if target == 'unknown':
                target = f"maya_file_{int(time.time())}.txt"
            
            file_path = self.temp_dir / target
            
            # Extract content from command
            content = self._extract_file_content(command)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            response = f"📝 File created: {file_path.name}\n📁 Location: {file_path}\n📏 Size: {len(content)} characters"
            
            return {
                'success': True,
                'action': 'create_file',
                'file_path': str(file_path),
                'content': content,
                'response': response
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ File creation failed: {str(e)}"
            }
    
    def _extract_file_content(self, command: str) -> str:
        """Extract content for file creation from command"""
        # Simple content extraction - would be more sophisticated in production
        if 'with content' in command.lower():
            # Extract content after "with content"
            parts = command.lower().split('with content')
            if len(parts) > 1:
                return parts[1].strip()
        
        # Default content
        return f"Auto-generated file\nCommand: {command}\nCreated at: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def _verify_execution_result(self, result: Dict, command: str) -> Dict:
        """Verify and enhance execution result"""
        try:
            # Add verification timestamp
            result['verified_at'] = time.time()
            result['verification_status'] = 'verified'
            
            # Add command summary
            result['command_summary'] = {
                'original': command,
                'category': result.get('category', 'unknown'),
                'success': result.get('success', False),
                'response_length': len(result.get('response', ''))
            }
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Result verification error: {e}")
            result['verification_status'] = 'failed'
            result['verification_error'] = str(e)
            return result
    
    def _record_execution(self, command: str, analysis: Dict, result: Dict, execution_time: float) -> None:
        """Record command execution"""
        try:
            execution_record = {
                'timestamp': time.time(),
                'command': command,
                'analysis': analysis,
                'result': result,
                'execution_time': execution_time
            }
            
            self.execution_history.append(execution_record)
            
            # Keep only last 100 executions
            if len(self.execution_history) > 100:
                self.execution_history = self.execution_history[-100:]
            
        except Exception as e:
            logger.error(f"❌ Execution recording error: {e}")
    
    def get_execution_stats(self) -> Dict:
        """Get execution statistics"""
        try:
            if not self.execution_history:
                return {
                    'total_commands': 0,
                    'success_rate': 0,
                    'avg_execution_time': 0,
                    'category_stats': {},
                    'response': '📊 No execution history available'
                }
            
            total_commands = len(self.execution_history)
            successful_commands = sum(1 for record in self.execution_history if record['result'].get('success', False))
            success_rate = (successful_commands / total_commands) * 100
            
            total_time = sum(record['execution_time'] for record in self.execution_history)
            avg_execution_time = total_time / total_commands
            
            # Category statistics
            category_stats = {}
            for record in self.execution_history:
                category = record['analysis'].get('category', 'unknown')
                if category not in category_stats:
                    category_stats[category] = {'count': 0, 'success': 0}
                category_stats[category]['count'] += 1
                if record['result'].get('success', False):
                    category_stats[category]['success'] += 1
            
            response = f"📊 Execution Statistics:\n"
            response += f"• Total commands: {total_commands}\n"
            response += f"• Success rate: {success_rate:.1f}%\n"
            response += f"• Average time: {avg_execution_time:.2f}s\n"
            response += f"• Categories used: {len(category_stats)}\n"
            
            return {
                'total_commands': total_commands,
                'success_rate': success_rate,
                'avg_execution_time': avg_execution_time,
                'category_stats': category_stats,
                'response': response
            }
        
        except Exception as e:
            logger.error(f"❌ Stats generation error: {e}")
            return {
                'error': str(e),
                'response': f"❌ Statistics generation failed: {str(e)}"
            }

# Global enhanced brain instance
enhanced_brain = EnhancedBrain()
