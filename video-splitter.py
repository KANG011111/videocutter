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
import yt_dlp
import re
from urllib.parse import urlparse


def is_youtube_url(url):
    """Check if the given URL is a YouTube URL."""
    youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com', 'm.youtube.com']
    try:
        parsed = urlparse(url)
        return parsed.netloc in youtube_domains
    except:
        return False


def clean_filename(filename):
    """Clean filename to be filesystem safe."""
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'[\s]+', '_', filename)
    return filename


def download_youtube_video(url, output_dir=None):
    """Download video from YouTube using yt-dlp."""
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Find ffmpeg path
    ffmpeg_path = check_ffmpeg()
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': '137+140/136+140/135+140/best',  # Try 1080p, 720p, 480p with audio, fallback to best
        'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
        'noplaylist': True,
        'merge_output_format': 'mp4',  # Merge to mp4 format
    }
    
    # Set ffmpeg path if found
    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = ffmpeg_path
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            info = ydl.extract_info(url, download=False)
            title = info['title']
            clean_title = clean_filename(title)
            
            # Update output template with clean filename
            ydl_opts['outtmpl'] = str(output_dir / f'{clean_title}.%(ext)s')
            
            # Download with updated options
            with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                ydl2.download([url])
            
            # Find the downloaded file
            for ext in ['mp4', 'webm', 'mkv', 'avi']:
                downloaded_file = output_dir / f'{clean_title}.{ext}'
                if downloaded_file.exists():
                    return downloaded_file
            
            return None
            
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None


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


def create_organized_directories(video_path):
    """Create organized directory structure for video files."""
    video_stem = Path(video_path).stem
    parent_dir = Path(video_path).parent
    
    # Main directory named after the video
    main_dir = parent_dir / video_stem
    mp3_dir = main_dir / "MP3"
    mp4_dir = main_dir / "MP4"
    
    # Create all directories
    main_dir.mkdir(exist_ok=True)
    mp3_dir.mkdir(exist_ok=True)
    mp4_dir.mkdir(exist_ok=True)
    
    if main_dir.exists():
        print(f"Output directory: {main_dir}")
    
    return {
        'main': main_dir,
        'mp3': mp3_dir,
        'mp4': mp4_dir
    }


