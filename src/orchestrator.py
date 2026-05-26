"""
Phase 6: Orchestration
Main orchestrator that chains all phases together
Provides a unified interface for full pipeline execution
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import phase modules
from phase1_ingest import run_phase1
from phase2_analysis import run_phase2
from phase3_tts import run_phase3
from phase4_upscale import run_phase4
from phase5_captions import run_phase5

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    """
    Main pipeline orchestrator
    Chains phases 1-5 together with proper error handling and state management
    """
    
    def __init__(self, config):
        self.config = config
        self.execution_log = {
            "start_time": datetime.now().isoformat(),
            "config": {
                "model": config.qwen.analysis_model,
                "tts_model": config.qwen.tts_model,
                "voice": config.voice.voice_id,
                "use_gpu": config.processing.use_gpu,
            },
            "phases": {}
        }
        self.outputs = {}
    
    def run_full_pipeline(self) -> dict:
        """
        Execute complete pipeline phases 1-5
        
        Returns:
            Final output with all phase results
        """
        logger.info("=" * 60)
        logger.info("LYRIA FULL PIPELINE START")
        logger.info("=" * 60)
        
        try:
            # Phase 1: Ingest
            logger.info("\n[PHASE 1] Video Ingest & Scene Detection")
            logger.info("-" * 60)
            phase1_result = run_phase1(self.config)
            self.outputs["phase1"] = phase1_result
            self.execution_log["phases"]["phase1"] = {
                "status": "success",
                "video_path": phase1_result.get("video_path"),
                "scenes_detected": len(phase1_result.get("scene_breaks", []))
            }
            
            # Phase 2: Analysis
            logger.info("\n[PHASE 2] Multimodal Analysis with Qwen")
            logger.info("-" * 60)
            phase2_result = run_phase2(self.config, phase1_result["video_path"])
            self.outputs["phase2"] = phase2_result
            self.execution_log["phases"]["phase2"] = {
                "status": "success",
                "segments_extracted": len(phase2_result.get("segments", []))
            }
            
            # Phase 3: TTS
            logger.info("\n[PHASE 3] Text-to-Speech with Audio Alignment")
            logger.info("-" * 60)
            phase3_result = run_phase3(
                self.config,
                phase2_result.get("segments", []),
                self.config.output_dir
            )
            self.outputs["phase3"] = phase3_result
            self.execution_log["phases"]["phase3"] = {
                "status": "success",
                "audio_segments": len(phase3_result.get("segments", [])),
                "total_duration_sec": phase3_result.get("total_audio_duration")
            }
            
            # Phase 4: Upscaling
            logger.info("\n[PHASE 4] 4K Upscaling Filter")
            logger.info("-" * 60)
            phase4_result = run_phase4(
                self.config,
                phase1_result["video_path"],
                self.config.output_dir
            )
            self.outputs["phase4"] = phase4_result
            self.execution_log["phases"]["phase4"] = {
                "status": "success",
                "scale_factor": phase4_result.get("scale_factor"),
                "message": phase4_result.get("message")
            }
            
            # Phase 5: Captions
            logger.info("\n[PHASE 5] Automatic Caption Generation")
            logger.info("-" * 60)
            # Use first audio segment for caption generation
            first_audio = phase3_result.get("segments", [{}])[0].get("audio_path")
            if first_audio:
                phase5_result = run_phase5(
                    self.config,
                    first_audio,
                    self.config.output_dir
                )
            else:
                logger.warning("No audio segments found, skipping Phase 5")
                phase5_result = {"status": "skipped", "reason": "no audio segments"}
            
            self.outputs["phase5"] = phase5_result
            self.execution_log["phases"]["phase5"] = {
                "status": phase5_result.get("status"),
                "segments": phase5_result.get("segment_count", 0)
            }
            
            return self._finalize_execution()
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            self.execution_log["error"] = str(e)
            return self._save_execution_log()
    
    def run_partial_pipeline(self, phases: list = None) -> dict:
        """
        Run specific phases only
        
        Args:
            phases: List of phase numbers to run (e.g., [1, 2, 3])
            
        Returns:
            Output with specified phases only
        """
        if phases is None:
            phases = [1, 2, 3]  # Default to first 3 phases
        
        logger.info(f"Running partial pipeline: phases {phases}")
        
        phase_functions = {
            1: ("Video Ingest", lambda: run_phase1(self.config)),
            2: ("Analysis", lambda: run_phase2(self.config, self.outputs.get("phase1", {}).get("video_path"))),
            3: ("TTS", lambda: run_phase3(self.config, self.outputs.get("phase2", {}).get("segments", []), self.config.output_dir)),
            4: ("Upscaling", lambda: run_phase4(self.config, self.outputs.get("phase1", {}).get("video_path"), self.config.output_dir)),
            5: ("Captions", lambda: run_phase5(self.config, "", self.config.output_dir)),
        }
        
        for phase_num in sorted(phases):
            if phase_num not in phase_functions:
                logger.warning(f"Unknown phase {phase_num}, skipping")
                continue
            
            phase_name, phase_func = phase_functions[phase_num]
            try:
                logger.info(f"\n[PHASE {phase_num}] {phase_name}")
                logger.info("-" * 60)
                result = phase_func()
                self.outputs[f"phase{phase_num}"] = result
            except Exception as e:
                logger.error(f"Phase {phase_num} failed: {e}")
                raise
        
        return self._finalize_execution()
    
    def _finalize_execution(self) -> dict:
        """Finalize execution and save logs"""
        self.execution_log["end_time"] = datetime.now().isoformat()
        return self._save_execution_log()
    
    def _save_execution_log(self) -> dict:
        """Save execution log to file"""
        log_path = self.config.output_dir / "execution_log.json"
        with open(log_path, "w") as f:
            json.dump(self.execution_log, f, indent=2)
        
        logger.info(f"\nExecution log saved to {log_path}")
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("=" * 60)
        for phase, info in self.execution_log.get("phases", {}).items():
            status = info.get("status", "unknown")
            logger.info(f"{phase}: {status}")
        
        return {
            "status": "complete",
            "output_dir": str(self.config.output_dir),
            "execution_log": self.execution_log,
            "phase_outputs": self.outputs
        }

def create_orchestrator(config):
    """Factory function to create orchestrator"""
    return PipelineOrchestrator(config)
