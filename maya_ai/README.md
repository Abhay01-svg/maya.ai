# MAYA AI - Intelligent Personal Assistant

## 🧠 Available Models

### Local Models
- **Llama 3.2 3B** - General reasoning and chat
- **Qwen Coder** - Programming and code generation
- **Moondream** - Vision/image analysis
- **Qwen2.5** - Enhanced conversational AI

### CLI Tools
- **Blackbox CLI** - Code generation via command line

## 🛠️ Available Tools

### Core Modules
- **calculator.py** - Engineering mathematics (algebra, matrix, calculus, statistics)
- **pc_control.py** - Full PC control (open/close apps, volume, brightness, automation)
- **memory.py** - User memory system (SQLite/JSON storage)
- **router.py** - Intelligent model/tool routing
- **tools.py** - API utilities and integrations

### Specialized Tools
- **OCR** - Text extraction from images
- **RAG** - Retrieval-Augmented Generation for document analysis
- **search.py** - Web search integration

## 🔌 Installed APIs

### Search APIs
- **SERP API** - Web search results
- **Zenserp API** - Alternative search engine
- **DuckDuckGo** - Privacy-focused search

### Information APIs
- **Weather API** - Current weather and forecasts
- **News API** - Latest news headlines and articles

## ✨ Supported Features

### File Processing
- **PDF Reading** - PDF document parsing and analysis
- **Document Analysis** - OCR + RAG for document understanding
- **Image Analysis** - Screenshot and image processing via vision models
- **File Operations** - Create, delete, rename, search files

### Voice Features
- **Voice Input** - Speech recognition (wake word: "Hey Maya")
- **Voice Output** - Text-to-speech with female voice
- **Hinglish Support** - Hindi + English mixed naturally

### Coding Features
- **Code Generation** - Professional code in multiple languages
- **Debugging** - Error analysis and fixes
- **Code UI** - Professional copyable code blocks with syntax highlighting

### Memory Features
- **User Memory** - Remember name, preferences, habits
- **Chat History** - Past conversation storage
- **Custom Commands** - User-defined shortcuts
- **Routine Learning** - Habit prediction and automation

### Automation
- **Smart Automation** - XGBoost-based intent prediction
- **Task Scheduling** - Background task execution
- **Multi-threading** - Parallel processing for speed

## 🎯 Decision Rules

### General Chat
- Use best conversational model (Llama 3.2 or Qwen2.5)

### Coding/Programming
- Use Qwen Coder for code generation
- Return in professional code UI format

### Live Data (News, Weather, Search)
- Use installed APIs (SERP, Zenserp, Weather API, DuckDuckGo)

### Image/Screenshot Analysis
- Use Moondream or best available vision model

### PDF/Documents/Files
- Use OCR + parser + RAG if available

### Calculations/Math
- Use calculator.py or sympy/numpy/scipy

### Memory Requests
- Use memory.py for storage (keywords: remember, save, yad rakhna)

### PC Control/Automation
- Use pc_control.py or automation scripts

### Research/Deep Search
- Use DuckDuckGo/search APIs + RAG summarization

## 🔄 Multi-Step Intelligence

### Example Chaining
- **Read PDF and make code** → PDF Reader + RAG + Coding Model
- **Analyze screenshot and search solution** → Vision + Search + Reasoning Model
- **Calculate and explain** → Calculator + Chat Model

## 📊 Speed & Quality Rules

- **Simple tasks** = Fastest route (no heavy models)
- **Complex tasks** = Smartest route (appropriate model)
- **Live data** = Search tools
- **Coding** = Coding model
- **Vision** = Image model
- **Memory** = Save intelligently

## 🔐 Security

- **Owner Mode** = Password protected admin access
- **Auto Refresh** = Re-read README.md on changes
- **Dynamic Adaptation** = Automatically detect new/removed models

## 📝 Version

Current Version: 2.0
Last Updated: April 25, 2026
