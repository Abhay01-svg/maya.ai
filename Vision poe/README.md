# Maya — Local Desktop AI Assistant (scaffold)

This repository contains a minimal scaffold for a desktop AI assistant called *Maya*. It provides a modular architecture, voice I/O, plugin system, and a few example plugins (system control and file manager).

Quick start

1. Create a virtual environment and install requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the CLI assistant:

```powershell
python main.py
```

Type commands or say "voice" to listen via microphone. Wake words are configured in `assistant/config.py`.

Safety notes

- System-level commands (shutdown/restart) are disabled by default. Set `assistant/config.py:ALLOW_SYSTEM_COMMANDS = True` and change `OWNER_PIN` before enabling.

Next steps

- Integrate an LLM for natural conversational responses.
- Add UI (PyQt) with floating widget and history.
- Implement more plugins (browser control, automation engine, macros).
Stable Diffusion UI — C++ backend integration
=============================================

This workspace contains a small Flask UI (`web_ui.py`) and a Python generator (`download_sd.py`).
By default `download_sd.py` uses the Python `diffusers` pipeline. For low-latency local runs you can plug
in a fast C++/native binary and have the Python code call it instead.

How it works
------------
- If the environment variable `SD_CPP_BIN` is set to the path (or name) of an executable and that executable
  is found in `PATH`, `download_sd.generate()` will call it with CLI args and return the produced image.
- If the C++ binary call fails or `SD_CPP_BIN` is not set, the code falls back to the Python `diffusers` pipeline.

Expected CLI for the C++ binary
------------------------------
The Python wrapper expects a binary that accepts these flags (POSIX-style long flags):

- `--prompt <text>` — text prompt
- `--out <path>` — output image path
- `--width <int>` — image width
- `--height <int>` — image height
- `--steps <int>` — inference steps
- `--guidance <float>` — guidance scale
- `--seed <int>` (optional)
- `--upscale` (optional flag)

If your chosen C++ project uses different flags, create a small wrapper script or symlink that translates
the expected args to the binary's format, then point `SD_CPP_BIN` at the wrapper.

Recommended C++/native projects
--------------------------------
- stable-diffusion.cpp / ggml-based ports — popular lightweight CPU/GPU runners with fast startup.
- ONNX Runtime or TensorRT C++ servers — for optimized inference on GPU with batched requests.

Example: set `SD_CPP_BIN` and run UI (Windows PowerShell)
------------------------------------------------------
1) Set env var then start the Flask UI:

   $env:SD_CPP_BIN = 'C:\path\to\sd_cpp_binary.exe'
   python web_ui.py

2) Open http://localhost:7860 and generate. The UI will call the binary and serve the output image from `outputs/`.

Example: set `SD_CPP_BIN` and run UI (cmd)
----------------------------------------
   set SD_CPP_BIN=C:\path\to\sd_cpp_binary.exe
   python web_ui.py

Minimal C++ stub (for local testing)
------------------------------------
If you don't have a ready binary, you can create a tiny stub that immediately writes a placeholder PNG and
prints success. The Python code will accept any binary that respects the expected CLI and exits with code 0.

Next steps
----------
- If you want, I can add a small C++ stub in this repo for quick end-to-end testing, or implement a wrapper
  for one specific project (stable-diffusion.cpp). Tell me which you prefer.

Notes
-----
- CPU inference with `diffusers` is slow — prefer a native binary or an optimized runtime if you need sub-second responses.
- The Flask UI and generator are intentionally simple for easy inspection and extension.
