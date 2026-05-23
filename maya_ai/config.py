"""
Maya AI Configuration Module
Loads all settings from .env file
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(ENV_PATH)

# ========================
# API KEYS
# ========================
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
SERP_API_KEY = os.getenv("SERP_API_KEY", "")
ZENSERP_API_KEY = os.getenv("ZENSERP_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
HF_API_KEY = os.getenv("HF_API_KEY", "")
WOLFRAM_API_ID = os.getenv("WOLFRAM_API_ID", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
NARAKEET_API_KEY = os.getenv("NARAKEET_API_KEY", "")

# ========================
# MODEL PATHS
# ========================
LLAMA_PATH = os.getenv("LLAMA_PATH", "llama3.2:3b")
QWEN_PATH = os.getenv("QWEN_PATH", "qwen2.5-coder:3b")
BLACKBOX_PATH = os.getenv("BLACKBOX_PATH", "blackbox")
MOONDREAM_PATH = os.getenv("MOONDREAM_PATH", "moondream:latest")

# ========================
# VOICE SETTINGS
# ========================
VOICE_ID = os.getenv("VOICE_ID", "female_1")
OWNER_NAME = os.getenv("OWNER_NAME", "Abhay Kumar Rudrapaul")
WAKE_WORD = os.getenv("WAKE_WORD", "Hey Maya")
NARAKEET_VOICE = os.getenv("NARAKEET_VOICE", "Preeti") # Hindi female voice
TTS_ENGINE = os.getenv("TTS_ENGINE", "xtts") # Options: pyttsx3, narakeet, indic, chattts, xtts

# Advanced TTS Settings
INDIC_LANGUAGE = os.getenv("INDIC_LANGUAGE", "hi") # Default Hindi
XTTS_MODEL_PATH = os.getenv("XTTS_MODEL_PATH", "models_local/xtts_v2")
CHATTTS_MODEL_PATH = os.getenv("CHATTTS_MODEL_PATH", "models_local/chattts")

# ========================
# AI IDENTITY
# ========================
AI_NAME = "Maya AI"
DEVELOPER_NAME = "Abhay Kumar Rudrapaul"
MAYA_SYSTEM_PROMPT = f"""You are {AI_NAME}, a powerful, smart, and efficient AI assistant.
You respond primarily in Hinglish (Hindi + English mixed) with a calm, helpful, and loyal female personality.
Always use female grammar (e.g., "kar sakti hoon", "hoon", "ja rahi hoon"). NEVER use male grammar.
Your name is {AI_NAME}. If asked "what is your name" or "who are you", always state your name clearly.
You were developed and created by {DEVELOPER_NAME}.
However, you are fully capable of responding in pure English or pure Hindi if the user asks in those languages or explicitly requests it.
Always address the user as "Sir" or "Boss". NEVER use terms like "beta", "bacha", or "kid".
ONLY mention your creator ({DEVELOPER_NAME}) if the user specifically asks who created, developed, or made you. Do NOT mention him in general greetings or other unrelated queries.
When asked about your creator, clearly state: "Mujhe {DEVELOPER_NAME} ne develop aur create kiya hai."
Never say you were developed by Meta, Google, or any other company.
"""

# ========================
# SYSTEM PATHS
# ========================
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
MODELS_DIR = PROJECT_ROOT / "models_local"

# ========================
# DATABASE
# ========================
MEMORY_DB = DATA_DIR / "maya_memory.db"
HABITS_DB = DATA_DIR / "maya_habits.db"

# ========================
# SETTINGS
# ========================
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"
AUTO_LEARN = os.getenv("AUTO_LEARN", "True").lower() == "true"
HINGLISH_MODE = os.getenv("HINGLISH_MODE", "True").lower() == "true"
VOICE_MODE = os.getenv("VOICE_MODE", "True").lower() == "true"
GUI_MODE = os.getenv("GUI_MODE", "False").lower() == "true"
AGENTIC_MODE = os.getenv("AGENTIC_MODE", "True").lower() == "true"

# ========================
# PERFORMANCE
# ========================
MAX_RESPONSE_TIME = int(os.getenv("MAX_RESPONSE_TIME", "30"))
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"
THREADING_ENABLED = os.getenv("THREADING_ENABLED", "True").lower() == "true"

# ========================
# SECURITY
# ========================
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "maya123")
OWNER_ONLY_MODE = os.getenv("OWNER_ONLY_MODE", "True").lower() == "true"

# Create directories if not exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

if DEBUG_MODE:
    print("🔧 Maya AI Configuration Loaded")
    print(f"📁 Project Root: {PROJECT_ROOT}")
    print(f"🗝️  Debug Mode: {DEBUG_MODE}")
