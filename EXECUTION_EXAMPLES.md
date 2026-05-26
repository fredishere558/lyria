# LYRIA Execution Examples

## Example 1: Quick Test (Phases 1-3)

**Command:**
```bash
python main.py --phases 1,2,3
```

This uses the pre-configured URL from `.env`. To use a different URL:
```bash
python main.py --phases 1,2,3 --url "https://downloadwella.com/YOUR_ID/YOUR_FILE.html"
```

**Expected Output:**
```
2026-05-25 10:30:45 - lyria - INFO - ============================================================
2026-05-25 10:30:45 - lyria - INFO - LYRIA FULL PIPELINE START
2026-05-25 10:30:45 - lyria - INFO - ============================================================

[PHASE 1] Video Ingest & Scene Detection
------------------------------------------------------------
2026-05-25 10:30:46 - phase1_ingest - INFO - Downloading video from https://...
2026-05-25 10:30:52 - phase1_ingest - INFO - Download completed
2026-05-25 10:30:52 - phase1_ingest - INFO - Video saved to ./outputs/videos/Never Gonna Give You Up.mp4
2026-05-25 10:30:52 - phase1_ingest - INFO - Detecting scenes in ./outputs/videos/Never Gonna Give You Up.mp4
2026-05-25 10:30:58 - phase1_ingest - INFO - Found 12 scene breaks

[PHASE 2] Multimodal Analysis with Qwen
------------------------------------------------------------
2026-05-25 10:30:58 - phase2_analysis - INFO - Sending video to Qwen for analysis: ...
2026-05-25 10:31:25 - phase2_analysis - INFO - Analysis complete
2026-05-25 10:31:25 - phase2_analysis - INFO - Parsing narration segments
2026-05-25 10:31:25 - phase2_analysis - INFO - Extracted 8 segments

[PHASE 3] Text-to-Speech with Audio Alignment
------------------------------------------------------------
2026-05-25 10:31:25 - phase3_tts - INFO - Generating speech for segment: seg_0
2026-05-25 10:31:30 - phase3_tts - INFO - Speech generated for seg_0
2026-05-25 10:31:30 - phase3_tts - INFO - Time-stretching audio to 3.5s
2026-05-25 10:31:30 - phase3_tts - INFO - Stretched 2.8s → 3.5s
2026-05-25 10:31:30 - phase3_tts - INFO - Audio saved to ./outputs/tts_audio/seg_0_aligned.wav
2026-05-25 10:31:30 - phase3_tts - INFO - Processed seg_0
[... 7 more segments ...]

============================================================
PIPELINE EXECUTION SUMMARY
============================================================
phase1: success
phase2: success
phase3: success

EXECUTION COMPLETE
============================================================
Output directory: /workspaces/lyria/outputs
Status: complete
```

**Generated Files:**
```
outputs/
├── videos/
│   └── Never Gonna Give You Up.mp4
├── phase1_metadata.json
│   {
│     "video_path": "./outputs/videos/Never Gonna Give You Up.mp4",
│     "scene_breaks": [1.2, 3.4, 5.6, ...]
│   }
├── phase2_analysis.json
│   {
│     "segments": [
│       {
│         "timestamp": "[00:00:05]",
│         "text": "An iconic music video begins..."
│       },
│       ...
│     ]
│   }
├── tts_audio/
│   ├── seg_0.wav
│   ├── seg_0_aligned.wav
│   ├── seg_1.wav
│   ├── seg_1_aligned.wav
│   └── ...
├── phase3_tts.json
│   {
│     "segments": [
│       {
│         "audio_path": "./outputs/tts_audio/seg_0_aligned.wav",
│         "duration": 3.5,
│         "text": "An iconic music video begins..."
│       }
│     ],
│     "total_audio_duration": 28.5
│   }
├── execution_log.json
│   {
│     "start_time": "2026-05-25T10:30:45...",
│     "config": {
│       "model": "qwen-max-latest",
│       "tts_model": "qwen3-tts-flash",
│       "voice": "sweet_tea_male"
│     },
│     "phases": {
│       "phase1": {"status": "success", "scenes_detected": 12},
│       "phase2": {"status": "success", "segments_extracted": 8},
│       "phase3": {"status": "success", "audio_segments": 8}
│     }
│   }
└── lyria.log
```

---

## Example 2: Full Pipeline with Captions

**Command:**
```bash
python main.py
```

