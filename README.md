# Whisper Cloud CLI

A command-line tool to transcribe audio and video files using OpenAI's Whisper model via the Groq API.

## Author

**Abdullah Adeeb**  
Website: [AbdullahAdeeb.xyz](https://AbdullahAdeeb.xyz)

## Description

Whisper Cloud CLI is a command-line tool that allows you to transcribe audio and video files using OpenAI's Whisper model hosted on Groq's platform. The tool supports various audio and video formats and can generate transcripts in multiple formats including plain text, SRT, VTT, and TSV.

## Features

- Transcribe audio and video files using Whisper Large v3 Turbo model
- Automatic conversion of video to audio
- Support for various audio formats (MP3, WAV, M4A, WEBM, OGG, FLAC)
- Support for various video formats (MP4, AVI, MOV, MKV, WEBM, FLV, WMV, MPEG)
- Generate transcripts in multiple formats (TXT, JSON, SRT, VTT, TSV)
- Automatically copy transcript to clipboard
- Customizable output directory
- Support for both transcription and translation tasks

## Installation

### Prerequisites

- Groq API key

### Install using binaries

#### Linux

```bash
# Install FFmpeg (required for video file support)
sudo apt update
sudo apt install ffmpeg

# Download binary
sudo curl -L https://github.com/AbdullahAdeebx/whisper-cloud-cli/raw/main/binary/linux/whisper -o /usr/local/bin/whisper

# Make it executable
sudo chmod +x /usr/local/bin/whisper

# Ensure /usr/local/bin is in PATH (usually is)
if ! echo $PATH | grep -q "/usr/local/bin"; then
  echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
fi
```

#### macOS

```bash
# Install FFmpeg (required for video file support)
brew install ffmpeg

# Download binary
sudo curl -L https://github.com/AbdullahAdeebx/whisper-cloud-cli/raw/main/binary/macos/whisper -o /usr/local/bin/whisper

# Make it executable
sudo chmod +x /usr/local/bin/whisper

# Ensure it's in PATH (zsh default)
if ! echo $PATH | grep -q "/usr/local/bin"; then
  echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
fi
```

#### Windows (PowerShell)

```powershell
# Install FFmpeg (required for video file support)
winget install FFmpeg

# Download binary
Invoke-WebRequest -Uri https://github.com/AbdullahAdeebx/whisper-cloud-cli/raw/main/binary/windows/whisper.exe -OutFile "$env:ProgramFiles\whisper.exe"

# Add to PATH permanently
$path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
if ($path -notlike "*$env:ProgramFiles*") {
    [System.Environment]::SetEnvironmentVariable("Path", "$path;$env:ProgramFiles", "Machine")
}
```

## Configuration

Set Groq API key as an environment variable:

```bash
export GROQ_API_KEY=your_groq_api_key_here
```

## Usage

```bash
whisper audio_or_video_file [options]
```

### Options

- `--model`: Whisper model to use (default: whisper-large-v3-turbo)
- `--language`: Language code (optional)
- `--task`: Task to perform: 'transcribe' or 'translate' (default: transcribe)
- `--output-dir`: Output directory (default: audio_filename_transcription)
- `--response-format`: API response format: 'verbose_json', 'json', 'text', 'srt', 'vtt' (default: verbose_json)
- `--version`: Show version information and exit

### Examples

Basic transcription:
```bash
whisper recording.mp3
```

Transcribe a video file:
```bash
whisper lecture.mp4
```

Translate audio to English:
```bash
whisper interview.mp3 --task translate
```

Specify language for better accuracy:
```bash
whisper lecture.mp3 --language en
```

Transcribe multiple files:
```bash
whisper file1.mp3 file2.wav video1.mp4
```

## Output Files

For each transcribed file, the following are generated in the output directory:

- `transcript.txt`: Plain text transcript
- `transcript.json`: JSON with detailed information
- `transcript.srt`: SubRip subtitle format
- `transcript.vtt`: WebVTT subtitle format
- `transcript.tsv`: Tab-separated values with timestamps

## License

MIT

## Acknowledgements
- [Abdullah Adeeb](https://www.abdullahadeeb.xyz)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Groq API](https://console.groq.com/docs/introduction)
- [FFmpeg](https://ffmpeg.org/)