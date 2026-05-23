"""
Maya AI Autonomous Agent
Complex multi-step task execution with automatic decision making
"""

import logging
import subprocess
import os
import glob
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from config import DEBUG_MODE

# Optional imports for specialized tasks
try:
    import win32com.client
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

logger = logging.getLogger(__name__)

class AutonomousAgent:
    """Autonomous agent for complex multi-step tasks"""
    
    def __init__(self):
        self.task_queue = []
        self.execution_history = []
        self.capabilities = {
            'screenshot': self._take_screenshot,
            'play_music': self._play_music,
            'open_web': self._open_web,
            'web_search': self._web_search,
            'create_pdf': self._create_pdf,
            'create_word_doc': self._create_word_doc,
            'research': self._research_and_document,
            'search_drives': self._search_drives,
            'find_images': self._find_images,
            'create_folder': self._create_folder,
            'scan_music_players': self._scan_music_players,
            'search_music_device': self._search_music_device,
            'open_office': self._open_office
        }
    
    def process_request(self, request: str) -> Dict[str, Any]:
        """
        Process complex user request and break it down into tasks
        Returns execution plan and results
        """
        request_lower = request.lower()
        
        # Analyze request and create task plan
        task_plan = self._create_task_plan(request_lower)
        
        if not task_plan:
            return {
                'success': False,
                'message': 'Could not determine task plan for this request',
                'request': request
            }
        
        logger.info(f"🤖 Agent task plan: {task_plan}")
        
        # Execute tasks
        results = []
        for task in task_plan:
            result = self._execute_task(task)
            results.append(result)
            self.execution_history.append(result)
        
        return {
            'success': True,
            'request': request,
            'task_plan': task_plan,
            'results': results,
            'summary': self._generate_summary(results)
        }
    
    def _create_task_plan(self, request: str) -> List[Dict[str, Any]]:
        """Break down complex request into executable tasks"""
        tasks = []
        request_lower = request.lower()
        
        # Screenshot task
        if any(word in request_lower for word in ['screenshot', 'screen', 'capture screen', 'what is on screen']):
            # Create organized folder for screenshots
            folder_name = f"screenshots_{datetime.now().strftime('%Y%m%d')}"
            tasks.append({
                'type': 'create_folder',
                'description': f'Create folder {folder_name}',
                'params': {'folder_name': folder_name}
            })
            tasks.append({
                'type': 'screenshot',
                'description': 'Capture screenshot of current screen',
                'params': {'folder': folder_name}
            })
        
        # Music task
        if any(word in request_lower for word in ['play music', 'music', 'song', 'play']):
            music_query = self._extract_music_query(request_lower)
            # Only search device if there's a specific song query
            if music_query and len(music_query) > 2:  # Minimum 3 characters
                tasks.append({
                    'type': 'scan_music_players',
                    'description': 'Scan device for music players',
                    'params': {}
                })
                tasks.append({
                    'type': 'search_music_device',
                    'description': f'Search device for: {music_query}',
                    'params': {'query': music_query}
                })
                tasks.append({
                    'type': 'play_music',
                    'description': 'Play music',
                    'params': {'query': music_query}
                })
            else:
                tasks.append({
                    'type': 'scan_music_players',
                    'description': 'Scan device for music players',
                    'params': {}
                })
                tasks.append({
                    'type': 'play_music',
                    'description': 'Play music',
                    'params': {'query': ''}
                })
        
        # Web task
        if any(word in request_lower for word in ['open web', 'open browser', 'website', 'url']):
            tasks.append({
                'type': 'open_web',
                'description': 'Open web browser',
                'params': {'url': self._extract_url(request_lower)}
            })
        
        # Search drives task
        if any(word in request_lower for word in ['search drives', 'search drive', 'list drives', 'available drives']):
            tasks.append({
                'type': 'search_drives',
                'description': 'Search available drives on device',
                'params': {}
            })
        
        # Find images task
        if any(word in request_lower for word in ['find pictures', 'find images', 'search pictures', 'search images', 'find photos']):
            tasks.append({
                'type': 'find_images',
                'description': 'Find images on device',
                'params': {
                    'drive': self._extract_drive(request_lower),
                    'description': self._extract_description(request_lower)
                }
            })
        
        # Create folder task
        if any(word in request_lower for word in ['create folder', 'make folder', 'new folder']):
            folder_name = self._extract_folder_name(request_lower)
            if folder_name:
                tasks.append({
                    'type': 'create_folder',
                    'description': f'Create folder {folder_name}',
                    'params': {'folder_name': folder_name}
                })
        
        # Research and document task
        if any(word in request_lower for word in ['research', 'make pdf', 'create pdf', 'document', 'report', 'search and create', 'create a file', 'save as pdf', 'save the file as pdf']):
            topic = self._extract_topic(request)
            if topic:
                # Special case: MS Office + Research + PDF
                if 'office' in request_lower or 'word' in request_lower:
                    tasks.append({
                        'type': 'research',
                        'description': f'Research and create Word document about {topic}',
                        'params': {'topic': topic, 'format': 'word', 'open_after': True, 'save_as_pdf': 'pdf' in request_lower}
                    })
                else:
                    tasks.append({
                        'type': 'research',
                        'description': f'Research and create document about {topic}',
                        'params': {'topic': topic, 'format': self._detect_format(request_lower)}
                    })
        
        return tasks
    
    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task"""
        task_type = task['type']
        
        if task_type in self.capabilities:
            try:
                result = self.capabilities[task_type](task.get('params', {}))
                return {
                    'task': task_type,
                    'description': task['description'],
                    'success': True,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"❌ Task execution failed: {e}")
                return {
                    'task': task_type,
                    'description': task['description'],
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        else:
            return {
                'task': task_type,
                'description': task['description'],
                'success': False,
                'error': f'Unknown task type: {task_type}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _take_screenshot(self, params: Dict[str, Any]) -> str:
        """Capture screenshot of current screen"""
        try:
            import pyautogui
            from PIL import Image
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            
            # Get folder from params or default
            folder = params.get('folder', 'screenshots')
            
            # Save with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = f"{folder}/screenshot_{timestamp}.png"
            
            # Create directory if not exists
            os.makedirs(folder, exist_ok=True)
            
            screenshot.save(screenshot_path)
            
            logger.info(f"📸 Screenshot saved to {screenshot_path}")
            return f"Screenshot saved to {screenshot_path}"
        except ImportError:
            # Fallback to Windows API
            try:
                from ctypes import windll
                import win32gui
                import win32ui
                from win32con import SRCCOPY
                
                hwnd = win32gui.GetDesktopWindow()
                width = win32api.GetSystemMetrics(0)
                height = win32api.GetSystemMetrics(1)
                
                hdesktop = win32gui.GetDesktopWindow()
                hwndDC = win32gui.GetWindowDC(hdesktop)
                mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                saveDC = mfcDC.CreateCompatibleDC()
                
                saveBitMap = win32ui.CreateBitmap()
                saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
                saveDC.SelectObject(saveBitMap)
                
                result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), SRCCOPY)
                
                folder = params.get('folder', 'screenshots')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                screenshot_path = f"{folder}/screenshot_{timestamp}.bmp"
                os.makedirs(folder, exist_ok=True)
                
                saveBitMap.SaveBitmapFile(saveDC, screenshot_path)
                
                # Cleanup
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hdesktop, hwndDC)
                
                logger.info(f"📸 Screenshot saved to {screenshot_path}")
                return f"Screenshot saved to {screenshot_path}"
            except Exception as e:
                return f"Screenshot failed: {str(e)}"
        except Exception as e:
            return f"Screenshot failed: {str(e)}"
    
    def _play_music(self, params: Dict[str, Any]) -> str:
        """Play music with smart search (device first, then web)"""
        query = params.get('query', '')
        
        try:
            # First try to search device for the song
            if query:
                device_results = self._search_music_device({'query': query})
                # Check if music files were actually found (not just "No music files found")
                if device_results and device_results.startswith('Found') and 'music file(s)' in device_results:
                    # Play from device
                    return f"Playing from device: {query}"
                else:
                    # Search web for the song
                    logger.info(f"🎵 Song not found on device, searching web for: {query}")
                    web_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                    self._open_web({'url': web_url})
                    return f"Song '{query}' not found on device. Opened web search on YouTube for: {query}"
            else:
                # Open default music player
                if os.name == 'nt':  # Windows
                    subprocess.run(['start', 'wmplayer'], shell=True)
                    return "Windows Media Player opened"
                else:
                    subprocess.run(['xdg-open', '--audio'], shell=True)
                    return "Default music player opened"
        except Exception as e:
            return f"Failed to play music: {str(e)}"
    
    def _open_web(self, params: Dict[str, Any]) -> str:
        """Open web browser"""
        url = params.get('url', 'https://www.google.com')
        
        try:
            import webbrowser
            webbrowser.open(url)
            return f"Opened {url} in browser"
        except Exception as e:
            return f"Failed to open web: {str(e)}"
    
    def _web_search(self, params: Dict[str, Any]) -> str:
        """Perform web search"""
        query = params.get('query', '')
        
        try:
            from modules.tools import search_api
            results = search_api.search(query)
            return f"Search results for '{query}': {len(results)} results found"
        except Exception as e:
            return f"Search failed: {str(e)}"
    
    def _create_pdf(self, params: Dict[str, Any]) -> str:
        """Create PDF from content"""
        content = params.get('content', '')
        filename = params.get('filename', f'output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
        
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            
            pdf_path = f"documents/{filename}"
            os.makedirs('documents', exist_ok=True)
            
            c = canvas.Canvas(pdf_path, pagesize=letter)
            c.drawString(100, 750, "Generated by Maya AI")
            c.drawString(100, 730, f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            y = 700
            for line in content.split('\n'):
                c.drawString(100, y, line)
                y -= 20
                if y < 50:
                    c.showPage()
                    y = 750
            
            c.save()
            return f"PDF created: {pdf_path}"
        except Exception as e:
            return f"PDF creation failed: {str(e)}"
    
    def _create_word_doc(self, params: Dict[str, Any]) -> str:
        """Create Word document with optional MS Word automation and images"""
        content = params.get('content', '')
        filename = params.get('filename', f'document_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx')
        open_after = params.get('open_after', False)
        save_as_pdf = params.get('save_as_pdf', False)
        images = params.get('images', []) # List of local image paths
        
        try:
            doc_path = os.path.abspath(f"documents/{filename}")
            os.makedirs('documents', exist_ok=True)
            
            # Method 1: Use win32com if available (Actual MS Word)
            if HAS_WIN32COM and (open_after or save_as_pdf or images):
                try:
                    word = win32com.client.Dispatch("Word.Application")
                    word.Visible = open_after
                    doc = word.Documents.Add()
                    
                    # Add content
                    selection = word.Selection
                    selection.Font.Name = "Arial"
                    selection.Font.Size = 14
                    selection.TypeText("Generated by Maya AI\n")
                    selection.Font.Size = 11
                    selection.TypeText(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    # Add images if provided
                    for img_path in images:
                        if os.path.exists(img_path):
                            try:
                                selection.InlineShapes.AddPicture(os.path.abspath(img_path))
                                selection.TypeText("\n\n")
                            except Exception as img_e:
                                logger.error(f"❌ Failed to insert image {img_path}: {img_e}")
                    
                    selection.TypeText(content)
                    
                    # Save as docx
                    doc.SaveAs(doc_path)
                    
                    # Save as PDF if requested
                    if save_as_pdf:
                        pdf_path = doc_path.replace('.docx', '.pdf')
                        # wdFormatPDF = 17
                        doc.SaveAs(pdf_path, FileFormat=17)
                        logger.info(f"✅ PDF saved via Word: {pdf_path}")
                    
                    if not open_after:
                        doc.Close()
                        word.Quit()
                    
                    return f"Word document created: {doc_path}" + (f" and PDF: {pdf_path}" if save_as_pdf else "")
                except Exception as e:
                    logger.warning(f"⚠️ MS Word automation failed, falling back to python-docx: {e}")
            
            # Method 2: Fallback to python-docx
            from docx import Document
            from docx.shared import Inches
            
            doc = Document()
            doc.add_heading('Generated by Maya AI', 0)
            doc.add_paragraph(f'Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            
            # Add images
            for img_path in images:
                if os.path.exists(img_path):
                    doc.add_picture(img_path, width=Inches(4.0))
            
            doc.add_paragraph(content)
            
            doc.save(doc_path)
            
            if open_after:
                os.startfile(doc_path)
                
            return f"Word document created: {doc_path}"
        except Exception as e:
            return f"Word document creation failed: {str(e)}"
    
    def _download_image(self, url: str, filename: str) -> str:
        """Download image from URL"""
        try:
            import requests
            os.makedirs('temp', exist_ok=True)
            path = os.path.join('temp', filename)
            
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 200:
                with open(path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return path
            return None
        except Exception as e:
            logger.error(f"❌ Image download failed: {e}")
            return None

    def _open_office(self, params: Dict[str, Any]) -> str:
        """Open MS Office application"""
        app = params.get('app', 'word').lower()
        try:
            if app == 'word':
                subprocess.Popen('winword')
                return "MS Word opened"
            elif app == 'excel':
                subprocess.Popen('excel')
                return "MS Excel opened"
            elif app == 'powerpoint':
                subprocess.Popen('powerpnt')
                return "MS PowerPoint opened"
            else:
                return f"Unknown office app: {app}"
        except Exception as e:
            return f"Failed to open {app}: {str(e)}"

    def _research_and_document(self, params: Dict[str, Any]) -> str:
        """Research topic and create document using AI models and images"""
        topic = params.get('topic', '')
        format = params.get('format', 'pdf')
        save_as_pdf = params.get('save_as_pdf', False)
        open_after = params.get('open_after', False)
        include_images = params.get('include_images', True)
        
        try:
            from modules.tools import search_api
            from modules.models import local_models
            
            # Perform web search
            logger.info(f"🔍 Researching: {topic}")
            search_results = search_api.search(topic)
            
            if not search_results:
                return f"No search results found for: {topic}"
            
            # Search for images if requested
            local_images = []
            if include_images:
                logger.info(f"🖼️ Searching for images: {topic}")
                image_results = search_api.search_images(topic, limit=2)
                for i, img_res in enumerate(image_results):
                    img_url = img_res.get('image')
                    if img_url:
                        img_path = self._download_image(img_url, f"research_{i}_{int(time.time())}.jpg")
                        if img_path:
                            local_images.append(img_path)
            
            # Use AI to generate content from search results
            context = "\n".join([str(r) for r in search_results[:5]])
            prompt = f"""Write a detailed research report about '{topic}' based on these search results:
{context}