def split_video(video_path, directories, start_time, duration, part_num, ffmpeg_path):
    """Split video into segments with both video and audio output."""
    video_stem = Path(video_path).stem
    
    # Output file paths in organized directories
    video_output = directories['mp4'] / f"{video_stem}_part{part_num}.mp4"
    audio_output = directories['mp3'] / f"{video_stem}_part{part_num}.mp3"
    
    # Split video (with audio)
    video_cmd = [
        ffmpeg_path, '-i', str(video_path),
        '-ss', str(start_time),
        '-t', str(duration),
        '-c', 'copy',
        '-avoid_negative_ts', 'make_zero',
        str(video_output),
        '-y'
    ]
    
    # Extract audio
    audio_cmd = [
        ffmpeg_path, '-i', str(video_path),
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
        print(f"  ✓ MP4/{video_output.name}")
        
        # Extract audio
        subprocess.run(audio_cmd, capture_output=True, check=True)
        print(f"  ✓ MP3/{audio_output.name}")
        
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


def extract_full_audio(video_path, directories, ffmpeg_path):
    """Extract complete audio from video to organized structure."""
    video_path = Path(video_path)
    audio_output = directories['mp3'] / f"{video_path.stem}.mp3"
    
    audio_cmd = [
        ffmpeg_path, '-i', str(video_path),
        '-vn',  # No video
        '-acodec', 'mp3',
        '-ab', '320k',  # High quality audio
        str(audio_output),
        '-y'  # Overwrite if exists
    ]
    
    try:
        print(f"Extracting complete audio...")
        subprocess.run(audio_cmd, capture_output=True, check=True)
        print(f"  ✓ MP3/{audio_output.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        return False


def process_video_no_split(video_path, ffmpeg_path, audio_only=False):
    """Process video without splitting - just extract complete audio."""
    video_path = Path(video_path).resolve()
    
    if not video_path.exists():
        print(f"Error: Video file '{video_path}' not found.")
        return False
    
    print(f"Processing (no split): {video_path.name}")
    
    # Create organized directory structure
    directories = create_organized_directories(video_path)
    
    # Move original video to main directory
    original_video = directories['main'] / video_path.name
    if not original_video.exists():
        import shutil
        shutil.move(str(video_path), str(original_video))
        print(f"Moved original video to: {directories['main'].name}/")
    
    # Extract complete audio using the moved video
    success = extract_full_audio(original_video, directories, ffmpeg_path)
    if not success:
        return False
    
    print(f"\nCompleted! Audio extracted from {video_path.name}")
    return True


def process_video_with_split(video_path, ffmpeg_path, audio_only=False):
    """Process video with splitting into 30-minute segments."""
    video_path = Path(video_path).resolve()
    
    if not video_path.exists():
        print(f"Error: Video file '{video_path}' not found.")
        return False
    
    print(f"Processing (with split): {video_path.name}")
    
    # Create organized directory structure
    directories = create_organized_directories(video_path)
    
    # Move original video to main directory
    original_video = directories['main'] / video_path.name
    if not original_video.exists():
        import shutil
        shutil.move(str(video_path), str(original_video))
        print(f"Moved original video to: {directories['main'].name}/")
    
    # Always extract complete audio first
    print("Step 1: Extracting complete audio...")
    extract_success = extract_full_audio(original_video, directories, ffmpeg_path)
    if not extract_success:
        return False
    
    # Then split into segments
    print("Step 2: Creating 30-minute segments...")
    
    # Get video duration
    duration = get_video_duration(original_video, ffmpeg_path)
    if duration is None:
        print("Error: Could not get video duration.")
        return False
    
    duration_minutes = duration / 60
    print(f"Video duration: {duration_minutes:.1f} minutes")
    
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
        
        if audio_only:
            # Only create audio segments
            success = split_audio_only(original_video, directories, current_time, segment_time, part_num, ffmpeg_path)
        else:
            # Create both video and audio segments
            success = split_video(original_video, directories, current_time, segment_time, part_num, ffmpeg_path)
        
        if not success:
            return False
        
        current_time += segment_time
        part_num += 1
    
    print(f"\nCompleted! Original video + complete audio + {part_num - 1} segments in {directories['main']}")
    return True


def split_audio_only(video_path, directories, start_time, duration, part_num, ffmpeg_path):
    """Split audio only into segments."""
    video_stem = Path(video_path).stem
    
    # Output audio file path in MP3 directory
    audio_output = directories['mp3'] / f"{video_stem}_part{part_num}.mp3"
    
    # Extract audio segment
    audio_cmd = [
        ffmpeg_path, '-i', str(video_path),
        '-ss', str(start_time),
        '-t', str(duration),
        '-vn',  # No video
        '-acodec', 'mp3',
        '-ab', '320k',  # High quality audio
        str(audio_output),
        '-y'
    ]
    
    try:
        print(f"Creating audio part {part_num}...")
        subprocess.run(audio_cmd, capture_output=True, check=True)
        print(f"  ✓ MP3/{audio_output.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating audio part {part_num}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Split video into 30-minute segments with audio extraction"
    )
    parser.add_argument(
        "video_file",
        nargs='?',
        help="Input video file path"
    )
    parser.add_argument(
        "--youtube",
        help="YouTube URL to download and process"
    )
    parser.add_argument(
        "--no-split",
        action="store_true",
        help="Don't split video, just extract audio"
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Only output audio files (keep original video)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.video_file and not args.youtube:
        parser.error("Either provide a video file or use --youtube with a URL")
    
    if args.video_file and args.youtube:
        parser.error("Cannot use both video file and --youtube option")
    
    # Check if FFmpeg is available
    ffmpeg_path = check_ffmpeg()
    if not ffmpeg_path:
        print("Error: FFmpeg is not installed or not found in PATH.")
        print("Please install FFmpeg to use this tool.")
        sys.exit(1)
    
    print(f"Using FFmpeg: {ffmpeg_path}")
    
    # Handle YouTube URL
    if args.youtube:
        if not is_youtube_url(args.youtube):
            print("Error: Invalid YouTube URL")
            sys.exit(1)
        
        print(f"Downloading from YouTube: {args.youtube}")
        video_file = download_youtube_video(args.youtube)
        
        if not video_file:
            print("Error: Failed to download video")
            sys.exit(1)
        
        print(f"Downloaded: {video_file}")
    else:
        video_file = Path(args.video_file)
    
    # Process the video
    if args.no_split:
        success = process_video_no_split(video_file, ffmpeg_path, args.audio_only)
    else:
        success = process_video_with_split(video_file, ffmpeg_path, args.audio_only)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()