**Additional Output (Phases 4-5):**
```
[PHASE 4] 4K Upscaling Filter
------------------------------------------------------------
2026-05-25 10:32:15 - phase4_upscale - INFO - Phase 4: Video upscaling (scale=2x)
2026-05-25 10:32:15 - phase4_upscale - INFO - CPU mode: Real video processing would be slow
2026-05-25 10:32:15 - phase4_upscale - INFO - Recommendation: Use GPU for production

[PHASE 5] Automatic Caption Generation
------------------------------------------------------------
2026-05-25 10:32:15 - phase5_captions - INFO - Generating captions with WhisperX: ...
2026-05-25 10:32:45 - phase5_captions - INFO - Generated 45 caption segments
2026-05-25 10:32:45 - phase5_captions - INFO - Converting to SRT format: ./outputs/captions/captions.srt
2026-05-25 10:32:45 - phase5_captions - INFO - Converting to VTT format: ./outputs/captions/captions.vtt
```

**Additional Files:**
```
outputs/
├── captions/
│   ├── captions.srt
│   │   1
│   │   00:00:05,200 --> 00:00:08,400
│   │   An iconic music video
│   │
│   │   2
│   │   00:00:08,400 --> 00:00:12,600
│   │   begins with pure energy
│   └── captions.vtt
│       WEBVTT
│
│       00:00:05.200 --> 00:00:08.400
│       An iconic music video
├── phase4_upscale.json
├── phase5_captions.json
```

---

## Example 3: Override Settings

**Command:**
```bash
python main.py --phases 2 --url "https://..." --output ./quick_test
```

**Notes:**
- Only Phase 2 runs (requires Phase 1 video from outputs/)
- Uses custom output directory `./quick_test/`
- Video URL overridden in command

---

## Example 4: Checking Results

**View captions:**
```bash
cat outputs/captions/captions.srt
```

**Play generated audio:**
```bash
ffplay outputs/tts_audio/seg_0_aligned.wav
```

**Review analysis:**
```bash
python -m json.tool outputs/phase2_analysis.json | head -30
```

**Monitor execution:**
```bash
tail -f lyria.log
```

---

## Expected Timings (Single Video, CPU Mode)

| Phase | Time | Status |
|-------|------|--------|
| 1 | 5-15 min | Fast (network bound) |
| 2 | 10-30 min | Medium (API latency) |
| 3 | 5-15 min | Fast (TTS generation) |
| 4 | ⏱️ 100+ hours | ⚠️ Impractical (CPU) |
| 5 | 5-10 min | Fast (speech recognition) |
| **1-3,5 MVP** | **30-60 min** | **✓ Production ready** |

---

## Error Scenarios

### Scenario 1: Invalid API Key

**Error Output:**
```
2026-05-25 10:31:15 - phase2_analysis - ERROR - Qwen analysis failed: 401 Unauthorized
...
Fatal error: Qwen analysis failed: 401 Unauthorized
```

**Fix:**
- Check `DASHSCOPE_API_KEY` in `.env`
- Verify key in DashScope dashboard
- Retry with correct key

### Scenario 2: Invalid Video URL

**Error Output:**
```
2026-05-25 10:30:52 - phase1_ingest - ERROR - Download failed: Video unavailable
```

**Fix:**
- Test URL in browser
- Ensure video is public/downloadable
- Check yt-dlp compatibility

### Scenario 3: Insufficient Disk Space

**Error Output:**
```
2026-05-25 10:32:15 - phase3_tts - ERROR - Audio saved to ...: No space left on device
```

**Fix:**
- Clear `./outputs/` directory
- Check disk space: `df -h`
- Clean up old builds

---

## Production Checklist Execution

✅ **Pre-Run**
- [ ] Test setup: `python main.py --phases 1 --url "..." `
- [ ] Check API key valid: Monitor first API call
- [ ] Verify disk space: 500MB+ free

✅ **Run**
- [ ] Start: `python main.py --phases 1,2,3,5`
- [ ] Monitor: `tail -f lyria.log`
- [ ] Wait: ~1 hour for output

✅ **Post-Run**
- [ ] Review audio: Check `./outputs/tts_audio/*_aligned.wav`
- [ ] Check captions: Open `./outputs/captions/captions.srt`
- [ ] Review metadata: `cat ./outputs/execution_log.json`
- [ ] Save results: Move `./outputs/` to archive location
