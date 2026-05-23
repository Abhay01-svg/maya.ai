import importlib
import pkgutil
import assistant.config as config
from assistant import llm


class Assistant:
    def __init__(self):
        self.plugins = {}
        self.load_plugins()

    def load_plugins(self):
        # Load built-in plugins from assistant.plugins package
        try:
            import assistant.plugins as plugins_pkg
        except Exception:
            return

        for finder, name, ispkg in pkgutil.iter_modules(plugins_pkg.__path__):
            full = f"assistant.plugins.{name}"
            try:
                mod = importlib.import_module(full)
                if hasattr(mod, "get_plugin"):
                    plugin = mod.get_plugin(self)
                    self.plugins[name] = plugin
            except Exception:
                continue

    def handle_text(self, text: str):
        txt = text.strip()
        lowered = txt.lower()
        # Wake word detection
        for w in config.WAKE_WORDS:
            if lowered.startswith(w):
                # strip wake word
                cmd = txt[len(w):].strip()
                return self.process_command(cmd)
        # If no wake word, treat as direct command
        return self.process_command(txt)

    def process_command(self, command: str):
        if not command:
            return "Yes?"
        parts = command.split()
        verb = parts[0].lower()
        args = parts[1:]
        # naive dispatch: check plugins if they implement verb
        for plugin in self.plugins.values():
            if hasattr(plugin, verb):
                try:
                    fn = getattr(plugin, verb)
                    return fn(" ".join(args))
                except Exception as e:
                    return f"Error executing {verb}: {e}"
        # No plugin handled it — use local LLM for conversational response
        try:
            resp = llm.query(command)
            return resp
        except Exception:
            return f"I don't know how to '{verb}' yet." 
