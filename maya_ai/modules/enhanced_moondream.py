"""
Maya AI Enhanced Moondream Integration
Advanced PDF, image, document understanding with OCR and analysis
"""

import logging
import time
import os
import json
from typing import Dict, List, Optional, Union, BinaryIO
from pathlib import Path
import base64
from io import BytesIO

# PDF processing
try:
    import PyPDF2
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("⚠️  PDF libraries not available")

# Image processing
try:
    from PIL import Image
    import pytesseract
    IMAGE_AVAILABLE = True
except ImportError:
    IMAGE_AVAILABLE = False
    logging.warning("⚠️  Image processing libraries not available")

# Document processing
try:
    import docx
    DOC_AVAILABLE = True
except ImportError:
    DOC_AVAILABLE = False
    logging.warning("⚠️  Document libraries not available")

from config import DEBUG_MODE

logger = logging.getLogger(__name__)

class EnhancedMoondream:
    """Enhanced Moondream integration for document and image analysis"""
    
    def __init__(self):
        self.supported_formats = {
            'pdf': self._process_pdf,
            'jpg': self._process_image,
            'jpeg': self._process_image,
            'png': self._process_image,
            'bmp': self._process_image,
            'tiff': self._process_image,
            'docx': self._process_docx,
            'doc': self._process_docx,
            'txt': self._process_text
        }
        
        # Analysis types
        self.analysis_types = {
            'summary': 'Provide a comprehensive summary of this document/image',
            'extract': 'Extract all text and key information from this document/image',
            'analyze': 'Analyze this document/image in detail and provide insights',
            'ocr': 'Perform OCR text extraction from this image',
            'translate': 'Extract and translate the content from this document/image',
            'compare': 'Analyze this document/image for comparison purposes'
        }
        
        if DEBUG_MODE:
            logger.info("📄 Enhanced Moondream initialized")
            logger.info(f"📋 Supported formats: {list(self.supported_formats.keys())}")
    
    def process_file(self, file_path: str, analysis_type: str = 'summary', 
                     query: str = None, context: Dict = None) -> Dict:
        """Process uploaded file with specified analysis type"""
        start_time = time.time()
        
        try:
            # Validate file
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': 'File not found',
                    'response': f"❌ File '{file_path}' nahi mili"
                }
            
            # Get file info
            file_info = self._get_file_info(file_path)
            file_extension = file_info['extension'].lower()
            
            # Check if format is supported
            if file_extension not in self.supported_formats:
                return {
                    'success': False,
                    'error': f'Unsupported format: {file_extension}',
                    'response': f"❌ Format '{file_extension}' supported nahi hai"
                }
            
            # Process file
            processor = self.supported_formats[file_extension]
            processed_content = processor(file_path)
            
            if not processed_content:
                return {
                    'success': False,
                    'error': 'File processing failed',
                    'response': f"❌ File processing failed"
                }
            
            # Perform analysis
            analysis_result = self._perform_analysis(processed_content, analysis_type, query, file_info)
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'file_info': file_info,
                'processed_content': processed_content,
                'analysis_type': analysis_type,
                'analysis_result': analysis_result,
                'processing_time': processing_time,
                'response': analysis_result.get('response', '❌ Analysis failed')
            }
            
        except Exception as e:
            logger.error(f"❌ File processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ File processing mein error: {str(e)}"
            }
    
    def _get_file_info(self, file_path: str) -> Dict:
        """Get file information"""
        try:
            file_path_obj = Path(file_path)
            stat = file_path_obj.stat()
            
            return {
                'name': file_path_obj.name,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'extension': file_path_obj.suffix[1:] if file_path_obj.suffix else '',
                'created': stat.st_ctime,
                'modified': stat.st_mtime
            }
        except Exception as e:
            logger.error(f"❌ File info error: {e}")
            return {'name': 'unknown', 'size': 0, 'extension': ''}
    
    def _process_pdf(self, file_path: str) -> Dict:
        """Process PDF file"""
        if not PDF_AVAILABLE:
            return {'error': 'PDF processing not available'}
        
        try:
            content = {
                'text': '',
                'pages': 0,
                'images': [],
                'metadata': {}
            }
            
            # Extract text using pdfplumber (better for tables and layouts)
            with pdfplumber.open(file_path) as pdf:
                content['pages'] = len(pdf.pages)
                content['metadata'] = pdf.metadata or {}
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        content['text'] += f"\n--- Page {page_num} ---\n{page_text}\n"
                    
                    # Extract tables if any
                    tables = page.extract_tables()
                    if tables:
                        content['text'] += f"\n--- Tables on Page {page_num} ---\n"
                        for table in tables:
                            content['text'] += self._format_table(table)
            
            # Also try PyPDF2 as backup
            if not content['text'].strip():
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    content['pages'] = len(pdf_reader.pages)
                    content['metadata'] = pdf_reader.metadata or {}
                    
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        page_text = page.extract_text()
                        if page_text:
                            content['text'] += f"\n--- Page {page_num} ---\n{page_text}\n"
            
            return content
            
        except Exception as e:
            logger.error(f"❌ PDF processing error: {e}")
            return {'error': str(e)}
    
    def _process_image(self, file_path: str) -> Dict:
        """Process image file with OCR"""
        if not IMAGE_AVAILABLE:
            return {'error': 'Image processing not available'}
        
        try:
            content = {
                'text': '',
                'metadata': {},
                'ocr_confidence': 0,
                'dimensions': {}
            }
            
            # Open image
            with Image.open(file_path) as img:
                content['dimensions'] = {
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format
                }
                
                # Perform OCR
                try:
                    ocr_text = pytesseract.image_to_string(img, lang='eng+hin')
                    content['text'] = ocr_text
                    content['ocr_confidence'] = 1.0  # Simplified confidence
                except Exception as ocr_error:
                    logger.warning(f"⚠️  OCR failed: {ocr_error}")
                    content['text'] = ''
                    content['ocr_confidence'] = 0.0
            
            # Use Moondream for visual analysis
            try:
                moondream_result = self._analyze_with_moondream(file_path, "Describe this image in detail")
                content['moondream_analysis'] = moondream_result
            except Exception as moondream_error:
                logger.warning(f"⚠️  Moondream analysis failed: {moondream_error}")
                content['moondream_analysis'] = ''
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Image processing error: {e}")
            return {'error': str(e)}
    
    def _process_docx(self, file_path: str) -> Dict:
        """Process DOCX file"""
        if not DOC_AVAILABLE:
            return {'error': 'DOCX processing not available'}
        
        try:
            content = {
                'text': '',
                'paragraphs': 0,
                'tables': [],
                'metadata': {}
            }
            
            doc = docx.Document(file_path)
            content['paragraphs'] = len(doc.paragraphs)
            
            # Extract text from paragraphs
            for para in doc.paragraphs:
                if para.text.strip():
                    content['text'] += para.text + '\n'
            
            # Extract tables
            for table in doc.tables:
                table_data = []
                for row in table.rows:
                    row_data = [cell.text for cell in row.cells]
                    table_data.append(row_data)
                content['tables'].append(table_data)
            
            # Format tables in text
            if content['tables']:
                content['text'] += '\n--- Tables ---\n'
                for table in content['tables']:
                    content['text'] += self._format_table(table)
            
            return content
            
        except Exception as e:
            logger.error(f"❌ DOCX processing error: {e}")
            return {'error': str(e)}
    
    def _analyze_with_moondream(self, image_path: str, query: str) -> str:
        """Analyze image using Moondream vision model"""
        try:
            # Try to use local models for vision analysis
            from modules.models import local_models
            
            # Create a simple prompt for vision analysis
            vision_prompt = f"Analyze this image and respond to: {query}"
            
            # Try to get vision analysis from local models
            try:
                result = local_models.smart_routing(vision_prompt, "vision")
                if result and result.get('response'):
                    return result['response']
            except:
                pass
            
            # Fallback to basic image description
            return f"This appears to be an image file. The system can see the image dimensions and basic properties, but detailed visual analysis requires additional vision model setup."
            
        except Exception as e:
            logger.error(f"❌ Moondream analysis error: {e}")
            return f"Unable to perform detailed image analysis: {str(e)}"

    def _process_text(self, file_path: str) -> Dict:
        """Process text file"""
        try:
            content = {
                'text': '',
                'lines': 0,
                'encoding': 'utf-8'
            }
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        text = file.read()
                        content['text'] = text
                        content['encoding'] = encoding
                        content['lines'] = len(text.splitlines())
                        break
                except UnicodeDecodeError:
                    continue
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Text processing error: {e}")
            return {'error': str(e)}
    
    def _format_table(self, table: List[List[str]]) -> str:
        """Format table data as readable text"""
        if not table:
            return ''
        
        formatted = []
        for row in table:
            if row:
                formatted.append(' | '.join(str(cell) for cell in row))
        
        return '\n'.join(formatted) + '\n'
    
    def _analyze_with_moondream(self, file_path: str, prompt: str) -> str:
        """Analyze file with Moondream model"""
        try:
            # Use existing Moondream integration
            result = local_models.vision_analysis(file_path, prompt)
            return result if result else '❌ Moondream analysis failed'
        except Exception as e:
            logger.error(f"❌ Moondream error: {e}")
            return f'❌ Moondream error: {str(e)}'
    
    def _perform_analysis(self, processed_content: Dict, analysis_type: str, 
                         query: str, file_info: Dict) -> Dict:
        """Perform analysis on processed content"""
        try:
            text_content = processed_content.get('text', '')
            
            if not text_content and not processed_content.get('moondream_analysis'):
                return {
                    'success': False,
                    'error': 'No content to analyze',
                    'response': '❌ File mein analyze karne ke liye content nahi hai'
                }
            
            # Get analysis prompt
            analysis_prompt = self.analysis_types.get(analysis_type, 'Analyze this content')
            
            # Add custom query if provided
            if query:
                analysis_prompt += f"\n\nSpecific focus: {query}"
            
            # Add file context
            context_info = f"File: {file_info['name']} ({file_info['size_mb']} MB)"
            if file_info.get('pages'):
                context_info += f", Pages: {file_info['pages']}"
            elif file_info.get('lines'):
                context_info += f", Lines: {file_info['lines']}"
            
            analysis_prompt += f"\n\n{context_info}"
            
            # Combine text content and Moondream analysis
            combined_content = text_content
            if processed_content.get('moondream_analysis'):
                combined_content += f"\n\nVisual Analysis:\n{processed_content['moondream_analysis']}"
            
            # Use Llama for analysis
            full_prompt = f"{analysis_prompt}\n\nContent to analyze:\n{combined_content[:8000]}"  # Limit content
            
            # Use brain system for analysis
            from .brain import brain
            result = brain.process_query(full_prompt)
            
            if result.get('success'):
                response = result.get('hinglish_response', result.get('response', ''))
            else:
                response = f"❌ Analysis failed: {result.get('response', 'Unknown error')}"
            
            return {
                'success': True,
                'analysis_type': analysis_type,
                'prompt': analysis_prompt,
                'response': response,
                'content_length': len(combined_content),
                'word_count': len(combined_content.split())
            }
            
        except Exception as e:
            logger.error(f"❌ Analysis error: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ Analysis mein error: {str(e)}"
            }
    
    def batch_process(self, file_paths: List[str], analysis_type: str = 'summary') -> Dict:
        """Process multiple files in batch"""
        try:
            batch_results = []
            total_processing_time = 0
            
            for file_path in file_paths:
                result = self.process_file(file_path, analysis_type)
                batch_results.append(result)
                total_processing_time += result.get('processing_time', 0)
            
            # Generate batch summary
            successful_files = [r for r in batch_results if r['success']]
            failed_files = [r for r in batch_results if not r['success']]
            
            summary = f"📊 Batch Processing Summary:\n"
            summary += f"• Total files: {len(file_paths)}\n"
            summary += f"• Successful: {len(successful_files)}\n"
            summary += f"• Failed: {len(failed_files)}\n"
            summary += f"• Total processing time: {total_processing_time:.2f}s\n"
            
            if successful_files:
                summary += f"• Average processing time: {total_processing_time/len(successful_files):.2f}s\n"
            
            return {
                'success': True,
                'batch_results': batch_results,
                'summary': summary,
                'total_files': len(file_paths),
                'successful_files': len(successful_files),
                'failed_files': len(failed_files),
                'total_processing_time': total_processing_time,
                'response': summary
            }
            
        except Exception as e:
            logger.error(f"❌ Batch processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ Batch processing failed: {str(e)}"
            }
    
    def compare_documents(self, file_paths: List[str], query: str = None) -> Dict:
        """Compare multiple documents"""
        try:
            if len(file_paths) < 2:
                return {
                    'success': False,
                    'error': 'Need at least 2 files to compare',
                    'response': '❌ Compare karne ke liye kam se kam 2 files chahiye'
                }
            
            # Process all files with extract analysis
            comparison_results = []
            
            for file_path in file_paths:
                result = self.process_file(file_path, 'extract', query)
                comparison_results.append(result)
            
            # Generate comparison
            comparison_text = self._generate_document_comparison(comparison_results, query)
            
            return {
                'success': True,
                'file_paths': file_paths,
                'comparison_results': comparison_results,
                'comparison': comparison_text,
                'response': comparison_text
            }
            
        except Exception as e:
            logger.error(f"❌ Document comparison error: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"❌ Document comparison failed: {str(e)}"
            }
    
    def _generate_document_comparison(self, results: List[Dict], query: str) -> str:
        """Generate document comparison analysis"""
        comparison_parts = []
        
        if query:
            comparison_parts.append(f"📋 Document Comparison for: {query}")
        else:
            comparison_parts.append("📋 Document Comparison:")
        
        for i, result in enumerate(results, 1):
            if result['success']:
                file_info = result['file_info']
                analysis_result = result['analysis_result']
                
                comparison_parts.append(f"\n{i}. {file_info['name']}")
                comparison_parts.append(f"   Size: {file_info['size_mb']} MB")
                
                if file_info.get('pages'):
                    comparison_parts.append(f"   Pages: {file_info['pages']}")
                
                # Add key insights from analysis
                response = analysis_result.get('response', '')
                if response:
                    # Extract first few sentences as summary
                    sentences = response.split('.')
                    key_insight = sentences[0] if sentences else ''
                    if key_insight:
                        comparison_parts.append(f"   Key insight: {key_insight.strip()}")
            else:
                comparison_parts.append(f"\n{i}. Processing failed")
        
        return '\n'.join(comparison_parts)

def analyze_image(image_path: str, query: str = "Describe this image in detail") -> Dict:
    """
    Analyze an image using enhanced vision capabilities
    """
    try:
        if not os.path.exists(image_path):
            return {
                'success': False,
                'error': 'Image file not found',
                'description': f"❌ Image '{image_path}' not found"
            }
        
        # Initialize enhanced moondream
        moondream = EnhancedMoondream()
        
        # Process the image
        result = moondream.process_file(image_path, 'summary', query)
        
        if result['success']:
            return {
                'success': True,
                'description': result.get('response', ''),
                'file_info': result.get('file_info', {}),
                'analysis_result': result.get('analysis_result', {})
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'description': f"❌ Image analysis failed: {result.get('error', 'Unknown error')}"
            }
            
    except Exception as e:
        logger.error(f"❌ Image analysis error: {e}")
        return {
            'success': False,
            'error': str(e),
            'description': f"❌ Image analysis failed: {str(e)}"
        }

# Global enhanced Moondream instance
enhanced_moondream = EnhancedMoondream()
