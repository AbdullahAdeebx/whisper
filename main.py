#!/usr/bin/env python3
# Whisper Cloud CLI - Transcribe audio files using Groq-hosted Whisper
# Author: Abdullah Adeeb (AbdullahAdeeb.xyz)
import argparse
import os
import sys
import json
import requests
import pyperclip
from pathlib import Path
from dotenv import load_dotenv

__version__ = "1.0.0"
__author__ = "Abdullah Adeeb"
__website__ = "AbdullahAdeeb.xyz"

def parse_args():
    parser = argparse.ArgumentParser(description='Whisper Cloud CLI - Transcribe audio files using Groq-hosted Whisper')
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
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.m4a': 'audio/m4a',
        '.mp4': 'video/mp4',
        '.mpeg': 'video/mpeg',
        '.mpga': 'audio/mpeg',
        '.webm': 'video/webm',
        '.ogg': 'audio/ogg',
        '.oga': 'audio/ogg',
        '.flac': 'audio/flac'
    }
    return mime_types.get(extension, 'audio/mpeg')  # Default to audio/mpeg if unknown

def transcribe_audio(api_key, audio_file, model, language=None, task='transcribe', response_format='verbose_json'):
    print(f"Transcribing {audio_file}...")
    
    # Ensure the file exists
    if not Path(audio_file).exists():
        print(f"Error: File not found: {audio_file}")
        return None
    
    # Check if file is too large (Groq has a 25MB limit)
    file_size = Path(audio_file).stat().st_size / (1024 * 1024)  # Convert to MB
    if file_size > 25:
        print(f"Warning: File size ({file_size:.2f} MB) exceeds Groq's 25MB limit")
        print("The API may reject this file or fail to process it completely")
    
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
    mime_type = get_file_mimetype(audio_file)
    
    with open(audio_file, 'rb') as f:
        files = {
            'file': (Path(audio_file).name, f, mime_type)
        }
        
        # Make the API request
        try:
            print("Sending request to Groq API...")
            response = requests.post(api_url, headers=headers, data=data, files=files)
            
            if response.status_code == 200:
                print("Transcription successful!")
                if response_format == 'verbose_json' or response_format == 'json':
                    return response.json()
                else:
                    # For text, srt, vtt formats, return as dict with text field
                    return {"text": response.text}
            else:
                print(f"Error: API request failed with status code {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            if 'response' in locals():
                print(f"Response: {response.text}")
            return None

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
    attribution = f"\n\n---\nTranscribed with Whisper Cloud CLI by {__author__} | {__website__}"
    
    # Save plain text
    txt_path = output_dir / "transcript.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(plain_text + attribution)
    print(f"✓ Saved text transcript: {txt_path}")
    
    # Save JSON
    json_path = output_dir / "transcript.json"
    # Add attribution metadata to the JSON
    result["metadata"] = {
        "transcribed_with": "Whisper Cloud CLI",
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
    print("\n🎤 Whisper Cloud CLI - Transcribe audio using Groq API")
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
    except KeyboardInterrupt:
        print("\n\nTranscription cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 