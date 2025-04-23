# Whisper Cloud CLI

**Whisper Cloud CLI** is a simple command-line tool that lets you use OpenAI's Whisper without installing anything locally. It runs entirely in the cloud, making transcription effortless and lightweight. Powered by Groq-hosted Whisper Large V3 Turbo, it delivers fast and accurate results without using your machine's resources.

## 🔧 Usage

To transcribe audio, just run:

```
whisper audio.mp3
```

This command will:

- Use the Whisper Large V3 Turbo model to transcribe `audio.mp3`
- Create a folder named `audio_transcription`
- Generate the following transcription output files in that folder:
  - `.srt` (SubRip)
  - `.txt` (Plain text)
  - `.json` (Structured data)
  - `.tsv` (Tab-separated values)
  - `.vtt` (WebVTT)
- Display the plain text transcript directly in your terminal
- Automatically copy the transcript to your clipboard

No setup. No local processing. Just pure cloud magic.