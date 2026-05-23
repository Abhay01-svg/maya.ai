# Smart Agent Response System - Documentation

## Overview

The Smart Agent Response System enhances Maya's responses with intelligent, context-aware, agent-like behavior. This system makes Maya respond more like a sophisticated AI assistant rather than a simple command-response system.

## Features

### 1. Contextual Awareness
- **Time-based greetings**: Automatically adjusts greetings based on time of day (morning, afternoon, evening, night)
- **Conversation history**: Uses previous queries to provide contextually relevant responses
- **Entity recognition**: Leverages extracted entities for more personalized responses
- **User preferences**: Adapts responses based on user settings (e.g., formal mode)

### 2. Intelligent Acknowledgments
- **Intent-specific acknowledgments**: Different acknowledgment messages for each type of request
- **Context-aware transitions**: Smooth transitions when switching between topics
- **Personalization**: Adjusts tone based on user preferences and conversation flow

### 3. Proactive Suggestions
- **Intent-based suggestions**: Offers relevant follow-up actions based on the current intent
- **Context filtering**: Avoids repeating suggestions from recent queries
- **Smart recommendations**: Suggests multi-step operations and advanced features

### 4. Clarifying Questions
- **Ambiguity detection**: Identifies when essential information is missing
- **Intent-specific questions**: Asks relevant clarifying questions based on intent
- **Entity validation**: Checks for required entities before proceeding

### 5. Multi-Step Operations
- **Workflow suggestions**: Recommends automation and workflow creation
- **Task chaining**: Suggests related tasks that might be useful
- **Advanced features**: Promotes users to use more sophisticated capabilities

## Architecture

### Core Components

#### SmartAgentResponse Class
The main class that handles all smart agent response generation.

**Key Methods:**
- `generate_smart_response()`: Main method to generate enhanced responses
- `format_final_response()`: Formats the final response with all smart features
- `_generate_acknowledgment()`: Creates intelligent acknowledgments
- `_generate_proactive_suggestions()`: Generates relevant suggestions
- `_check_clarification_needed()`: Determines if clarification is required
- `_maintain_conversation_flow()`: Manages conversation continuity

#### ResponseContext Dataclass
Stores context information for response generation:
- `query`: User's original query
- `intent`: Detected intent
- `entities`: Extracted entities
- `conversation_history`: Previous conversation turns
- `user_preferences`: User's settings
- `time_of_day`: Current time period
- `previous_queries`: Recent query history

### Integration Points

#### brain.py Integration
The smart agent system is integrated into Maya's main brain module:
- Imported at module level
- Applied in `process_query()` method
- Enhances both successful responses and fallback responses
- Adds `smart_agent_features` to response metadata

#### decision_making.py Integration
The decision maker references the smart agent system:
- Legacy templates maintained as fallback
- Smart agent loaded when available
- Graceful degradation if smart agent unavailable

## Response Templates

The system uses sophisticated response templates for each intent:

```python
'calculation': {
    'acknowledgment': "I'll calculate that for you.",
    'working': "Processing the mathematical expression...",
    'completion': "Here's the result.",
    'follow_up': "Would you like me to explain the steps or try another calculation?"
}
```

Each intent has templates for:
- **acknowledgment**: Initial response to user request
- **working**: Message during processing (optional)
- **completion**: Confirmation of task completion
- **follow_up**: Suggested next actions

## Proactive Suggestions

Suggestions are generated based on intent and context:

**Weather Intent:**
- Check the forecast for the week?
- Get weather alerts?
- Compare weather between cities?

**Coding Intent:**
- Need code review?
- Want debugging help?
- Need documentation?

**PC Control Intent:**
- Automate this task?
- Create a shortcut?
- Schedule this action?

## Clarifying Questions

When essential information is missing, the system asks clarifying questions:

**Weather without city:**
- "Which city would you like the weather for?"

**News without topic:**
- "What topic are you interested in?"

**Coding without language:**
- "What programming language do you prefer?"

## Usage Example

```python
from modules.smart_agent_response import smart_agent

# Generate smart response
result = smart_agent.generate_smart_response(
    query="What's the weather like?",
    intent="weather",
    entities={"city": "Delhi"},
    raw_response="Currently in Delhi, it's 28°C with clear skies.",
    conversation_history=[],
    user_preferences={}
)

# Format final response
final_response = smart_agent.format_final_response(
    result, 
    "Currently in Delhi, it's 28°C with clear skies."
)
```

## Testing

Run the test suite to validate the smart agent features:

```bash
cd maya_ai
python test_smart_agent.py
```

The test suite validates:
- Basic response generation
- Clarifying questions
- Proactive suggestions
- Context awareness
- Formatted responses
- Multi-step suggestions

## Benefits

1. **More Natural Conversations**: Responses feel more like talking to an intelligent assistant
2. **Better User Experience**: Proactive suggestions help users discover features
3. **Reduced Friction**: Clarifying questions prevent errors from ambiguous queries
4. **Context Awareness**: Responses consider conversation history and user preferences
5. **Professional Tone**: More sophisticated and agent-like than simple responses

## Configuration

### Agentic Mode Setting

The smart agent system can be toggled via the `AGENTIC_MODE` environment variable:

**In .env file:**
```bash
AGENTIC_MODE=True  # Enable smart agent responses
AGENTIC_MODE=False # Disable smart agent responses (use direct responses)
```

**Default:** `True` (enabled)

When `AGENTIC_MODE` is disabled, Maya will use direct responses without:
- Intelligent acknowledgments
- Proactive suggestions
- Clarifying questions
- Multi-step hints
- Context-aware formatting

### User Preferences

The system also respects user preferences:
- **formal_mode**: Uses more formal language ("I shall" instead of "I'll")
- **conversation_history_length**: Controls how much context is used
- **suggestion_limit**: Limits number of proactive suggestions

### Checking Current Mode

To check if agentic mode is enabled:
```bash
maya settings
```

This will show the current status of all settings including agentic mode.

## Future Enhancements

Potential improvements:
- Learning from user feedback on suggestions
- Personalized suggestion ranking
- Advanced conversation state management
- Multi-language support for acknowledgments
- Integration with more Maya modules

## Troubleshooting

**Smart agent not loading:**
- Check that `smart_agent_response.py` exists in modules directory
- Verify import statement in brain.py
- Check logs for import errors

**Suggestions not appearing:**
- Verify intent is in proactive_suggestions dictionary
- Check if suggestions are being filtered by conversation history
- Ensure entities are properly extracted

**Clarifying questions not triggering:**
- Verify intent is in clarification_patterns
- Check that required entities are truly missing
- Review entity extraction in decision_making.py

## Performance Impact

The smart agent system adds minimal overhead:
- Response generation: ~5-10ms additional processing
- Memory: Small footprint for conversation state
- No impact on tool execution or model inference

**When AGENTIC_MODE is disabled:** Zero overhead (system behaves as before)

## License

Part of Maya AI - Intelligent Personal Assistant
