import cv2
import os
import time
import threading


class CameraPlugin:
    def __init__(self, assistant):
        self.assistant = assistant
        self._preview_thread = None
        self._preview_stop = threading.Event()

    def selfie(self, args=""):
        """Capture a single photo from the default webcam and save to outputs/"""
        out_dir = os.path.abspath("outputs")
        os.makedirs(out_dir, exist_ok=True)
        timestamp = int(time.time())
        fname = f"selfie_{timestamp}.jpg"
        path = os.path.join(out_dir, fname)
        cap = None
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return "No webcam found or cannot access camera."
            # warm up
            for i in range(3):
                ret, frame = cap.read()
                time.sleep(0.05)
            ret, frame = cap.read()
            cap.release()
            if not ret or frame is None:
                return "Failed to capture image from webcam."
            # write image
            cv2.imwrite(path, frame)
            return f"Saved selfie -> {path}"
        except Exception as e:
            try:
                if cap is not None:
                    cap.release()
            except Exception:
                pass
            return f"Camera error: {e}"

    def _preview_loop(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Camera preview: cannot open webcam.")
            return
        window_name = "Maya Camera - Preview"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        while not self._preview_stop.is_set():
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow(window_name, frame)
            # exit preview on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyWindow(window_name)

    def preview(self, args=""):
        """Start a non-blocking webcam preview. Close the window or press 'q' to stop."""
        if self._preview_thread and self._preview_thread.is_alive():
            return "Preview already running."
        self._preview_stop.clear()
        t = threading.Thread(target=self._preview_loop, daemon=True)
        self._preview_thread = t
        t.start()
        return "Preview started (press 'q' in window to stop)."

    def stop_preview(self, args=""):
        if self._preview_thread and self._preview_thread.is_alive():
            self._preview_stop.set()
            return "Stopping preview..."
        return "No active preview."

    # support 'take' verb: 'take a selfie'
    def take(self, args=""):
        if "selfie" in args.lower():
            return self.selfie(args)
        return "Usage: take selfie"


def get_plugin(assistant):
    return CameraPlugin(assistant)
