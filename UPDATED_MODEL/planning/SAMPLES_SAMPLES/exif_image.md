---
format: html
---

# Image with EXIF Metadata

**Filename**: `exif_image.jpg` (or `.png`)  
**Type**: JPEG/PNG Image  
**Extraction Method**: EXIF metadata parsing  
**Expected Nodes**: 1  
**Expected Edges**: 0  
**Confidence**: High (when EXIF available)  
**Creation Difficulty**: ⭐ Easy

---

## 📋 Overview

Image files contain **EXIF metadata** that includes:
- Date and time photo was taken
- Camera make and model
- Camera settings (aperture, shutter speed, ISO)
- GPS coordinates (if available)
- Image orientation
- Dimensions

The extractor can read this metadata and create a knowledge graph node with the creation timestamp.

---

## 🎯 Creation Steps

### Option 1: Use Your Phone (EASIEST - 1 minute)

1. **Open your phone's camera app**
2. **Take a photo** (any subject)
3. **Transfer to computer**:
   - Email it to yourself
   - Use USB cable
   - Use cloud storage (Google Drive, iCloud, etc.)
4. **Rename** to `exif_image.jpg`
5. **Save** to `samples4/`

**Result**: Photo with full EXIF metadata including timestamp, camera info, GPS (if enabled).

### Option 2: Use Digital Camera

1. **Take a photo** with your digital camera
2. **Connect camera to computer** via USB
3. **Copy photo** to `samples4/exif_image.jpg`

### Option 3: Download Sample Image

```bash
# Download a sample image with EXIF
curl -o samples4/exif_image.jpg https://raw.githubusercontent.com/recurser/exif-samples/master/jpg/gps.jpg
```

This image has GPS coordinates and full EXIF data.

### Option 4: Use Online EXIF Editor

1. Go to https://exif.tools/
2. Upload any image (or use sample from site)
3. Edit EXIF data:
   - **DateTimeOriginal**: `2024-02-03T10:00:00Z`
   - **DateTimeDigitized**: `2024-02-03T10:00:00Z`
   - **Make**: `Test Camera`
   - **Model**: `Test Model`
   - **Artist**: `Test Photographer`
   - **Copyright**: `Test Image`
4. Download modified image
5. Save as `samples4/exif_image.jpg`

### Option 5: Create with Python (requires Pillow)

```bash
pip install Pillow

python << 'EOF'
from PIL import Image, ImageDraw
import datetime

# Create a simple image
img = Image.new('RGB', (800, 600), color='white')
draw = ImageDraw.Draw(img)

# Add some content
draw.text((100, 100), "EXIF Test Image", fill='black')
draw.text((100, 200), f"Created: {datetime.datetime.utcnow().isoformat()}Z", fill='black')

# Save with EXIF metadata
img.save("samples4/exif_image.jpg", 
         exif=b"\x00\x00\x00\x00\x00\x00")  # Basic EXIF

# For proper EXIF, we need a real image or use exif library
print("Image created. For full EXIF, use a real photo.")
EOF
```

**Note**: This creates an image but with limited EXIF. For best results, use a real photo from a camera or phone.

---

## 🔍 File Verification

```bash
# Check file exists
ls -la samples4/exif_image.jpg

# Check file type
file samples4/exif_image.jpg  # Should be: "JPEG image data" or "PNG image data"

# View EXIF metadata (requires exiftool or Pillow)
python -c "
from PIL import Image
from PIL.ExifTags import TAGS
img = Image.open('samples4/exif_image.jpg')
exif = img._getexif()
if exif:
    for tag, value in exif.items():
        print(f'{TAGS.get(tag, tag)}: {value}')
else:
    print('No EXIF data found. Use a real photo.')
"

# Or use exiftool
# sudo apt install libimage-exiftool-perl  # Ubuntu/Debian
# exiftool samples4/exif_image.jpg
```

---

## 🎯 Extraction Commands

### Basic Version
```bash
python extract.py samples4/exif_image.jpg --output results/exif_image.json
```

### Expected Output (Basic)
```json
{
  "extraction_metadata": {
    "file": "samples4/exif_image.jpg",
    "timestamp": "2026-10-05T16:10:00Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": 2048000,
      "created_time": "2026-10-05T16:05:00Z",
      "modified_time": "2026-10-05T16:05:00Z",
      "accessed_time": "2026-10-05T16:10:00Z"
    },
    "file_type": "image/jpeg"
  },
  "version_history": {
    "edits": [
      {
        "node_id": "fs_exif_image.jpg",
        "node_type": "edit",
        "timestamp": "2026-10-05T16:05:00Z",
        "author": null,
        "edit_type": "create",
        "content_after": "[Binary file: exif_image.jpg]",
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

### Full Version (with Pillow)
```bash
pip install Pillow

