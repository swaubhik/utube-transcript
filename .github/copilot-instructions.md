# AI Coding Agent Instructions for utube-transcript

## Project Overview

YouTube transcript generator CLI tool that downloads audio from YouTube videos and transcribes them using multiple Whisper backends (OpenAI API, local faster-whisper, or Ollama).

**Key Architecture Pattern**: Three-layer separation

- `downloader.py`: YouTube audio extraction via yt-dlp
- `transcriber.py`: Backend-agnostic transcription with pluggable engines
- `cli.py` / `interactive.py`: Two UX modes (CLI args vs. interactive prompts)

## Critical Components

### Backend Architecture (`transcriber.py`)

The project supports **three transcription backends** via runtime polymorphism:

1. **`openai`**: Uses OpenAI Whisper API (requires `OPENAI_API_KEY`)
2. **`local`**: Uses faster-whisper library (GPU-accelerated, not available on M1/M2 Macs)
3. **`ollama`**: Uses Ollama's llava model for audio transcription (Docker-based)

**Pattern**: Single `Transcriber` class with backend selection in `__init__()`, delegating to `_transcribe_openai()`, `_transcribe_local()`, or `_transcribe_ollama()` based on `self.backend`.

**Known Issue in Code**: `transcriber.py` has duplicate `__init__()` method definitions (lines ~20-53) - the second definition shadows the first, effectively disabling the ollama backend initialization code in production.

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
- `OLLAMA_HOST`: Default `http://localhost:11434`
- `DEFAULT_BACKEND`: Recommended `ollama` (no API key needed)

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
   utube-transcript --url URL --backend ollama --format srt -o output.srt
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
- `tests/test_ollama.py`: Integration test with real YouTube download

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
pytest -k ollama                # Integration tests (requires Ollama running)
```

**Note**: `test_ollama.py` requires Ollama service running on `localhost:11434`. Tests will fail if not available.

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

Check Ollama availability:

```python
from utube_transcript.ollama_client import OllamaClient
client = OllamaClient()
available, error = client.check_availability()
```

## Project-Specific Conventions

1. **Audio format standardization**: Always convert to 16kHz mono WAV for Ollama backend (see `ollama_client.py` ffmpeg command)

2. **Error message format**: User-facing errors should be actionable:

   ```python
   raise RuntimeError(
       "ffmpeg not found. Please install it first:\n"
       "macOS: brew install ffmpeg\n..."
   )
   ```

3. **Timestamp format**: Use SRT-standard `HH:MM:SS.mmm` via `_format_timestamp()` - never roll your own time formatting

4. **Temp file handling**: Use `tempfile.gettempdir()` for audio downloads, never hardcode `/tmp` (Windows compatibility)

5. **Import organization**: All internal imports use relative imports (`.utils`, `.downloader`, etc.)

## Known Issues & TODOs

1. **Duplicate `__init__` in `transcriber.py`** (lines ~20-53): Second definition shadows first, breaking ollama backend initialization
2. **OpenAI SRT support incomplete**: `_transcribe_openai()` comment says "TODO: Implement proper SRT formatting"
3. **Ollama transcription quality**: Currently uses llava model as workaround - proper whisper model integration pending
4. **Interactive mode .env updates**: Modifies `.env` file in-place when saving API key - assumes specific format

## Installation & Setup

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

## Key Files Reference

- `src/utube_transcript/cli.py` - Main CLI entrypoint and argument parsing
- `src/utube_transcript/transcriber.py` - Core transcription logic (contains the duplicate `__init__` bug)
- `src/utube_transcript/downloader.py` - YouTube audio extraction with SABR workaround
- `src/utube_transcript/ollama_client.py` - Ollama API integration
- `pyproject.toml` - Package metadata, defines both CLI entry points
