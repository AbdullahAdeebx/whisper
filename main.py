#!/usr/bin/env python3
# Whisper - Transcribe audio files using Groq-hosted Whisper
# Author: Abdullah Adeeb (AbdullahAdeeb.xyz)
import argparse
import os
import sys
import json
import requests
import pyperclip
import tempfile
import subprocess
import time
import gc
from pathlib import Path
from dotenv import load_dotenv

__version__ = "1.0.0"
__author__ = "Abdullah Adeeb"
__website__ = "AbdullahAdeeb.xyz"

def parse_args():
    parser = argparse.ArgumentParser(description='whisper - Transcribe audio files using Groq-hosted Whisper')
    parser.add_argument('audio_file', nargs='*', help='Path to audio file(s) to transcribe')
    parser.add_argument('--model', default='whisper-large-v3-turbo', help='Whisper model to use')
    parser.add_argument('--language', help='Language code (optional)')
    parser.add_argument('--task', default='transcribe', choices=['transcribe', 'translate'], help='Task: transcribe or translate')
    parser.add_argument('--output-dir', help='Output directory (defaults to audio_filename_transcription)')
    parser.add_argument('--response-format', default='verbose_json', choices=['verbose_json', 'json', 'text', 'srt', 'vtt'], help='API response format')
    parser.add_argument('--version', action='store_true', help='Show version information and exit')
    return parser.parse_args()

def get_api_key():
    # Try to load from .env.local first
    load_dotenv('.env.local')
    api_key = os.getenv('GROQ_API_KEY')
    
    # If not found, try to load from environment directly
    if not api_key:
        api_key = os.getenv('GROQ_API_KEY')
    
    # If still not found, check for .env file
    if not api_key:
        if Path('.env').exists():
            load_dotenv('.env')
            api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("Error: GROQ_API_KEY not found in .env.local file or environment variables")
        print("Please create a .env.local file with your GROQ_API_KEY or set it as an environment variable")
        sys.exit(1)
    
    return api_key

def create_output_directory(audio_file, output_dir=None):
    if output_dir:
        directory = Path(output_dir)
    else:
        base_name = Path(audio_file).stem
        directory = Path(f"{base_name}_transcription")
    
    directory.mkdir(exist_ok=True)
    return directory

def get_file_mimetype(file_path):
    """Determine the MIME type based on file extension"""
    extension = Path(file_path).suffix.lower()
    mime_types = {
        # Audio formats
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.m4a': 'audio/m4a',
        '.mpga': 'audio/mpeg',
        '.ogg': 'audio/ogg',
        '.oga': 'audio/ogg',
        '.flac': 'audio/flac',
        '.aac': 'audio/aac',
        '.wma': 'audio/x-ms-wma',
        
        # Video formats
        '.mp4': 'video/mp4',
        '.mpeg': 'video/mpeg',
        '.mpg': 'video/mpeg',
        '.webm': 'video/webm',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.wmv': 'video/x-ms-wmv',
        '.flv': 'video/x-flv',
        '.mkv': 'video/x-matroska',
        '.ts': 'video/mp2t',
        '.3gp': 'video/3gpp'
    }
    
    # Default to audio/mpeg if unknown for transcription services
    if extension not in mime_types:
        print(f"Warning: Unknown file extension '{extension}'. Using default MIME type.")
    
    return mime_types.get(extension, 'audio/mpeg')

