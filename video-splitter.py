#!/usr/bin/env python3
"""
Video Splitter Tool
Splits long videos into 30-minute segments and extracts audio files.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse


def check_ffmpeg():
    """Check if FFmpeg is available in the system."""
    # Try different possible locations for ffmpeg
    ffmpeg_paths = [
        'ffmpeg',
        '/usr/local/bin/ffmpeg',
        os.path.expanduser('~/bin/ffmpeg')
    ]
    
    for ffmpeg_path in ffmpeg_paths:
        try:
            subprocess.run([ffmpeg_path, '-version'], capture_output=True, check=True)
            return ffmpeg_path
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    return None


def get_video_duration(video_path, ffmpeg_path):
    """Get video duration in seconds using FFmpeg."""
    try:
        # Use FFmpeg to get duration info
        cmd = [
            ffmpeg_path, '-i', video_path, '-f', 'null', '-'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse duration from FFmpeg output
        output = result.stderr
        duration_line = None
        for line in output.split('\n'):
            if 'Duration:' in line:
                duration_line = line
                break
        
        if duration_line:
            # Extract duration in format HH:MM:SS.ss
            import re
            duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})', duration_line)
            if duration_match:
                hours = int(duration_match.group(1))
                minutes = int(duration_match.group(2))
                seconds = int(duration_match.group(3))
                centiseconds = int(duration_match.group(4))
                
                total_seconds = hours * 3600 + minutes * 60 + seconds + centiseconds / 100
                return total_seconds
        
        return None
    except (subprocess.CalledProcessError, ValueError):
        return None


def create_output_directory(video_path):
    """Create output directory for split files."""
    video_stem = Path(video_path).stem
    output_dir = Path(video_path).parent / f"{video_stem}_parts"
    
    if output_dir.exists():
        print(f"Warning: Directory {output_dir} already exists. Files may be overwritten.")
    else:
        output_dir.mkdir(exist_ok=True)
    
    return output_dir


def split_video(video_path, output_dir, start_time, duration, part_num, ffmpeg_path):
    """Split video into segments with both video and audio output."""
    video_stem = Path(video_path).stem
    
    # Output file paths
    video_output = output_dir / f"{video_stem}_part{part_num}.mp4"
    audio_output = output_dir / f"{video_stem}_part{part_num}.mp3"
    
    # Split video (with audio)
    video_cmd = [
        ffmpeg_path, '-i', video_path,
        '-ss', str(start_time),
        '-t', str(duration),
        '-c', 'copy',
        '-avoid_negative_ts', 'make_zero',
        str(video_output),
        '-y'
    ]
    
    # Extract audio
    audio_cmd = [
        ffmpeg_path, '-i', video_path,
        '-ss', str(start_time),
        '-t', str(duration),
        '-vn',  # No video
        '-acodec', 'mp3',
        '-ab', '320k',  # High quality audio
        str(audio_output),
        '-y'
    ]
    
    try:
        print(f"Creating part {part_num}...")
        
        # Create video segment
        subprocess.run(video_cmd, capture_output=True, check=True)
        print(f"  ✓ {video_output.name}")
        
        # Extract audio
        subprocess.run(audio_cmd, capture_output=True, check=True)
        print(f"  ✓ {audio_output.name}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating part {part_num}: {e}")
        return False


def process_video(video_path, ffmpeg_path):
    """Main function to process and split video."""
    video_path = Path(video_path).resolve()
    
    if not video_path.exists():
        print(f"Error: Video file '{video_path}' not found.")
        return False
    
    print(f"Processing: {video_path.name}")
    
    # Get video duration
    duration = get_video_duration(video_path, ffmpeg_path)
    if duration is None:
        print("Error: Could not get video duration.")
        return False
    
    duration_minutes = duration / 60
    print(f"Video duration: {duration_minutes:.1f} minutes")
    
    # Create output directory
    output_dir = create_output_directory(video_path)
    print(f"Output directory: {output_dir}")
    
    # Calculate segments
    segment_duration = 30 * 60  # 30 minutes in seconds
    current_time = 0
    part_num = 1
    
    while current_time < duration:
        remaining_time = duration - current_time
        
        if remaining_time <= segment_duration:
            # Last segment - use all remaining time
            segment_time = remaining_time
        else:
            # Regular 30-minute segment
            segment_time = segment_duration
        
        success = split_video(video_path, output_dir, current_time, segment_time, part_num, ffmpeg_path)
        if not success:
            return False
        
        current_time += segment_time
        part_num += 1
    
    print(f"\nCompleted! Generated {part_num - 1} segments in {output_dir}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Split video into 30-minute segments with audio extraction"
    )
    parser.add_argument(
        "video_file",
        help="Input video file path"
    )
    
    args = parser.parse_args()
    
    # Check if FFmpeg is available
    ffmpeg_path = check_ffmpeg()
    if not ffmpeg_path:
        print("Error: FFmpeg is not installed or not found in PATH.")
        print("Please install FFmpeg to use this tool.")
        sys.exit(1)
    
    print(f"Using FFmpeg: {ffmpeg_path}")
    
    # Process the video
    success = process_video(args.video_file, ffmpeg_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()