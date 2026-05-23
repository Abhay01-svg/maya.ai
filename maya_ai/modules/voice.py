"""
Maya AI Voice Module
Speech recognition and text-to-speech
Wake word detection and voice commands
"""

import logging
import time
import os
import subprocess
import requests
from gtts import gTTS
from playsound import playsound
from config import WAKE_WORD, VOICE_MODE, DEBUG_MODE, HINGLISH_MODE, NARAKEET_API_KEY, NARAKEET_VOICE, TTS_ENGINE, INDIC_LANGUAGE, XTTS_MODEL_PATH, CHATTTS_MODEL_PATH

logger = logging.getLogger(__name__)

try:
    import speech_recognition as sr
    from pyttsx3 import init as tts_init
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    logger.warning("⚠️  Voice libraries not available (speech_recognition, pyttsx3)")


class VoiceRecognition:
    """Speech recognition system"""
    
    def __init__(self):
        global VOICE_AVAILABLE
        self.recognizer = None
        self.microphone = None
        
        if VOICE_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                logger.info("✅ Voice recognition initialized")
            except Exception as e:
                logger.error(f"❌ Voice init error: {e}")
                VOICE_AVAILABLE = False
    
    def listen_for_command(self, timeout: int = 10) -> str:
        """Listen for voice command"""
        if not VOICE_AVAILABLE or not self.recognizer:
            return None
        
        try:
            with self.microphone as source:
                logger.info("🎤 Listening...")
                # Reduce noise adjustment duration for faster response
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.recognizer.energy_threshold = 4000 # Standard threshold
                self.recognizer.dynamic_energy_threshold = True
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Try multiple recognition engines
            try:
                # Try Google Speech Recognition (free) with English for better accuracy
                text = self.recognizer.recognize_google(audio, language="en-US")
                # Clean up the text for exact output
                if text:
                    text = text.strip().lower()
                    # Remove common recognition errors
                    text = text.replace(" um ", " ").replace(" uh ", " ")
                    text = text.replace("  ", " ").strip()
                logger.info(f"✅ Recognized: {text}")
                return text
            except sr.UnknownValueError:
                logger.warning("⚠️  Could not understand audio")
                return None
            except sr.RequestError as e:
                logger.error(f"❌ Recognition error: {e}")
                # Fallback to local recognition if offline (optional/future)
                return None
        
        except sr.RequestError as e:
            logger.error(f"❌ Microphone error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None
    
    def detect_wake_word(self, audio_text: str) -> bool:
        """Detect if audio contains wake word"""
        if not audio_text:
            return False
        
        # More precise wake word detection
        wake_words = [WAKE_WORD.lower(), "maya", "hey maya", "hey"]
        audio_lower = audio_text.lower().strip()
        
        # Check for exact matches first
        for wake_word in wake_words:
            if wake_word in audio_lower:
                return True
        
        # Check for partial matches
        for wake_word in wake_words:
            if wake_word in audio_lower.split():
                return True
        
        return False
    
    def continuous_listen(self, callback):
        """Continuously listen for commands"""
        if not VOICE_AVAILABLE:
            return
        
        logger.info(f"👂 Waiting for '{WAKE_WORD}'...")
        
        while True:
            try:
                text = self.listen_for_command(timeout=5)
                
                if text and self.detect_wake_word(text):
                    logger.info(f"🎙️  Wake word detected: {text}")
                    
                    # Extract command after wake word
                    command = text.replace(WAKE_WORD.lower(), "").strip()
                    command = command.replace("hey maya", "").strip()
                    command = command.replace("maya", "").strip()
                    
                    if command:
                        callback(command)
                
            except Exception as e:
                logger.error(f"❌ Listening error: {e}")
                time.sleep(1)


class AdvancedTTS:
    """Wrapper for high-end AI TTS models: Indic-TTS, ChatTTS, and XTTS-v2"""
    
    def __init__(self, model_type="chattts"):
        self.model_type = model_type
        self.temp_dir = "temp_audio"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Lazy load the selected model"""
        try:
            if self.model_type == "xtts":
                try:
                    from TTS.api import TTS
                    logger.info("⏳ Loading Coqui XTTS-v2...")
                    # XTTS usually requires Python 3.9-3.11
                    self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
                    import torch
                    if torch.cuda.is_available():
                        self.model.to("cuda")
                    logger.info("✅ XTTS-v2 Loaded")
                except ImportError:
                    logger.error("❌ Coqui TTS (XTTS) is not compatible with Python 3.12. Falling back to ChatTTS.")
                    self.model_type = "chattts"
                    self._initialize_model()
                
            if self.model_type == "chattts":
                try:
                    import ChatTTS
                    import torch
                    logger.info("⏳ Loading ChatTTS...")
                    self.model = ChatTTS.Chat()
                    # self.model.load_models() # Removed due to attribute error in newer versions
                    logger.info("✅ ChatTTS Loaded")
                except Exception as e:
                    logger.error(f"❌ ChatTTS load error: {e}")
                    self.model = None
                
            elif self.model_type == "indic":
                logger.info("🎙️ Indic-TTS (AI4Bharat) mode initialized")
                
        except Exception as e:
            logger.error(f"❌ Failed to load {self.model_type}: {e}")
            self.model = None

    def speak(self, text: str, wait: bool = True) -> bool:
        """Generate speech using advanced models"""
        if not self.model and self.model_type != "indic":
            logger.warning(f"⚠️ {self.model_type} model not loaded, falling back to Local TTS...")
            # Emergency fallback to pyttsx3 if advanced model fails
            fallback = TextToSpeech()
            return fallback.speak(text, wait)

        try:
            filename = f"maya_adv_{int(time.time())}.wav"
            filepath = os.path.join(self.temp_dir, filename)
            
            if self.model_type == "xtts":
                # XTTS v2 generation
                self.model.tts_to_file(
                    text=text, 
                    file_path=filepath, 
                    speaker_wav="data/voice_samples/maya_ref.wav", # You can add a reference voice
                    language="hi" if "hi" in text.lower() else "en"
                )
            
            elif self.model_type == "chattts":
                # ChatTTS generation
                wavs = self.model.infer([text])
                import scipy
                scipy.io.wavfile.write(filepath, 24000, wavs[0])
                
            elif self.model_type == "indic":
                # AI4Bharat Indic-TTS implementation
                # This would typically call a local subprocess or API
                logger.info("Indic-TTS generation active...")
                # Placeholder for Indic-TTS specific logic
                return False

            self._play_audio(filepath)
            return True
            
        except Exception as e:
            logger.error(f"❌ Advanced TTS generation error: {e}")
            return False

    def _play_audio(self, filepath):
        """Native Windows playback"""
        abs_path = os.path.abspath(filepath)
        cmd = f"powershell -c \"$m = New-Object -ComObject WMPlayer.OCX; $m.url = '{abs_path}'; $m.controls.play(); while($m.playState -ne 1){{start-sleep -m 100}}\""
        subprocess.Popen(cmd, shell=True)


class NarakeetTTS:
    """Narakeet Cloud TTS for high-quality voice output"""
    
    def __init__(self):
        self.api_key = NARAKEET_API_KEY
        self.voice = NARAKEET_VOICE
        self.temp_dir = "temp_audio"
        os.makedirs(self.temp_dir, exist_ok=True)
        
    def speak(self, text: str, wait: bool = True) -> bool:
        """Generate and play audio using Narakeet API"""
        if not self.api_key:
            logger.error("❌ Narakeet API Key missing")
            return False
            
        try:
            # Clean text
            clean_text = text.replace('🌍', '').replace('🌡️', '').replace('☁️', '').replace('💧', '').replace('💨', '').replace('🌫️', '').replace('📰', '').replace('🦆', '').replace('🔗', '')
            clean_text = clean_text.replace('*', '').replace('#', '').replace('_', '')
            
            logger.info(f"🌐 Narakeet TTS Request: {clean_text[:50]}...")
            
            url = f"https://api.narakeet.com/text-to-speech/mp3?voice={self.voice}"
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "text/plain"
            }
            
            response = requests.post(url, headers=headers, data=clean_text.encode('utf-8'), timeout=15)
            
            if response.status_code == 200:
                filename = f"maya_voice_{int(time.time())}.mp3"
                filepath = os.path.join(self.temp_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # Play using PowerShell (Windows native)
                self._play_audio(filepath)
                
                # Cleanup old files
                self._cleanup_temp()
                return True
            else:
                logger.error(f"❌ Narakeet API Error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Narakeet Error: {e}")
            return False

    def _play_audio(self, filepath):
        """Play MP3 using Windows Media Player via PowerShell"""
        abs_path = os.path.abspath(filepath)
        cmd = f"powershell -c \"$m = New-Object -ComObject WMPlayer.OCX; $m.url = '{abs_path}'; $m.controls.play(); while($m.playState -ne 1){{start-sleep -m 100}}\""
        subprocess.Popen(cmd, shell=True)

    def _cleanup_temp(self):
        """Remove old audio files"""
        try:
            for f in os.listdir(self.temp_dir):
                f_path = os.path.join(self.temp_dir, f)
                # Remove files older than 5 minutes
                if os.path.getmtime(f_path) < time.time() - 300:
                    os.remove(f_path)
        except:
            pass


class TextToSpeech:
    """Text-to-speech system with Hinglish phonetic mapping and natural speech processing"""
    
    def __init__(self):
        global VOICE_AVAILABLE
        self.engine = None
        self.voice_female = None
        
        # Hinglish phonetic mapping dictionary
        self.hinglish_phonetics = {
            # Common Hinglish words and their phonetic mappings
            'namaste': 'nah-mah-stay',
            'kya': 'kya',
            'hai': 'hai',
            'hoon': 'hoon',
            'aap': 'aap',
            'tum': 'tum',
            'mein': 'mein',
            'hum': 'hum',
            'kar': 'kar',
            'sakta': 'sakta',
            'sakti': 'sakti',
            'hain': 'hain',
            'tha': 'tha',
            'thi': 'thi',
            'the': 'the',
            'karna': 'karna',
            'dena': 'dena',
            'lena': 'lena',
            'aana': 'aana',
            'jaana': 'jaana',
            'dekhna': 'dekhna',
            'samajh': 'samajh',
            'nahi': 'nahi',
            'accha': 'accha',
            'achhe': 'achhe',
            'bahut': 'bahut',
            'zyada': 'zyada',
            'kam': 'kam',
            'dost': 'dost',
            'pyaar': 'pyaar',
            'dil': 'dil',
            'khushi': 'khushi',
            'gussa': 'gussa',
            'maaf': 'maaf',
            'shukriya': 'shukriya',
            'dhanyawaad': 'dhanyawaad',
            'phir': 'phir',
            'abhi': 'abhi',
            'der': 'der',
            'baad': 'baad',
            'pehle': 'pehle',
            'baadmein': 'baadmein',
            'ka': 'ka',
            'ki': 'ki',
            'ke': 'ke',
            'ko': 'ko',
            'se': 'se',
            'ne': 'ne',
            'par': 'par',
            'tak': 'tak',
            'tha': 'tha',
            'ho': 'ho',
            'raha': 'raha',
            'rahi': 'rahi',
            'rahe': 'rahe',
            'hua': 'hua',
            'hui': 'hua',
            'hue': 'hue',
            'gaya': 'gaya',
            'gayi': 'gayi',
            'gaye': 'gaye',
            'liya': 'liya',
            'diya': 'diya',
            'kiya': 'kiya',
            'badhiya': 'badhiya',
            'kaise': 'kaise',
            'kahan': 'kahan',
            'kab': 'kab',
            'kyun': 'kyun',
            'kaun': 'kaun',
            'kitna': 'kitna',
            'theek': 'theek',
            'sahi': 'sahi',
            'galat': 'galat',
            'pata': 'pata',
            'pyaar': 'pyaar',
            'bhai': 'bhai',
            'behen': 'behen',
            'papa': 'papa',
            'mummy': 'mummy',
            'ghara': 'ghara',
            'kaam': 'kaam',
            'aaj': 'aaj',
            'kal': 'kal',
            'parso': 'parso',
            'subah': 'subah',
            'shaam': 'shaam',
            'raat': 'raat',
            'din': 'din',
            'waqt': 'waqt',
            'samay': 'samay',
            'mausam': 'mausam',
            'baaki': 'baaki',
            'bilkul': 'bilkul',
            'shayad': 'shayad',
            'zaroori': 'zaroori',
            'koshish': 'koshish',
            'mehnat': 'mehnat',
            'sapna': 'sapna',
            'zindagi': 'zindagi',
            'maut': 'maat',
            'khuda': 'khuda',
            'bhagwan': 'bhagwan',
            'ishwar': 'ishwar',
            'duniya': 'duniya',
            'insan': 'insan',
            'jaan': 'jaan',
            'rooh': 'rooh',
            'saans': 'saans',
            'dharkan': 'dharkan',
            'khoon': 'khoon',
            'jism': 'jism',
            'dimag': 'dimag',
            'soch': 'soch',
            'fikr': 'fikr',
            'umeed': 'umeed',
            'bharosa': 'bharosa',
            'vishwaas': 'vishwaas',
            'himmat': 'himmat',
            'takat': 'takat',
            'shakti': 'shakti',
            'samajh': 'samajh',
            'gyaan': 'gyaan',
            'vidya': 'vidya',
            'shiksha': 'shakti',
            'kalam': 'kalam',
            'kitaab': 'kitaab',
            'paisa': 'paisa',
            'daulat': 'daulat',
            'shaurat': 'shaurat',
            'izzat': 'izzat',
            'beizzati': 'beizzati',
            'sharam': 'sharam',
            'haya': 'sharam',
            'wafa': 'vafa',
            'bewafa': 'bevafa',
            'dhoka': 'dhoka',
            'saza': 'saza',
            'gunaah': 'gunaah',
            'paap': 'paap',
            'punya': 'punya',
            'swarg': 'swarg',
            'narak': 'narak',
            'jahannum': 'jahannum',
            'jannat': 'jannat',
            'khwab': 'khwab',
            'haqeeqat': 'haqeeqat',
            'sach': 'sach',
            'jhooth': 'jhooth',
            'pyaar': 'pyaar',
            'mohabbat': 'mohabbat',
            'ishq': 'ishq',
            'nafrat': 'nafrat',
            'dushmani': 'nafrat',
            'dosti': 'dosti',
            'yaari': 'dosti',
            'vada': 'vada',
            'kasam': 'kasam',
            'intezaar': 'intezaar',
            'mulakat': 'mulakat',
            'judai': 'judai',
            'dard': 'dard',
            'gham': 'gham',
            'khushi': 'khushi',
            'hasna': 'hasna',
            'rona': 'rona',
            'chillana': 'rona',
            'khamoshi': 'khamoshi',
            'shor': 'shor',
            'awaaz': 'awaaz',
            'sangeet': 'sangeet',
            'gaana': 'gaana',
            'nachna': 'naachna',
            'khelna': 'khelna',
            'parhna': 'parhna',
            'likhna': 'likhna',
            'bolna': 'bolna',
            'sunna': 'sunna',
            'khana': 'khana',
            'peena': 'peena',
            'sona': 'sona',
            'jagna': 'jaagna',
            'uthna': 'uthna',
            'baithna': 'baithna',
            'chalna': 'chalna',
            'daurna': 'daurna',
            'koodna': 'koodna',
            'marna': 'marna',
            'jeena': 'jeena',
            'rakhna': 'rakhna',
            'chorna': 'chorna',
            'pakarna': 'pakarna',
            'girna': 'girna',
            'uthana': 'uthana',
            'feinkna': 'fenkna',
            'tootna': 'tootna',
            'jorna': 'jorna',
            'banana': 'banana',
            'mitana': 'mitana',
            'sajana': 'sajana',
            'bikherna': 'bikherna',
            'dhundna': 'dhundna',
            'khona': 'khona',
            'milna': 'mulakat',
            'bicharna': 'bicharna',
            'yaad': 'yaad',
            'bhool': 'bhool',
            'maafi': 'maaf',
            'shukrana': 'shukriya',
            'dua': 'dua',
            'bad-dua': 'bad-dua',
            'barkat': 'barkat',
            'rahmat': 'barkat',
            'naseeb': 'kismat',
            'kismat': 'kismat',
            'takdeer': 'kismat',
            'lakheer': 'lakheer',
            'haath': 'haath',
            'pair': 'pair',
            'aankh': 'aankh',
            'kaan': 'kaan',
            'naak': 'naak',
            'muh': 'muh',
            'daant': 'daant',
            'jeebh': 'jeebh',
            'baal': 'baal',
            'chehra': 'chehra',
            'badan': 'sharir',
            'sharir': 'sharir',
            'dil': 'dil',
            'jigar': 'jigar',
            'phephre': 'phephre',
            'pet': 'pet',
            'kamar': 'kamar',
            'haddi': 'haddi',
            'nas': 'nas',
            'rag': 'nas',
            'khoon': 'khoon',
            'pasina': 'paseena',
            'aansu': 'aansoo',
            'khwab': 'khvaab',
            'neend': 'neend',
            'sukoon': 'shanti',
            'shanti': 'shanti',
            'chain': 'shanti',
            'dard': 'dard',
            'bechaini': 'dard',
            'tadap': 'dard',
            'jalan': 'jalan',
            'hasrat': 'ichha',
            'khwaish': 'ichha',
            'tamanna': 'ichha',
            'armaan': 'ichha',
            'umeed': 'asha',
            'asha': 'asha',
            'nirasha': 'nirasha',
            'bharosa': 'vishwaas',
            'vishwaas': 'vishwaas',
            'yaqeen': 'vishwaas',
            'shak': 'shak',
            'sandeh': 'shak',
            'galatfehmi': 'shak',
            'sachai': 'sach',
            'haq': 'haq',
            'insaf': 'insaf',
            'zulm': 'atyachar',
            'atyachar': 'atyachar',
            'na-insafi': 'atyachar',
            'chor': 'chor',
            'daku': 'chor',
            'qaatil': 'hatyara',
            'hatyara': 'hatyara',
            'mujrima': 'apradhi',
            'apradhi': 'apradhi',
            'saza': 'dand',
            'dand': 'dand',
            'kaidi': 'apradhi',
            'jail': 'jail',
            'thaana': 'police station',
            'police': 'police',
            'vakeel': 'vakeel',
            'adalat': 'court',
            'court': 'adalat',
            'faisla': 'faisla',
            'kanoon': 'kanoon',
            'samvidhan': 'kanoon',
            'desh': 'desh',
            'vatan': 'desh',
            'mulk': 'desh',
            'dharti': 'dharti',
            'zameen': 'dharti',
            'aasman': 'aakash',
            'aakash': 'aakash',
            'falak': 'aakash',
            'chand': 'chaand',
            'chaand': 'chaand',
            'suraj': 'sooraj',
            'sooraj': 'sooraj',
            'sitare': 'taare',
            'taare': 'taare',
            'graha': 'graha',
            'prithvi': 'dharti',
            'brahmand': 'universe',
            'ishwar': 'bhagwan',
            'bhagwan': 'bhagwan',
            'allah': 'khuda',
            'khuda': 'khuda',
            'farishta': 'devdoot',
            'devta': 'bhagwan',
            'shaitan': 'rakshas',
            'rakshas': 'shaitan',
            'bhoot': 'pret',
            'aatma': 'rooh',
            'rooh': 'rooh',
            'jannat': 'swarg',
            'swarg': 'swarg',
            'jahannum': 'narak',
            'narak': 'narak',
            'qayamat': 'pralay',
            'pralay': 'qayamat',
            'dharm': 'dharm',
            'mazhab': 'dharm',
            'iman': 'iman',
            'neki': 'punya',
            'badi': 'paap',
            'paap': 'paap',
            'punya': 'punya',
            'ibadat': 'pooja',
            'pooja': 'pooja',
            'namaz': 'prarthana',
            'prarthana': 'pooja',
            'dua': 'dua',
            'mandir': 'mandir',
            'masjid': 'masjid',
            'gurudwara': 'gurudwara',
            'church': 'girjaghar',
            'teerth': 'teerth',
            'haj': 'haj',
            'mazar': 'dargah',
            'dargah': 'dargah',
            'pavitra': 'pavitra',
            'paak': 'pavitra',
            'shuddh': 'saaf',
            'saaf': 'saaf',
            'ganda': 'ganda',
            'na-paak': 'ganda',
            'kaafir': 'nastik',
            'nastik': 'nastik',
            'aastik': 'bhakt',
            'bhakt': 'bhakt',
            'shradha': 'vishwaas',
            'saburi': 'dhairya',
            'dhairya': 'shanti',
            'shanti': 'shanti',
            'aman': 'shanti',
            'chain': 'shanti',
            'sukoon': 'shanti',
            'khushi': 'khushi',
            'gham': 'dukh',
            'dard': 'dard',
            'takleef': 'dard',
            'museebat': 'samasya',
            'samasya': 'samasya',
            'uljhan': 'duvidha',
            'duvidha': 'duvidha',
            'pareshani': 'chinta',
            'chinta': 'fikr',
            'fikr': 'fikr',
            'dar': 'bhaya',
            'bhaya': 'dar',
            'khauf': 'dar',
            'dahshat': 'dar',
            'nafrat': 'nafrat',
            'gussa': 'krodh',
            'krodh': 'gussa',
            'jalan': 'jalan',
            'irshya': 'jalan',
            'hasad': 'jalan',
            'pyaar': 'prem',
            'prem': 'pyaar',
            'mohabbat': 'pyaar',
            'ishq': 'pyaar',
            'ulfat': 'pyaar',
            'chahat': 'pyaar',
            'vafa': 'vafa',
            'aitbaar': 'vishwaas',
            'intezaar': 'intezaar',
            'umra': 'aayu',
            'aayu': 'umra',
            'bachpan': 'bachpan',
            'jawani': 'jawani',
            'burhapa': 'budhapa',
            'budhapa': 'budhapa',
            'maut': 'mrityu',
            'mrityu': 'maut',
            'janm': 'paidaish',
            'paidaish': 'janm',
            'zindagi': 'jeevan',
            'jeevan': 'zindagi',
            'hayat': 'zindagi',
            'mulaqat': 'milna',
            'saath': 'saath',
            'tanhai': 'akela-pan',
            'akela': 'akela',
            'bheer': 'bheer',
            'duniya': 'jahan',
            'jahan': 'duniya',
            'zamana': 'duniya',
            'waqt': 'samay',
            'daur': 'waqt',
            'sadi': 'shatabdi',
            'itne': 'itne',
            'utne': 'utne',
            'kitne': 'kitne',
            'jitne': 'jitne',
            'kafi': 'bahut',
            'bilkul': 'bilkul',
            'sirf': 'sirf',
            'keval': 'sirf',
            'bas': 'sirf',
            'magar': 'lekin',
            'lekin': 'lekin',
            'par': 'par',
            'aur': 'aur',
            'ya': 'ya',
            'athwa': 'ya',
            'kyunki': 'kyonki',
            'isliye': 'isliye',
            'taki': 'taki',
            'agar': 'yadi',
            'yadi': 'agar',
            'magar': 'lekin',
            'halanki': 'halanki',
            'phir': 'fir',
            'phir bhi': 'phir bhi',
            'varna': 'anyatha',
            'anyatha': 'varna',
            'shayad': 'shayad',
            'kadachit': 'shayad',
            'zaroor': 'zaroor',
            'avashya': 'zaroor',
            'bilkul': 'bilkul',
            'hamesha': 'sada',
            'sada': 'hamesha',
            'kabhi': 'kabhi',
            'aksar': 'aksar',
            'prayash': 'aksar',
            'kabhi nahi': 'kabhi nahi',
            'turant': 'turant',
            'fauran': 'turant',
            'jaldi': 'jaldi',
            'shighra': 'jaldi',
            'dheere': 'dheere',
            'mand': 'dheere',
            'abhi': 'abhi',
            'baad': 'baad',
            'pehle': 'pehle',
            'aaj': 'aaj',
            'kal': 'kal',
            'parso': 'parso',
            'roz': 'roz',
            'har din': 'har din',
            'saal': 'saal',
            'mahina': 'mahina',
            'hafta': 'hafta',
            'ghanta': 'ghanta',
            'minat': 'minat',
            'sekand': 'sekand',
            'subah': 'subah',
            'shaam': 'shaam',
            'raat': 'raat',
            'dopahar': 'dopahar',
            'din': 'din',
            'kal': 'kal',
            'pichla': 'pichla',
            'agla': 'agla',
            'naya': 'naya',
            'purana': 'purana',
            'accha': 'badhiya',
            'badhiya': 'badhiya',
            'sundar': 'khubsoorat',
            'khubsoorat': 'khubsoorat',
            'bad-surat': 'ganda',
            'ganda': 'ganda',
            'saaf': 'saaf',
            'mehenga': 'mehenga',
            'sasta': 'sasta',
            'amir': 'amir',
            'gareeb': 'gareeb',
            'bara': 'bara',
            'chota': 'chota',
            'lamba': 'lamba',
            'ooncha': 'ooncha',
            'neecha': 'neecha',
            'gehra': 'gehra',
            'bhari': 'bhari',
            'halka': 'halka',
            'tez': 'tez',
            'dheema': 'dheere',
            'sakht': 'kathin',
            'naram': 'mulayam',
            'mulayam': 'mulayam',
            'garam': 'garam',
            'thanda': 'thanda',
            'meetha': 'meetha',
            'kadva': 'kadva',
            'namkeen': 'namkeen',
            'khatta': 'khatta',
            'taza': 'naya',
            'basi': 'purana',
            'khula': 'khula',
            'band': 'band',
            'asli': 'asli',
            'nakli': 'nakli',
            'sahi': 'sahi',
            'galat': 'galat',
            'pata': 'pata',
            'jaankari': 'pata',
            'gyaan': 'gyaan',
            'shakti': 'takat',
            'himmat': 'himmat',
            'dar': 'dar',
            'sharam': 'sharam',
            'haya': 'sharam',
            'garv': 'abhimaan',
            'abhimaan': 'abhimaan',
            'ghamand': 'abhimaan',
            'prem': 'pyaar',
            'pyaar': 'pyaar',
            'mohabbat': 'pyaar',
            'ishq': 'pyaar',
            'nafrat': 'nafrat',
            'dosti': 'dosti',
            'yaari': 'dosti',
            'vada': 'vada',
            'kasam': 'kasam',
            'shukriya': 'dhanyawaad',
            'dhanyawaad': 'dhanyawaad',
            'maafi': 'maaf',
            'dua': 'dua',
            'namaste': 'namaste',
            'hello': 'hello',
            'bye': 'alvida',
            'alvida': 'alvida',
            'theek': 'theek',
            'bas': 'bas',
            'kafi': 'bahut',
            'itna': 'itna',
            'utna': 'utna',
            'kitna': 'kitna',
            'kyun': 'kyun',
            'kaise': 'kaise',
            'kahan': 'kahan',
            'kab': 'kab',
            'kaun': 'kaun',
            'kya': 'kya',
            'haan': 'haan',
            'nahi': 'nahi',
            'mat': 'mat',
            'na': 'na',
            'shukriya': 'shukriya',
            'theek hai': 'theek hai',
            'zaroor': 'zaroor',
            'shayad': 'shayad',
            'bahut': 'bahut',
            'thoda': 'thoda',
            'kuch': 'kuch',
            'sab': 'sab',
            'koi': 'koi',
            'koi nahi': 'koi nahi',
            'har': 'har',
            'hamesha': 'hamesha',
            'kabhi': 'kabhi',
            'aksar': 'aksar',
            'kabhi nahi': 'kabhi nahi',
            'phir': 'phir',
            'phir se': 'phir se',
            'ek baar': 'ek baar',
            'baar baar': 'baar baar',
            'abhi': 'abhi',
            'turant': 'turant',
            'jaldi': 'jaldi',
            'dheere': 'dheere',
            'sath': 'saath',
            'saath': 'saath',
            'sath mein': 'saath mein',
            'saath mein': 'saath mein',
            'liye': 'liye',
            'liye': 'liye',
            'waaste': 'liye',
            'khilaaf': 'viruddh',
            'viruddh': 'viruddh',
            'vajah': 'kaaran',
            'kaaran': 'kaaran',
            'baare mein': 'baare mein',
            'mutabik': 'anusar',
            'anusar': 'anusar',
            'jagah': 'sthan',
            'sthan': 'sthan',
            'taraf': 'dishaa',
            'dishaa': 'dishaa',
            'andar': 'andar',
            'bahar': 'bahar',
            'upar': 'upar',
            'neeche': 'neeche',
            'aage': 'aage',
            'peeche': 'peeche',
            'dayein': 'dayein',
            'baayein': 'baayein',
            'beech mein': 'beech mein',
            'paas': 'paas',
            'door': 'door',
            'saamne': 'saamne',
            'pehle': 'pehle',
            'baad': 'baad',
            'saath': 'saath',
            'bina': 'bina',
            'alawa': 'bina',
            'is': 'is',
            'us': 'us',
            'ye': 'ye',
            'yeh': 'ye',
            'wo': 'vo',
            'voh': 'vo',
            'mera': 'mera',
            'meri': 'meri',
            'mere': 'mere',
            'tera': 'tera',
            'teri': 'teri',
            'tere': 'tere',
            'iska': 'iska',
            'iski': 'iski',
            'iske': 'iske',
            'uska': 'uska',
            'uski': 'uski',
            'uske': 'uske',
            'hamara': 'hamara',
            'hamari': 'hamari',
            'hamare': 'hamare',
            'tumhara': 'tumhara',
            'tumhari': 'tumhara',
            'tumhare': 'tumhara',
            'unka': 'unka',
            'unki': 'unka',
            'unke': 'unka',
            'apna': 'apna',
            'apni': 'apna',
            'apne': 'apna',
            'main': 'main',
            'tu': 'tu',
            'tum': 'tum',
            'aap': 'aap',
            'woh': 'vo',
            'voh': 'vo',
            'hum': 'hum',
            've': 've',
            'kisi': 'kisi',
            'sab': 'sab',
            'sab log': 'sab log',
            'kuch': 'kuch',
            'koi': 'koi',
            'kaun': 'kaun',
            'kya': 'kya',
            'jo': 'jo',
            'wohi': 'vohi',
            'vohi': 'vohi',
            'yahi': 'yahi',
            'wahi': 'vahi',
            'vahi': 'vahi',
            'maya': 'my-ah',
            'abhay': 'uh-bh-ay',
            'kumar': 'koo-maar',
            'rudrapaul': 'rud-rah-paul',
            'brain': 'brain',
            'system': 'system',
            'status': 'status',
            'ready': 'ready',
            'hello': 'hello',
            'hi': 'hi',
            'good': 'good',
            'morning': 'morning',
            'evening': 'evening',
            'night': 'night',
            'today': 'today',
            'tomorrow': 'tomorrow',
            'yesterday': 'yesterday',
            'weather': 'weather',
            'temperature': 'temperature',
            'forecast': 'forecast',
            'news': 'news',
            'search': 'search',
            'result': 'result',
            'answer': 'answer',
            'calculation': 'calculation',
            'math': 'math',
            'sin': 'sine',
            'cos': 'cosine',
            'tan': 'tangent',
            'sqrt': 'square root',
            'log': 'logarithm',
            'plus': 'plus',
            'minus': 'minus',
            'times': 'times',
            'divided': 'divided',
            'equal': 'equal',
            'zero': 'zero',
            'one': 'one',
            'two': 'two',
            'three': 'three',
            'four': 'four',
            'five': 'five',
            'six': 'six',
            'seven': 'seven',
            'eight': 'eight',
            'nine': 'nine',
            'ten': 'ten',
            'hundred': 'hundred',
            'thousand': 'thousand',
            'lakh': 'lakh',
            'crore': 'crore',
            'rupee': 'rupee',
            'rupees': 'rupees',
            'degree': 'degree',
            'degrees': 'degrees',
            'celsius': 'celsius',
            'fahrenheit': 'fahrenheit',
            'percent': 'percent',
            'humidity': 'humidity',
            'wind': 'wind',
            'speed': 'speed',
            'km': 'kilometers',
            'km/h': 'kilometers per hour',
            'city': 'city',
            'country': 'country',
            'india': 'india',
            'tripura': 'tripura',
            'agartala': 'agartala',
            'delhi': 'delhi',
            'mumbai': 'mumbai',
            'bangalore': 'bangalore',
            'kolkata': 'kolkata',
            'chennai': 'chennai',
            'hyderabad': 'hyderabad',
            'pune': 'pune',
            'ahmedabad': 'ahmedabad',
            'jaipur': 'jaipur',
            'lucknow': 'lucknow',
            'patna': 'patna',
            'guwahati': 'guwahati',
            'shillong': 'shillong',
            'imphal': 'imphal',
            'kohima': 'kohima',
            'aizawl': 'aizawl',
            'gangtok': 'gangtok',
            'itanagar': 'itanagar',
            'she': 'she',
            'it': 'it',
            'this': 'this',
            'that': 'that',
            'these': 'these',
            'those': 'those',
            'what': 'what',
            'where': 'where',
            'when': 'when',
            'why': 'why',
            'how': 'how',
            'who': 'who',
            'which': 'which',
            'can': 'can',
            'will': 'will',
            'would': 'would',
            'should': 'should',
            'could': 'could',
            'may': 'may',
            'might': 'might',
            'must': 'must',
            'shall': 'shall',
            'do': 'do',
            'does': 'does',
            'did': 'did',
            'done': 'done',
            'doing': 'doing',
            'go': 'go',
            'goes': 'goes',
            'went': 'went',
            'gone': 'gone',
            'going': 'going',
            'come': 'come',
            'comes': 'comes',
            'came': 'came',
            'coming': 'coming',
            'see': 'see',
            'sees': 'sees',
            'saw': 'saw',
            'seen': 'seen',
            'seeing': 'seeing',
            'get': 'get',
            'gets': 'gets',
            'got': 'got',
            'gotten': 'gotten',
            'getting': 'getting',
            'make': 'make',
            'makes': 'makes',
            'made': 'made',
            'making': 'making',
            'take': 'take',
            'takes': 'takes',
            'took': 'took',
            'taken': 'taken',
            'taking': 'taking',
            'give': 'give',
            'gives': 'gives',
            'gave': 'gave',
            'given': 'given',
            'giving': 'giving',
            'know': 'know',
            'knows': 'knows',
            'knew': 'knew',
            'known': 'known',
            'knowing': 'knowing',
            'think': 'think',
            'thinks': 'thinks',
            'thought': 'thought',
            'thinking': 'thinking',
            'say': 'say',
            'says': 'says',
            'said': 'said',
            'saying': 'saying',
            'tell': 'tell',
            'tells': 'tells',
            'told': 'told',
            'telling': 'telling',
            'ask': 'ask',
            'asks': 'asks',
            'asked': 'asked',
            'asking': 'asking',
            'work': 'work',
            'works': 'works',
            'worked': 'worked',
            'working': 'working',
            'try': 'try',
            'tries': 'tries',
            'tried': 'tried',
            'trying': 'trying',
            'need': 'need',
            'needs': 'needs',
            'needed': 'needed',
            'needing': 'needing',
            'want': 'want',
            'wants': 'wants',
            'wanted': 'wanted',
            'wanting': 'wanting',
            'like': 'like',
            'likes': 'likes',
            'liked': 'liked',
            'liking': 'liking',
            'love': 'love',
            'loves': 'loves',
            'loved': 'loved',
            'loving': 'loving',
            'hate': 'hate',
            'hates': 'hates',
            'hated': 'hated',
            'hating': 'hating',
            'good': 'good',
            'bad': 'bad',
            'better': 'better',
            'best': 'best',
            'worse': 'worse',
            'worst': 'worst',
            'big': 'big',
            'small': 'small',
            'large': 'large',
            'little': 'little',
            'long': 'long',
            'short': 'short',
            'high': 'high',
            'low': 'low',
            'hot': 'hot',
            'cold': 'cold',
            'warm': 'warm',
            'cool': 'cool',
            'fast': 'fast',
            'slow': 'slow',
            'quick': 'quick',
            'new': 'new',
            'old': 'old',
            'young': 'young',
            'easy': 'easy',
            'hard': 'hard',
            'difficult': 'difficult',
            'simple': 'simple',
            'complex': 'complex',
            'important': 'important',
            'special': 'special',
            'normal': 'normal',
            'regular': 'regular',
            'strange': 'strange',
            'weird': 'weird',
            'funny': 'funny',
            'serious': 'serious',
            'happy': 'happy',
            'sad': 'sad',
            'angry': 'angry',
            'excited': 'excited',
            'bored': 'bored',
            'tired': 'tired',
            'sleepy': 'sleepy',
            'hungry': 'hungry',
            'thirsty': 'thirsty',
            'sick': 'sick',
            'healthy': 'healthy',
            'strong': 'strong',
            'weak': 'weak',
            'rich': 'rich',
            'poor': 'poor',
            'expensive': 'expensive',
            'cheap': 'cheap',
            'free': 'free',
            'busy': 'busy',
            'free': 'free',
            'available': 'available',
            'ready': 'ready',
            'prepared': 'prepared',
            'sure': 'sure',
            'certain': 'certain',
            'uncertain': 'uncertain',
            'confused': 'confused',
            'clear': 'clear',
            'unclear': 'unclear',
            'true': 'true',
            'false': 'false',
            'right': 'right',
            'wrong': 'wrong',
            'correct': 'correct',
            'incorrect': 'incorrect',
            'yes': 'yes',
            'no': 'no',
            'maybe': 'maybe',
            'perhaps': 'perhaps',
            'possibly': 'possibly',
            'definitely': 'definitely',
            'absolutely': 'absolutely',
            'exactly': 'exactly',
            'approximately': 'approximately',
            'almost': 'almost',
            'nearly': 'nearly',
            'completely': 'completely',
            'partially': 'partially',
            'finally': 'finally',
            'eventually': 'eventually',
            'suddenly': 'suddenly',
            'immediately': 'immediately',
            'quickly': 'quickly',
            'slowly': 'slowly',
            'carefully': 'carefully',
            'easily': 'easily',
            'difficultly': 'difficultly',
            'happily': 'happily',
            'sadly': 'sadly',
            'angrily': 'angrily',
            'quietly': 'quietly',
            'loudly': 'loudly',
            'softly': 'softly',
            'hardly': 'hardly',
            'barely': 'barely',
            'rarely': 'rarely',
            'often': 'often',
            'sometimes': 'sometimes',
            'always': 'always',
            'never': 'never',
            'again': 'again',
            'once': 'once',
            'twice': 'twice',
            'first': 'first',
            'second': 'second',
            'third': 'third',
            'last': 'last',
            'next': 'next',
            'previous': 'previous',
            'before': 'before',
            'after': 'after',
            'during': 'during',
            'while': 'while',
            'until': 'until',
            'since': 'since',
            'already': 'already',
            'still': 'still',
            'yet': 'yet',
            'now': 'now',
            'then': 'then',
            'soon': 'soon',
            'later': 'later',
            'early': 'early',
            'late': 'late',
            'today': 'today',
            'tomorrow': 'tomorrow',
            'yesterday': 'yesterday',
            'morning': 'morning',
            'afternoon': 'afternoon',
            'evening': 'evening',
            'night': 'night',
            'day': 'day',
            'week': 'week',
            'month': 'month',
            'year': 'year',
            'hour': 'hour',
            'minute': 'minute',
            'second': 'second',
            'moment': 'moment',
            'time': 'time',
            'place': 'place',
            'space': 'space',
            'area': 'area',
            'location': 'location',
            'position': 'position',
            'direction': 'direction',
            'way': 'way',
            'path': 'path',
            'road': 'road',
            'street': 'street',
            'house': 'house',
            'home': 'home',
            'room': 'room',
            'building': 'building',
            'office': 'office',
            'school': 'school',
            'hospital': 'hospital',
            'store': 'store',
            'shop': 'shop',
            'market': 'market',
            'city': 'city',
            'town': 'town',
            'village': 'village',
            'country': 'country',
            'world': 'world',
            'earth': 'earth',
            'sky': 'sky',
            'sun': 'sun',
            'moon': 'moon',
            'star': 'star',
            'cloud': 'cloud',
            'rain': 'rain',
            'snow': 'snow',
            'wind': 'wind',
            'weather': 'weather',
            'temperature': 'temperature',
            'season': 'season',
            'spring': 'spring',
            'summer': 'summer',
            'fall': 'fall',
            'autumn': 'autumn',
            'winter': 'winter',
            'person': 'person',
            'people': 'people',
            'man': 'man',
            'woman': 'woman',
            'child': 'child',
            'children': 'children',
            'baby': 'baby',
            'boy': 'boy',
            'girl': 'girl',
            'family': 'family',
            'friend': 'friend',
            'enemy': 'enemy',
            'neighbor': 'neighbor',
            'stranger': 'stranger',
            'guest': 'guest',
            'host': 'host',
            'customer': 'customer',
            'client': 'client',
            'boss': 'boss',
            'employee': 'employee',
            'worker': 'worker',
            'student': 'student',
            'teacher': 'teacher',
            'doctor': 'doctor',
            'nurse': 'nurse',
            'driver': 'driver',
            'pilot': 'pilot',
            'engineer': 'engineer',
            'artist': 'artist',
            'musician': 'musician',
            'writer': 'writer',
            'reader': 'reader',
            'speaker': 'speaker',
            'listener': 'listener',
            'helper': 'helper',
            'leader': 'leader',
            'follower': 'follower',
            'winner': 'winner',
            'loser': 'loser',
            'player': 'player',
            'team': 'team',
            'group': 'group',
            'crowd': 'crowd',
            'audience': 'audience',
            'public': 'public',
            'society': 'society',
            'community': 'community',
            'government': 'government',
            'police': 'police',
            'army': 'army',
            'navy': 'navy',
            'air': 'air',
            'force': 'force',
            'power': 'power',
            'energy': 'energy',
            'strength': 'strength',
            'force': 'force',
            'pressure': 'pressure',
            'weight': 'weight',
            'mass': 'mass',
            'size': 'size',
            'shape': 'shape',
            'color': 'color',
            'colour': 'colour',
            'sound': 'sound',
            'noise': 'noise',
            'music': 'music',
            'song': 'song',
            'voice': 'voice',
            'speech': 'speech',
            'language': 'language',
            'word': 'word',
            'sentence': 'sentence',
            'paragraph': 'paragraph',
            'story': 'story',
            'book': 'book',
            'page': 'page',
            'letter': 'letter',
            'number': 'number',
            'count': 'count',
            'amount': 'amount',
            'quantity': 'quantity',
            'quality': 'quality',
            'value': 'value',
            'price': 'price',
            'cost': 'cost',
            'money': 'money',
            'cash': 'cash',
            'card': 'card',
            'bank': 'bank',
            'account': 'account',
            'debt': 'debt',
            'loan': 'loan',
            'credit': 'credit',
            'debit': 'debit',
            'payment': 'payment',
            'bill': 'bill',
            'check': 'check',
            'cheque': 'cheque',
            'currency': 'currency',
            'dollar': 'dollar',
            'rupee': 'rupee',
            'pound': 'pound',
            'euro': 'euro',
            'yen': 'yen',
            'yuan': 'yuan',
            'computer': 'computer',
            'phone': 'phone',
            'mobile': 'mobile',
            'tablet': 'tablet',
            'laptop': 'laptop',
            'desktop': 'desktop',
            'screen': 'screen',
            'monitor': 'monitor',
            'keyboard': 'keyboard',
            'mouse': 'mouse',
            'printer': 'printer',
            'scanner': 'scanner',
            'camera': 'camera',
            'video': 'video',
            'photo': 'photo',
            'picture': 'picture',
            'image': 'image',
            'file': 'file',
            'folder': 'folder',
            'document': 'document',
            'data': 'data',
            'information': 'information',
            'knowledge': 'knowledge',
            'education': 'education',
            'learning': 'learning',
            'teaching': 'teaching',
            'training': 'training',
            'practice': 'practice',
            'exercise': 'exercise',
            'game': 'game',
            'sport': 'sport',
            'play': 'play',
            'match': 'match',
            'competition': 'competition',
            'contest': 'contest',
            'race': 'race',
            'fight': 'fight',
            'battle': 'battle',
            'war': 'war',
            'peace': 'peace',
            'conflict': 'conflict',
            'argument': 'argument',
            'discussion': 'discussion',
            'conversation': 'conversation',
            'talk': 'talk',
            'chat': 'chat',
            'meeting': 'meeting',
            'conference': 'conference',
            'presentation': 'presentation',
            'speech': 'speech',
            'lecture': 'lecture',
            'class': 'class',
            'course': 'course',
            'lesson': 'lesson',
            'subject': 'subject',
            'topic': 'topic',
            'theme': 'theme',
            'idea': 'idea',
            'thought': 'thought',
            'opinion': 'opinion',
            'view': 'view',
            'perspective': 'perspective',
            'attitude': 'attitude',
            'belief': 'belief',
            'faith': 'faith',
            'trust': 'trust',
            'hope': 'hope',
            'dream': 'dream',
            'wish': 'wish',
            'desire': 'desire',
            'goal': 'goal',
            'target': 'target',
            'objective': 'objective',
            'purpose': 'purpose',
            'reason': 'reason',
            'cause': 'cause',
            'effect': 'effect',
            'result': 'result',
            'outcome': 'outcome',
            'consequence': 'consequence',
            'impact': 'impact',
            'influence': 'influence',
            'change': 'change',
            'development': 'development',
            'progress': 'progress',
            'improvement': 'improvement',
            'growth': 'growth',
            'success': 'success',
            'failure': 'failure',
            'mistake': 'mistake',
            'error': 'error',
            'problem': 'problem',
            'issue': 'issue',
            'challenge': 'challenge',
            'difficulty': 'difficulty',
            'obstacle': 'obstacle',
            'barrier': 'barrier',
            'limitation': 'limitation',
            'restriction': 'restriction',
            'rule': 'rule',
            'law': 'law',
            'regulation': 'regulation',
            'policy': 'policy',
            'procedure': 'procedure',
            'process': 'process',
            'method': 'method',
            'technique': 'technique',
            'approach': 'approach',
            'strategy': 'strategy',
            'plan': 'plan',
            'program': 'program',
            'project': 'project',
            'task': 'task',
            'job': 'job',
            'work': 'work',
            'duty': 'duty',
            'responsibility': 'responsibility',
            'role': 'role',
            'position': 'position',
            'function': 'function',
            'operation': 'operation',
            'activity': 'activity',
            'action': 'action',
            'behavior': 'behavior',
            'performance': 'performance',
            'achievement': 'achievement',
            'accomplishment': 'accomplishment',
            'skill': 'skill',
            'ability': 'ability',
            'talent': 'talent',
            'capacity': 'capacity',
            'potential': 'potential',
            'possibility': 'possibility',
            'opportunity': 'opportunity',
            'chance': 'chance',
            'risk': 'risk',
            'danger': 'danger',
            'threat': 'threat',
            'warning': 'warning',
            'advice': 'advice',
            'suggestion': 'suggestion',
            'recommendation': 'recommendation',
            'request': 'request',
            'demand': 'demand',
            'offer': 'offer',
            'proposal': 'proposal',
            'invitation': 'invitation',
            'application': 'application',
            'form': 'form',
            'application': 'application',
            'registration': 'registration',
            'reservation': 'reservation',
            'booking': 'booking',
            'order': 'order',
            'purchase': 'purchase',
            'sale': 'sale',
            'deal': 'deal',
            'agreement': 'agreement',
            'contract': 'contract',
            'promise': 'promise',
            'commitment': 'commitment',
            'decision': 'decision',
            'choice': 'choice',
            'selection': 'selection',
            'option': 'option',
            'alternative': 'alternative',
            'possibility': 'possibility',
            'solution': 'solution',
            'answer': 'answer',
            'response': 'response',
            'reply': 'reply',
            'reaction': 'reaction',
            'feedback': 'feedback',
            'comment': 'comment',
            'remark': 'remark',
            'statement': 'statement',
            'declaration': 'declaration',
            'announcement': 'announcement',
            'news': 'news',
            'information': 'information',
            'message': 'message',
            'communication': 'communication',
            'contact': 'contact',
            'connection': 'connection',
            'relationship': 'relationship',
            'friendship': 'friendship',
            'partnership': 'partnership',
            'marriage': 'marriage',
            'family': 'family',
            'relative': 'relative',
            'parent': 'parent',
            'mother': 'mother',
            'father': 'father',
            'son': 'son',
            'daughter': 'daughter',
            'brother': 'brother',
            'sister': 'sister',
            'husband': 'husband',
            'wife': 'wife',
            'uncle': 'uncle',
            'aunt': 'aunt',
            'cousin': 'cousin',
            'nephew': 'nephew',
            'niece': 'niece',
            'grandfather': 'grandfather',
            'grandmother': 'grandmother',
            'grandson': 'grandson',
            'granddaughter': 'granddaughter'
        }
        
        if VOICE_AVAILABLE:
            try:
                self.engine = tts_init()
                
                # Set sweet girl voice
                voices = self.engine.getProperty('voices')
                if len(voices) > 0:
                    # Try to find a female voice
                    indian_voice = None
                    female_voice = None
                    zira_voice = None
                    
                    for voice in voices:
                        voice_id = voice.id.lower()
                        voice_name = voice.name.lower()
                        
                        # Look for Indian voices first (high priority)
                        if any(kw in voice_name or kw in voice_id for kw in ['india', 'hindi', 'kalpana', 'heera', 'ravi']):
                            indian_voice = voice
                            break
                        
                        # Look for Zira specifically (sweet female voice)
                        if 'zira' in voice_id or 'zira' in voice_name:
                            zira_voice = voice
                        # Look for other female voices
                        elif any(keyword in voice_id or keyword in voice_name for keyword in ['female', 'woman', 'girl', 'hazel', 'samantha']):
                            if not female_voice:
                                female_voice = voice
                    
                    # Priority: Indian > Zira > other female > any non-male voice
                    selected_voice = indian_voice or zira_voice or female_voice
                    
                    if selected_voice:
                        self.engine.setProperty('voice', selected_voice.id)
                        self.voice_female = selected_voice
                        print(f"🌸 Selected female voice: {selected_voice.name}")
                    elif len(voices) > 1:
                        # Fallback to second voice (avoid David which is male)
                        for voice in voices:
                            voice_name = voice.name.lower()
                            if 'david' not in voice_name:
                                self.engine.setProperty('voice', voice.id)
                                self.voice_female = voice
                                print(f"🌸 Selected alternative female voice: {voice.name}")
                                break
                
                # Set sweet girl voice parameters
                self.engine.setProperty('rate', 150)  # Slightly slower for sweet speech
                self.engine.setProperty('volume', 0.9)  # Slightly softer volume
                
                # Try to set higher pitch for more feminine sound
                try:
                    self.engine.setProperty('pitch', 200)  # Higher pitch for girl voice
                except:
                    pass  # Some TTS engines don't support pitch
                
                logger.info("✅ TTS initialized")
            except Exception as e:
                logger.error(f"❌ TTS init error: {e}")
                VOICE_AVAILABLE = False
    
    def _hinglish_to_phonetic(self, text: str) -> str:
        """Convert Hinglish text to phonetic English for better TTS pronunciation"""
        if not HINGLISH_MODE:
            return text
        
        words = text.lower().split()
        converted = []
        for word in words:
            # Remove punctuation for lookup
            clean_word = word.strip('.,!?;:')
            if clean_word in self.hinglish_phonetics:
                # Replace with phonetic but keep original punctuation
                suffix = word[len(clean_word):] if len(word) > len(clean_word) else ''
                converted.append(self.hinglish_phonetics[clean_word] + suffix)
            else:
                converted.append(word)
        return ' '.join(converted)
    
    def speak(self, text: str, wait: bool = True) -> bool:
        """Speak text with Hinglish phonetic conversion and queue handling"""
        if not VOICE_AVAILABLE or not self.engine:
            if DEBUG_MODE:
                logger.info(f"💬 [Would speak]: {text}")
            return False
        
        try:
            # Clean text for better speech
            clean_text = text.replace('🌍', '').replace('🌡️', '').replace('☁️', '').replace('💧', '').replace('💨', '').replace('🌫️', '').replace('📰', '').replace('🦆', '').replace('🔗', '')
            clean_text = clean_text.replace('*', '').replace('#', '').replace('_', '')
            
            # Convert Hinglish to phonetic English for better pronunciation
            if HINGLISH_MODE:
                phonetic_text = self._hinglish_to_phonetic(clean_text)
                if phonetic_text != clean_text:
                    logger.info(f"🔄 Hinglish converted: {phonetic_text[:60]}...")
                    clean_text = phonetic_text
            
            logger.info(f"🔊 Speaking: {clean_text[:50]}...")
            
            # Stop any current speech to prevent "run loop already started" error
            try:
                self.engine.stop()
            except:
                pass
            
            self.engine.say(clean_text)
            
            if wait:
                try:
                    self.engine.runAndWait()
                except RuntimeError:
                    # If run loop already started, just say without waiting
                    logger.warning("⚠️ TTS run loop busy, speaking without wait")
                    pass
            
            return True
        except Exception as e:
            logger.error(f"❌ TTS error: {e}")
            return False
    
    def speak_async(self, text: str):
        """Speak without waiting"""
        return self.speak(text, wait=False)


class GoogleIndianTTS:
    """Google TTS for soft and clear Indian pronunciation"""
    
    def __init__(self):
        self.temp_dir = "temp_audio"
        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info("🎙️ Google Indian TTS initialized")

    def _play_audio(self, filepath):
        """Play audio using playsound"""
        try:
            playsound(filepath)
        except Exception as e:
            logger.error(f"❌ Audio playback error: {e}")

    def speak(self, text: str, wait: bool = True) -> bool:
        """Speak text with soft Indian English and Hindi accent"""
        try:
            # Clean text
            clean_text = text.replace('🌍', '').replace('🌡️', '').replace('☁️', '').replace('💧', '').replace('💨', '').replace('🌫️', '').replace('📰', '').replace('🦆', '').replace('🔗', '')
            clean_text = clean_text.replace('*', '').replace('#', '').replace('_', '')
            
            # Detect language (simple check for Hindi characters)
            lang = 'hi' if any('\u0900' <= c <= '\u097F' for c in clean_text) else 'en'
            tld = 'co.in' # Use Indian domain for better accent
            
            filename = f"maya_gtts_{int(time.time())}.mp3"
            filepath = os.path.join(self.temp_dir, filename)
            
            tts = gTTS(text=clean_text, lang=lang, tld=tld, slow=False)
            tts.save(filepath)
            
            logger.info(f"🔊 Speaking (Google Indian): {clean_text[:50]}...")
            self._play_audio(filepath)
            
            # Simple cleanup
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except:
                pass
                
            return True
        except Exception as e:
            logger.error(f"❌ Google TTS error: {e}")
            return False


class VoiceInterface:
    """Complete voice interface"""
    
    def __init__(self):
        self.recognizer = VoiceRecognition()
        
        # Priority: gTTS (Google Indian) for soft/clear pronunciation
        try:
            self.speaker = GoogleIndianTTS()
            logger.info("🎙️ Using Google Indian TTS (Soft & Clear)")
        except Exception as e:
            logger.warning(f"⚠️ Google TTS init failed, falling back: {e}")
            # Choose fallback TTS engine
            if TTS_ENGINE == "narakeet":
                self.speaker = NarakeetTTS()
                logger.info("🎙️ Using Narakeet Cloud TTS")
            elif TTS_ENGINE in ["xtts", "chattts", "indic"]:
                self.speaker = AdvancedTTS(model_type=TTS_ENGINE)
                logger.info(f"🎙️ Using Advanced AI TTS: {TTS_ENGINE}")
            else:
                self.speaker = TextToSpeech()
                logger.info("🎙️ Using pyttsx3 Local TTS")
            
        self.enabled = VOICE_AVAILABLE and VOICE_MODE
    
    def _get_user_name(self) -> str:
        """Get respectful title for user - Maya calls user 'sir' or 'boss'"""
        import random
        return random.choice(["sir", "boss"])
    
    def _get_conversational_fallback(self) -> str:
        """Get a friendly, varied response when speech isn't understood"""
        import random
        user_name = self._get_user_name()
        name_prefix = f" {user_name}" if user_name else ""
        
        fallbacks = [
            f"Sorry{name_prefix}, mujhe theek se samajh nahi aaya. Kya aap please dobara bol sakte hain?",
            f"Hmm{name_prefix}, main thoda confuse ho gayi. Aap phir se bolo?",
            f"Excuse me{name_prefix}, kya aap please slow mein bolo?",
            f"Sorry{name_prefix}, awaaz clear nahi aayi. Ek baar aur?",
            f"Main sunn rahi hoon{name_prefix}, lekin samajh nahi paayi. Please repeat?",
        ]
        return random.choice(fallbacks)
    
    def _get_personalized_greeting(self) -> str:
        """Get a warm, personalized greeting using memory"""
        import random
        from datetime import datetime
        
        user_name = self._get_user_name()
        name_part = f" {user_name}" if user_name else ""
        
        hour = datetime.now().hour
        if 5 <= hour < 12:
            time_greeting = random.choice([
                f"Good morning{name_part}! Aaj ka din shubh ho!",
                f"Namaste{name_part}! Subah ho gayi, kya plan hai?",
                f"Good morning{name_part}! Main aapke liye ready hoon.",
            ])
        elif 12 <= hour < 17:
            time_greeting = random.choice([
                f"Good afternoon{name_part}! Kaise chal raha hai din?",
                f"Hey{name_part}! Main yahan hoon, bolo kya karna hai?",
                f"Hello{name_part}! Aapki madad ke liye ready hoon.",
            ])
        elif 17 <= hour < 21:
            time_greeting = random.choice([
                f"Good evening{name_part}! Shaam ka time, thoda relax karo.",
                f"Evening{name_part}! Kuch chai-coffee ho jaye?",
                f"Hey{name_part}! Main hoon na, bolo kya chahiye?",
            ])
        else:
            time_greeting = random.choice([
                f"Hello{name_part}! Der ho gayi hai, par main ready hoon.",
                f"Hi{name_part}! Aap abhi tak jag rahe ho? Main bhi hoon!",
                f"Good night{name_part}! Kuch last minute kaam hai?",
            ])
        
        return time_greeting
    
    def voice_chat(self, query: str = None) -> str:
        """Voice chat interface with conversational personality"""
        if not self.enabled:
            return None
        
        try:
            # Listen for command if not provided
            if not query:
                query = self.listen_for_command(timeout=10)
                
                if not query:
                    # Use friendly conversational fallback instead of static "samajh nahi aaya"
                    fallback = self._get_conversational_fallback()
                    print(f"🤖 {fallback}")
                    self.speaker.speak(fallback)
                    return None
            
            # Extract command from wake word
            if self.recognizer.detect_wake_word(query):
                query = query.replace(WAKE_WORD.lower(), "").strip()
                query = query.replace("maya", "").strip()
                query = query.replace("hey", "").strip()
            
            return query
        
        except Exception as e:
            logger.error(f"❌ Voice chat error: {e}")
            # Even on error, be friendly
            try:
                self.speaker.speak("Sorry, ek choti si problem ho gayi. Please phir se bolo.")
            except:
                pass
            return None

    def listen_for_command(self, timeout: int = 10) -> str:
        """Bridge to recognizer.listen_for_command"""
        return self.recognizer.listen_for_command(timeout)
    
    def speak_response(self, text: str, async_mode: bool = False):
        """Speak response"""
        if not self.enabled:
            return
        
        try:
            if async_mode:
                self.speaker.speak_async(text)
            else:
                self.speaker.speak(text)
        except Exception as e:
            logger.error(f"❌ Error speaking: {e}")
    
    def _get_farewell(self) -> str:
        """Get a warm, personalized farewell"""
        import random
        user_name = self._get_user_name()
        name_part = f" {user_name}" if user_name else ""
        
        return random.choice([
            f"Bye bye{name_part}! Aapka khayal rakhna!",
            f"Theek hai{name_part}, phir milenge! Take care!",
            f"Alvida{name_part}! Aapka din shubh ho!",
            f"Bye{name_part}! Jab bhi zaroorat ho, bas bolo!",
            f"See you{name_part}! Main hamesha yahan hoon!",
        ])
    
    def interactive_mode(self, process_callback):
        """Interactive voice mode with conversational personality and memory"""
        if not self.enabled:
            logger.warning("⚠️  Voice mode disabled")
            return
        
        logger.info("🎤 Entering voice mode...")
        print("\n🎤 Voice Mode Active - Speak your command")
        print("Say 'exit' to quit\n")
        
        # Use personalized greeting based on memory
        greeting = self._get_personalized_greeting()
        print(f"🤖 {greeting}")
        
        # Use voice_processor's non-blocking TTS to avoid COM conflicts
        try:
            from modules.voice_processor import voice_output
            voice_output.speak(greeting, blocking=True)
        except Exception as e:
            logger.warning(f"⚠️ Voice greeting via voice_processor failed: {e}")
            # Fallback to regular TTS
            try:
                self.speaker.speak(greeting)
                time.sleep(2)
            except:
                pass
        
        # Conversational flow counter
        interaction_count = 0
        
        try:
            while True:
                # Listen for command with better error handling
                query = None
                try:
                    query = self.voice_chat()
                except Exception as listen_err:
                    logger.error(f"❌ Listening error: {listen_err}")
                    continue
                
                if query:
                    interaction_count += 1
                    logger.info(f"📝 Query #{interaction_count}: {query}")
                    print(f"📝 Heard: '{query}'")
                    
                    # Handle 'exit' command
                    if query.lower() in ['exit', 'quit', 'bye', 'goodbye', 'band karo', 'chalo bye']:
                        farewell = self._get_farewell()
                        print(f"🤖 {farewell}")
                        self.speak_response(farewell, async_mode=False)
                        print("👋 Voice mode ended by user")
                        break
                    
                    # Process query with callback - instant brain connection
                    response = None
                    try:
                        response = process_callback(query)
                    except Exception as proc_err:
                        logger.error(f"❌ Processing error: {proc_err}")
                        err_msg = "Sorry, kuch error ho gaya. Phir se bolo."
                        print(f"\n❌ {err_msg}\n")
                        self.speak_response(err_msg, async_mode=False)
                        continue
                    
                    if response:
                        # Show and speak response in VUI
                        logger.info(f"🔊 Response: {str(response)[:80]}...")
                        print(f"🔊 Response delivered")
                        
                        # After 3+ interactions, add a friendly follow-up occasionally
                        if interaction_count > 0 and interaction_count % 5 == 0:
                            follow_ups = [
                                "Kuch aur bhi chahiye?",
                                "Aur koi madad?",
                                "Main yahan hoon, bolo!",
                            ]
                            import random
                            follow = random.choice(follow_ups)
                            time.sleep(0.5)
                            self.speak_response(follow, async_mode=False)
                
                time.sleep(0.3)  # Faster loop for instant response
        
        except KeyboardInterrupt:
            logger.info("👋 Voice mode ended")
            farewell = self._get_farewell()
            self.speak_response(farewell, async_mode=False)
        except Exception as e:
            logger.error(f"❌ VUI Loop error: {e}")
            try:
                self.speak_response("Voice mode band ho gaya. Phir milenge!", async_mode=False)
            except:
                pass


# Singleton
voice_interface = VoiceInterface()

if DEBUG_MODE:
    print("🎤 Maya Voice Module initialized")
    if VOICE_AVAILABLE and VOICE_MODE:
        print("🔊 Voice mode ENABLED")
    else:
        print("🔇 Voice mode disabled")
