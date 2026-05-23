import sys
import os
import re

# Add maya_ai to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../maya_ai')))

from modules.brain import brain
from modules.decision_making import DecisionMaker
from modules.calculator import calculator

def test_intent_detection():
    print("\n--- Testing Intent Detection ---")
    dm = DecisionMaker()
    queries = [
        "weather of Agartala Tripura",
        "sin 30",
        "2 + 2",
        "research about space",
        "open notepad",
        "hello maya"
    ]
    for q in queries:
        decision = dm.decide_module("unknown", q)
        print(f"Query: '{q}' -> Intent: {decision['intent']}, Tool: {decision['primary_module']}")
        if decision.get('entities'):
            print(f"   Entities: {decision['entities']}")

def test_math():
    print("\n--- Testing Math Calculation ---")
    queries = [
        "sin 30",
        "2 + 2",
        "sqrt 16",
        "log 100"
    ]
    for q in queries:
        result = calculator.parse_and_calculate(q)
        print(f"Query: '{q}' -> Result: {result['result']}, Hinglish: {result['hinglish']}")

def test_brain_verification():
    print("\n--- Testing Brain Verification (Llama) ---")
    # This will actually call Llama if available
    query = "sin 30"
    print(f"Processing query: {query}")
    response = brain.process_query(query)
    print(f"Hinglish Response: {response['hinglish_response']}")
    print(f"Model used: {response['model_used']}")

def test_creator():
    print("\n--- Testing Creator Info ---")
    queries = [
        "who developed you",
        "who is your creator",
        "tell me about your developer"
    ]
    for q in queries:
        response = brain.process_query(q)
        print(f"Query: '{q}' -> Response: {response['hinglish_response']}")

def test_location():
    print("\n--- Testing Location Detection ---")
    queries = [
        "what is the weather here",
        "current weather"
    ]
    for q in queries:
        response = brain.process_query(q)
        # Check if the response contains a city (IP detection)
        print(f"Query: '{q}' -> Response: {response['hinglish_response'][:100]}...")

def test_system_context():
    print("\n--- Testing System Context (Device/Location) ---")
    queries = [
        "what is my battery level",
        "how much ram am i using",
        "search for coffee shops near me",
        "what is the weather right now"
    ]
    for q in queries:
        response = brain.process_query(q)
        print(f"Query: '{q}' -> Response: {response['hinglish_response']}")

def test_tone():
    print("\n--- Testing Tone (Sir/Boss) ---")
    queries = [
        "hello maya",
        "how are you",
        "what is my name"
    ]
    for q in queries:
        response = brain.process_query(q)
        print(f"Query: '{q}' -> Response: {response['hinglish_response']}")

def test_language_flexibility():
    print("\n--- Testing Language Flexibility ---")
    queries = [
        "What is the capital of France?",
        "Bharat ki rajdhani kya hai?",
        "Tell me a joke in Hinglish"
    ]
    for q in queries:
        response = brain.process_query(q)
        print(f"Query: '{q}' -> Response: {response['hinglish_response']}")

def test_identity_and_gender():
    print("\n--- Testing Identity and Gender Consistency ---")
    queries = [
        "what is your name",
        "who are you",
        "hello",
        "how are you"
    ]
    for q in queries:
        # Clear cache for fresh results
        from modules.models import model_cache
        model_cache.clear()
        
        response = brain.process_query(q)
        print(f"Query: '{q}' -> Response: {response['hinglish_response']}")
        print(f"   Intent: {response['intent']}, Tool: {response['tool_used']}")

def test_synthesis():
    print("\n--- Testing Multi-Source Synthesis ---")
    # Clear cache
    from modules.models import model_cache
    model_cache.clear()
    
    queries = [
        "Tell me about the latest AI news and the weather in Delhi",
        "Who is the current Prime Minister of India?"
    ]
    for q in queries:
        response = brain.process_query(q)
        print(f"Query: '{q}' -> Response: {response['hinglish_response'][:200]}...")
        print(f"   Model: {response['model_used']}")

def test_intelligence():
    print("\n--- Testing Intelligence (Context & Self-Thinking) ---")
    # Clear cache
    from modules.models import model_cache
    model_cache.clear()
    
    # Sequence of related queries
    queries = [
        "Cristiano Ronaldo",
        "MS Dhoni"
    ]
    for q in queries:
        response = brain.process_query(q)
        print(f"Query: '{q}'")
        print(f"   Thought: {response.get('thought')}")
        print(f"   Response: {response['hinglish_response'][:300]}...")
        print(f"   Model: {response['model_used']}")

def test_wolfram():
    print("\n--- Testing Wolfram Alpha Integration ---")
    queries = [
        "What is the distance to the moon?",
        "What is the molecular weight of water?",
        "Solve equation x^2 + 5x + 6 = 0"
    ]
    for q in queries:
        response = brain.process_query(q)
        print(f"Query: '{q}' -> Response: {response['hinglish_response'][:200]}...")
        print(f"   Intent: {response['intent']}, Tool: {response['tool_used']}")

def test_xai():
    print("\n--- Testing XAI (Explainable AI) & Reasoning Trace ---")
    queries = [
        "What is the weather in Delhi and tell me about its history",
        "Explain this code: def hello(): print('hi')"
    ]
    for q in queries:
        response = brain.process_query(q)
        print(f"Query: '{q}'")
        if response.get('xai_report'):
            report = response['xai_report']
            print(f"   Intent: {report['intent']} (Logic: {report['logic_type']})")
            print(f"   Attention: {report['attention_map']}")
            print("   Decision Path:")
            for step in report['decision_path']:
                print(f"     - {step['step_name']}: {step['reasoning']}")
        print(f"   Final Response: {response['hinglish_response'][:100]}...")

if __name__ == "__main__":
    test_identity_and_gender()
    test_intent_detection()
    test_math()
    test_creator()
    test_location()
    test_system_context()
    test_tone()
    test_language_flexibility()
    test_synthesis()
    test_intelligence()
    test_wolfram()
    test_xai()