def is_video_file(file_path):
    """Check if the file is a video based on its extension"""
    video_extensions = [
        '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', 
        '.wmv', '.mpeg', '.mpg', '.m4v', '.3gp', '.ts'
    ]
    
    extension = Path(file_path).suffix.lower()
    is_video = extension in video_extensions
    
    # If we have ffprobe available, use it to more accurately detect video files
    try:
        # Try to get file info using ffprobe
        result = subprocess.run(
            [
                'ffprobe', 
                '-v', 'error', 
                '-select_streams', 'v:0', 
                '-show_entries', 'stream=codec_type', 
                '-of', 'csv=p=0', 
                file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        
        # If ffprobe detects a video stream, it will output "video"
        if "video" in result.stdout.strip().lower():
            return True
        
    except (subprocess.SubprocessError, FileNotFoundError):
        # If ffprobe fails or isn't installed, fall back to extension check
        pass
    
    return is_video

def convert_video_to_audio(video_path):
    """Convert video to audio using ffmpeg and return the path to the temporary audio file"""
    print(f"Detected video file: {video_path}. Converting to audio...")
    print("This may take a few moments depending on the file size...")
    
    # Create a temporary file with .mp3 extension
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
    temp_file.close()
    temp_audio_path = temp_file.name
    
    try:
        # Use ffmpeg to convert video to audio, with progress output
        command = [
            'ffmpeg',
            '-y',  # Overwrite output files without asking
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'libmp3lame',  # Use MP3 codec
            '-q:a', '4',  # Quality setting
            '-hide_banner',  # Hide ffmpeg compilation details
            '-loglevel', 'warning',  # Show only warnings and errors
            temp_audio_path
        ]
        
        # Check if ffmpeg is available
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Error: FFmpeg is not installed or not available in PATH")
            print("Please install FFmpeg: https://ffmpeg.org/download.html")
            return None
        
        # Run the ffmpeg command with a timeout
        print("Converting video to audio (this might take a while for large files)...")
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300,  # 5 minute timeout
            check=False  # Don't raise exception on non-zero exit
        )
        
        # Check if the conversion was successful
        if process.returncode != 0:
            print(f"Error converting video to audio. FFmpeg return code: {process.returncode}")
            print(f"Error message: {process.stderr}")
            
            # Clean up the temporary file
            safely_remove_temp_file(temp_audio_path)
            
            # Try an alternative command with different settings
            print("Trying alternative conversion method...")
            alt_command = [
                'ffmpeg',
                '-y',
                '-i', video_path,
                '-vn',
                '-ar', '44100',  # Audio sample rate
                '-ac', '2',  # Audio channels (stereo)
                '-b:a', '192k',  # Audio bitrate
                temp_audio_path
            ]
            
            try:
                alt_process = subprocess.run(
                    alt_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=300,
                    check=False
                )
                
                if alt_process.returncode != 0:
                    print(f"Alternative conversion also failed: {alt_process.stderr}")
                    safely_remove_temp_file(temp_audio_path)
                    return None
            except Exception as e:
                print(f"Alternative conversion also failed: {e}")
                safely_remove_temp_file(temp_audio_path)
                return None
        
        # Check if the audio file was created and has content
        if not os.path.exists(temp_audio_path) or os.path.getsize(temp_audio_path) == 0:
            print("Error: FFmpeg did not produce an output file or the file is empty")
            safely_remove_temp_file(temp_audio_path)
            return None
            
        print(f"Successfully converted video to audio: {temp_audio_path}")
        return temp_audio_path
    
    except subprocess.TimeoutExpired:
        print("Error: FFmpeg process timed out after 5 minutes")
        print("The video file may be too large or in an unsupported format")
        
        # Clean up the temporary file if there was an error
        safely_remove_temp_file(temp_audio_path)
        
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error converting video to audio: {e}")
        print(f"FFMPEG Error output: {e.stderr}")
        
        # Clean up the temporary file if there was an error
        safely_remove_temp_file(temp_audio_path)
        
        return None
    except Exception as e:
        print(f"An unexpected error occurred during conversion: {e}")
        
        # Clean up the temporary file if there was an error
        safely_remove_temp_file(temp_audio_path)
        
        return None

def extract_audio_direct(video_path):
    """
    Directly extract audio from video without re-encoding.
    This is faster but may not work with all video formats.
    """
    print("Attempting direct audio extraction (faster method)...")
    
    # Create a temporary file with .mp3 extension instead of .aac to ensure Groq API compatibility
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
    temp_file.close()
    temp_audio_path = temp_file.name
    
    try:
        # Extract audio stream with re-encoding to MP3
        command = [
            'ffmpeg',
            '-y',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'libmp3lame',  # Use MP3 codec instead of copying
            '-q:a', '4',  # Quality setting
            '-hide_banner',
            '-loglevel', 'warning',
            temp_audio_path
        ]
        
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,  # Shorter timeout as this should be quick
            check=False
        )
        
        if process.returncode != 0:
            print("Direct extraction failed, will try conversion instead.")
            safely_remove_temp_file(temp_audio_path)
            return None
            
        # Check if the audio file was created and has content
        if not os.path.exists(temp_audio_path) or os.path.getsize(temp_audio_path) == 0:
            print("Direct extraction produced empty file, will try conversion instead.")
            safely_remove_temp_file(temp_audio_path)
            return None
            
        print(f"Successfully extracted audio: {temp_audio_path}")
        return temp_audio_path
        
    except Exception as e:
        print(f"Direct extraction error: {e}")
        safely_remove_temp_file(temp_audio_path)
        return None

