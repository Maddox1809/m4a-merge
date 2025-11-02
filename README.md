# M4A Merger Tool

Merge multiple M4A files into one using FFmpeg.

## Requirements
- FFmpeg must be installed: https://ffmpeg.org/download.html

## Usage
```bash
python3 m4a_merger.py --input <folder> --output <filename>
```

## Examples
```bash
# Merge files from basemedia/ folder
python3 m4a_merger.py --input basemedia/ --output merged.m4a

# With verbose output
python3 m4a_merger.py -i basemedia/ -o result.m4a --verbose
```

## Features
- Natural file sorting (media1.m4a, media2.m4a, ..., media10.m4a)
- Automatic output to `merged/` folder
- High-quality concatenation without re-encoding
- Cross-platform support