import sys
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import threading
import queue
import time
import pyperclip
from pynput.keyboard import Controller, Key
import pystray
import subprocess
from PIL import Image, ImageDraw

import logging

# Configuração de log para arquivo
logging.basicConfig(
    filename='debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Redirecionar stdout e stderr para o log para evitar erro no pythonw.exe
class LogStream:
    def write(self, message):
        if message.strip():
            logging.info(f"[STDOUT/STDERR] {message.strip()}")
    def flush(self):
        pass

sys.stdout = LogStream()
sys.stderr = LogStream()

logging.info("Iniciando LocalWisp...")

# Add src to path
try:
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    from recorder import AudioRecorder
    from transcriber import Transcriber
    from vad import VADDetector
    from listener import HotkeyListener
    logging.info("Módulos carregados com sucesso.")
except Exception as e:
    logging.error(f"Erro ao carregar módulos: {e}")
    raise

import tkinter as tk

class LocalWispApp:
    def __init__(self):
        # Initialize UI first to avoid threading issues with Tkinter
        self._setup_indicator()

        self.recorder = AudioRecorder()
        self.vad = VADDetector()
        # Using large-v3-turbo for best accuracy and speed
        print("Initializing Transcriber (this may take a few seconds)...")
        self.transcriber = Transcriber(model_size="large-v3-turbo", cpu_threads=8)
        print("Transcriber ready.")
        self.keyboard_controller = Controller()
        self.task_queue = queue.Queue()
        self.running = True
        self.status = "Inativo"
        self.icon = None
        self.recording_started = False # Track if recording actually started
        logging.info("App object initialized.")

    def _setup_indicator(self):
        """Creates a modern pill-shaped HUD above the taskbar with transparency."""
        self.indicator_root = tk.Tk()
        self.indicator_root.withdraw()
        self.indicator_root.overrideredirect(True)
        self.indicator_root.attributes("-topmost", True)
        self.indicator_root.attributes("-transparentcolor", "#121212")
        self.indicator_root.attributes("-alpha", 0.75) # Ghost-like transparency

        # Modern Pill Dimensions
        self.ind_w = 200
        self.ind_h = 42

        sw = self.indicator_root.winfo_screenwidth()
        sh = self.indicator_root.winfo_screenheight()

        # Position: bottom center, roughly 80px above the bottom
        px = (sw // 2) - (self.ind_w // 2)
        py = sh - 100 # Adjust if necessary

        self.indicator_root.geometry(f"{self.ind_w}x{self.ind_h}+{px}+{py}")

        self.canvas = tk.Canvas(self.indicator_root, width=self.ind_w, height=self.ind_h,
                                bg='#121212', highlightthickness=0)
        self.canvas.pack()

        # Pill background (More subtle grey)
        radius = 20
        x1, y1, x2, y2 = 2, 2, self.ind_w-2, self.ind_h-2
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        self.canvas.create_polygon(points, fill="#252525", outline="#333333", smooth=True, width=1)

        # Status Light (Subtle circle)
        self.light = self.canvas.create_oval(18, 13, 29, 24, fill="#ff4b4b", outline="")

        # Status Text (Softer White/Grey)
        self.label = self.canvas.create_text(110, 21, text="ESCUTANDO", fill="#cccccc",
                                           font=("Segoe UI Variable", 10, "bold"))

    def update_ui(self, status_type, show=True):
        """Updates HUD visuals based on current app state."""
        configs = {
            'recording': ('#ff4b4b', 'ESCUTANDO...'),
            'processing': ('#4ba3ff', 'PROCESSANDO...'),
            'error': ('#ff9500', 'ERRO NO MIC'),
            'idle': ('#00ff00', '')
        }

        color, text = configs.get(status_type, ('gray', ''))

        def _update():
            if show and status_type != 'idle':
                self.canvas.itemconfig(self.light, fill=color)
                self.canvas.itemconfig(self.label, text=text)
                self.indicator_root.deiconify()
                self.indicator_root.lift()
            else:
                self.indicator_root.withdraw()
        self.indicator_root.after(0, _update)

    def create_image(self, color):
        # Generate a simple icon (a circle)
        width, height = 64, 64
        image = Image.new('RGB', (width, height), (30, 30, 30))  # Background dark grey
        dc = ImageDraw.Draw(image)
        dc.ellipse((10, 10, 54, 54), fill=color)
        return image

    def on_hotkey_press(self):
        try:
            logging.info("Hotkey pressed")
            self.update_ui('recording', show=True)
            if self.icon:
                self.icon.icon = self.create_image('red')
            self.recorder.start_recording()
            self.recording_started = True # Succesfully started
        except Exception as e:
            logging.error(f"Erro ao iniciar gravação: {e}")
            self.recording_started = False
            self.update_ui('error')

    def on_hotkey_release(self):
        try:
            logging.info("Hotkey released")
            if not self.recording_started:
                # If it never started (mic error), just hide the HUD
                self.update_ui('idle', show=False)
                if self.icon:
                    self.icon.icon = self.create_image('green')
                return

            self.update_ui('processing', show=True)
            if self.icon:
                self.icon.icon = self.create_image('blue')

            audio_data = self.recorder.stop_recording()
            self.recording_started = False # Reset flag

            if audio_data is not None and audio_data.size > 0:
                self.task_queue.put(audio_data)
            else:
                self.update_ui('idle', show=False)
                if self.icon:
                    self.icon.icon = self.create_image('green')
        except Exception as e:
            logging.error(f"Erro ao parar gravação: {e}")
            self.recording_started = False
            self.update_ui('error')

    def processing_worker(self):
        while self.running:
            try:
                audio_data = self.task_queue.get(timeout=1)

                if self.vad.is_speech(audio_data):
                    text = self.transcriber.transcribe(audio_data)

                    if text:
                        logging.info(f"Transcription: {text}")
                        pyperclip.copy(text)

                        # Release all potentially stuck keys
                        time.sleep(0.3)
                        for key in [Key.cmd, Key.cmd_l, Key.cmd_r, Key.ctrl, Key.ctrl_l, Key.ctrl_r, Key.alt, Key.shift]:
                            self.keyboard_controller.release(key)

                        # Simulate Ctrl+V
                        with self.keyboard_controller.pressed(Key.ctrl):
                            self.keyboard_controller.press('v')
                            self.keyboard_controller.release('v')

                self.task_queue.task_done()
                self.update_ui('idle', show=False)
                if self.icon:
                    self.icon.icon = self.create_image('green')
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Processing error: {e}")
                self.update_ui('orange')

    def quit_app(self, icon, item):
        logging.info("Finalizando LocalWisp...")
        self.running = False
        self.indicator_root.quit()
        icon.stop()
        os._exit(0)

    def restart_app(self, icon, item):
        logging.info("Reiniciando LocalWisp...")
        self.running = False
        self.indicator_root.after(0, self.indicator_root.quit)
        icon.stop()

        # Spawn a new process and exit current one
        subprocess.Popen([sys.executable] + sys.argv)
        os._exit(0)

    def run(self):
        # Start worker thread
        threading.Thread(target=self.processing_worker, daemon=True).start()

        # Start hotkey listener in separate thread
        listener = HotkeyListener(self.on_hotkey_press, self.on_hotkey_release)
        threading.Thread(target=listener.start, daemon=True).start()

        # Create System Tray Icon
        self.icon = pystray.Icon("LocalWisp",
                               self.create_image('green'),
                               "LocalWisp (Win+Ctrl)",
                               menu=pystray.Menu(
                                   pystray.MenuItem("Reiniciar", self.restart_app),
                                   pystray.MenuItem("Sair", self.quit_app)
                               ))
        threading.Thread(target=self.icon.run, daemon=True).start()

        print("LocalWisp pronto com HUD moderno.")
        self.indicator_root.mainloop()

if __name__ == "__main__":
    try:
        app = LocalWispApp()
        app.run()
    except Exception as e:
        logging.error(f"Erro fatal na execução: {e}", exc_info=True)
