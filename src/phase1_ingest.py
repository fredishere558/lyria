"""
Phase 1: Video Ingest & Scene Detection
- Downloads video from downloadwella.com
- Detects scene changes automatically
- Extracts most content-dense window
"""

import json
import re
import requests
from pathlib import Path
from scenedetect import detect, AdaptiveDetector
import logging

logger = logging.getLogger(__name__)

class VideoIngestor:
    """Handles video download and scene detection"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.video_dir = output_dir / "videos"
        self.video_dir.mkdir(parents=True, exist_ok=True)
    
    def download_video(self, url: str) -> Path:
        """
        Download video from downloadwella.com
        
        Args:
            url: Video URL from downloadwella.com
            
        Returns:
            Path to downloaded video
        """
        logger.info(f"Downloading video from {url}")
        
        # Extract ID from URL
        match = re.search(r'downloadwella\.com/([^/]+)', url)
        if not match:
            raise ValueError("Error: Could not extract file ID from URL. Expected downloadwella.com URL.")
        
        file_id = match.group(1).split('.')[0]
        logger.info(f"Extracted file ID: {file_id}")
        
        data = {
            "op": "download2",
            "id": file_id,
            "rand": "",
            "referer": "",
            "method_free": "",
            "method_premium": ""
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": url
        }

        try:
            logger.info(f"Sending download request for file ID: {file_id}")
            response = requests.post(url, data=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Look for the direct download link in the response
            # The link pattern: https://dwbe01.downloadwella.com/d/...
            download_match = re.search(r'href="(https://[^"]+\.downloadwella\.com/d/[^"]+)"', response.text)
            
            if not download_match:
                logger.warning("Could not find direct download link in the response")
                if "captcha" in response.text.lower():
                    logger.error("The site might be requiring a CAPTCHA. Please check the page manually.")
                raise ValueError("Could not find direct download link in the response.")
            
            direct_link = download_match.group(1)
            logger.info(f"Direct download link found: {direct_link}")
            
            # Extract filename from direct link or use file_id as default
            filename = direct_link.split('/')[-1]
            if not filename:
                filename = f"{file_id}.mkv"
            
            video_path = self.video_dir / filename
            logger.info(f"Downloading {filename}...")
            
            with requests.get(direct_link, stream=True, timeout=300) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                
                with open(video_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size:
                                progress = (downloaded / total_size) * 100
                                logger.debug(f"Download progress: {progress:.1f}%")
            
            logger.info(f"Download complete: {video_path.absolute()}")
            return video_path
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Download request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred during download: {e}")
            raise
    
    def detect_scenes(self, video_path: Path, threshold: float = 27.0) -> list:
        """
        Detect scene changes using adaptive detector
        
        Args:
            video_path: Path to video file
            threshold: Content change threshold (lower = more sensitive)
            
        Returns:
            List of scene change timestamps
        """
        logger.info(f"Detecting scenes in {video_path}")
        
        try:
            scenes = detect(str(video_path), AdaptiveDetector(luma_only=False))
            
            # Convert to seconds
            timestamps = [float(scene[0].get_seconds()) for scene in scenes]
            logger.info(f"Found {len(timestamps)} scene breaks")
            
            return timestamps
            
        except Exception as e:
            logger.error(f"Scene detection failed: {e}")
            raise
    
    def extract_dense_window(self, video_path: Path, duration_sec: int = 600) -> dict:
        """
        Extract most content-dense window (default 10 minutes)
        For now, returns info about the video - actual extraction happens in phase 2
        
        Args:
            video_path: Path to video file
            duration_sec: Target clip duration in seconds
            
        Returns:
            Dict with clip metadata
        """
        logger.info(f"Analyzing video density for {duration_sec}s window")
        
        result = {
            "video_path": str(video_path),
            "duration_sec": duration_sec,
            "start_time": 0,
            "end_time": duration_sec,
            "metadata": {
                "filename": video_path.name,
                "file_size_mb": video_path.stat().st_size / (1024*1024),
            }
        }
        
        logger.info(f"Ready to process: {result}")
        return result

def run_phase1(config) -> dict:
    """
    Execute Phase 1 end-to-end
    
    Returns:
        Output dict with video path and metadata
    """
    ingestor = VideoIngestor(config.output_dir)
    
    # Download
    video_path = ingestor.download_video(config.video_source_url)
    
    # Detect scenes
    scenes = ingestor.detect_scenes(video_path)
    
    # Extract dense window
    clip_info = ingestor.extract_dense_window(video_path)
    clip_info["scene_breaks"] = scenes
    
    # Save metadata
    metadata_path = config.output_dir / "phase1_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(clip_info, f, indent=2)
    
    logger.info(f"Phase 1 complete. Metadata saved to {metadata_path}")
    
    return clip_info
