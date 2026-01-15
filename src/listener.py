from pynput import keyboard
import threading

class HotkeyListener:
    def __init__(self, on_press_callback, on_release_callback):
        self.on_press_callback = on_press_callback
        self.on_release_callback = on_release_callback
        self.win_pressed = False
        self.ctrl_pressed = False
        self.active = False

    def _on_press(self, key):
        if key == keyboard.Key.cmd or key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
            self.win_pressed = True
        elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = True

        if self.win_pressed and self.ctrl_pressed and not self.active:
            self.active = True
            self.on_press_callback()

    def _on_release(self, key):
        if key == keyboard.Key.cmd or key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
            self.win_pressed = False
        elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = False

        if (not self.win_pressed or not self.ctrl_pressed) and self.active:
            self.active = False
            self.on_release_callback()

    def start(self):
        with keyboard.Listener(on_press=self._on_press, on_release=self._on_release) as listener:
            listener.join()