def normalize_path(path):
    """Normalize file path to handle spaces and special characters."""
    # Convert to absolute path
    abs_path = os.path.abspath(path)
    
    # Handle Windows paths correctly
    if os.name == 'nt':
        # Remove any surrounding quotes already present
        abs_path = abs_path.strip('"\'')
        
    return abs_path

def process_webm_file(video_path):
    """Special processing for webm files which can be problematic"""
    print("Detected WebM file - attempting specialized processing...")
    
    # Create a temporary file with .mp3 extension
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
    temp_file.close()
    temp_audio_path = temp_file.name
    wav_audio_path = temp_audio_path.replace('.mp3', '.wav')
    
    try:
        # Try a different approach specifically for WebM files
        command = [
            'ffmpeg',
            '-y',
            '-i', video_path,
            '-vn',
            '-ab', '192k',
            '-ar', '44100',
            '-f', 'mp3',
            temp_audio_path
        ]
        
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300,
            check=False
        )
        
        if process.returncode != 0:
            print(f"WebM processing failed: {process.stderr}")
            
            # Try an even more aggressive approach
            print("Trying alternative WebM processing method...")
            alt_command = [
                'ffmpeg',
                '-y',
                '-i', video_path,
                '-acodec', 'pcm_s16le',
                '-f', 'wav',
                temp_audio_path.replace('.mp3', '.wav')
            ]
            
            alt_process = subprocess.run(
                alt_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300,
                check=False
            )
            
            if alt_process.returncode == 0:
                # If wav worked, use the wav file instead
                temp_audio_path = wav_audio_path
            else:
                print(f"Alternative WebM processing also failed: {alt_process.stderr}")
                safely_remove_temp_file(temp_audio_path)
                safely_remove_temp_file(wav_audio_path)
                return None
        
        if not os.path.exists(temp_audio_path) or os.path.getsize(temp_audio_path) == 0:
            if os.path.exists(wav_audio_path) and os.path.getsize(wav_audio_path) > 0:
                temp_audio_path = wav_audio_path
            else:
                print("WebM processing failed to produce a valid output file")
                safely_remove_temp_file(temp_audio_path)
                safely_remove_temp_file(wav_audio_path)
                return None
        
        print(f"Successfully processed WebM file: {temp_audio_path}")
        return temp_audio_path
        
    except Exception as e:
        print(f"WebM processing error: {e}")
        
        # Clean up temporary files
        safely_remove_temp_file(temp_audio_path)
        safely_remove_temp_file(wav_audio_path)
            
        return None

