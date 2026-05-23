"""
Maya AI Modules Package
Core modules for the intelligent desktop assistant
"""

# Import main modules
try:
    from modules.brain import brain, MayaBrain
    from modules.router import router, Router
    from modules.calculator import calculator, MayaCalculator
    from modules.tools import weather_api, news_api, search_api
    from modules.pc_control import pc_control, PCControl
    from modules.memory import memory, MayaMemory
    from modules.models import local_models, model_cache
    from modules.voice import voice_interface, VoiceInterface
    from modules.hinglish import hinglish, HinglishConverter
    
    __all__ = [
        # Brain and routing
        'brain', 'MayaBrain',
        'router', 'Router',
        
        # Core tools
        'calculator', 'MayaCalculator',
        'weather_api', 'news_api', 'search_api',
        'pc_control', 'PCControl',
        
        # Memory
        'memory', 'MayaMemory',
        
        # AI models
        'local_models', 'model_cache',
        
        # Voice
        'voice_interface', 'VoiceInterface',
        
        # Hinglish
        'hinglish', 'HinglishConverter'
    ]

except ImportError as e:
    print(f"⚠️  Warning importing Maya modules: {e}")
    __all__ = []

