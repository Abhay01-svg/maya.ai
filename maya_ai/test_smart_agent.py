"""
Test script for Smart Agent Response System
Validates that the smart agent response features work correctly
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.smart_agent_response import smart_agent

def test_basic_response_generation():
    """Test basic smart response generation"""
    print("🧪 Test 1: Basic Response Generation")
    
    query = "What's the weather like?"
    intent = "weather"
    entities = {"city": "Delhi"}
    raw_response = "Currently in Delhi, it's 28°C with clear skies."
    
    result = smart_agent.generate_smart_response(
        query=query,
        intent=intent,
        entities=entities,
        raw_response=raw_response,
        conversation_history=[],
        user_preferences={}
    )
    
    print(f"✓ Query: {query}")
    print(f"✓ Intent: {intent}")
    print(f"✓ Acknowledgment: {result['acknowledgment']}")
    print(f"✓ Proactive suggestions: {result['proactive_suggestions']}")
    print(f"✓ Context aware: {result['context_aware']}")
    print()

def test_clarifying_questions():
    """Test clarifying question generation"""
    print("🧪 Test 2: Clarifying Questions")
    
    # Missing city for weather
    result = smart_agent.generate_smart_response(
        query="What's the weather?",
        intent="weather",
        entities={},  # Missing city
        raw_response="I need a city to check weather.",
        conversation_history=[],
        user_preferences={}
    )
    
    print(f"✓ Query: What's the weather?")
    print(f"✓ Clarifying question: {result['clarifying_question']}")
    print()

def test_proactive_suggestions():
    """Test proactive suggestion generation"""
    print("🧪 Test 3: Proactive Suggestions")
    
    result = smart_agent.generate_smart_response(
        query="Calculate 25 * 89",
        intent="calculation",
        entities={"expression": "25 * 89"},
        raw_response="2225",
        conversation_history=[],
        user_preferences={}
    )
    
    print(f"✓ Query: Calculate 25 * 89")
    print(f"✓ Suggestions: {result['proactive_suggestions']}")
    print()

def test_context_awareness():
    """Test context awareness from conversation history"""
    print("🧪 Test 4: Context Awareness")
    
    conversation_history = [
        {"query": "What's the weather in Delhi?", "response": "28°C clear skies"},
        {"query": "What about Mumbai?", "response": "32°C humid"}
    ]
    
    result = smart_agent.generate_smart_response(
        query="And Bangalore?",
        intent="weather",
        entities={"city": "Bangalore"},
        raw_response="27°C pleasant",
        conversation_history=conversation_history,
        user_preferences={}
    )
    
    print(f"✓ Conversation history: {len(conversation_history)} previous queries")
    print(f"✓ Context aware: {result['context_aware']}")
    print(f"✓ Acknowledgment: {result['acknowledgment']}")
    print()

def test_formatted_response():
    """Test final formatted response"""
    print("🧪 Test 5: Formatted Final Response")
    
    result = smart_agent.generate_smart_response(
        query="Search for Python tutorials",
        intent="search",
        entities={"query": "Python tutorials"},
        raw_response="Found 5 great Python tutorials for beginners.",
        conversation_history=[],
        user_preferences={}
    )
    
    formatted = smart_agent.format_final_response(result, "Found 5 great Python tutorials for beginners.")
    
    print(f"✓ Full formatted response:")
    print(formatted)
    print()

def test_multi_step_suggestions():
    """Test multi-step operation suggestions"""
    print("🧪 Test 6: Multi-step Suggestions")
    
    result = smart_agent.generate_smart_response(
        query="Open Chrome browser",
        intent="pc_control",
        entities={"action": "open", "app": "chrome"},
        raw_response="Chrome browser opened successfully.",
        conversation_history=[],
        user_preferences={}
    )
    
    print(f"✓ Multi-step hint: {result['multi_step_hint']}")
    print()

def main():
    """Run all tests"""
    print("=" * 60)
    print("🤖 Smart Agent Response System - Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_basic_response_generation()
        test_clarifying_questions()
        test_proactive_suggestions()
        test_context_awareness()
        test_formatted_response()
        test_multi_step_suggestions()
        
        print("=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
