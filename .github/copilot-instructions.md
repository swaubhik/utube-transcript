# AI Coding Agent Instructions for utube-transcript

## Project Overview

YouTube transcript generator CLI tool that downloads audio from YouTube videos and transcribes them using Whisper backends (OpenAI API or local faster-whisper).

**Key Architecture Pattern**: Three-layer separation

- `downloader.py`: YouTube audio extraction via yt-dlp
- `transcriber.py`: Backend-agnostic transcription with pluggable engines
- `cli.py` / `interactive.py`: Two UX modes (CLI args vs. interactive prompts)

## Critical Components

### Backend Architecture (`transcriber.py`)

The project supports **two transcription backends** via runtime polymorphism:

1. **`openai`**: Uses OpenAI Whisper API (requires `OPENAI_API_KEY`)
2. **`local`**: Uses faster-whisper library (GPU-accelerated, not available on M1/M2 Macs)

**Note**: Ollama is **not supported** as Whisper models are not available in Ollama.

**Pattern**: Single `Transcriber` class with backend selection in `__init__()`, delegating to `_transcribe_openai()` or `_transcribe_local()` based on `self.backend`.

### yt-dlp Integration (`downloader.py`)

**Critical workaround** for YouTube's SABR streaming issues:

```python
'extractor_args': {
    'youtube': {
        'player_client': ['android'],  # Bypass SABR issues
        'player_skip': ['webpage', 'configs']
    }
}
```

Without this, downloads fail on modern YouTube videos. Always preserve when modifying download logic.

### Output Format Handling

Three formats supported: `txt`, `srt`, `json`

- **txt**: Plain text concatenation of segments
- **srt**: Timestamped SubRip format using `_format_timestamp()` helper
- **json**: Raw segment data with `{start, end, text}` structure

**Current Limitation**: OpenAI backend (`_transcribe_openai()`) only returns plain text for all formats due to API response structure. SRT/JSON support is incomplete for this backend.

## Environment & Dependencies

### Environment Variables (`.env`)

Required variables defined in `.env.example`:

- `OPENAI_API_KEY`: Required for OpenAI backend
- `DEFAULT_BACKEND`: Recommended `openai` (most accurate)

**Pattern**: Use `utils.get_env_var()` which auto-loads `.env` via python-dotenv, never directly access `os.getenv()` for config.

### Dependency Constraints

From `requirements.txt`:

```python
faster-whisper>=0.10.0; platform_system != "Darwin" or platform_machine != "arm64"
```

**Why**: faster-whisper requires CUDA which isn't available on Apple Silicon. Tests must skip local backend on M1/M2 Macs.

### System Dependencies

**ffmpeg is mandatory** - both yt-dlp and Whisper require it for audio processing. `utils.check_ffmpeg_installed()` validates presence before any download/transcription operations.

## Entry Points & CLI Design

### Two Usage Modes

1. **CLI mode** (`utube-transcript`): Argument-based, scriptable

   ```bash
   utube-transcript --url URL --backend openai --format srt -o output.srt
   ```

2. **Interactive mode** (`utube-transcript-interactive`): Menu-driven prompts
   - Guides users through backend selection (with explanations)
   - Auto-saves OpenAI API keys to `.env` if entered during session
   - Builds `argparse.Namespace` and delegates to `cli.main(args=namespace)`

**Pattern**: Both modes funnel through `cli.main()` - interactive is a wrapper that constructs args programmatically.

### CLI Conventions

- Progress messages print to `stderr` to keep `stdout` clean for piping
- Errors exit with code 1 via `sys.exit(1)`
- Default output: `transcript.<format>` in current directory
- Temporary audio files auto-cleanup via `downloader.cleanup()`

## Testing Strategy

### Test Organization

- `tests/test_basic.py`: Unit tests for utilities, initialization, error handling
- `tests/test_ollama.py`: Disabled test file (Ollama backend not supported)

**Pattern**: Integration tests use `tmp_path` fixture for isolated file operations:

```python
def test_ollama_transcription(tmp_path):
    downloader = YouTubeDownloader(str(tmp_path))
    # Ensures cleanup doesn't affect other tests
```

### Running Tests

```bash
pytest tests/                    # Run all tests
pytest tests/test_basic.py      # Unit tests only
```

**Note**: Integration tests may require internet connectivity for YouTube downloads.

## Common Development Workflows

### Adding a New Backend

1. Add backend choice to `Transcriber.__init__()` elif chain
2. Implement `_transcribe_<backend>()` method following signature:
   ```python
   def _transcribe_<backend>(self, audio_path: str, output_format: str) -> Union[str, dict]:
   ```
3. Handle all three output formats (txt/srt/json)
4. Add to `--backend` choices in `cli.py` argparse
5. Update interactive.py backend menu

### Debugging Transcription Issues

Enable verbose output by modifying yt-dlp options:

```python
'quiet': False,  # Change to False in downloader.py
'no_warnings': False,
```

## Project-Specific Conventions

1. **Error message format**: User-facing errors should be actionable:

   ```python
   raise RuntimeError(
       "ffmpeg not found. Please install it first:\n"
       "macOS: brew install ffmpeg\n..."
   )
   ```

2. **Timestamp format**: Use SRT-standard `HH:MM:SS.mmm` via `_format_timestamp()` - never roll your own time formatting

3. **Temp file handling**: Use `tempfile.gettempdir()` for audio downloads, never hardcode `/tmp` (Windows compatibility)

4. **Import organization**: All internal imports use relative imports (`.utils`, `.downloader`, etc.)

## Known Issues & TODOs

1. **OpenAI SRT support incomplete**: `_transcribe_openai()` comment says "TODO: Implement proper SRT formatting"
2. **Interactive mode .env updates**: Modifies `.env` file in-place when saving API key - assumes specific format

## Installation & Setup

### Local Development

```bash
# Install with optional local backend (skip on M1/M2 Macs)
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY if using OpenAI backend

# Verify ffmpeg
ffmpeg -version

# Install in editable mode for development
pip install -e .
```

### Docker Deployment

```bash
# Create output directory
mkdir -p output

# Build images
docker-compose build utube-transcript-cpu  # CPU variant
docker-compose build utube-transcript-gpu  # GPU variant (requires nvidia-docker)

# Run interactively
docker-compose --profile cpu up utube-transcript-cpu

# Run CLI mode
docker-compose run --rm utube-transcript-cli \
  --url "URL" --format srt -o transcript.srt
```

**Docker Architecture:**

- **CPU image**: Based on `python:3.11-slim`, uses OpenAI API backend
- **GPU image**: Based on `pytorch/pytorch:2.9.0-cuda12.8-cudnn9-runtime`, uses local Whisper with CUDA
- Multi-stage build separates CPU and GPU variants
- Volume mount to `./output` for transcript files

## Key Files Reference

- `src/utube_transcript/cli.py` - Main CLI entrypoint and argument parsing
- `src/utube_transcript/transcriber.py` - Core transcription logic with backend selection
- `src/utube_transcript/downloader.py` - YouTube audio extraction with SABR workaround
- `src/utube_transcript/ollama_client.py` - Ollama client (currently unused - Whisper not available in Ollama)
- `pyproject.toml` - Package metadata, defines both CLI entry points
