"""
Phase 2: Multimodal Analysis with Qwen
- Sends video to Qwen 3.7-max via DashScope
- Generates timestamped narration
- Returns structured analysis for TTS processing
"""

import json
import logging
import base64
from pathlib import Path
import requests
from typing import Optional

logger = logging.getLogger(__name__)

class QwenAnalyzer:
    """Handles Qwen API calls for video analysis"""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    
    def analyze_video(self, video_path: Path, prompt: Optional[str] = None) -> dict:
        """
        Send video to Qwen for analysis
        
        Args:
            video_path: Path to video file
            prompt: Custom analysis prompt (optional)
            
        Returns:
            Dict with analyzed content and timestamps
        """
        logger.info(f"Sending video to Qwen for analysis: {video_path}")
        
        if not prompt:
            prompt = """Analyze this video carefully and provide a detailed breakdown:

1. CUTTING POINTS (Most Important):
   - Identify and timestamp where the ACTUAL CONTENT STARTS (skip intros, logos, credits, boring openings)
   - Format: [HH:MM:SS] - [reason for cut point]
   - Also identify natural ending points where content concludes
   - Example: [00:02:15] - Main action/story begins here, skip intro

2. CONTENT DESCRIPTION:
   - Provide a compelling narration that explains what's happening in the video
   - Key moments with timestamps (format: [HH:MM:SS] description)
   - Emotional tone and pacing notes

3. LANGUAGE & AUDIO DETECTION:
   - What is the original audio language of the video?
   - Is there dialogue that needs to be preserved?
   - Any important sound effects or music cues?

4. SUMMARY:
   - Brief content summary
   - Recommended total runtime after cutting (removing intros/outros)

Format your response as JSON with keys: 
- cutting_points (array with timestamps and reasons)
- content_description (string)
- key_moments (array with timestamps)
- tone (string)
- language_detected (string)
- summary (string)
- recommended_start (HH:MM:SS format)
- recommended_end (HH:MM:SS format)"""
        
        try:
            # Read video file
            with open(video_path, "rb") as f:
                video_data = base64.b64encode(f.read()).decode("utf-8")
            
            # Prepare request
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "video",
                                "video": f"data:video/mp4;base64,{video_data}"
                            }
                        ]
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
            }
            
            # Make API call
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=300  # 5 min timeout for video processing
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract content
            content = result["choices"][0]["message"]["content"]
            logger.info("Analysis complete - identified cutting points and language")
            
            return {
                "raw_analysis": content,
                "model": self.model,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Qwen analysis failed: {e}")
            raise
    
    def parse_narration_segments(self, analysis: dict) -> list:
        """
        Parse analysis response into narration segments for TTS
        Also extracts cutting points and language detection
        
        Args:
            analysis: Raw analysis from Qwen
            
        Returns:
            List of segments with timestamps and text
        """
        logger.info("Parsing narration segments and cutting points")
        
        segments = []
        raw = analysis.get("raw_analysis", "")
        
        # Try to parse as JSON first
        try:
            import json
            parsed = json.loads(raw)
            
            # Extract cutting points
            cutting_points = parsed.get("cutting_points", [])
            if cutting_points:
                logger.info(f"Found {len(cutting_points)} cutting points:")
                for cp in cutting_points:
                    logger.info(f"  - {cp}")
            
            # Extract language detection
            language = parsed.get("language_detected", "Unknown")
            logger.info(f"Detected original language: {language}")
            
            # Extract recommended start/end
            rec_start = parsed.get("recommended_start", None)
            rec_end = parsed.get("recommended_end", None)
            if rec_start:
                logger.info(f"Recommended cut: {rec_start} to {rec_end}")
            
            # Extract key moments for narration
            key_moments = parsed.get("key_moments", [])
            if not key_moments:
                key_moments = parsed.get("narration", "").split("\n")
            
            for idx, moment in enumerate(key_moments):
                if isinstance(moment, dict):
                    segments.append({
                        "timestamp": moment.get("timestamp", ""),
                        "text": moment.get("text", ""),
                        "duration": None
                    })
                elif isinstance(moment, str) and moment.strip():
                    segments.append({
                        "timestamp": f"[Moment {idx}]",
                        "text": moment.strip(),
                        "duration": None
                    })
        
        except (json.JSONDecodeError, KeyError):
            # Fallback: simple line-by-line parsing
            logger.debug("JSON parsing failed, using fallback line parsing")
            for line in raw.split("\n"):
                line = line.strip()
                if line.startswith("["):
                    end_bracket = line.find("]")
                    if end_bracket > 0:
                        timestamp_str = line[1:end_bracket]
                        text = line[end_bracket+1:].strip()
                        
                        segments.append({
                            "timestamp": timestamp_str,
                            "text": text,
                            "duration": None
                        })
        
        logger.info(f"Extracted {len(segments)} narration segments")
        return segments

def run_phase2(config, video_path: str) -> dict:
    """
    Execute Phase 2 end-to-end
    
    Args:
        config: Lyria config
        video_path: Path from Phase 1
        
    Returns:
        Output dict with analysis and segments
    """
    analyzer = QwenAnalyzer(
        config.qwen.api_key,
        config.qwen.base_url,
        config.qwen.analysis_model
    )
    
    video_file = Path(video_path)
    
    # Analyze video
    analysis = analyzer.analyze_video(video_file)
    
    # Parse segments
    segments = analyzer.parse_narration_segments(analysis)
    
    output = {
        "analysis": analysis,
        "segments": segments,
        "segment_count": len(segments)
    }
    
    # Save analysis
    metadata_path = config.output_dir / "phase2_analysis.json"
    with open(metadata_path, "w") as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"Phase 2 complete. Analysis saved to {metadata_path}")
    
    return output
