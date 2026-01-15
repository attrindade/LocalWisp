import os
import sys
import torch

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from transcriber import Transcriber
from vad import VADDetector

def download_models():
    print("--- Downloading/Initializing Models ---")

    # 1. Faster-Whisper (Small)
    print("\n[1/3] Checking Whisper 'small' model...")
    Transcriber(model_size="small", cpu_threads=8)

    # 2. Faster-Whisper (Medium)
    print("\n[2/4] Checking Whisper 'medium' model...")
    Transcriber(model_size="medium", cpu_threads=8)

    # 3. Faster-Whisper (Large V3 Turbo)
    print("\n[3/4] Checking Whisper 'large-v3-turbo' model...")
    Transcriber(model_size="large-v3-turbo", cpu_threads=8)

    # 4. Silero VAD
    print("\n[4/4] Checking Silero VAD model...")
    VADDetector()

    print("\n--- All models are ready! ---")

if __name__ == "__main__":
    download_models()
