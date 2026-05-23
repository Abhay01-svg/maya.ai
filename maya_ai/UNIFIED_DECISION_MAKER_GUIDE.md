# 🧠 MAYA AI - Unified Decision Maker Guide

## Overview

The **Unified Decision Maker** is the intelligent brain of MAYA AI that analyzes user requests, classifies them accurately, and routes them to the best-suited model, API, or tool for handling.

It replaces both `decision_making.py` and `decision_making_brain.py` with a single, cohesive system that combines:
- **NLP-based classification** using spaCy
- **Dynamic capability mapping** from README.md
- **Comprehensive intent detection** with proper priorities
- **Intelligent fallback chains** and multi-step workflows

---

## How It Works

### Step 1: Analyze User Input
When a user sends a message, the system analyzes it to understand:
- **What does the user want?** (intent classification)
- **Is it a question, command, task, or casual chat?**
- **Does it need latest/live information?**
- **Is it old/general knowledge?**

### Step 2: Classify the Request
The decision maker classifies requests into categories:

| Intent | Keywords | Example |
|--------|----------|---------|
| **Calculation** | calculate, compute, solve, +, -, *, / | "What's 15 * 23?" |
| **Weather** | weather, temperature, forecast, rain | "What's the weather today?" |
| **News** | news, headlines, breaking, latest | "Latest AI news" |
| **Time/Date** | time, date, timezone, convert | "What time is it?" |
| **Coding** | code, program, debug, write script | "Write a Python function" |
| **Search** | search, find, information, look for | "Find info about X" |
| **Vision** | screenshot, image, analyze screen | "What's on my screen?" |
| **Document** | PDF, document, read file, summarize | "Summarize this PDF" |
| **Memory** | remember, save, note this | "Remember to call mom" |
| **PC Control** | open, close, shutdown, launch | "Open Chrome browser" |
| **Greeting** | hello, hi, hey, good morning | "Hello! How are you?" |

### Step 3: Detect Live vs Historical Info
The system checks if the request needs **current/live information**:

```
Live Information Keywords:
- latest, today, current, now, recent
- live, updated, this week, breaking

Examples:
✅ "What's the weather TODAY?" → Uses Weather API (live)
✅ "Latest AI news" → Uses News API (live)
✅ "Bitcoin price NOW" → Uses Search API (live)
❌ "Who is Nikola Tesla?" → Uses internal knowledge (historical)
❌ "Explain gravity" → Uses internal knowledge (historical)
```

### Step 4: Route to Best Module
Based on intent and available capabilities, route to:

| Module | Purpose | Speed |
|--------|---------|-------|
| `calculator` | Math expressions | ⚡ 0.1s |
| `weather_api` | Weather information | 🔄 1.0s |
| `news_api` | News & headlines | 🔄 2.0s |
| `search_api` | Web search | 🔄 1.5s |
| `time_date_module` | Time & date queries | ⚡ 0.1s |
| `pc_control` | System automation | ⚡ 0.5s |
| `memory` | Save/recall info | ⚡ 0.2s |
| `coding` | Programming tasks | 🚀 3.0s |
| `vision` | Image analysis | 🚀 2.0s |
| `document` | PDF/document analysis | 🚀 2.5s |
| `general_chat` | Conversation | 🚀 2.5s |

---

## Usage Examples

### Basic Usage (New API)

```python
from modules.unified_decision_maker import unified_decision_maker

# Analyze a user message
decision = unified_decision_maker.decide("What's 15 * 23?")

print(decision['intent'])           # 'calculation'
print(decision['primary_module'])   # 'calculator'
print(decision['confidence'])       # 0.95
print(decision['requires_live_info']) # False

# Get execution time estimate
time_estimate = unified_decision_maker.estimate_response_time('calculator')
print(f"Estimated: {time_estimate}s")
```

### Backward Compatible API (Old Code Still Works!)

```python
# Old code continues to work without changes
from modules.unified_decision_maker import unified_decision_maker as decision_maker

# Works with old API
decision = decision_maker.decide_module("", "What's the weather today?")

print(decision['primary_module'])     # 'weather_api'
print(decision['start_ollama'])       # False
print(decision['confidence'])         # 0.95
```

### Complete Workflow

