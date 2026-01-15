# LocalWisp 🎙️

LocalWisp is an offline voice dictation utility for Windows. It allows you to dictate text directly into any active application by holding a shortcut, with all audio processing occurring entirely on your local CPU.

## Features
- **Privacy First**: 100% offline; no audio or text data is ever transmitted over the internet.
- **CPU Inference**: Optimized for multi-core processors using `faster-whisper` and `int8` quantization.
- **High Accuracy**: Powered by the `large-v3-turbo` model and `silero-vad` for robust speech detection.
- **Minimalist HUD**: A semi-transparent overlay provides real-time status feedback (Recording/Processing).
- **Direct Injection**: Automatically pastes the transcribed text at your current cursor position.

## Hardware & Current Optimization
The utility is currently tuned for a specific performance profile based on the developer's hardware:
- **Reference CPU**: AMD Ryzen 7 5700G (8 Cores / 16 Threads).
- **Thread Management**: Hardcoded to 8 CPU threads to ensure fast processing without system lag.
- **Memory**: 32 GB RAM recommended for the `large-v3-turbo` model footprint.

## Future Development & Collaboration
LocalWisp is an open project. While built for a specific setup, future iterations aim to:
- Implement automatic hardware detection to dynamically set thread counts.
- Improve flexibility for different model sizes based on available system resources.
- We welcome collaborative efforts to improve hardware abstraction and performance.

## Installation & Usage
1. **Install dependencies**: `pip install -r requirements.txt`.
2. **Setup models**: `python setup_models.py`.
3. **Run**: Use `Launch_LocalWisp.bat` to start the tool in the background.
4. **Operation**: Hold **`Win + Ctrl`** to record. Release the keys to transcribe and paste.

## License
Copyright (c) 2026 ATTrindade and LocalWisp Contributors.
Distributed under the **MIT License**.
