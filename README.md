# 🤖 Maya AI - Advanced Personal Desktop Assistant

## 🌟 Overview
Maya AI is a powerful, smart, efficient, self-learning, multilingual AI assistant for Windows PC with owner-mode architecture. She responds primarily in Hinglish (Hindi + English mixed) with a calm, helpful, loyal, and intelligent female personality.

## 🎯 Core Features
- **General Chat** - Natural conversation with personality
- **Coding Help** - Code generation and debugging
- **Weather Reports** - Real-time weather information
- **News Summaries** - Latest news in Hinglish
- **Search Engine Queries** - Web search integration
- **RAG Deep Research** - Advanced research with web content extraction
- **PC Full Control** - Complete Windows automation
- **Smart Automation** - Self-learning and suggestions
- **Engineering Mathematics** - Advanced calculations
- **Self Learning** - Habit prediction and adaptation
- **Memory System** - User preferences and history
- **Local AI Inference** - Efficient model routing
- **Voice Features** - Speech recognition and TTS

## 🏗️ Architecture

### Modular Design
```
maya_ai/
├── maya.py              # Main launcher
├── config.py            # Configuration management
├── web_app.py           # Web interface
├── requirements.txt     # Dependencies
├── .env                 # Environment variables
├── modules/
│   ├── brain.py         # Decision engine
│   ├── router.py        # Intent detection & routing
│   ├── memory.py        # User memory system
│   ├── calculator.py    # Engineering math engine
│   ├── models.py        # Local AI models
│   ├── tools.py         # APIs & utilities
│   ├── pc_control.py    # PC automation
│   ├── learner.py       # Self-learning system
│   ├── voice.py         # Speech I/O
│   ├── hinglish.py      # Hinglish converter
│   ├── scheduler.py     # Task scheduling
│   └── utils.py         # Helper functions
└── templates/
    └── index.html       # Web UI
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Windows 10/11
- Ollama (for local models)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd maya_brain/maya_ai
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Ollama models**
```bash
ollama pull llama3.2:3b
ollama pull qwen2.5-coder:3b
ollama pull moondream:latest
```

4. **Configure environment variables**
Create `.env` file:
```env
# API Keys
WEATHER_API_KEY=your_weather_api_key
SERP_API_KEY=your_serp_api_key
ZENSERP_API_KEY=your_zenserp_api_key
NEWS_API_KEY=your_news_api_key
HF_API_KEY=your_huggingface_key
WOLFRAM_API_ID=your_wolfram_id

# Model Paths
LLAMA_PATH=llama3.2:3b
QWEN_PATH=qwen2.5-coder:3b
BLACKBOX_PATH=blackbox
MOONDREAM_PATH=moondream:latest

# User Settings
OWNER_NAME=Bhai
WAKE_WORD=Hey Maya
VOICE_ID=female_1

# Feature Flags
DEBUG_MODE=False
AUTO_LEARN=True
HINGLISH_MODE=True
VOICE_MODE=False
GUI_MODE=False
OWNER_ONLY_MODE=True

# Performance
MAX_RESPONSE_TIME=30
CACHE_ENABLED=True
THREADING_ENABLED=True

# Security
ADMIN_PASSWORD=maya123
```

## 🎮 Usage

### Command Line Interface
```bash
# Interactive mode
python maya.py

# Single query
python maya.py "What is 25*89?"

# Voice mode
python maya.py --voice

# Show status
python maya.py --status
```

### Web Interface
```bash
# Start web server
python web_app.py

# Access at http://localhost:5000
```

## 🧠 Intelligent Routing System

Maya AI uses smart routing to minimize model usage:

### No Model Needed (Fastest)
- **Math**: "25 * 89", "sin90", "matrix determinant"
- **File Operations**: "open chrome", "create folder"
- **System**: "shutdown", "volume up", "screenshot"
- **Weather**: "weather in Delhi"
- **News**: "latest tech news"
- **Search**: "search best laptop under 50k"

### Coding Tasks
- **Qwen 2.5 3B**: "write python function", "debug this code"

### General Reasoning
- **Llama 3.2 3B**: "what is black hole?", "explain quantum physics"

### Hybrid Operations
- Multiple tools combined for complex tasks

## 🗣️ Hinglish Response Style

Maya AI responds in natural Hinglish:

```
User: "What's the weather today?"
Maya: "Bhai, aaj weather clean hai! Temperature 31°C hai, sunny mood mein hai 😊"

User: "Open chrome for me"
Maya: "Chrome open kar diya bhai! Ab browsing kar sakte ho ✅"