# Then run with full extract.py
python extract.py samples4/exif_image.jpg --output results/exif_image_full.json
```

### Expected Output (Full)
```json
{
  "extraction_metadata": {
    "file": "samples4/exif_image.jpg",
    "timestamp": "2026-10-05T16:15:00Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": 2048000,
      "created_time": "2026-10-05T16:05:00Z",
      "modified_time": "2026-10-05T16:05:00Z",
      "accessed_time": "2026-10-05T16:10:00Z"
    },
    "file_type": "image/jpeg",
    "image_pillow": {
      "format": "JPEG",
      "mode": "RGB",
      "size": {"width": 4032, "height": 3024},
      "bits": 8
    },
    "exif": {
      "parsed": {
        "datetime": "2024:02:03 10:00:00",
        "datetime_original": "2024:02:03 10:00:00",
        "datetime_digitized": "2024:02:03 10:00:00",
        "make": "Test Camera",
        "model": "Test Model",
        "artist": "Test Photographer"
      }
    }
  },
  "version_history": {
    "edits": [
      {
        "node_id": "exif_20240203T100000Z",
        "node_type": "edit",
        "timestamp": "2024-02-03T10:00:00Z",
        "author": null,
        "edit_type": "create",
        "description": "Image created (from EXIF DateTimeOriginal)",
        "source": "exif",
        "evaluation_band": "high"
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
    "sources_used": ["exif"],
    "confidence_distribution": {"high": 1}
  }
}
```

---

## 📊 Validation Commands

```bash
# Check if EXIF was extracted
python -c "
import json
d = json.load(open('results/exif_image.json'))
if 'exif' in d['file_metadata']:
    print('✅ EXIF metadata extracted')
    print(f'DateTime: {d[\"file_metadata\"][\"exif\"][\"parsed\"].get(\"datetime\", \"N/A\")}')
else:
    print('❌ EXIF metadata NOT extracted')
"

# Check knowledge graph
python -c "
import json
d = json.load(open('results/exif_image.json'))
kg = d['knowledge_graph']
print(f'Nodes: {kg[\"total_nodes\"]}')
print(f'Edges: {kg[\"total_edges\"]}')
print(f'Source: {d[\"summary\"][\"sources_used\"]}')
"
```

---

## 🎓 Key Concepts Demonstrated

1. **Image metadata extraction** - Reading EXIF from JPEG/PNG
2. **Timestamp extraction** - Getting creation date from EXIF
3. **Camera info extraction** - Getting make/model/artist
4. **Binary file handling** - Reading image files
5. **High confidence data** - EXIF timestamps are very reliable
6. **Knowledge graph node** - Single node for image creation

---

## 💡 Tips

1. **Use a real photo** from a camera or phone for best results
2. **Check EXIF before extraction** using `exiftool` or Python
3. **Phones usually include** DateTimeOriginal, Make, Model
4. **DSLR cameras include** aperture, shutter speed, ISO, GPS
5. **If no EXIF**, the script falls back to filesystem metadata

---

## 📚 Technical Details

### EXIF Date Format

EXIF stores dates in format: `YYYY:MM:DD HH:MM:SS`

The script converts this to ISO format: `YYYY-MM-DDTHH:MM:SSZ`

### Common EXIF Tags

| Tag | Description | Example |
|-----|-------------|---------|
| DateTimeOriginal | When photo was taken | 2024:02:03 10:00:00 |
| DateTimeDigitized | When digital image was created | 2024:02:03 10:00:00 |
| DateTime | Generic timestamp | 2024:02:03 10:00:00 |
| Make | Camera manufacturer | Apple |
| Model | Camera model | iPhone 13 |
| Artist | Photographer | John Doe |
| Copyright | Copyright info | © 2024 John Doe |
| Orientation | Image orientation | 1 (normal) |
| GPSInfo | GPS coordinates | (latitude, longitude) |

---

## ⚠️ Common Issues

### Issue: No EXIF data
**Symptom**: EXIF section is empty or not present

**Solution**: Use a real photo from a camera or phone. Many web images have EXIF stripped.

### Issue: Wrong date format
**Symptom**: Date appears as "2024:02:03 10:00:00" instead of "2024-02-03T10:00:00Z"

**Solution**: The date parsing needs to be fixed in the extraction script.

### Issue: Image not detected
**Symptom**: File type is "application/octet-stream" instead of "image/jpeg"

**Solution**: Install `python-magic` library: `pip install python-magic`

---

## 🔗 Related

- **Previous**: [PDF with Metadata](metadata_pdf.md)
- **Next**: [Audio with ID3 Tags](sample_audio.md)
- **Full Specs**: [../../artifacts/specs.md](../../artifacts/specs.md)

---

**Image files provide excellent EXIF timestamp data. Even smartphone photos contain enough metadata for testing.**
