"""
Maya AI Hinglish Response Generator
Converts English responses to Hinglish (Hindi + English mix)
"""

import random
import logging
from config import HINGLISH_MODE

logger = logging.getLogger(__name__)


class HinglishConverter:
    """Convert responses to Hinglish style with Maya AI personality"""
    
    # Maya AI personality prefixes and suffixes
    MAYA_PREFIXES = [
        "Bhai, ",
        "Arre, ",
        "Haan bhai, ",
        "Dekho bhai, ",
        "Samjho bhai, ",
        "Main keh rahi hoon ki, ",
        "Meri taraf se, ",
        ""
    ]
    
    MAYA_SUFFIXES = [
        " bhai!",
        " bhai 😊",
        " jaaneman!",
        " samjhe?",
        " theek hai?",
        "!",
        " 😊",
        ""
    ]
    
    # Common Hinglish replacements
    REPLACEMENTS = {
        # Greetings
        "hello": "Namaste",
        "hi": "Hi",
        "goodbye": "Phir se milenge",
        "bye": "Bye",
        "good morning": "Subah ki namaste",
        "good afternoon": "Dophahaar",
        "good evening": "Shaam ko namaste",
        "good night": "Raat ko sone jaao",
        
        # Common actions
        "please": "Kripaya",
        "thank you": "Shukriya",
        "thanks": "Thanks",
        "yes": "Haan",
        "no": "Nahi",
        "ok": "Theek hai",
        "okay": "Theek hai",
        "sure": "Bilkul",
        "done": "Kar diya",
        
        # Emotions
        "happy": "Khush",
        "sad": "Udas",
        "angry": "Gussa",
        "excited": "Utsaah",
        "tired": "Thak gaya",
        
        # Questions
        "what": "Kya",
        "where": "Kahan",
        "when": "Kab",
        "who": "Kaun",
        "why": "Kyun",
        "how": "Kaise",
        
        # Common words
        "open": "Khol",
        "close": "Band",
        "start": "Shuru",
        "stop": "Ruko",
        "wait": "Ruko",
        "quick": "Jaldi",
        "fast": "Tez",
        "slow": "Slow",
        "small": "Chota",
        "big": "Bada",
        "good": "Acha",
        "bad": "Bura",
        "help": "Madad",
        "error": "Galti",
        "problem": "Masla",
        "solution": "Hal",
    }
    
    # Response prefixes and suffixes
    PREFIXES = [
        "✅ ",
        "🤖 ",
        "💫 ",
        "⚡ ",
    ]
    
    HINGLISH_PHRASES = {
        "understood": "Samajh gaya",
        "i will do": "Main kar dunga",
        "let me": "Main",
        "processing": "Process kar raha hoon",
        "completed": "Complete ho gaya",
        "working on it": "Kaam kar raha hoon",
        "found": "Mil gaya",
        "not found": "Nahi mila",
        "success": "Kamyab",
        "failed": "Fail",
        "trying": "Koshish kar raha hoon",
        "check again": "Dobara check karo",
        "seems like": "Lag raha hai",
        "might be": "Ho sakta hai",
        "about": "Lagbhag",
        "approx": "Lagbhag",
        "almost": "Lagbhag",
        "very": "Bahut",
        "too much": "Bahut zyada",
        "too little": "Bahut kam",
        "average": "Madhyam",
        "recent": "Haal",
        "just now": "Abhi",
        "wait": "Ruko",
        "later": "Baad mein",
        "soon": "Jaldi",
        "finally": "Akhir",
    }
    
    def convert(self, text: str, mode: str = "light", add_personality: bool = True) -> str:
        """Convert text to Hinglish with Maya AI personality
        
        Args:
            text: English text to convert
            mode: "light" (minimal), "medium" (moderate), "heavy" (maximum mixing)
            add_personality: Add Maya AI personality prefixes/suffixes
        
        Returns:
            Hinglish converted text
        """
        if not HINGLISH_MODE or not text:
            return text
        
        result = text.lower()
        
        # Add Maya AI personality
        if add_personality and random.random() > 0.3:  # 70% chance to add personality
            prefix = random.choice(self.MAYA_PREFIXES)
            suffix = random.choice(self.MAYA_SUFFIXES)
            result = prefix + result + suffix
        
        if mode in ["light", "medium", "heavy"]:
            # Apply phrase replacements first (higher priority)
            for eng, hindi in HinglishConverter.HINGLISH_PHRASES.items():
                if eng in result:
                    result = result.replace(eng, hindi)
            
            # Apply word replacements
            for eng, hindi in HinglishConverter.REPLACEMENTS.items():
                # Use word boundaries for more accurate replacement
                import re
                pattern = r'\b' + eng + r'\b'
                result = re.sub(pattern, hindi, result, flags=re.IGNORECASE)
        
        # Capitalize first letter if present
        if result and result[0].isalpha():
            result = result[0].upper() + result[1:]
        
        return result
    
    @staticmethod
    def add_hinglish_flair(text: str) -> str:
        """Add Hinglish expressions and flair"""
        flair_phrases = [
            " 🇮🇳",
            " Bhai!",
            " Samjhe?",
            " Theek hai",
            " Bilkul",
            " Haan Bhai",
            " Phir se mil",
        ]
        
        # Randomly add flair sometimes
        if random.random() < 0.3:
            return text + random.choice(flair_phrases[:3])
        
        return text
    
    @staticmethod
    def make_response_hinglish(response: str, style: str = "light") -> str:
        """Transform entire response to Hinglish"""
        # Split into sentences
        sentences = response.split('. ')
        converted = []
        
        for sentence in sentences:
            converted.append(HinglishConverter.convert(sentence.strip(), style))
        
        result = '. '.join(converted)
        
        if style == "heavy":
            result = HinglishConverter.add_hinglish_flair(result)
        
        return result


