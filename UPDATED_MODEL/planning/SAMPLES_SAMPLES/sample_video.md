# Video File with Metadata

**Filename**: `sample_video.mp4` (or `.mov`, `.avi`)  
**Type**: Video File  
**Extraction Method**: Video metadata parsing  
**Expected Nodes**: 1  
**Expected Edges**: 0  
**Confidence**: Medium  
**Creation Difficulty**: ⭐⭐ Easy

---

## 📋 Overview

Video files contain **rich metadata** including:
- Duration
- Resolution (width x height)
- Frame rate (fps)
- Video codec (H.264, H.265, etc.)
- Audio codec (AAC, MP3, etc.)
- Bit rate
- Creation timestamp (sometimes)
- Camera metadata (for videos from cameras)

The extractor can read this metadata and create a knowledge graph node with video information.

---

## 🎯 Creation Steps

### Option 1: Record on Phone (EASIEST - 1 minute)

1. **Open your phone's camera app**
2. **Switch to video mode**
3. **Record** 5-10 seconds of video
4. **Stop recording**
5. **Transfer to computer**:
   - Email it to yourself
   - Use USB cable
   - Use cloud storage
6. **Rename** to `sample_video.mp4`
7. **Save** to `samples4/`

**Result**: Video file with full metadata (duration, resolution, codec, timestamps).

### Option 2: Use Online Video Recorder

1. Go to https://record.cast/ or https://screenapp.io/
2. **Start recording** (webcam or screen)
3. **Record** 5-10 seconds
4. **Stop and download**
5. **Rename** to `sample_video.mp4`
6. **Save** to `samples4/`

### Option 3: Convert Existing Video

```bash
# Using FFmpeg (recommended)
ffmpeg -i input.avi -c:v libx264 -c:a aac -movflags +faststart samples4/sample_video.mp4

# If FFmpeg not installed
sudo apt install ffmpeg  # Ubuntu/Debian
# OR
brew install ffmpeg     # macOS
```

### Option 4: Use OBS Studio

1. Download and install **OBS Studio** (free)
2. **Start recording** (any source: webcam, screen, etc.)
3. **Record** 5-10 seconds
4. **Stop recording**
5. **Save** as `sample_video.mp4` to `samples4/`

### Option 5: Use Python (requires OpenCV)

```bash
pip install opencv-python numpy

python << 'EOF'
import cv2
import numpy as np

# Create a simple test video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('samples4/sample_video.mp4', fourcc, 30.0, (640, 480))

# Create 100 frames of different colors
for i in range(100):
    # Create frame with gradient
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:, :] = (i * 255 // 100, i * 255 // 200, i * 255 // 150)  # Gradient color
    
    # Add text
    cv2.putText(frame, f'Frame {i}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    out.write(frame)

out.release()
print("Video created: samples4/sample_video.mp4")
EOF
```

---

## 🔍 File Verification

```bash
# Check file exists
ls -la samples4/sample_video.mp4

# Check file type
file samples4/sample_video.mp4  # Should be: "ISO Media, MP4 Base Media v1 [ISOM]"

# View video metadata (requires ffprobe)
ffprobe -v error -show_entries format=duration,bit_rate -show_entries stream=codec_type,codec_name,width,height,avg_frame_rate -of json samples4/sample_video.mp4

# Duration in seconds
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 samples4/sample_video.mp4

# Resolution
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 samples4/sample_video.mp4
```

---

## 🎯 Extraction Commands

### Basic Version
```bash
python extract.py samples4/sample_video.mp4 --output results/sample_video.json
```

### Expected Output (Basic)
```json
{
  "extraction_metadata": {
    "file": "samples4/sample_video.mp4",
    "timestamp": "2026-10-05T16:30:00Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": 5000000,
      "created_time": "2026-10-05T16:25:00Z",
      "modified_time": "2026-10-05T16:25:00Z",
      "accessed_time": "2026-10-05T16:30:00Z"
    },
    "file_type": "video/mp4"
  },
  "version_history": {
    "edits": [
      {
        "node_id": "fs_sample_video.mp4",
        "node_type": "edit",
        "timestamp": "2026-10-05T16:25:00Z",
        "author": null,
        "edit_type": "create",
        "content_after": "[Binary file: sample_video.mp4]",
        "source": "filesystem",
        "evaluation_band": "low"
      }
    ],
    "edit_count": 1
  },
  "knowledge_graph": {
    "nodes": 1,
    "edges": 0,
    "total_nodes": 1,
    "total_edges": 0
  },
  "summary": {
    "total_edits": 1,
    "sources_used": ["filesystem"],
    "confidence_distribution": {"low": 1}
  }
}
```

