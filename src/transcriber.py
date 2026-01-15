from faster_whisper import WhisperModel
import os

class Transcriber:
    def __init__(self, model_size="small", device="cpu", compute_type="int8", cpu_threads=8):
        """
        Initialize the faster-whisper model.
        Optimized for Ryzen 7 5700G (8 cores / 16 threads).
        """
        print(f"Loading Whisper model '{model_size}' on {device} with {compute_type}...")
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
            cpu_threads=cpu_threads,
            download_root=os.path.join(os.getcwd(), "models")
        )

    def transcribe(self, audio_data):
        """
        Transcribe audio data (numpy array).
        Returns the concatenated text of all segments.
        """
        segments, info = self.model.transcribe(audio_data, beam_size=5, language="pt")

        text = ""
        for segment in segments:
            text += segment.text

        return text.strip()
