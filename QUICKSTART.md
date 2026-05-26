# QUICKSTART Guide

## 1. Prerequisites Check

```bash
# Verify Python version
python --version  # Should be 3.9+

# Verify ffmpeg
ffmpeg -version  # Required for video processing

# Verify git
git --version
```

## 2. Initial Setup

```bash
# Clone repo
cd /workspaces/lyria

# Install dependencies
pip install -r requirements.txt
```

## 3. Configure .env

Your `.env` file is already pre-configured with:
- ✅ DASHSCOPE_API_KEY (provided)
- ✅ Models: qwen-max-latest + qwen3-tts-flash
- ✅ Voice: Sweet Tea male (american_drama_tension)
- ✅ LUT Preset: Sunset color grade
- ✅ CPU mode enabled (GPU-ready)
- ✅ Custom downloader for downloadwella.com

**Current Setup**: Video URL is pre-configured with Azure example
```env
VIDEO_SOURCE_URL=https://downloadwella.com/hg8nwy6xu862/Azure.Spring.S01E01.(THENKIRI.COM).mkv.html
```

**To use a different video**: Replace VIDEO_SOURCE_URL with your downloadwella.com link
```env
VIDEO_SOURCE_URL=https://downloadwella.com/YOUR_FILE_ID/YOUR_FILE_NAME.html
```

## 4. Run Pipeline

### Option A: Full Pipeline
```bash
python main.py
```
Runs all 5 phases: download → analyze → TTS → upscale → captions

### Option B: Quick Test (Phases 1-3)
```bash
python main.py --phases 1,2,3
```
✅ Fast (30-60 min)
✅ Output: narrated video with audio
❌ No upscaling/captions (Phases 4-5 skipped)

### Option C: Just Analysis
```bash
python main.py --phases 2
```
Requires phase 1 to run first

## 5. Monitor Progress

**Console output**: Real-time logs
**Log file**: `lyria.log` - detailed debugging
**JSON metadata**: `outputs/execution_log.json` - structured data

## 6. Check Results

After execution, check `outputs/`:
```
outputs/
├── videos/                    # Downloaded video
├── phase2_analysis.json       # Extracted narration
├── tts_audio/
│   ├── seg_0_aligned.wav     # Generated audio
│   └── ...
├── captions/
│   ├── captions.srt          # Subtitles
│   └── captions.vtt
└── execution_log.json         # Full summary
```

## 7. Common Next Steps

### Change Video
```bash
python main.py --url "https://www.youtube.com/watch?v=NEW_VIDEO"
```

### Change Voice
Edit `.env`:
```env
VOICE_ID=your_voice_id
VOICE_STYLE=your_style
```
See `voice_and_preset_config.json` for options

### Change Output Location
```bash
python main.py --output ./my_custom_outputs
```

### Run Without Phase 4 (Skip Slow Upscaling)
```bash
python main.py --phases 1,2,3,5
```
Much faster! Phase 4 takes 100+ hours on CPU.

## 8. Understanding Each Phase

| Phase | Input | Output | Features |
|-------|-------|--------|----------|
| 1 | URL | Downloaded video | Fast download from downloadwella.com |
| 2 | Video | Narration + cutting points | **Smart cutting** (skips intros), language detection |
| 3 | Segments | TTS audio + timing | **English-only** narration, Sweet Tea voice |
| 4 | Video | 4K upscaled | Sunrise LUT preset, CAS sharpening |
| 5 | Audio | Captions (SRT/VTT) | Word-level timing, karaoke style |

**Note on Phase 4**: 
- CPU mode is impractical for full videos
- Use GPU for production (8 hours on T4)
- Consider skipping for MVP testing

## 9. Troubleshooting

### Issue: "VIDEO_SOURCE_URL not set"
**Fix**: Add video URL to `.env` and retry

### Issue: "API key invalid"
**Fix**: Check DASHSCOPE_API_KEY in `.env` is correct

### Issue: "Phase 4 taking too long"
**Expected**: Takes 100+ hours on CPU
**Solutions**:
- Skip with `--phases 1,2,3,5`
- Enable GPU mode in `.env`
- Use cloud GPU (Kaggle T4 = 8 hours)

### Issue: Audio sync issues
**Fix**: Verify `seg_*_aligned.wav` files generated in Phase 3
- If missing: phase 3 time-stretching failed
- Check logs in `lyria.log`

## 10. Production Checklist

Before running on production videos:
- [ ] Test with short video first (< 5 min)
- [ ] Verify DASHSCOPE_API_KEY has sufficient quota
- [ ] Check available disk space (10-min video = ~500MB+)
- [ ] Run `python main.py --phases 1,2,3` to test core pipeline
- [ ] Review generated narration (phase2_analysis.json)
- [ ] Confirm audio alignment (phase3_tts.json)
- [ ] For final output, consider GPU for Phase 4

## 11. Next Features Coming

- [ ] Web UI dashboard
- [ ] Batch processing (multiple videos)
- [ ] Custom voice training
- [ ] Advanced color grading UI
- [ ] Cloud storage integration

## 12. Support

Check logs:
```bash
# Real-time logs
tail -f lyria.log

# Full execution summary
cat outputs/execution_log.json | python -m json.tool
```

Have issues? Check README.md for detailed phase documentation.
