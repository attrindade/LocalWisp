import sounddevice as sd
import numpy as np
import threading

class AudioRecorder:
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.audio_buffer = []

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"Error in recording: {status}")
        if self.recording:
            self.audio_buffer.append(indata.copy())

    def start_recording(self):
        try:
            self.recording = True
            self.audio_buffer = []
            self.stream = sd.InputStream(samplerate=self.sample_rate,
                                       channels=self.channels,
                                       callback=self._callback)
            self.stream.start()
            print("Recording started...")
        except Exception as e:
            self.recording = False
            print(f"Failed to start recording: {e}")
            raise e

    def stop_recording(self):
        self.recording = False
        try:
            if hasattr(self, 'stream'):
                self.stream.stop()
                self.stream.close()
                del self.stream
        except Exception as e:
            print(f"Error closing stream: {e}")

        print("Recording stopped.")

        if not self.audio_buffer:
            return np.array([], dtype=np.float32)

        return np.concatenate(self.audio_buffer, axis=0).flatten()
