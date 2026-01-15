import torch
import numpy as np
import os

class VADDetector:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        # Load Silero VAD model locally
        self.model, self.utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                              model='silero_vad',
                                              force_reload=False,
                                              onnx=False)
        (self.get_speech_timestamps, _, self.read_audio, _, _) = self.utils

    def is_speech(self, audio_data, threshold=0.5):
        """
        Check if the audio data contains speech.
        audio_data: numpy array (1D)
        """
        # Convert numpy array to torch tensor
        audio_tensor = torch.from_numpy(audio_data).float()

        # Get speech timestamps
        speech_timestamps = self.get_speech_timestamps(audio_tensor, self.model, sampling_rate=self.sample_rate, threshold=threshold)

        return len(speech_timestamps) > 0
