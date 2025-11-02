#!/usr/bin/env python3
"""
M4A Merger Tool
A command-line tool to merge multiple M4A files into one using FFmpeg.
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import re


def check_ffmpeg():
    """Check if FFmpeg is available on the system."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def natural_sort_key(text):
    """Natural sorting key for filenames like media1.m4a, media2.m4a, media10.m4a."""
    if isinstance(text, Path):
        text = text.name
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]


def find_m4a_files(directory):
    """Find all M4A files in the specified directory and sort them naturally."""
    directory_path = Path(directory)
    
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory '{directory}' does not exist")
    
    if not directory_path.is_dir():
        raise NotADirectoryError(f"'{directory}' is not a directory")
    
    m4a_files = list(directory_path.glob("*.m4a"))
    
    if not m4a_files:
        raise ValueError(f"No M4A files found in '{directory}'")
    
    # Sort files naturally (media1.m4a, media2.m4a, ..., media10.m4a, etc.)
    m4a_files.sort(key=natural_sort_key)
    
    return m4a_files


def create_file_list(m4a_files, temp_dir):
    """Create a temporary file list for FFmpeg concatenation."""
    file_list_path = Path(temp_dir) / "filelist.txt"
    
    with open(file_list_path, 'w') as f:
        for m4a_file in m4a_files:
            # Use absolute paths and escape single quotes
            abs_path = m4a_file.resolve()
            f.write(f"file '{abs_path}'\n")
    
    return file_list_path


def merge_m4a_files(m4a_files, output_file):
    """Merge M4A files using FFmpeg concatenation."""
    
    # Create temporary directory for file list
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create file list for FFmpeg
        file_list_path = create_file_list(m4a_files, temp_dir)
        
        # FFmpeg command for concatenation
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(file_list_path),
            '-c', 'copy',
            '-y',  # Overwrite output file if it exists
            str(output_file)
        ]
        
        print(f"Merging {len(m4a_files)} M4A files...")
        print(f"Output: {output_file}")
        
        try:
            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✓ Merge completed successfully!")
                return True
            else:
                print(f"✗ FFmpeg error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("✗ Merge timed out (5 minutes)")
            return False
        except Exception as e:
            print(f"✗ Error during merge: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Merge multiple M4A files into one using FFmpeg",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python m4a_merger.py --input basemedia/ --output merged.m4a
  python m4a_merger.py -i ./audio -o result.m4a
  
Note: If no directory is specified for output, files are saved to 'merged/' folder.
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Directory containing M4A files to merge'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output M4A file path'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information'
    )
    
    args = parser.parse_args()
    
    # Check FFmpeg availability
    if not check_ffmpeg():
        print("✗ FFmpeg is not installed or not in PATH")
        print("Please install FFmpeg: https://ffmpeg.org/download.html")
        sys.exit(1)
    
    try:
        # Find M4A files
        m4a_files = find_m4a_files(args.input)
        
        if args.verbose:
            print(f"Found {len(m4a_files)} M4A files:")
            for i, file in enumerate(m4a_files, 1):
                print(f"  {i}. {file.name}")
            print()
        
        # Validate output path - default to merged/ folder if no directory specified
        output_path = Path(args.output)
        if output_path.parent == Path('.'):
            output_path = Path('merged') / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Merge files
        success = merge_m4a_files(m4a_files, output_path)
        
        if success:
            print(f"✓ Merged file saved to: {output_path.resolve()}")
            sys.exit(0)
        else:
            print("✗ Merge failed")
            sys.exit(1)
            
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n✗ Merge cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()