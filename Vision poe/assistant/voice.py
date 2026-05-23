import threading
import time
import speech_recognition as sr
import pyttsx3

_engine = None

def _init_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        # optional voice selection can be added here

def speak(text: str):
    _init_engine()
    try:
        _engine.say(text)
        _engine.runAndWait()
    except Exception:
        pass

def listen(timeout: int = 5, phrase_time_limit: int = 8):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            return r.recognize_google(audio)
        except sr.WaitTimeoutError:
            return ""
        except Exception:
            return ""
