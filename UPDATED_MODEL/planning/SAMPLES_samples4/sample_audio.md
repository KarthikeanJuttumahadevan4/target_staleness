---
format: html
---

# Audio File with Metadata

**Filename**: `sample_audio.mp3` (or `.wav`)  
**Type**: Audio File (MP3, WAV, etc.)  
**Extraction Method**: Audio metadata parsing  
**Expected Nodes**: 1  
**Expected Edges**: 0  
**Confidence**: Medium  
**Creation Difficulty**: ⭐⭐ Easy

---

## 📋 Overview

Audio files contain **metadata** that includes:
- Duration
- Bit rate
- Sample rate
- Channels (mono/stereo)
- ID3 tags (for MP3): Title, Artist, Album, Year, Genre
- Other formats have similar metadata

The extractor can read this metadata and create a knowledge graph node with audio information.

---

## 🎯 Creation Steps

### Option 1: Record on Phone (EASIEST - 1 minute)

1. **Open voice recorder/voice memo app** on your phone
2. **Record** 10-30 seconds of speech or any audio
3. **Stop recording**
4. **Transfer to computer**:
   - Email it to yourself
   - Use USB cable
   - Use cloud storage
5. **Rename** to `sample_audio.mp3` or `sample_audio.m4a`
6. **Save** to `samples4/`

**Result**: Audio file with basic metadata (duration, format). MP4/M4A may have limited ID3 tags.

### Option 2: Use Online Audio Recorder

1. Go to https://vocaroo.com/
2. Click **"Click to Record"**
3. **Allow microphone access** when prompted
4. **Record** your audio (10-30 seconds)
5. Click **"Stop"**
6. Click **"Save"**
7. **Download** the MP3 file
8. **Rename** to `sample_audio.mp3`
9. **Save** to `samples4/`

### Option 3: Convert Existing Audio

If you have any audio file (WAV, M4A, OGG, etc.), convert to MP3:

```bash
# Using FFmpeg (recommended)
ffmpeg -i input.wav -c:a libmp3lame -q:a 2 samples4/sample_audio.mp3

# If FFmpeg not installed
sudo apt install ffmpeg  # Ubuntu/Debian
# OR
brew install ffmpeg     # macOS
```

### Option 4: Use Audacity

1. Open **Audacity** (free audio editor)
2. **Record** or **Import** an audio file
3. **Export as MP3**: File → Export → Export as MP3
4. Set metadata:
   - Title: "Test Audio"
   - Artist: "Audio Tester"
   - Album: "Universal Extractor Test"
   - Year: "2024"
   - Genre: "Speech"
5. **Save** as `samples4/sample_audio.mp3`

### Option 5: Use Python (requires pydub)

```bash
pip install pydub

python << 'EOF'
from pydub import AudioSegment
from pydub.generators import WhiteNoise
import os

# Create 10 seconds of white noise
noise = WhiteNoise().to_audio_segment(duration=10000)

# Set sample rate, bit rate, channels
noise = noise.set_frame_rate(44100)
noise = noise.set_channels(2)

# Export as MP3
noise.export("samples4/sample_audio.mp3", format="mp3", bitrate="128k")

print("Audio file created: samples4/sample_audio.mp3")
print("Note: For ID3 tags, use Audacity or another tool")
EOF
```

---

## 🔍 File Verification

```bash
# Check file exists
ls -la samples4/sample_audio.mp3

# Check file type
file samples4/sample_audio.mp3  # Should be: "MPEG ADTS, layer III" or similar

# Check audio metadata (requires ffprobe or mutagen)
python -c "
try:
    from pydub import AudioSegment
    audio = AudioSegment.from_file('samples4/sample_audio.mp3')
    print(f'Duration: {len(audio) / 1000:.1f} seconds')
    print(f'Channels: {audio.channels}')
    print(f'Sample rate: {audio.frame_rate} Hz')
    print(f'Frame width: {audio.frame_width} bytes')
except ImportError:
    print('pydub not installed')
except Exception as e:
    print(f'Error: {e}')
"

# Or use ffprobe
ffprobe samples4/sample_audio.mp3
```

---

## 🎯 Extraction Commands

### Basic Version
```bash
python extract.py samples4/sample_audio.mp3 --output results/sample_audio.json
```

