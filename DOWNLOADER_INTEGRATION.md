# Custom Downloader Integration

## Overview
Phase 1 now uses a custom downloader for `downloadwella.com` instead of yt-dlp. This allows downloading directly from file-sharing sites.

## How It Works

### 1. URL Format
The downloader expects downloadwella.com URLs:
```
https://downloadwella.com/[FILE_ID]/[FILE_NAME].html
```

Example:
```
https://downloadwella.com/hg8nwy6xu862/Azure.Spring.S01E01.(THENKIRI.COM).mkv.html
```

### 2. Download Process

**Step 1: Extract File ID**
- Parses the URL to extract the file ID (e.g., `hg8nwy6xu862`)

**Step 2: POST Request**
- Sends a POST request to the page URL with parameters:
  ```
  op: "download2"
  id: [FILE_ID]
  rand: ""
  referer: ""
  method_free: ""
  method_premium: ""
  ```

**Step 3: Find Direct Link**
- Parses the response HTML for the direct download URL pattern:
  ```
  https://dwbe01.downloadwella.com/d/...
  ```

**Step 4: Download File**
- Downloads the file from the direct link
- Saves to `./outputs/videos/[FILENAME]`

### 3. Configuration

**In `.env`:**
```env
VIDEO_SOURCE_URL=https://downloadwella.com/hg8nwy6xu862/Azure.Spring.S01E01.(THENKIRI.COM).mkv.html
```

**Override via CLI:**
```bash
python main.py --url "https://downloadwella.com/YOUR_ID/YOUR_FILE.html"
```

## Features

✅ **Automatic File Extraction** - Extracts filename from direct link  
✅ **Progress Tracking** - Logs download progress  
✅ **Error Handling** - Detects CAPTCHA requirements  
✅ **Timeout Protection** - 30s connection timeout, 300s download timeout  
✅ **Headers Spoofing** - Uses realistic browser headers  

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Could not extract file ID" | Invalid URL format | Use correct downloadwella.com URL |
| "Could not find direct download link" | Response parsing failed | Site may have changed; check manually |
| "CAPTCHA" message | Site detected automation | Requires manual intervention |
| Timeout | Server too slow | Check network/try again |

## Implementation Details

**File**: `src/phase1_ingest.py`  
**Class**: `VideoIngestor`  
**Method**: `download_video(url: str) -> Path`

**Key Code Section:**
```python
def download_video(self, url: str) -> Path:
    # 1. Extract file ID from URL
    match = re.search(r'downloadwella\.com/([^/]+)', url)
    file_id = match.group(1).split('.')[0]
    
    # 2. POST request with download parameters
    response = requests.post(url, data=data, headers=headers)
    
    # 3. Find direct download link in response
    download_match = re.search(r'href="(https://[^"]+\.downloadwella\.com/d/[^"]+)"', response.text)
    direct_link = download_match.group(1)
    
    # 4. Download file with streaming
    with requests.get(direct_link, stream=True) as r:
        with open(video_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    
    return video_path
```

## Integration Points

**Phase 1 → Phase 2**: 
- Phase 1 returns video file path
- Phase 2 sends that video to Qwen for analysis
- Rest of pipeline unchanged

**Changes Made**:
- ✅ Removed: `yt-dlp` import and subprocess calls
- ✅ Removed: `yt-dlp>=2024.1.0` from requirements.txt
- ✅ Added: Custom download logic using `requests` + `re`
- ✅ Updated: All documentation & examples

## Testing

**Verify Integration:**
```bash
python main.py --phases 1
```

**Expected Output:**
```
INFO - Downloading video from https://downloadwella.com/...
INFO - Extracted file ID: hg8nwy6xu862
INFO - Sending download request for file ID: hg8nwy6xu862
INFO - Direct download link found: https://dwbe01.downloadwella.com/d/...
INFO - Downloading Azure.Spring.S01E01.(THENKIRI.COM).mkv...
INFO - Download complete: /workspaces/lyria/outputs/videos/Azure.Spring.S01E01.(THENKIRI.COM).mkv
```

## Troubleshooting

### Issue: Download fails silently
**Check**: Review `lyria.log` for detailed error messages

### Issue: "Could not find direct download link"
**Try**: 
1. Test URL manually in browser
2. Check if CAPTCHA appears
3. Verify file still exists on downloadwella.com

### Issue: Download is very slow
**Note**: This is expected depending on:
- Server load
- Your internet speed
- File size

## Future Enhancements

- [ ] Add retry logic for failed downloads
- [ ] Support multiple file hosting sites
- [ ] Implement CAPTCHA detection & user notification
- [ ] Add parallel downloads for multiple files
- [ ] Cache download links for batch processing
