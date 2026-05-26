import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass
class QwenConfig:
    """Qwen API configuration"""
    api_key: str
    base_url: str
    analysis_model: str
    tts_model: str
    
    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-oa/v1"),
            analysis_model=os.getenv("ANALYSIS_MODEL", "qwen-max-latest"),
            tts_model=os.getenv("TTS_MODEL", "qwen3-tts-flash"),
        )

@dataclass
class VoiceConfig:
    """TTS voice configuration"""
    voice_id: str
    style: str
    language: str = "en-US"
    narration_language: str = "English"
    
    @classmethod
    def from_env(cls):
        return cls(
            voice_id=os.getenv("VOICE_ID", "sweet_tea_male"),
            style=os.getenv("VOICE_STYLE", "american_drama_tension"),
            language=os.getenv("LANGUAGE", "en-US"),
            narration_language=os.getenv("NARRATION_LANGUAGE", "English"),
        )

@dataclass
class ProcessingConfig:
    """Processing configuration"""
    use_gpu: bool
    cpu_threads: int
    batch_size: int
    
    @classmethod
    def from_env(cls):
        return cls(
            use_gpu=os.getenv("USE_GPU", "false").lower() == "true",
            cpu_threads=int(os.getenv("CPU_THREADS", "4")),
            batch_size=int(os.getenv("BATCH_SIZE", "4")),
        )

@dataclass
class LyriaConfig:
    """Master configuration for Lyria"""
    qwen: QwenConfig
    voice: VoiceConfig
    processing: ProcessingConfig
    video_source_url: str
    output_dir: Path
    local_delivery: bool
    lut_file: Path
    caption_model: str
    
    @classmethod
    def from_env(cls):
        output_dir = Path(os.getenv("OUTPUT_DIR", "./outputs"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        lut_file = Path(os.getenv("LUT_FILE", "./07_Davinci Resolve LUTs_Sunset.cube"))
        
        return cls(
            qwen=QwenConfig.from_env(),
            voice=VoiceConfig.from_env(),
            processing=ProcessingConfig.from_env(),
            video_source_url=os.getenv("VIDEO_SOURCE_URL"),
            output_dir=output_dir,
            local_delivery=os.getenv("LOCAL_DELIVERY", "true").lower() == "true",
            lut_file=lut_file,
            caption_model=os.getenv("CAPTION_MODEL", "faster-whisper"),
        )

# Global config instance
config = LyriaConfig.from_env()
