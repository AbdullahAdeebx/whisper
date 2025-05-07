# whisper

a cli tool i made for myself.

one simple way to transcribe audio from terminal.

all in native python.
no subscription.
blazingly fast. free. enjoy.

![img](https://raw.githubusercontent.com/AbdullahAdeebx/whisper/main/introducing-whisper.gif)

## Features

* **Supports Many Formats:** Works with popular audio (MP3, WAV, M4A) and video (MP4, AVI, MOV) files.
* **Automatic Audio Extraction:** Extracts audio from video files on the fly using ffmpeg.
* **Different Output Options:** Save transcriptions in formats like TXT, JSON, SRT, VTT, and TSV.

## Installation

### Prerequisites

* Python 3.x
* FFmpeg (for video file support)

```bash
pip install aa-whisper
```

#### Install FFmpeg

FFmpeg is required if you want to transcribe video files.

**Linux:**

```bash
sudo apt install ffmpeg
```

**macOS:**

```bash
brew install ffmpeg
```

**Windows (PowerShell):**

```powershell
winget install FFmpeg
```

## Configuration

Set your Groq API key as an environment variable.

**Linux:**

```bash
echo 'export GROQ_API_KEY="your_groq_api_key_here"' >> ~/.bashrc && source ~/.bashrc
```

**macOS:**

```bash
echo 'export GROQ_API_KEY="your_groq_api_key_here"' >> ~/.zshrc && source ~/.zshrc
```

**Windows:**

```powershell
[System.Environment]::SetEnvironmentVariable("GROQ_API_KEY", "your_groq_api_key_here", "User")
```

## Usage

```bash
whisper audio_or_video_file [options]
```

### Options

* `--model`: Whisper model to use (default: whisper-large-v3-turbo)
* `--language`: Language code (optional)
* `--task`: 'transcribe' or 'translate' (default: transcribe)
* `--output-dir`: Output directory (default: audio\_filename\_transcription)
* `--response-format`: 'verbose\_json', 'json', 'text', 'srt', 'vtt' (default: verbose\_json)
* `--version`: Show version info

### Examples

Transcribe audio:

```bash
whisper recording.mp3
```

Transcribe video:

```bash
whisper lecture.mp4
```

Translate to English:

```bash
whisper interview.mp3 --task translate
```

Multiple files at once:

```bash
whisper file1.mp3 file2.wav video1.mp4
```

## Output Files

Each transcription will generate:

* `transcript.txt`: Plain text
* `transcript.json`: JSON metadata
* `transcript.srt`: SubRip subtitles
* `transcript.vtt`: WebVTT format
* `transcript.tsv`: Timestamps and text

## License

MIT

## Acknowledgements

* [Abdullah Adeeb](https://www.abdullahadeeb.xyz)
* [OpenAI Whisper](https://github.com/openai/whisper)
* [Groq API](https://console.groq.com/docs/introduction)
* [FFmpeg](https://ffmpeg.org/)