# LYRIA - AI Video Narration & Enhancement Pipeline

A production-ready, modular system for transforming videos into AI-narrated, enhanced content with automatic captions, color grading, and 4K upscaling.

## Architecture Overview

```
Phase 1: Video Ingest          → Download + Scene Detection (downloadwella.com)
Phase 2: Multimodal Analysis   → Generate Narration (Qwen 3.7-max)
Phase 3: TTS + Audio Alignment → Generate Speech + Timing (Qwen 3-TTS-Flash)
Phase 4: 4K Upscaling          → ESRGAN + LUT Color Grade
Phase 5: Caption Generation    → Word-Level Timestamps (WhisperX)
Phase 6: Orchestration         → Full Pipeline Execution
```

## Setup

### Prerequisites
- Python 3.9+
- DashScope API Key (for Qwen models)
- ffmpeg (for video processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/fredishere558/lyria.git
   cd lyria
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # .env file is already configured with:
   # - DASHSCOPE_API_KEY: Your DashScope API key
   # - ANALYSIS_MODEL: qwen-max-latest
   # - TTS_MODEL: qwen3-tts-flash
   # - VOICE_ID: sweet_tea_male
   # - VOICE_STYLE: american_drama_tension
   # - OUTPUT_DIR: ./outputs
   # - USE_GPU: false (CPU mode for now)
   # - LUT_FILE: ./07_Davinci Resolve LUTs_Sunset.cube (preset applied)
   
   # Update .env with your settings:
   # - VIDEO_SOURCE_URL: YouTube URL or local video path
   ```

## Usage

### Full Pipeline (All Phases)
```bash
python main.py
```

### Specific Phases Only
```bash
# Run phases 1-3 (download, analyze, generate audio)
python main.py --phases 1,2,3

# Run phase 2 only (analysis)
python main.py --phases 2
```

### With Custom Parameters
```bash
# Override video URL
python main.py --url "https://www.youtube.com/watch?v=..."

# Override output directory
python main.py --output ./my_outputs

# Combine options
python main.py --phases 1,2 --url "..." --output ./results
```

## Configuration (.env)

### API & Model Settings
```env
DASHSCOPE_API_KEY=sk-...              # Your DashScope API key
DASHSCOPE_BASE_URL=https://...        # DashScope endpoint
ANALYSIS_MODEL=qwen-max-latest        # Model for video analysis
TTS_MODEL=qwen3-tts-flash             # Model for speech synthesis
CAPTION_MODEL=faster-whisper          # Model for caption generation
```

### Voice Configuration
```env
VOICE_ID=sweet_tea_male               # Sweet Tea male voice
VOICE_STYLE=american_drama_tension    # American drama tension style
```

### Processing Settings
```env
USE_GPU=false                         # CPU mode (false) or GPU (true)
CPU_THREADS=4                         # Number of CPU threads
BATCH_SIZE=4                          # Processing batch size
```

### Output & Presets
```env
VIDEO_SOURCE_URL=https://downloadwella.com/...  # downloadwella.com URL
OUTPUT_DIR=./outputs                  # Output directory
LOCAL_DELIVERY=true                   # Local storage (vs cloud)
LUT_FILE=./07_Davinci Resolve LUTs_Sunset.cube  # Color preset
```

## Output Structure

```
outputs/
├── videos/                          # Downloaded/original videos
├── tts_audio/                       # Generated audio segments
│   ├── seg_0.wav
│   ├── seg_0_aligned.wav           # Time-stretched for sync
│   └── ...
├── captions/                        # Generated captions
│   ├── captions.srt                # SRT format
│   └── captions.vtt                # WebVTT format
├── phase1_metadata.json             # Ingest metadata
├── phase2_analysis.json             # Analysis results
├── phase3_tts.json                  # TTS metadata
├── phase4_upscale.json              # Upscaling config
├── phase5_captions.json             # Caption metadata
├── execution_log.json               # Full pipeline log
└── lyria.log                        # Detailed log file
```

## Phase Details

### Phase 1: Video Ingest
- **Input**: downloadwella.com URL
- **Process**: Download video, detect scene breaks
- **Output**: Video file + scene metadata
- **Key Feature**: Automatic scene detection for clip segmentation

### Phase 2: Multimodal Analysis
- **Input**: Video file
- **Process**: Send to Qwen 3.7-max for analysis
- **Output**: Timestamped narration segments + cutting points
- **Key Features**: 
  - Identifies where to cut (skip boring intros/outros)
  - Detects original video language
  - Recommends optimal start/end points
  - Generates English narration description

### Phase 3: Text-to-Speech
- **Input**: Narration segments from Phase 2
- **Process**: Generate speech with Qwen 3-TTS-Flash, time-stretch for alignment
- **Output**: Aligned audio segments in English
- **Key Features**: 
  - Ensures English-only narration regardless of original video language
  - Time-stretching prevents "chipmunk effect" and maintains natural speed
  - Sweet Tea male voice with drama tension style

### Phase 4: 4K Upscaling
- **Input**: Original video
- **Process**: Real-ESRGAN + CAS sharpening + LUT color grading
- **Output**: Upscaled, color-graded video
- **Config**: Sunset LUT preset applied
- **Note**: CPU mode ready; GPU (T4) reduces processing time from 100+ hours to ~8 hours

### Phase 5: Caption Generation
- **Input**: Audio from Phase 3
- **Process**: WhisperX for word-level timestamps
- **Output**: SRT and WebVTT subtitle files
- **Key Feature**: Word-level timing enables karaoke-style highlighting

### Phase 6: Orchestration
- **Chains Phases 1-5** with error handling and logging
- **Supports partial execution** (run specific phases)
- **Logs detailed execution** for debugging and monitoring

## Key Technical Decisions

### Qwen Models Instead of Gemini
- ✅ Better performance on video analysis (native multimodal support)
- ✅ Lower latency via DashScope
- ✅ Cost-effective at scale
- ✅ Works with CPU processing

### Audio Time-Stretching (Phase 3)
- **Critical**: Prevents audio desync and "chipmunk" effect
- **Method**: Librosa time-stretch (maintains pitch)
- **Result**: Perfect sync without quality loss

### Word-Level Captions (Phase 5)
- **WhisperX unlock**: Word-level timestamps instead of sentence-level
- **Use Case**: Enables viral karaoke-style word highlighting
- **Fallback**: Faster-whisper if WhisperX unavailable

### LUT Color Grading (Phase 4)
- **Preset**: DaVinci Resolve Sunset LUT (already included)
- **Processing**: Applied on top of ESRGAN for polished final output
- **CAS Sharpening**: Adds crispness beyond standard upscaling

## Performance Notes

### CPU vs GPU

**CPU Mode (Current)**
- Phase 1-3: ~30-60 minutes
- Phase 4 (upscaling): 100-200 hours for 10-min video (not practical)
- Phase 5: ~5-10 minutes

**GPU Mode (T4)**
- Phase 1-3: Same (~30-60 min)
- Phase 4 (upscaling): ~8 hours for 10-min video
- Phase 5: Same (~5-10 min)
- **Parallel T4s**: ~4 hours with 2 GPUs

### Recommended Production Setup
- **Phases 1-3, 5**: Run on CPU (fast enough)
- **Phase 4**: Parallel T4 GPUs on Kaggle or cloud (cost-effective)
- **Time to Production Video**: 4-6 hours total

## Development & Customization

### Adding Custom Analysis Prompts
Edit `phase2_analysis.py`:
```python
custom_prompt = """Your custom analysis instructions here"""
analyzer.analyze_video(video_path, prompt=custom_prompt)
```

### Switching Voice
Update `.env`:
```env
VOICE_ID=your_voice_id
VOICE_STYLE=your_style
```

### Changing LUT Preset
Update `.env`:
```env
LUT_FILE=./path/to/your/preset.cube
```

### GPU Acceleration
Set in `.env`:
```env
USE_GPU=true
```
Then install CUDA dependencies and ESRGAN GPU backend.

## Logging

All operations are logged to both:
- **Console**: Real-time progress
- **File**: `lyria.log` for debugging
- **JSON**: `execution_log.json` for structured analysis

## Troubleshooting

### "DASHSCOPE_API_KEY not set"
- Ensure `.env` file has your DashScope API key
- Check: `echo $DASHSCOPE_API_KEY` in terminal

### "VIDEO_SOURCE_URL not set"
- Add YouTube URL or local path to `.env`
- Test URL directly in browser first

### Phase 4 (upscaling) is very slow
- **Expected on CPU**: Can take 100+ hours for full video
- **Solution**: Use GPU mode or run Phase 4 on parallel T4s
- **Workaround**: Process shorter clips or skip Phase 4 initially

### Audio sync issues
- Ensure Phase 3 time-stretching completed successfully
- Check aligned audio files: `seg_*_aligned.wav`

### Caption timing off
- Verify audio duration matches expected segment duration
- Check WhisperX vs faster-whisper output

## API Rate Limits

DashScope API has standard rate limits. For batch processing:
- Implement request queuing
- Add exponential backoff for retries
- Monitor quota usage in DashScope dashboard

## Future Enhancements

- [ ] Multi-language narration support
- [ ] Custom voice cloning
- [ ] Advanced video editing (transitions, effects)
- [ ] Automated metadata generation
- [ ] Cloud storage integration (S3, etc.)
- [ ] Web UI for pipeline management
- [ ] Scheduled batch processing
- [ ] Multi-video project support

## License

MIT

## Contact & Support

For issues, questions, or contributions, please visit the GitHub repository.