# Whisper Cloud CLI

A command-line tool to transcribe audio files using OpenAI's Whisper model via the Groq API.

## Author

**Abdullah Adeeb**  
Website: [AbdullahAdeeb.xyz](https://AbdullahAdeeb.xyz)

## Description

Whisper Cloud CLI is a command-line tool that allows you to transcribe audio files using OpenAI's Whisper model hosted on Groq's platform. The tool supports various audio formats and can generate transcripts in multiple formats including plain text, SRT, VTT, and TSV.

## Features

- Transcribe audio files using Whisper Large v3 Turbo model
- Support for various audio formats (MP3, WAV, M4A, MP4, WEBM, OGG, FLAC)
- Generate transcripts in multiple formats (TXT, JSON, SRT, VTT, TSV)
- Automatically copy transcript to clipboard
- Customizable output directory
- Support for both transcription and translation tasks

## Installation

### Prerequisites

- Python 3.6+
- Groq API key

### Install from source

```bash
git clone https://github.com/AbdullahAdeebx/whisper-cloud-cli.git
cd whisper-cloud-cli
pip install -r requirements.txt
```

## Configuration

Create a `.env.local` file in the project directory with your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

Alternatively, you can set it as an environment variable:

```bash
export GROQ_API_KEY=your_groq_api_key_here
```

## Usage

```bash
python whisper_cloud.py audio_file.mp3 [options]
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
python whisper_cloud.py recording.mp3
```

Translate audio to English:
```bash
python whisper_cloud.py interview.mp3 --task translate
```

Specify language for better accuracy:
```bash
python whisper_cloud.py lecture.mp3 --language en
```

Transcribe multiple files:
```bash
python whisper_cloud.py file1.mp3 file2.wav file3.m4a
```

## Output Files

For each transcribed audio file, the following files are generated in the output directory:

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