### Expected Output (Basic)
```json
{
  "extraction_metadata": {
    "file": "samples4/sample_audio.mp3",
    "timestamp": "2026-10-05T16:20:00Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": 1500000,
      "created_time": "2026-10-05T16:15:00Z",
      "modified_time": "2026-10-05T16:15:00Z",
      "accessed_time": "2026-10-05T16:20:00Z"
    },
    "file_type": "audio/mpeg"
  },
  "version_history": {
    "edits": [
      {
        "node_id": "fs_sample_audio.mp3",
        "node_type": "edit",
        "timestamp": "2026-10-05T16:15:00Z",
        "author": null,
        "edit_type": "create",
        "content_after": "[Binary file: sample_audio.mp3]",
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

### Full Version (with pydub/mutagen)
```bash
pip install pydub mutagen

# Then run with full extract.py
python extract.py samples4/sample_audio.mp3 --output results/sample_audio_full.json
```

### Expected Output (Full)
```json
{
  "extraction_metadata": {
    "file": "samples4/sample_audio.mp3",
    "timestamp": "2026-10-05T16:25:00Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": 1500000,
      "created_time": "2026-10-05T16:15:00Z",
      "modified_time": "2026-10-05T16:15:00Z",
      "accessed_time": "2026-10-05T16:20:00Z"
    },
    "file_type": "audio/mpeg",
    "audio_pydub": {
      "duration_seconds": 15.5,
      "channels": 2,
      "sample_width": 2,
      "frame_rate": 44100
    },
    "audio_mutagen": {
      "duration": 15.5,
      "bitrate": 128000,
      "tags": {
        "title": ["Test Audio"],
        "artist": ["Audio Tester"],
        "album": ["Universal Extractor Test"],
        "date": ["2024"]
      }
    }
  },
  "version_history": {
    "edits": [
      {
        "node_id": "audio_create",
        "node_type": "edit",
        "timestamp": "2024-01-01T00:00:00Z",  // From ID3 tags if available
        "author": null,
        "edit_type": "create",
        "description": "Audio file created",
        "source": "audio_metadata",
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
    "sources_used": ["audio_metadata"],
    "confidence_distribution": {"medium": 1}
  }
}
```

---

## 📊 Validation Commands

```bash
# Check audio metadata was extracted
python -c "
import json
d = json.load(open('results/sample_audio.json'))
if any(k.startswith('audio') for k in d['file_metadata'].keys()):
    print('✅ Audio metadata extracted')
else:
    print('❌ Audio metadata NOT extracted')
"

# Check knowledge graph
python -c "
import json
d = json.load(open('results/sample_audio.json'))
kg = d['knowledge_graph']
print(f'Nodes: {kg[\"total_nodes\"]}')
print(f'Edges: {kg[\"total_edges\"]}')
print(f'Source: {d[\"summary\"][\"sources_used\"]}')
"
```

---

## 🎓 Key Concepts Demonstrated

1. **Audio metadata extraction** - Reading audio file properties
2. **Duration extraction** - Getting audio length
3. **Format info extraction** - Channels, sample rate, bit rate
4. **ID3 tag extraction** - Title, artist, album, etc.
5. **Binary file handling** - Reading audio files
6. **Medium confidence data** - Audio metadata reliability

---

## 💡 Tips

1. **MP3 files** contain ID3 tags with song info
2. **WAV files** contain basic audio properties but limited metadata
3. **M4A/AAC files** contain metadata but may require special handling
4. **Use phone recordings** for quick testing
5. **Audacity** is great for adding custom metadata

---

## ⚠️ Common Issues

### Issue: File not recognized as audio
**Symptom**: File type is "application/octet-stream"

**Solution**: Install `python-magic`: `pip install python-magic`

### Issue: Can't read audio metadata
**Symptom**: Audio metadata not extracted

**Solution**: Install audio libraries: `pip install pydub mutagen`

### Issue: Missing FFmpeg for pydub
**Symptom**: `Couldn't find ffmpeg` error

**Solution**: Install FFmpeg:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/
```

---

## 🔗 Related

- **Previous**: [Image with EXIF](exif_image.md)
- **Next**: [Video with Metadata](sample_video.md)
- **Full Specs**: [../../artifacts/specs.md](../../artifacts/specs.md)

---

**Audio files provide good testing for binary file handling. Even without ID3 tags, basic audio properties (duration, format) can be extracted.**