class ResponseFormatter:
    """Format responses nicely"""
    
    @staticmethod
    def format_success(message: str) -> str:
        """Format success response"""
        return f"✅ {message}"
    
    @staticmethod
    def format_error(message: str) -> str:
        """Format error response"""
        return f"❌ {message}"
    
    @staticmethod
    def format_info(message: str) -> str:
        """Format info response"""
        return f"ℹ️  {message}"
    
    @staticmethod
    def format_warning(message: str) -> str:
        """Format warning response"""
        return f"⚠️  {message}"
    
    @staticmethod
    def format_processing(message: str) -> str:
        """Format processing response"""
        return f"⏳ {message}"
    
    @staticmethod
    def format_custom(emoji: str, message: str) -> str:
        """Format with custom emoji"""
        return f"{emoji} {message}"


# Common response templates
RESPONSE_TEMPLATES = {
    "greeting": {
        "morning": "🌅 Subah ki namaste, {name}!",
        "afternoon": "☀️  Dophahaar, {name}!",
        "evening": "🌅 Shaam ko namaste, {name}!",
        "night": "🌙 Raat ko sona chahiye, {name}!",
    },
    "success": {
        "action": "✅ {action} kar diya, {name}!",
        "search": "✅ Mil gaya! {result}",
        "calculation": "✅ Answer hai: {result}",
    },
    "error": {
        "not_found": "❌ {item} nahi mila",
        "api_error": "❌ API se kuch galti huyi",
        "general": "❌ Kuch galti huvi: {error}",
    }
}


def get_hinglish_response(template_key: str, **kwargs) -> str:
    """Get response from template"""
    keys = template_key.split('.')
    template = RESPONSE_TEMPLATES
    
    for key in keys:
        if key in template:
            template = template[key]
        else:
            return ""
    
    if isinstance(template, str):
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    
    return ""


# Singleton
hinglish = HinglishConverter()

if __name__ == "__main__":
    # Test conversions
    test_texts = [
        "Hello, how are you doing today?",
        "I found the answer for your question.",
        "Please wait a moment while I process this.",
    ]
    
    for text in test_texts:
        print(f"Original: {text}")
        print(f"Light:    {hinglish.convert(text, 'light')}")
        print(f"Medium:   {hinglish.convert(text, 'medium')}")
        print(f"Heavy:    {hinglish.convert(text, 'heavy')}")
        print()