```python
from modules.unified_decision_maker import unified_decision_maker

def handle_user_request(user_message: str):
    # Step 1: Analyze and decide
    decision = unified_decision_maker.decide(user_message)
    
    print(f"🎯 Intent: {decision['intent']}")
    print(f"📊 Confidence: {decision['confidence']:.0%}")
    print(f"🔧 Primary Module: {decision['primary_module']}")
    print(f"⏱️ Est. Time: {unified_decision_maker.estimate_response_time(decision['primary_module']):.1f}s")
    
    # Step 2: Execute the decision
    result = unified_decision_maker.execute_decision(decision, user_message)
    
    if result:
        print(f"✅ Response: {result['response']}")
        print(f"🔌 Module Used: {result['module_used']}")
    else:
        print("❌ No module could handle this request")
    
    return result

# Test it
result = handle_user_request("Write a Python function for binary search")
```

---

## Decision Structure

The `decide()` method returns a comprehensive decision object:

```python
{
    'intent': 'coding',                    # Detected intent type
    'confidence': 0.95,                    # Confidence score (0-1)
    'reasoning': 'Programming query...',   # Why this decision was made
    'requires_live_info': False,           # Needs current information?
    'classification_method': 'NLP',        # 'NLP' or 'Rule-based'
    
    # Primary routing
    'primary_module': 'coding',            # Main module to use
    'fallback_modules': ['llama_general'], # Backup options
    'requires_model': True,                # Needs ML model?
    'model_type': 'qwen_coder',           # Which model
    
    # Workflow
    'chain': ['code_generation', 'syntax_check']  # Multi-step execution
}
```

---

## Smart Routing Examples

### Example 1: Mathematical Expression
```
Input: "What's 15 * 23?"
Classification: calculation
Route: calculator (0.95 confidence)
Speed: 0.1s
No Ollama needed
```

### Example 2: Latest News
```
Input: "Latest AI news"
Classification: news (has "latest" keyword)
Requires Live Info: YES
Route: news_api (0.95 confidence)
Speed: 2.0s
```

### Example 3: Programming Task
```
Input: "Write a Python function to check palindrome"
Classification: coding
Requires Model: YES (Qwen Coder)
Route: coding module with Qwen Coder
Speed: 3.0s
Chain: [code_generation, syntax_check]
```

### Example 4: General Knowledge
```
Input: "Who is Nikola Tesla?"
Classification: general_chat
Requires Live Info: NO (general knowledge)
Requires Model: YES (Llama 3.2)
Route: general_chat with Llama
Speed: 2.5s
```

---

## Live vs Historical Information Detection

```python
# Check if a request needs live information
message1 = "What's the weather TODAY?"
message2 = "What is gravity?"

has_live1 = unified_decision_maker._has_live_info_keywords(message1)  # True
has_live2 = unified_decision_maker._has_live_info_keywords(message2)  # False
```

Live keywords trigger:
- **Web Search API** for quick results
- **News API** for current events
- **Weather API** for current conditions

---

## Fallback Chains

If primary module fails, system automatically tries fallback modules:

```python
decision = unified_decision_maker.decide("Calculate 2+2")

# Try in order:
# 1. calculator (primary)
# 2. llama_general (fallback 1)
# 3. qwen_coder (fallback 2)

result = unified_decision_maker.execute_decision(decision, "Calculate 2+2")
```

---

## API Reference

### Main Methods

#### `decide(message: str) -> Dict`
Main decision-making function. Analyzes input and returns routing decision.

```python
decision = unified_decision_maker.decide("What's the weather today?")
```

#### `execute_decision(decision: Dict, message: str) -> Optional[Dict]`
Executes the decision - runs primary module, falls back if needed.

```python
result = unified_decision_maker.execute_decision(decision, message)
```

#### `estimate_response_time(module: str) -> float`
Get estimated response time in seconds.

```python
time = unified_decision_maker.estimate_response_time('calculator')  # 0.1s
```

### Backward Compatibility Methods

#### `decide_module(context: str, message: str) -> Dict`
Old API wrapper for compatibility with existing code.

```python
# Old code continues to work
decision = decision_maker.decide_module("", "What's 25*4?")
```

#### `validate_output(response: str, intent: str) -> Tuple[bool, str]`
Validate response quality.

```python
is_valid, msg = unified_decision_maker.validate_output(response, 'coding')
```

#### `get_fallback_response(modules: List[str], message: str) -> Optional[Dict]`
Get response from fallback modules.

```python
result = unified_decision_maker.get_fallback_response(['llama_general'], message)
```

---

## Advanced Features

