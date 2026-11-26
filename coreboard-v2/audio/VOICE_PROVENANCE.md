# Coreboard offline voice provenance

- Engine: Piper TTS, piper-tts 1.8.0
- Voice: en_US-lessac-medium (English, 22050 Hz, mono)
- Official source: https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/lessac/medium
- Voice model SHA256: 5efe09e69902187827af646e1a6e9d269dee769f9877d17b16b1b46eeaaf019f
- Voice config SHA256: efe19c417bed055f2d69908248c6ba650fa135bc868b0e6abb3da181dab690a0
- Text/filename map: audio/manifest.json (119 unique paths)
- Rebuild tool: tools/rebuild_piper_audio.py
- Processing: FFmpeg loudnorm=I=-18:TP=-2:LRA=7, then per-clip RMS gain toward -19 dB with peak limiting to 0.89 linear full-scale; MP3 22050 Hz mono
- Offline use: built-in English words, tasks, and presets use local MP3. Chinese and edited text use iPad system speech.
- The ONNX binaries are not bundled in the public repository. Download the source model, verify the SHA256, install Piper TTS in an isolated environment, and run the rebuild tool.

This records provenance and reproducibility, not an independent perceptual assessment of voice naturalness. Physical iPad Safari audio needs its own device test.
