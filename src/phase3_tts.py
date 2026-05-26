"""
Phase 3: Text-to-Speech with Qwen + Audio Alignment
- Generates narration audio using Qwen TTS
- Applies voice configuration (Sweet Tea male, American drama tension)
- Critical: Time-stretch audio to prevent desync/chipmunk effect
"""

import json
import logging
import base64
from pathlib import Path
from typing import List, Optional
import requests
import librosa
import soundfile as sf
import numpy as np

logger = logging.getLogger(__name__)

class TTSGenerator:
    """Handles Qwen TTS generation and audio alignment"""
    
    def __init__(self, api_key: str, base_url: str, model: str, voice_config):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.voice_config = voice_config
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    
    def generate_speech(self, text: str, segment_id: str = "seg_0") -> dict:
        """
        Generate speech from text using Qwen TTS
        Ensures English-only narration with proper language settings
        
        Args:
            text: Text to synthesize (should be in English)
            segment_id: Unique segment identifier
            
        Returns:
            Dict with audio data and metadata
        """
        logger.info(f"Generating English speech for segment: {segment_id}")
        
        # Ensure we're requesting English narration
        payload = {
            "model": self.model,
            "input": text,
            "voice": self.voice_config.voice_id,
            "language": "en-US",  # Force English only
            "sample_rate": 44100,
            "style": self.voice_config.style,
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/audio/speech",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            
            # Decode audio
            audio_data = response.content
            
            logger.info(f"English speech generated for {segment_id}")
            
            return {
                "segment_id": segment_id,
                "audio_data": audio_data,
                "text": text,
                "voice": self.voice_config.voice_id,
                "language": "en-US",
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            raise
    
    def time_stretch_audio(self, audio_path: Path, target_duration_sec: float) -> np.ndarray:
        """
        Time-stretch audio to fit target duration without pitch change
        This prevents the "chipmunk" effect and maintains natural speed
        
        Args:
            audio_path: Path to audio file
            target_duration_sec: Target duration in seconds
            
        Returns:
            Time-stretched audio array
        """
        logger.info(f"Time-stretching audio to {target_duration_sec}s")
        
        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=44100)
            
            # Calculate stretch factor
            original_duration = librosa.get_duration(y=y, sr=sr)
            stretch_factor = original_duration / target_duration_sec
            
            # Apply time-stretch (maintains pitch)
            y_stretched = librosa.effects.time_stretch(y, rate=stretch_factor)
            
            logger.info(f"Stretched {original_duration:.2f}s → {target_duration_sec:.2f}s")
            
            return y_stretched
            
        except Exception as e:
            logger.error(f"Time-stretch failed: {e}")
            raise
    
    def save_audio(self, audio_array: np.ndarray, output_path: Path, sr: int = 44100):
        """Save audio array to file"""
        sf.write(str(output_path), audio_array, sr)
        logger.info(f"Audio saved to {output_path}")

def run_phase3(config, segments: List[dict], output_dir: Path) -> dict:
    """
    Execute Phase 3 end-to-end
    
    Args:
        config: Lyria config
        segments: Narration segments from Phase 2
        output_dir: Output directory
        
    Returns:
        Output dict with generated audio segments
    """
    tts_dir = output_dir / "tts_audio"
    tts_dir.mkdir(parents=True, exist_ok=True)
    
    generator = TTSGenerator(
        config.qwen.api_key,
        config.qwen.base_url,
        config.qwen.tts_model,
        config.voice
    )
    
    generated_segments = []
    
    for idx, segment in enumerate(segments):
        text = segment.get("text", "")
        if not text:
            logger.warning(f"Segment {idx} has no text, skipping")
            continue
        
        segment_id = f"seg_{idx}"
        
        # Generate speech
        speech_result = generator.generate_speech(text, segment_id)
        
        # Save audio
        audio_path = tts_dir / f"{segment_id}.wav"
        with open(audio_path, "wb") as f:
            f.write(speech_result["audio_data"])
        
        # Calculate target duration (rough estimate from text length)
        # Approximate: 10 chars = 1 second of speech
        target_duration = max(len(text) / 10, 1.0)
        
        # Time-stretch to align
        try:
            stretched = generator.time_stretch_audio(audio_path, target_duration)
            
            # Save stretched version
            stretched_path = tts_dir / f"{segment_id}_aligned.wav"
            generator.save_audio(stretched, stretched_path)
            
            segment["audio_path"] = str(stretched_path)
            segment["duration"] = target_duration
            
        except Exception as e:
            logger.warning(f"Time-stretch failed for {segment_id}: {e}, using original")
            segment["audio_path"] = str(audio_path)
        
        generated_segments.append(segment)
        logger.info(f"Processed {segment_id}")
    
    output = {
        "segments": generated_segments,
        "voice_config": {
            "voice_id": config.voice.voice_id,
            "style": config.voice.style,
        },
        "total_audio_duration": sum(s.get("duration", 0) for s in generated_segments)
    }
    
    # Save metadata
    metadata_path = output_dir / "phase3_tts.json"
    with open(metadata_path, "w") as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"Phase 3 complete. TTS saved to {tts_dir}")
    
    return output