Format the report with:
1. Title
2. Introduction
3. Key Findings
4. Future Outlook
5. Conclusion

Write in a professional yet engaging tone."""
            
            logger.info("🧠 Generating report content using local AI model...")
            model_response = local_models.smart_routing(prompt, "general_chat")
            content = model_response.get('response', "Failed to generate AI content.")
            
            # Create document
            filename_base = f'research_{topic.replace(" ", "_")}'
            
            if format == 'word':
                return self._create_word_doc({
                    'content': content,
                    'filename': f'{filename_base}.docx',
                    'open_after': open_after,
                    'save_as_pdf': save_as_pdf,
                    'images': local_images
                })
            else:
                # Default to PDF
                return self._create_pdf({
                    'content': content,
                    'filename': f'{filename_base}.pdf'
                })
                
        except Exception as e:
            logger.error(f"❌ Research failed: {e}")
            return f"Research failed: {str(e)}"
    
    def _search_drives(self, params: Dict[str, Any]) -> str:
        """Search available drives on device"""
        try:
            if os.name == 'nt':  # Windows
                import win32api
                drives = win32api.GetLogicalDriveStrings()
                drive_list = drives.split('\000')[:-1]  # Remove empty string at end
                
                result = "Available drives:\n"
                for drive in drive_list:
                    try:
                        free_space = win32api.GetDiskFreeSpaceEx(drive)[2]
                        free_space_gb = free_space / (1024**3)
                        result += f"  {drive} - {free_space_gb:.2f} GB free\n"
                    except:
                        result += f"  {drive} - (not accessible)\n"
                
                return result
            else:
                # Unix-like systems
                import subprocess
                result = subprocess.run(['df', '-h'], capture_output=True, text=True)
                return f"Available drives:\n{result.stdout}"
        except Exception as e:
            return f"Drive search failed: {str(e)}"
    
    def _find_images(self, params: Dict[str, Any]) -> str:
        """Find images on device with metadata"""
        drive = params.get('drive', 'C:\\')
        description = params.get('description', '')
        
        try:
            # Limit search to common image folders to avoid slow full-drive search
            common_folders = [
                os.path.join(drive, 'Users'),
                os.path.join(drive, 'Documents'),
                os.path.join(drive, 'Pictures'),
                os.path.join(drive, 'Desktop'),
                os.path.join(drive, 'Downloads')
            ]
            
            # Image extensions to search for
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff']
            
            image_files = []
            for folder in common_folders:
                if not os.path.exists(folder):
                    continue
                for ext in image_extensions:
                    # Search recursively but limited to common folders
                    search_path = os.path.join(folder, '**', ext)
                    try:
                        files = glob.glob(search_path, recursive=True)
                        image_files.extend(files)
                    except PermissionError:
                        continue
            
            # Filter by description if provided
            if description:
                image_files = [f for f in image_files if description.lower() in f.lower()]
            
            # Get file metadata
            result = f"Found {len(image_files)} images on {drive}\n\n"
            
            # Show first 20 results with metadata
            for i, image_path in enumerate(image_files[:20], 1):
                try:
                    stat = os.stat(image_path)
                    size = stat.st_size / 1024  # KB
                    created = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                    result += f"{i}. {os.path.basename(image_path)}\n"
                    result += f"   Size: {size:.1f} KB\n"
                    result += f"   Created: {created}\n"
                    result += f"   Path: {image_path}\n\n"
                except:
                    result += f"{i}. {image_path}\n\n"
            
            if len(image_files) > 20:
                result += f"... and {len(image_files) - 20} more images\n"
            
            return result
        except Exception as e:
            return f"Image search failed: {str(e)}"
    
    def _create_folder(self, params: Dict[str, Any]) -> str:
        """Create a new folder"""
        folder_name = params.get('folder_name', '')
        
        try:
            # Create folder in current directory
            folder_path = folder_name
            os.makedirs(folder_path, exist_ok=True)
            
            logger.info(f"📁 Folder created: {folder_path}")
            return f"Folder created: {folder_path}"
        except Exception as e:
            return f"Folder creation failed: {str(e)}"
    
    def _scan_music_players(self, params: Dict[str, Any]) -> str:
        """Scan device for available music players"""
        try:
            players = []
            
            if os.name == 'nt':  # Windows
                # Check for common Windows music players
                common_players = [
                    ('Windows Media Player', 'wmplayer.exe'),
                    ('Spotify', 'Spotify.exe'),
                    ('iTunes', 'iTunes.exe'),
                    ('VLC Media Player', 'vlc.exe'),
                    ('Groove Music', 'Microsoft.ZuneMusic.exe'),
                    ('Winamp', 'winamp.exe'),
                ]
                
                for player_name, exe_name in common_players:
                    try:
                        # Search in Program Files
                        program_paths = [
                            os.path.join(os.environ.get('ProgramFiles', ''), exe_name),
                            os.path.join(os.environ.get('ProgramFiles(x86)', ''), exe_name),
                            os.path.join(os.environ.get('LOCALAPPDATA', ''), exe_name),
                        ]
                        
                        for path in program_paths:
                            if os.path.exists(path):
                                players.append(player_name)
                                break
                    except:
                        continue
                
                # Also check via registry for installed apps
                try:
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths")
                    i = 0
                    while True:
                        try:
                            app_name = winreg.EnumKey(key, i)
                            if any(player.lower() in app_name.lower() for player in ['music', 'player', 'spotify', 'itunes', 'vlc']):
                                players.append(app_name)
                            i += 1
                        except:
                            break
                    winreg.CloseKey(key)
                except:
                    pass
            
            else:
                # Unix-like systems
                common_players = ['vlc', 'spotify', 'rhythmbox', 'audacious', 'xmms']
                for player in common_players:
                    try:
                        subprocess.run(['which', player], capture_output=True, check=True)
                        players.append(player)
                    except:
                        continue
            
            if players:
                result = f"Found {len(players)} music player(s):\n"
                for player in players:
                    result += f"  - {player}\n"
                return result
            else:
                return "No music players found on device. Will use web browser for playback."
                
        except Exception as e:
            return f"Music player scan failed: {str(e)}"
    
    def _search_music_device(self, params: Dict[str, Any]) -> str:
        """Search device for music files"""
        query = params.get('query', '').lower()
        
        try:
            # Common music file extensions
            music_extensions = ['*.mp3', '*.wav', '*.flac', '*.m4a', '*.wma', '*.ogg', '*.aac']
            
            # Search in common music folders
            common_folders = [
                os.path.join(os.environ.get('USERPROFILE', ''), 'Music'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'Documents'),
            ]
            
            music_files = []
            for folder in common_folders:
                if not os.path.exists(folder):
                    continue
                for ext in music_extensions:
                    search_path = os.path.join(folder, '**', ext)
                    try:
                        files = glob.glob(search_path, recursive=True)
                        music_files.extend(files)
                    except PermissionError:
                        continue
            
            # Filter by query if provided
            if query:
                music_files = [f for f in music_files if query in os.path.basename(f).lower()]
            
            if music_files:
                result = f"Found {len(music_files)} music file(s) on device\n\n"
                for i, music_path in enumerate(music_files[:10], 1):
                    try:
                        stat = os.stat(music_path)
                        size = stat.st_size / (1024 * 1024)  # MB
                        result += f"{i}. {os.path.basename(music_path)}\n"
                        result += f"   Size: {size:.2f} MB\n"
                        result += f"   Path: {music_path}\n\n"
                    except:
                        result += f"{i}. {music_path}\n\n"
                
                if len(music_files) > 10:
                    result += f"... and {len(music_files) - 10} more files\n"
                
                return result
            else:
                return f"No music files found matching '{query}' on device"
                
        except Exception as e:
            return f"Music search failed: {str(e)}"
    
    def _extract_music_query(self, request: str) -> str:
        """Extract music query from request"""
        words = request.replace('play music', '').replace('play', '').replace('music', '').strip()
        return words
    
    def _extract_drive(self, request: str) -> str:
        """Extract drive letter from request"""
        import re
        drive_match = re.search(r'[A-Za-z]:', request)
        if drive_match:
            return drive_match.group(0) + '\\'
        return 'C:\\'
    
    def _extract_description(self, request: str) -> str:
        """Extract description/filter from request"""
        # Remove common words
        words_to_remove = ['find', 'pictures', 'images', 'photos', 'on', 'drive', 'search']
        description = request
        for word in words_to_remove:
            description = description.replace(word, '')
        return description.strip()
    
    def _extract_folder_name(self, request: str) -> str:
        """Extract folder name from request"""
        import re
        # Remove common words
        words_to_remove = ['create', 'folder', 'make', 'new']
        folder_name = request
        for word in words_to_remove:
            folder_name = folder_name.replace(word, '')
        return folder_name.strip()
    
    def _extract_url(self, request: str) -> str:
        """Extract URL from request"""
        import re
        url_match = re.search(r'https?://[^\s]+', request)
        if url_match:
            return url_match.group(0)
        return 'https://www.google.com'
    
    def _extract_topic(self, request: str) -> str:
        """Extract research topic from request"""
        # Remove common words
        words_to_remove = [
            'research', 'about', 'make', 'pdf', 'create', 'document', 
            'search', 'and', 'for', 'open', 'ms', 'office', 'a', 'file', 
            'on', 'using', 'data', 'from', 'web', 'save', 'the', 'as'
        ]
        topic = request.lower()
        for word in words_to_remove:
            # Use regex to replace whole words only to avoid partial replacements
            import re
            topic = re.sub(rf'\b{word}\b', '', topic)
        
        return topic.strip()
    
    def _detect_format(self, request: str) -> str:
        """Detect desired document format"""
        if 'pdf' in request.lower():
            return 'pdf'
        elif 'word' in request.lower() or 'doc' in request.lower():
            return 'word'
        else:
            return 'pdf'  # Default
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> str:
        """Generate summary of execution results"""
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        summary = f"Executed {total} task(s), {successful} successful\n"
        
        for result in results:
            status = "✅" if result['success'] else "❌"
            summary += f"{status} {result['description']}\n"
        
        return summary

# Singleton
autonomous_agent = AutonomousAgent()

if DEBUG_MODE:
    print("🤖 Autonomous Agent initialized")