def transcribe_audio(api_key, audio_file, model, language=None, task='transcribe', response_format='verbose_json'):
    print(f"Transcribing {audio_file}...")
    
    # Normalize the path to handle spaces and special characters
    audio_file = normalize_path(audio_file)
    
    # Ensure the file exists
    if not Path(audio_file).exists():
        print(f"Error: File not found: {audio_file}")
        return None
    
    # Check if the file is a video and convert if necessary
    temp_audio_file = None
    file_to_transcribe = audio_file
    
    if is_video_file(audio_file):
        # Check if it's a webm file which needs special handling
        if audio_file.lower().endswith('.webm'):
            temp_audio_file = process_webm_file(audio_file)
        else:
            # First try direct extraction (faster)
            temp_audio_file = extract_audio_direct(audio_file)
            
            # If that fails, try full conversion
            if not temp_audio_file:
                temp_audio_file = convert_video_to_audio(audio_file)
                
        if temp_audio_file:
            file_to_transcribe = temp_audio_file
        else:
            print("All conversion methods failed. Attempting to transcribe original file...")
    
    # Check if file is too large (Groq has a 25MB limit)
    file_size = Path(file_to_transcribe).stat().st_size / (1024 * 1024)  # Convert to MB
    if file_size > 25:
        print(f"Warning: File size ({file_size:.2f} MB) exceeds Groq's 25MB limit")
        print("The API may reject this file or fail to process it completely")
    
    # Check for unsupported file types
    supported_extensions = ['.flac', '.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.ogg', '.opus', '.wav', '.webm']
    file_ext = Path(file_to_transcribe).suffix.lower()
    if file_ext not in supported_extensions:
        print(f"Warning: File extension '{file_ext}' may not be supported by the Groq API")
        print(f"Supported formats are: {', '.join(supported_extensions)}")
        print("The API may reject this file")
    
    # Prepare the API endpoint
    api_url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Prepare the form data
    data = {
        "model": model,
        "response_format": response_format
    }
    
    # Add language if specified
    if language:
        data["language"] = language
    
    # The task parameter is not supported by Groq's API, so we'll use the appropriate endpoint
    if task == 'translate':
        api_url = "https://api.groq.com/openai/v1/audio/translations"
    
    # Prepare the file for upload
    mime_type = get_file_mimetype(file_to_transcribe)
    
    result = None
    f = None
    
    try:
        f = open(file_to_transcribe, 'rb')
        files = {
            'file': (Path(file_to_transcribe).name, f, mime_type)
        }
        
        # Make the API request
        print("Sending request to Groq API...")
        response = requests.post(api_url, headers=headers, data=data, files=files)
        
        if response.status_code == 200:
            print("Transcription successful!")
            if response_format == 'verbose_json' or response_format == 'json':
                result = response.json()
            else:
                # For text, srt, vtt formats, return as dict with text field
                result = {"text": response.text}
        else:
            print(f"Error: API request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Make sure to close the file handle
        if f:
            f.close()
        
        # Force garbage collection to release any lingering file handles
        gc.collect()
        
        # Add a small delay to ensure file handles are fully released
        time.sleep(0.5)
        
        # Try to safely remove the temporary file
        safely_remove_temp_file(temp_audio_file)
    
    return result

def safely_remove_temp_file(file_path):
    """Safely remove a temporary file with retries"""
    if not file_path or not os.path.exists(file_path):
        return
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            os.unlink(file_path)
            return
        except PermissionError:
            if attempt < max_attempts - 1:
                # Wait a bit and retry
                print(f"File still in use, waiting to retry cleanup... ({attempt+1}/{max_attempts})")
                time.sleep(1)
                gc.collect()  # Force garbage collection
            else:
                print(f"Warning: Could not remove temporary file {file_path}")
                print("The file will remain in your temp directory")
        except Exception as e:
            print(f"Warning: Error removing temporary file: {e}")
            break

def format_srt(segments):
    srt_content = ""
    for i, segment in enumerate(segments):
        start_time = format_timestamp_srt(segment["start"])
        end_time = format_timestamp_srt(segment["end"])
        srt_content += f"{i+1}\n{start_time} --> {end_time}\n{segment['text']}\n\n"
    return srt_content

def format_vtt(segments):
    vtt_content = "WEBVTT\n\n"
    for i, segment in enumerate(segments):
        start_time = format_timestamp_vtt(segment["start"])
        end_time = format_timestamp_vtt(segment["end"])
        vtt_content += f"{start_time} --> {end_time}\n{segment['text']}\n\n"
    return vtt_content

def format_tsv(segments):
    tsv_content = "start\tend\ttext\n"
    for segment in segments:
        tsv_content += f"{segment['start']}\t{segment['end']}\t{segment['text']}\n"
    return tsv_content

def format_timestamp_srt(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"

def format_timestamp_vtt(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d}.{milliseconds:03d}"

def save_transcription_files(result, output_dir):
    if "text" not in result:
        print("Error: Transcription result does not contain 'text' field")
        return
    
    plain_text = result["text"]
    attribution = f"\n\n---\nTranscribed with whisper by {__author__} | {__website__}"
    
    # Save plain text
    txt_path = output_dir / "transcript.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(plain_text + attribution)
    print(f"✓ Saved text transcript: {txt_path}")
    
    # Save JSON
    json_path = output_dir / "transcript.json"
    # Add attribution metadata to the JSON
    result["metadata"] = {
        "transcribed_with": "whisper",
        "author": __author__,
        "website": __website__,
        "version": __version__
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved JSON transcript: {json_path}")
    
    # If segments are available, create the other formats
    if "segments" in result:
        segments = result["segments"]
        
        # Save SRT
        srt_path = output_dir / "transcript.srt"
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(format_srt(segments))
        print(f"✓ Saved SRT transcript: {srt_path}")
        
        # Save VTT
        vtt_path = output_dir / "transcript.vtt"
        with open(vtt_path, "w", encoding="utf-8") as f:
            f.write(format_vtt(segments))
        print(f"✓ Saved VTT transcript: {vtt_path}")
        
        # Save TSV
        tsv_path = output_dir / "transcript.tsv"
        with open(tsv_path, "w", encoding="utf-8") as f:
            f.write(format_tsv(segments))
        print(f"✓ Saved TSV transcript: {tsv_path}")
    
    return plain_text

def copy_to_clipboard(text):
    try:
        pyperclip.copy(text)
        print("✓ Transcript copied to clipboard!")
    except Exception as e:
        print(f"Could not copy to clipboard: {e}")
        print("Please manually copy the text from the transcript.txt file")

def main():
    # Print a welcome message
    print("\n🎤 whisper - Transcribe audio using Groq API")
    print("====================================================")
    
    # Different terminal types support different link formats
    if os.environ.get('TERM_PROGRAM') == 'iTerm.app':
        # iTerm2 hyperlink format
        url = __website__
        print(f"  By {__author__} | \033]8;;https://{url}\033\\{url}\033]8;;\033\\")
    elif "WT_SESSION" in os.environ or "WINDOWS_TERMINAL" in os.environ:
        # Windows Terminal may support ANSI hyperlinks
        url = __website__
        print(f"  By {__author__} | \033]8;;https://{url}\033\\{url}\033]8;;\033\\")
    else:
        # Standard terminals - not clickable but clearly marked as a URL
        print(f"  By {__author__} | https://{__website__}")
    
    print()
    
    temp_files = []  # Track any temporary files created
    
    try:
        args = parse_args()
        
        # Handle --version flag
        if args.version:
            print(f"Version: {__version__}")
            print(f"Author: {__author__}")
            
            # Different terminal types support different link formats
            if os.environ.get('TERM_PROGRAM') == 'iTerm.app' or "WT_SESSION" in os.environ:
                # Supported terminals - clickable link
                print(f"Website: \033]8;;https://{__website__}\033\\{__website__}\033]8;;\033\\")
            else:
                # Standard terminals - not clickable
                print(f"Website: https://{__website__}")
            
            sys.exit(0)
        
        # Check if audio file is provided
        if not args.audio_file:
            print("Error: No audio file provided")
            print("Use --help for usage information")
            sys.exit(1)
            
        api_key = get_api_key()
        
        for audio_file in args.audio_file:
            # Normalize paths to handle spaces and quotes in filenames
            audio_file = normalize_path(audio_file)
            
            output_dir = create_output_directory(audio_file, args.output_dir)
            
            result = transcribe_audio(
                api_key=api_key,
                audio_file=audio_file,
                model=args.model,
                language=args.language,
                task=args.task,
                response_format=args.response_format
            )
            
            if result:
                print("\n📝 TRANSCRIPT:\n")
                
                if "text" in result:
                    print(result["text"])
                    print("\n" + "=" * 50 + "\n")
                    
                    plain_text = save_transcription_files(result, output_dir)
                    if plain_text:
                        copy_to_clipboard(plain_text)
                else:
                    print("No transcript returned from API")
            
            # Pause briefly before next file to ensure resources are freed
            time.sleep(1)
            gc.collect()
    except KeyboardInterrupt:
        print("\n\nTranscription cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Final cleanup of any leftover temporary files in the temp directory
        try:
            # Look for our temporary files pattern in the temp directory
            temp_dir = tempfile.gettempdir()
            current_time = time.time()
            one_hour_ago = current_time - 3600  # 1 hour in seconds
            
            # Find any temp files created by this script that might have been left behind
            for temp_file in os.listdir(temp_dir):
                try:
                    if temp_file.startswith('tmp') and (temp_file.endswith('.mp3') or 
                                                    temp_file.endswith('.wav') or 
                                                    temp_file.endswith('.aac')):
                        file_path = os.path.join(temp_dir, temp_file)
                        # Only remove files older than 1 hour to avoid conflicts with running processes
                        if os.path.isfile(file_path) and os.path.getmtime(file_path) < one_hour_ago:
                            safely_remove_temp_file(file_path)
                except Exception:
                    # Ignore errors in cleanup - it's just a best effort
                    pass
        except Exception:
            # Ignore any errors in the final cleanup
            pass

if __name__ == "__main__":
    main() 