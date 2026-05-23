"""
Maya AI Voice Processor
High-performance voice processing with wake word detection
Supports "Maya", "Hey Maya", "Hello Maya" wake words
"""

import numpy as np
import threading
import queue
import time
import logging
from typing import Dict, List, Optional, Callable
from collections import deque

logger = logging.getLogger(__name__)

class VoiceProcessor:
    """High-performance voice processing with C optimization"""
    
    def __init__(self):
        self.is_listening = False
        self.is_processing = False
        self.use_c_module = False
        self.auto_mode = False  # Automatic wake/stop detection
        self.wake_words = ["maya", "hey maya", "hello maya", "hi maya"]
        self.stop_words = ["stop", "stop listening", "deactivate", "sleep", "quiet", "shut up", "stop maya"]
        self.c_detector = None
        self.callback = None
        self.listen_thread = None
        self.processing_thread = None
        self._init_c_detector()
        self.wake_word_thresholds = {
            "maya": 0.85,
            "hey maya": 0.80,
            "hello maya": 0.80
        }
        
        # Audio processing parameters
        self.sample_rate = 16000
        self.frame_size = 400
        self.hop_size = 160
        self.buffer_size = 2048
        
        # Processing queues
        self.audio_queue = queue.Queue(maxsize=100)
        self.result_queue = queue.Queue(maxsize=10)
        
        # Wake word detection state
        self.detection_buffer = deque(maxlen=50)
        self.detection_state = 0
        self.last_detection_time = 0
        
        # Background processing thread
        self.processing_thread = None
        self.callbacks = {}
        
        # Try to import C module for maximum performance
        self.use_c_module = False
        self._init_c_detector()
    
    def _init_c_detector(self):
        """Initialize C-based wake word detector"""
        try:
            # Try to import and use C module for high performance
            import sys
            import os
            
            # Add the voice_processor directory to path
            voice_processor_path = os.path.join(os.path.dirname(__file__), '..', 'voice_processor')
            if voice_processor_path not in sys.path:
                sys.path.insert(0, voice_processor_path)
            
            # Try to import the C extension
            try:
                import wake_word_detector
                self.c_detector = wake_word_detector
                self.use_c_module = True
                logger.info("🚀 Using C-based wake word detector")
                return True
            except ImportError:
                # Silently use Python fallback without warning (C module is optional)
                self.use_c_module = False
                self._init_python_detector()
                return False
                
        except Exception as e:
            # Silently use Python fallback without warning (C module is optional)
            self.use_c_module = False
            self._init_python_detector()
            return False
    
    def _init_python_detector(self):
        """Initialize Python-based wake word detection"""
        # Simple energy-based detection for Python fallback
        self.energy_threshold = 0.01
        self.silence_threshold = 0.001
        self.min_wake_word_duration = 0.3  # seconds
    
    def start_listening(self, callback: Optional[Callable] = None):
        """Start wake word detection"""
        if self.is_listening:
            return False
        
        self.is_listening = True
        self.callback = callback
        
        if self.use_c_module and self.c_detector:
            return self._start_c_listening()
        else:
            return self._start_python_listening()
    
    def start_auto_detection(self, callback: Optional[Callable] = None):
        """Start automatic wake word detection with stop word monitoring"""
        if self.is_listening:
            return False
        
        self.auto_mode = True
        self.is_listening = True
        self.callback = callback
        
        logger.info("🎤 Starting automatic wake/stop word detection")
        
        if self.use_c_module and self.c_detector:
            return self._start_c_auto_detection()
        else:
            return self._start_python_auto_detection()
    
    def _start_python_auto_detection(self):
        """Start Python-based automatic detection"""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Optimization for noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.recognizer.energy_threshold = 300 # Dynamic threshold
                self.recognizer.dynamic_energy_threshold = True
            
            def auto_listen_thread():
                while self.is_listening and self.auto_mode:
                    try:
                        with self.microphone as source:
                            # Listen for audio with shorter timeouts for wake word
                            audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                            
                            # Recognize speech using Google (Fast & Accurate)
                            text = self.recognizer.recognize_google(audio, language='en-US').lower()
                            
                            if text:
                                # Check for wake words
                                if self._detect_wake_word(text):
                                    logger.info(f"🎯 Wake word detected: {text}")
                                    if self.callback:
                                        self.callback(text, "wake_word")
                                
                                # Check for stop words
                                elif self._detect_stop_word(text):
                                    logger.info(f"🛑 Stop word detected: {text}")
                                    if self.callback:
                                        self.callback(text, "stop_word")
                                    self.stop_listening()
                                    break
                                
                    except sr.WaitTimeoutError:
                        continue  # No speech detected, continue listening
                    except sr.UnknownValueError:
                        continue  # Speech not understood, continue listening
                    except Exception as e:
                        logger.error(f"❌ Auto detection error: {e}")
                        time.sleep(0.1)
                        continue
            
            # Start the auto detection thread
            self.listen_thread = threading.Thread(target=auto_listen_thread, daemon=True)
            self.listen_thread.start()
            
            return True
            
        except ImportError:
            logger.error("❌ Speech recognition library not available")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to start auto detection: {e}")
            return False
    
    def _detect_wake_word(self, text: str) -> bool:
        """Detect wake words in text"""
        text_lower = text.lower().strip()
        
        for wake_word in self.wake_words:
            if wake_word in text_lower:
                return True
        
        return False
    
    def _detect_stop_word(self, text: str) -> bool:
        """Detect stop words in text"""
        text_lower = text.lower().strip()
        
        for stop_word in self.stop_words:
            if stop_word in text_lower:
                return True
        
        return False
    
    def stop_listening(self):
        """Stop voice listening"""
        self.is_listening = False
        self.auto_mode = False
        if hasattr(self, 'listen_thread') and self.listen_thread:
            self.listen_thread.join(timeout=1.0)
        if hasattr(self, 'processing_thread') and self.processing_thread:
            self.processing_thread.join(timeout=1.0)
        logger.info("🔇 Voice processor stopped")
    
    def process_audio_chunk(self, audio_data: np.ndarray) -> Optional[str]:
        """Process a chunk of audio data and return detected wake word"""
        try:
            if self.use_c_module:
                return self._process_with_c_module(audio_data)
            else:
                return self._process_with_python(audio_data)
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            return None
    
    def _process_with_c_module(self, audio_data: np.ndarray) -> Optional[str]:
        """Process audio using C module for maximum performance"""
        try:
            # Convert numpy array to Python list for C module
            audio_list = audio_data.tolist()
            detected = self.wake_detector.detect_wake_word(audio_list, len(audio_list))
            
            if detected and len(detected) > 0:
                current_time = time.time()
                # Prevent duplicate detections within 2 seconds
                if current_time - self.last_detection_time > 2.0:
                    self.last_detection_time = current_time
                    return detected.lower()
            
            return None
        except Exception as e:
            logger.error(f"C module processing error: {e}")
            return self._process_with_python(audio_data)  # Fallback to Python
    
    def _process_with_python(self, audio_data: np.ndarray) -> Optional[str]:
        """Process audio using Python implementation"""
        try:
            # Calculate energy
            energy = np.mean(audio_data ** 2)
            
            # Check if energy exceeds threshold
            if energy > self.energy_threshold:
                self.detection_state += 1
                self.detection_buffer.append(energy)
                
                # Check for sustained energy (wake word pattern)
                if len(self.detection_buffer) >= 10:
                    avg_energy = np.mean(self.detection_buffer)
                    if avg_energy > self.energy_threshold and self.detection_state >= 5:
                        # Simple wake word detection based on energy pattern
                        detected = self._detect_wake_word_pattern(audio_data)
                        if detected:
                            current_time = time.time()
                            if current_time - self.last_detection_time > 2.0:
                                self.last_detection_time = current_time
                                self.detection_state = 0
                                self.detection_buffer.clear()
                                return detected
            else:
                self.detection_state = 0
                self.detection_buffer.clear()
            
            return None
        except Exception as e:
            logger.error(f"Python processing error: {e}")
            return None
    
    def _detect_wake_word_pattern(self, audio_data: np.ndarray) -> Optional[str]:
        """Simple pattern-based wake word detection"""
        # This is a simplified implementation
        # In production, this would use trained ML models
        
        # Check for "maya" pattern (2-3 syllables)
        zero_crossings = np.sum(np.diff(np.sign(audio_data)) != 0)
        spectral_centroid = np.sum(np.abs(np.fft.fftfreq(len(audio_data))[:len(audio_data)//2] * 
                                        np.abs(np.fft.fft(audio_data)[:len(audio_data)//2]))) / np.sum(np.abs(np.fft.fft(audio_data)[:len(audio_data)//2]))
        
        # Simple heuristic for "maya" detection
        if 500 < zero_crossings < 2000 and 1000 < spectral_centroid < 3000:
            return "maya"
        
        return None
    
    def _processing_loop(self):
        """Background processing loop"""
        while self.is_listening:
            try:
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get(timeout=0.1)
                    detected = self.process_audio_chunk(audio_data)
                    
                    if detected and 'wake_word' in self.callbacks:
                        self.callbacks['wake_word'](detected)
                
                time.sleep(0.01)  # 10ms processing interval
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Processing loop error: {e}")
                time.sleep(0.1)
    
    def add_audio_data(self, audio_data: np.ndarray):
        """Add audio data to processing queue"""
        try:
            if not self.audio_queue.full():
                self.audio_queue.put(audio_data, block=False)
        except queue.Full:
            # Drop oldest audio data if queue is full
            try:
                self.audio_queue.get(block=False)
                self.audio_queue.put(audio_data, block=False)
            except queue.Empty:
                pass
    
    def get_supported_wake_words(self) -> List[str]:
        """Get list of supported wake words"""
        if self.use_c_module:
            try:
                return list(self.wake_detector.get_wake_words())
            except:
                pass
        return self.wake_words.copy()
    
    def set_wake_word_callback(self, callback: Callable):
        """Set callback for wake word detection"""
        self.callbacks['wake_word'] = callback

# Global voice processor instance
voice_processor = VoiceProcessor()

class VoiceOutput:
    """High-performance text-to-speech output"""
    
    def __init__(self):
        self.tts_engine = None
        self.is_speaking = False
        self.voice_queue = queue.Queue(maxsize=10)
        self.speaking_thread = None
        
        self._init_tts()
    
    def _init_tts(self):
        """Initialize TTS engine with natural feminine voice"""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            
            # Get all available voices
            voices = self.tts_engine.getProperty('voices')
            selected_voice = None
            
            # Prioritize soft, natural female voices
            voice_priority = [
                'zira',      # Microsoft Zira (natural female)
                'david',     # Microsoft David (male, but clear)
                'hazel',     # Microsoft Hazel (female)
                'susan',     # Apple Susan (female)
                'samantha',  # Apple Samantha (female)
                'karen',     # macOS Karen (Australian female)
                'female',    # Generic female
                'woman'      # Generic woman
            ]
            
            # Find the best available voice
            for priority in voice_priority:
                for voice in voices:
                    if priority in voice.name.lower():
                        selected_voice = voice
                        break
                if selected_voice:
                    break
            
            # If no priority voice found, use the first available
            if not selected_voice and voices:
                selected_voice = voices[0]
            
            if selected_voice:
                self.tts_engine.setProperty('voice', selected_voice.id)
                logger.info(f"🔊 Selected voice: {selected_voice.name}")
            
            # Configure for soft, natural feminine speech
            self.tts_engine.setProperty('rate', 135)      # Even slower for more feminine delivery
            self.tts_engine.setProperty('volume', 0.80)    # Softer volume for gentler sound
            
            # Try to set voice pitch (if supported)
            try:
                # Higher pitch for more feminine sound (120-130 range)
                self.tts_engine.setProperty('pitch', 125)  # More feminine pitch
            except:
                pass  # Pitch not supported, continue without it
            
            logger.info("🔊 TTS initialized with natural feminine voice settings")
        except Exception as e:
            logger.error(f"TTS initialization failed: {e}")
    
    def speak(self, text: str, blocking: bool = False):
        """Speak text using TTS"""
        if not self.tts_engine:
            return False
        
        if blocking:
            return self._speak_blocking(text)
        else:
            return self._speak_non_blocking(text)
    
    def _speak_blocking(self, text: str) -> bool:
        """Speak text with blocking"""
        try:
            self.is_speaking = True
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            self.is_speaking = False
            return True
        except Exception as e:
            logger.error(f"Blocking TTS error: {e}")
            self.is_speaking = False
            return False
    
    def _speak_non_blocking(self, text: str) -> bool:
        """Speak text without blocking"""
        try:
            if not self.voice_queue.full():
                self.voice_queue.put(text, block=False)
                
                if not self.speaking_thread or not self.speaking_thread.is_alive():
                    self.speaking_thread = threading.Thread(target=self._speaking_loop, daemon=True)
                    self.speaking_thread.start()
                
                return True
        except queue.Full:
            pass
        except Exception as e:
            logger.error(f"Non-blocking TTS error: {e}")
        
        return False
    
    def _speaking_loop(self):
        """Background speaking loop"""
        while not self.voice_queue.empty():
            try:
                text = self.voice_queue.get(timeout=0.1)
                self._speak_blocking(text)
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Speaking loop error: {e}")
    
    def stop(self):
        """Stop current speech"""
        try:
            if self.tts_engine:
                self.tts_engine.stop()
            self.is_speaking = False
        except Exception as e:
            logger.error(f"Stop TTS error: {e}")
    
    def is_busy(self) -> bool:
        """Check if TTS is currently speaking"""
        return self.is_speaking

# Global voice output instance
voice_output = VoiceOutput()
