# LocalWisp

LocalWisp is an offline voice dictation utility for Windows. It allows you to dicate text directly into any active application by holding a shortcut, processing the audio entirely on your local CPU.

## Features
- **Privacy**: 100% offline. No audio or text data is transmitted over the internet.
- **CPU Inference**: Optimized for multi-core processors using `faster-whisper` and `int8` quantization.
- **High Accuracy**: Uses the `large-v3-turbo` model and `silero-vad` for robust speech detection.
- **Visual HUD**: A minimalist, semi-transparent overlay indicates when the tool is recording or transcribing.
- **Direct Injection**: Automatically pastes the transcribed text into your current cursor position.

## Hardware & Optimization
The current configuration is tuned for specific 8-core hardware parameters:
- **Reference CPU**: AMD Ryzen 7 5700G (8 Cores / 16 Threads).
- **Thread Management**: Hardcoded to 8 CPU threads to ensure fast processing without system lag.
- **Memory**: 32 GB RAM (Recommended for handling the `large-v3-turbo` model footprint).

## Future Development
This utility was built to match a specific hardware setup. Future versions aim to:
- Implement automatic hardware detection to dynamically set thread counts.
- Allow for easier model switching based on available system resources.

## Installation & Usage
1. Install dependencies: `pip install -r requirements.txt`.
2. Setup models: `python setup_models.py`.
3. Run: Use `Launch_LocalWisp.bat` to start the tool in the background.
4. **Operation**: Hold **`Win + Ctrl`** to record. Release to transcribe and paste.

## License
**Copyright (c) 2026 ATTrindade**
Distributed under the **MIT License**.
