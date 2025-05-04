# Whisper

A command-line tool to transcribe audio and video files using OpenAI's Whisper model via the Groq API.

## Author

**Abdullah Adeeb**
Website: [AbdullahAdeeb.xyz](https://AbdullahAdeeb.xyz)

## Description

Whisper is a lightweight CLI tool that transcribes audio and video files using OpenAI's Whisper model hosted on Groq's ultra-fast inference platform. It supports a wide range of media formats and can generate transcripts in multiple file types such as plain text, SRT, VTT, and TSV.

## Features

* Transcribe audio and video files using the Whisper Large v3 Turbo model
* Automatic extraction of audio from video files
* Support for popular audio formats: MP3, WAV, M4A, WEBM, OGG, FLAC
* Support for common video formats: MP4, AVI, MOV, MKV, WEBM, FLV, WMV, MPEG
* Output transcripts in TXT, JSON, SRT, VTT, and TSV
* Optionally copy transcript to clipboard
* Custom output directory support
* Transcription and translation tasks supported

## Installation

### Prerequisites

* Groq API key

### Install using prebuilt binaries

#### Linux

```bash
# Install FFmpeg (required for video file support)
sudo apt update
sudo apt install ffmpeg

# Download binary
sudo curl -L https://github.com/AbdullahAdeebx/whisper-cloud-cli/raw/main/binary/linux/whisper -o /usr/local/bin/whisper

# Make it executable
sudo chmod +x /usr/local/bin/whisper

# Ensure /usr/local/bin is in PATH
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

### Build from source (if binaries didn’t work for you)

```bash
# Clone the repo
git clone https://github.com/AbdullahAdeebx/whisper-cloud-cli.git
cd whisper-cloud-cli

# Install dependencies
pip install -r requirements.txt

# Optional: Make the script executable globally with pyinstaller
pip install pyinstaller
pyinstaller main.py --onefile --name whisper

# Move the binary to a location in your PATH
mv dist/whisper /usr/local/bin/
chmod +x /usr/local/bin/whisper
```

> On Windows, this will produce `dist/whisper.exe`, which you can move anywhere and add to your PATH.

## Configuration

Set your Groq API key as an environment variable:

```bash
export GROQ_API_KEY=your_groq_api_key_here
```

## Usage

```bash
whisper audio_or_video_file [options]
```

### Options

* `--model`: Whisper model to use (default: whisper-large-v3-turbo)
* `--language`: Language code (optional)
* `--task`: Task to perform: 'transcribe' or 'translate' (default: transcribe)
* `--output-dir`: Output directory (default: audio\_filename\_transcription)
* `--response-format`: API response format: 'verbose\_json', 'json', 'text', 'srt', 'vtt' (default: verbose\_json)
* `--version`: Show version information and exit

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

Each transcription will create a folder with:

* `transcript.txt`: Plain text
* `transcript.json`: JSON with detailed metadata
* `transcript.srt`: SubRip subtitles
* `transcript.vtt`: WebVTT format
* `transcript.tsv`: Tab-separated timestamps and text

## License

MIT

## Acknowledgements

* [Abdullah Adeeb](https://www.abdullahadeeb.xyz)
* [OpenAI Whisper](https://github.com/openai/whisper)
* [Groq API](https://console.groq.com/docs/introduction)
* [FFmpeg](https://ffmpeg.org/)