### 1. Dynamic Capability Reading
The system automatically reads `README.md` to discover available:
- Models (Llama, Qwen, Moondream, etc.)
- Tools (Calculator, Memory, PC Control, etc.)
- APIs (Weather, News, Search, etc.)
- Features (Voice, Code Generation, RAG, etc.)

```python
# Capabilities are loaded automatically
print(unified_decision_maker.capability_map['models'])
print(unified_decision_maker.capability_map['tools'])
print(unified_decision_maker.capability_map['apis'])
```

### 2. Auto-Refresh
Every 60 seconds, the system checks if README.md changed and updates capabilities.

### 3. Ollama Management
Built-in Ollama service management:

```python
unified_decision_maker.ollama.is_ollama_running()
unified_decision_maker.ollama.start_ollama()
unified_decision_maker.ollama.stop_ollama()
```

### 4. Performance Tracking
Track module performance (populated during execution):

```python
print(unified_decision_maker.module_performance)
```

---

## Testing

Run the included test suite:

```bash
python -m maya_ai.test_decision_brain
python -m maya_ai.test_all_systems
python -m maya_ai.test_all_models
```

Or test directly:

```python
from modules.unified_decision_maker import analyze_user_input, execute_request

# Test analysis
decision = analyze_user_input("Write a REST API in Python")
print(f"Intent: {decision['intent']}")

# Test complete execution
result = execute_request("What's 2 + 2?")
print(f"Result: {result['response']}")
```

---

## Migration from Old System

### What Changed?

| Old | New |
|-----|-----|
| `decision_making.py` | `unified_decision_maker.py` |
| `decision_making_brain.py` | `unified_decision_maker.py` |
| Two separate classes | One unified class |
| Manual merging needed | Automatic fallback chains |

### What Stayed the Same?

✅ All imports work (backward compatible)
✅ Old API still works
✅ All existing code continues without changes
✅ Same module routing logic
✅ Ollama management

### Updated Imports

```python
# Old (still works)
from modules.unified_decision_maker import unified_decision_maker as decision_maker

# New preferred style
from modules.unified_decision_maker import unified_decision_maker

# Helper functions
from modules.unified_decision_maker import analyze_user_input, execute_request
```

---

## Performance Benchmarks

| Task | Speed | Module |
|------|-------|--------|
| 15 * 23 | ⚡ 0.1s | calculator |
| What time is it? | ⚡ 0.1s | time_date_module |
| Write code | 🚀 3.0s | coding (Qwen) |
| Weather today? | 🔄 1.0s | weather_api |
| Latest news | 🔄 2.0s | news_api |
| General chat | 🚀 2.5s | llama_general |

---

## Troubleshooting

### Issue: "spaCy model not found"
```
❌ Failed to load spaCy model
→ Falls back to rule-based classification (slower but functional)
→ Install with: python -m spacy download en_core_web_sm
```

### Issue: "README.md not found"
```
❌ README.md not found
→ Uses default capabilities
→ Ensure README.md exists in maya_ai/ directory
```

### Issue: "Module not found"
```
❌ Failed to execute module X
→ System tries fallback modules automatically
→ Check if required module is installed
```

---

## Key Principles

The Unified Decision Maker follows these principles:

1. **🎯 Accurate Classification**: Uses NLP when available, rule-based fallback
2. **⚡ Speed**: Routes to fastest module for the task
3. **🔄 Fallback Chains**: Automatic recovery if primary module fails
4. **📚 Dynamic**: Reads capabilities from README.md
5. **🔧 Compatible**: All old code continues to work
6. **🧠 Intelligent**: Understands live vs historical info needs
7. **📊 Traceable**: Logs all decisions and reasoning

---

## Contributing

To improve the decision maker:

1. **Add new intent**: Add keywords to `intent_keywords` dict
2. **Add new module**: Update `capability_map` and `_execute_module()`
3. **Improve routing**: Enhance `_route_to_module()` logic
4. **Add keywords**: Expand intent detection patterns

---

## Summary

The **Unified Decision Maker** is MAYA's intelligent brain that:

✅ Analyzes what users really want
✅ Detects if they need live or historical information  
✅ Chooses the best model, API, or tool
✅ Handles fallbacks and multi-step workflows
✅ Maintains backward compatibility
✅ Works with or without NLP
✅ Auto-discovers capabilities from README.md

**Result**: Intelligent, fast, and accurate request routing! 🚀
