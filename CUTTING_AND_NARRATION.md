# Movie Cutting & English Narration Guide

## Overview
Phase 2 (Analysis) now intelligently identifies where to cut movies to remove boring intros/outros. Phase 3 (TTS) ensures English-only narration regardless of the original video language.

## How It Works

### Phase 2: Intelligent Cutting Points

The AI model analyzes the video and identifies:

1. **Where Content Starts** - Skips:
   - Long intros/logos
   - Opening credits
   - Boring slow sections
   - Format: `[HH:MM:SS] - reason for cut`

2. **Language Detection** - Reports:
   - Original audio language
   - Whether dialogue should be preserved
   - Important sound cues

3. **Recommended Timeline** - Suggests:
   - Optimal start point (where action begins)
   - Optimal end point (where story concludes)
   - Total runtime after cutting

### Phase 3: English-Only Narration

The TTS engine:
- Generates narration ONLY in English (en-US)
- Uses Sweet Tea male voice with drama tension style
- Ignores original video language
- Produces clean, professional narration

## Example Output

When you run `python main.py --phases 1,2,3`, you'll see:

```
[PHASE 2] Multimodal Analysis
INFO - Sending video to Qwen for analysis
INFO - Detected original language: Hindi
INFO - Found 3 cutting points:
    - [00:00:00] - Studio logos and intro
    - [00:02:15] - Main action/story begins here
    - [01:45:30] - Story concludes, credits start
INFO - Recommended cut: 00:02:15 to 01:45:30
INFO - Extracted 8 narration segments

[PHASE 3] Text-to-Speech
INFO - Generating English speech for segment: seg_0
INFO - English speech generated for seg_0
INFO - Language: en-US, Voice: sweet_tea_male
```

## Configuration

### In .env

```env
# Voice settings
VOICE_ID=sweet_tea_male
VOICE_STYLE=american_drama_tension
LANGUAGE=en-US
NARRATION_LANGUAGE=English
```

### Force English Narration

The system always outputs English narration. To use different:
```bash
# Change voice (same language)
VOICE_ID=other_male_voice
VOICE_STYLE=conversational

# Change language (requires new model config)
LANGUAGE=es-ES  # Changes TTS output language
```

## Output Format

### Phase 2 Analysis Output (phase2_analysis.json)

```json
{
  "raw_analysis": {
    "cutting_points": [
      "[00:00:00] - Studio logos",
      "[00:02:15] - Main content starts",
      "[01:45:30] - Story ends"
    ],
    "language_detected": "Hindi",
    "recommended_start": "00:02:15",
    "recommended_end": "01:45:30",
    "content_description": "...",
    "key_moments": [...]
  }
}
```

### Phase 3 TTS Output (phase3_tts.json)

```json
{
  "segments": [
    {
      "text": "The story begins...",
      "duration": 5.2,
      "audio_path": "./outputs/tts_audio/seg_0_aligned.wav",
      "language": "en-US",
      "voice": "sweet_tea_male"
    }
  ]
}
```

## Use Cases

### Case 1: Movie with 20-min Intro
```
Original: 120 minutes
- 0-20 min: Long intro/credits
- 20-110 min: Actual story
- 110-120 min: Credits

Cutting Points Identified:
- START: [00:20:00] (skip intro)
- END: [01:50:00] (before credits)
- Final: 90-minute cut
```

**Result**: Viewers skip the boring intro, jump straight to action.

### Case 2: Non-English Film
```
Original: Hindi audio, 90 minutes
- Audio: Hindi dialogue + music
- Detected: "Language: Hindi"

Action:
1. Video plays with original Hindi audio/scenes
2. AI generates English narration overlay
3. English voice explains what's happening
4. No language barrier for English viewers
```

**Result**: Non-English content becomes accessible with English narration.

### Case 3: Mixed Language Video
```
Original: Multi-language segments
- Opening: English
- Middle: French
- Ending: German
- Detected: "Language: Multiple"

Action:
- AI identifies language switches
- Narration bridges gaps
- Final output: Consistent English narration throughout
```

## Advanced: Using Cutting Points Programmatically

### Extract Cutting Points from Analysis

```python
from src.phase2_analysis import run_phase2
import json

result = run_phase2(config, video_path)
analysis = result["analysis"]["raw_analysis"]

cutting_points = analysis.get("cutting_points", [])
rec_start = analysis.get("recommended_start", "00:00:00")
rec_end = analysis.get("recommended_end", "FULL")

print(f"Cut movie from {rec_start} to {rec_end}")
```

### Generate Cutting Script

You could extend Phase 4 to use these cutting points:

```python
# Pseudo-code for future enhancement
def cut_video(video_path, start_time, end_time):
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-ss", start_time,      # Start trim
        "-to", end_time,        # End trim
        "-c", "copy",           # Copy codec (fast)
        f"{output_path}/cut_video.mp4"
    ]
    subprocess.run(cmd)
```

## Technical Details

### Phase 2 Prompt

The analysis model receives this detailed prompt:

```
1. CUTTING POINTS:
   - Where does actual content start? (skip intros)
   - Where does it end? (before credits)
   
2. LANGUAGE DETECTION:
   - What's the original audio language?
   - Preserve important sound cues?
   
3. NARRATION:
   - Compelling description of what's happening
   - Key moments with timestamps
   
4. FORMAT:
   Return JSON with cutting_points, language_detected, recommended_start, recommended_end
```

### Phase 3 Language Enforcement

```python
payload = {
    "model": "qwen3-tts-flash",
    "input": text,
    "voice": "sweet_tea_male",
    "language": "en-US",         # ALWAYS en-US
    "sample_rate": 44100,
}
```

The `language: "en-US"` parameter ensures all narration is English, regardless of input text language.

## Troubleshooting

### Issue: Cutting Points Not Found
**Cause**: AI couldn't identify clear intro/outro  
**Solution**: Review phase2_analysis.json for `recommended_start` and `recommended_end` fields

### Issue: Narration Not in English
**Cause**: Text input wasn't English  
**Solution**: Ensure Phase 2 outputs English narration (AI should translate if needed)

### Issue: Missing Language Detection
**Cause**: Video analysis was incomplete  
**Solution**: Check Phase 2 logs for full analysis results

## Future Enhancements

- [ ] Automatic video cutting based on identified points (Phase 4)
- [ ] Multi-language narration support (keep original audio + add English narration as track)
- [ ] User-adjustable cutting thresholds
- [ ] Preview mode to review cutting points before processing
- [ ] Audio mixing (preserve original audio + add English narration)

## Example: Full Workflow

```bash
# Run full pipeline with cutting
python main.py --phases 1,2,3,5

# Expected Flow:
# Phase 1: Download movie (120 min)
# Phase 2: Identify cuts + generate English narration description
#   - "Cut from 00:20:00 to 01:50:00"
#   - "Original language: Hindi"
#   - Narration: "In this scene, the hero..."
# Phase 3: Generate English audio overlay
#   - Sweet Tea voice, drama tension
#   - Perfectly timed to narration segments
# Phase 5: Generate English captions
#   - Synced with narration audio

# Output: Professional English-narrated, intelligently-cut video ready for viewers
```