### Full Version (with OpenCV/FFmpeg)
```bash
pip install opencv-python

# Then run with full extract.py
python extract.py samples4/sample_video.mp4 --output results/sample_video_full.json
```

### Expected Output (Full)
```json
{
  "extraction_metadata": {
    "file": "samples4/sample_video.mp4",
    "timestamp": "2026-10-05T16:35:00Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": 5000000,
      "created_time": "2026-10-05T16:25:00Z",
      "modified_time": "2026-10-05T16:25:00Z",
      "accessed_time": "2026-10-05T16:30:00Z"
    },
    "file_type": "video/mp4",
    "video_opencv": {
      "duration_seconds": 3.33,
      "frame_count": 100,
      "fps": 30.0,
      "resolution": {"width": 640, "height": 480}
    }
  },
  "version_history": {
    "edits": [
      {
        "node_id": "video_20240205T100000Z",
        "node_type": "edit",
        "timestamp": "2024-02-05T10:00:00Z",  // From creation date if available
        "author": null,
        "edit_type": "create",
        "description": "Video created",
        "source": "video_metadata",
        "evaluation_band": "medium"
      }
    ],
    "edit_count": 1
  },
  "knowledge_graph": {
    "nodes": 1,
    "edges": 0,
    "total_nodes": 1,
    "total_edges": 0
  },
  "summary": {
    "total_edits": 1,
    "sources_used": ["video_metadata"],
    "confidence_distribution": {"medium": 1}
  }
}
```

---

## 📊 Validation Commands

```bash
# Check video metadata was extracted
python -c "
import json
d = json.load(open('results/sample_video.json'))
if any(k.startswith('video') for k in d['file_metadata'].keys()):
    print('✅ Video metadata extracted')
else:
    print('❌ Video metadata NOT extracted')
"

# Check knowledge graph
python -c "
import json
d = json.load(open('results/sample_video.json'))
kg = d['knowledge_graph']
print(f'Nodes: {kg[\"total_nodes\"]}')
print(f'Edges: {kg[\"total_edges\"]}')
print(f'Source: {d[\"summary\"][\"sources_used\"]}')
"
```

---

## 🎓 Key Concepts Demonstrated

1. **Video metadata extraction** - Reading video file properties
2. **Duration extraction** - Getting video length
3. **Resolution extraction** - Width and height
4. **Frame rate extraction** - FPS value
5. **Codec extraction** - Video and audio codecs
6. **Binary file handling** - Reading video files
7. **Medium confidence data** - Video metadata reliability

---

## 💡 Tips

1. **Phone videos** work perfectly for testing
2. **MP4 format** is most widely supported
3. **H.264 codec** is standard for MP4
4. **Keep videos short** (5-10 seconds) for faster extraction
5. **Use FFmpeg** for format conversion and metadata viewing

---

## ⚠️ Common Issues

### Issue: File not recognized as video
**Symptom**: File type is "application/octet-stream"

**Solution**: Install `python-magic`: `pip install python-magic`

### Issue: OpenCV can't read video
**Symptom**: `OpenCV: FFmpeg not found` or similar

**Solution**: Install FFmpeg:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg libopencv-dev

# macOS
brew install ffmpeg opencv

# Then reinstall opencv-python
pip uninstall opencv-python
pip install opencv-python-headless
```

### Issue: Video metadata missing
**Symptom**: No duration/resolution extracted

**Solution**: Ensure video is in a supported format (MP4 with H.264). Try re-encoding:
```bash
ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mp4
```

---

## 🔗 Related

- **Previous**: [Audio with ID3 Tags](sample_audio.md)
- **Next**: [Git Version History](git_history.md)
- **Full Specs**: [../../artifacts/specs.md](../../artifacts/specs.md)

---

**Video files provide excellent testing for complex binary file handling. Even basic extraction can get file type and size.**
