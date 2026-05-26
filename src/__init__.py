"""
LYRIA - AI-Powered Video Narration & Enhancement Pipeline
A modular, production-ready system for transforming videos into narrated content

Components:
- Phase 1: Video ingest & scene detection (yt-dlp)
- Phase 2: Multimodal analysis (Qwen 3.7-max)
- Phase 3: Text-to-speech with alignment (Qwen 3-TTS-Flash)
- Phase 4: 4K upscaling & color grading (Real-ESRGAN + LUT)
- Phase 5: Automatic caption generation (WhisperX)
- Phase 6: Pipeline orchestration

Configuration: .env file
Models: Qwen (via DashScope API)
Processing: CPU (for now), GPU-ready for production
"""

__version__ = "0.1.0"
__author__ = "Lyria Team"
