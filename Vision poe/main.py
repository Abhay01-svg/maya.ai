import argparse
import threading
import time
from assistant import Assistant
from assistant import voice
import assistant.config as config


def run_cli():
    a = Assistant()
    print("Maya assistant (type 'exit' to quit). Say 'Hey Maya' to wake via voice if microphone available.")
    while True:
        try:
            text = input("You: ")
        except EOFError:
            break
        if not text:
            continue
        if text.lower() in ("exit", "quit"):
            print("Goodbye")
            break
        if text.lower() == "voice":
            print("Listening (5s)...")
            spoken = voice.listen()
            print("Heard:", spoken)
            resp = a.handle_text(spoken)
            print("Maya:", resp)
            voice.speak(resp)
            continue
        resp = a.handle_text(text)
        print("Maya:", resp)
        voice.speak(resp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-voice", action="store_true", help="Disable voice I/O and run text-only CLI")
    parser.add_argument("--voice-trigger", action="store_true", help="Enable background voice trigger to listen for wake words and actions")
    args = parser.parse_args()
    stop_event = threading.Event()

    def voice_trigger_loop(assistant, stop_ev: threading.Event):
        print("Voice-trigger: started")
        while not stop_ev.is_set():
            try:
                spoken = voice.listen(timeout=4, phrase_time_limit=6)
            except Exception:
                spoken = ""
            if not spoken:
                time.sleep(0.2)
                continue
            lowered = spoken.lower()
            # detect wake word anywhere and a selfie intent
            woke = any(w in lowered for w in config.WAKE_WORDS)
            if woke:
                if "selfie" in lowered or "take a selfie" in lowered:
                    resp = assistant.handle_text("take selfie")
                    print("Voice-trigger ->", spoken)
                    print("Maya:", resp)
                    voice.speak(resp)
            time.sleep(0.2)

    if args.voice_trigger:
        assistant_main = Assistant()
        vt = threading.Thread(target=voice_trigger_loop, args=(assistant_main, stop_event), daemon=True)
        vt.start()
        try:
            # run interactive CLI while background voice trigger runs
            run_cli()
        finally:
            stop_event.set()
    else:
        run_cli()


if __name__ == "__main__":
    main()
