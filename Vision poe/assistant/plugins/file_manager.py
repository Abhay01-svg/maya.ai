import os

class FileManagerPlugin:
    def __init__(self, assistant):
        self.assistant = assistant

    def search(self, args=""):
        """Search files by name under given path. Usage: 'search <query> [path]'"""
        parts = args.split()
        if not parts:
            return "Usage: search <query> [path]"
        query = parts[0].lower()
        root = parts[1] if len(parts) > 1 else os.path.expanduser("~")
        matches = []
        for dirpath, dirnames, filenames in os.walk(root):
            for fn in filenames:
                if query in fn.lower():
                    matches.append(os.path.join(dirpath, fn))
            if len(matches) >= 50:
                break
        if not matches:
            return "No files found."
        return "\n".join(matches[:20])

    def open(self, args=""):
        path = args.strip()
        if not path:
            return "Usage: open <full-path>"
        try:
            os.startfile(path)
            return f"Opened {path}"
        except Exception as e:
            return f"Open failed: {e}"


def get_plugin(assistant):
    return FileManagerPlugin(assistant)
