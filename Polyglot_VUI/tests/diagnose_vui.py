import sys
import os
import logging
from pathlib import Path

# Add maya_ai to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../maya_ai')))

from modules.brain import brain
from modules.groq_api import GroqAPI
from modules.rag_search import WebRAGEngine
from config import GROQ_API_KEY, DEBUG_MODE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_groq():
    print("\n--- Testing Groq API ---")
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not found in .env")
        return
    
    groq = GroqAPI(GROQ_API_KEY)
    if groq.is_ready():
        print("✅ Groq API is ready")
        response = groq.infer("Hello, who are you?")
        print(f"Groq Response: {response[:100]}...")
    else:
        print("❌ Groq API is not ready. Check if 'groq' library is installed and key is valid.")

def test_rag():
    print("\n--- Testing RAG Engine ---")
    rag = WebRAGEngine()
    query = "Who is the current President of India?"
    print(f"Query: {query}")
    result = rag.deep_search(query)
    if result.get('success'):
        print(f"✅ RAG Success! Response: {result.get('response')[:200]}...")
    else:
        print(f"❌ RAG Failed: {result.get('error')}")

def test_brain_rag():
    print("\n--- Testing Brain with RAG intent ---")
    # Manually trigger RAG via brain if possible, or see if brain routes it
    query = "Research about the latest SpaceX launch"
    print(f"Query: {query}")
    response = brain.process_query(query)
    print(f"Intent detected: {response.get('intent')}")
    print(f"Response: {response.get('hinglish_response')[:200]}...")

def test_automation():
    print("\n--- Testing Automation (PC Control) ---")
    from modules.pc_control import pc_control
    print("Testing 'list_running_apps'...")
    apps = pc_control.list_running_apps(limit=5)
    if apps:
        print(f"✅ Found {len(apps)} running apps:")
        for app in apps:
            print(f"   - {app['name']} (PID: {app['pid']})")
    else:
        print("❌ Could not list running apps")

if __name__ == "__main__":
    test_groq()
    test_rag()
    test_brain_rag()
    test_automation()
