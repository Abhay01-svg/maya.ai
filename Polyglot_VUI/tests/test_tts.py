import sys
import os
import time

# Add maya_ai to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../maya_ai')))

from modules.voice import GoogleIndianTTS

def test_google_indian_tts():
    print("\n--- Testing Google Indian TTS (Soft & Clear) ---")
    speaker = GoogleIndianTTS()
    
    test_texts = [
        "Hello Sir, I am Maya. How can I help you today?",
        "Namaste Boss, main aapki kya madad kar sakti hoon?",
        "Shillong mein aaj ka mausam bahut suhana hai, Sir."
    ]
    
    for text in test_texts:
        print(f"Speaking: {text}")
        speaker.speak(text)
        time.sleep(1)

if __name__ == "__main__":
    test_google_indian_tts()