User: "Calculate 25 * 89"
Maya: "Arre, calculation kar diya! 25 * 89 = 2225 hai bhai!"
```

## 🎛️ PC Control Features

### Application Control
- `open chrome` - Launch Chrome
- `close firefox` - Close Firefox
- `open vs code` - Launch VS Code

### System Control
- `shutdown pc` - Shutdown computer
- `restart pc` - Restart computer
- `sleep mode` - Sleep mode
- `screenshot` - Take screenshot

### Volume & Display
- `volume up` - Increase volume
- `mute` - Mute audio
- `brightness up` - Increase brightness

### File Operations
- `create folder test` - Create folder
- `delete file test.txt` - Delete file
- `rename file old.txt new.txt` - Rename file

### Automation
- `type hello world` - Type text
- `mouse move 100 200` - Move mouse
- `click left` - Mouse click

## 🔧 Engineering Mathematics

Advanced mathematical capabilities:

### Basic Math
- Arithmetic: `25 * 89`, `45 + 67`
- Trigonometry: `sin90`, `cos45`, `tan30`
- Logarithms: `log100`, `ln10`

### Advanced Math
- Algebra: `solve x^2 - 5x + 6 = 0`
- Matrices: `determinant [[1,2],[3,4]]`
- Calculus: `integrate x^2`, `differentiate sin(x)`
- Complex Numbers: `complex 3+4i`

### Electrical Engineering
- Ohm's Law calculations
- Circuit analysis
- Power calculations

## 🛠️ Tools

- **Calculator** - Engineering mathematics (algebra, matrix, calculus, statistics)
- **PC Control** - Full PC control (open/close apps, volume, brightness, automation)
- **Memory** - User memory system (SQLite/JSON storage)
- **Router** - Intelligent model/tool routing
- **Tools** - API utilities and integrations
- **time_date** - Time and date queries with timezone support
- **OCR** - Text extraction from images
- **RAG** - Retrieval-Augmented Generation for document analysis
- **Search** - Web search integration

## 🧠 Self-Learning System

Maya AI learns from:

### User Habits
- Frequently used applications
- Daily routines and timings
- Preferred commands
- Language patterns

### Smart Suggestions
```
Maya: "Bhai, roz 9 baje chrome open karte ho. Kya main abhi chrome khol du?"
```

### Adaptation
- Intent prediction improves over time
- Personalized responses
- Habit-based automation

## 🗣️ Voice Features

### Wake Word
- Say "Hey Maya" to activate
- Always listening when enabled

### Speech Recognition
- Hinglish speech understanding
- Accurate command recognition

### Text-to-Speech
- Natural female voice
- Hinglish pronunciation
- Fast response

## 📊 APIs Integration

### Weather API
- Current conditions
- Temperature, humidity, wind
- Air quality index

### News API
- India news
- Tech news
- Finance news
- Sports news

### Search APIs
- SerpAPI integration
- Zenserp fallback
- Shopping searches
- People information

## 🔒 Security Features

### Owner Mode
- Only responds to owner
- Password protection
- Secure admin mode

### Privacy
- Local processing preferred
- Minimal data sharing
- User data encryption

## 📈 Performance Optimization

### Efficiency Rules
1. **Speed** - Fastest response first
2. **Accuracy** - Correct results
3. **Low Cost** - Minimal model usage
4. **Offline** - Work without internet
5. **Smart Routing** - Intelligent tool selection

### Caching System
- Response caching
- Model result caching
- Memory optimization

## 🛠️ Advanced Features

### Automation Engine
- Scheduled tasks
- Trigger-based actions
- Custom workflows

### Plugin System
- Easy model addition
- API extensions
- Custom tools

### Error Recovery
- Automatic retry
- Fallback mechanisms
- Graceful degradation

### Multi-threading
- Background tasks
- Parallel processing
- Non-blocking operations

## 📝 Configuration

### Environment Variables
All configuration via `.env` file:
- API keys and secrets
- Model paths
- Feature flags
- User preferences

### Debug Mode
Enable detailed logging:
```env
DEBUG_MODE=True
```

## 🚨 Troubleshooting

### Common Issues

**Model not responding**
```bash
# Check Ollama status
ollama list

# Restart Ollama
ollama serve
```

**API errors**
- Check API keys in `.env`
- Verify internet connection
- Check API rate limits

**Voice not working**
- Check microphone permissions
- Verify voice module installation
- Check audio drivers

### Logs
Check `logs/` directory for detailed logs.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is proprietary software for personal use.

## 🙏 Acknowledgments

- Ollama for local AI models
- OpenAI for model inspiration
- HuggingFace for AI tools
- Python community for libraries

---

## 🎯 Final Goal

Maya AI aims to be a production-level personal AI assistant that functions as an intelligent operating system brain for your PC, providing better functionality than common voice assistants while maintaining privacy and efficiency.

**Created with ❤️ for advanced personal computing**
