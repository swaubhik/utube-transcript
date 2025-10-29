# Docker Usage Guide for utube-transcript

## Quick Start

### Using Makefile (Recommended)

```bash
# 1. Setup environment
make setup

# 2. Edit .env and add your OPENAI_API_KEY
nano .env

# 3. Build images
make build-cpu    # CPU only
make build-gpu    # GPU support

# 4. Run interactively
make run          # CPU mode
make run-gpu      # GPU mode

# 5. Or use CLI mode
make cli URL="https://www.youtube.com/watch?v=VIDEO_ID"
make cli URL="https://youtube.com/watch?v=xxx" FORMAT=srt OUTPUT=transcript.srt
```

See all available commands: `make help`

### Manual Docker Commands

### 1. Set up environment

```bash
# Create output directory
mkdir -p output

# Copy environment file and add your OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Choose your mode

#### Option A: CPU-only (OpenAI API backend)

**Best for:** Most users, works on all systems

```bash
# Interactive mode
docker-compose --profile cpu up utube-transcript-cpu

# CLI mode
docker-compose run --gpus all --rm utube-transcript-cli \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --backend openai \
  --format srt \
  -o transcript.srt
```

#### Option B: GPU-enabled (Local Whisper backend)

**Requires:** NVIDIA GPU + nvidia-docker
**Best for:** Privacy, offline use, no API costs

```bash
# Interactive mode
docker-compose --profile gpu up utube-transcript-gpu

# CLI mode with GPU
docker-compose --profile gpu run --rm utube-transcript-gpu \
  utube-transcript \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --backend local \
  --format srt \
  -o transcript.srt
```

## Build Images

```bash
# Build CPU variant
docker-compose build utube-transcript-cpu

# Build GPU variant
docker-compose build utube-transcript-gpu
```

## Output Files

All transcripts are saved to the `./output` directory on your host machine.

## Environment Variables

Set these in your `.env` file:

- `OPENAI_API_KEY` - Your OpenAI API key (required for OpenAI backend)
- `DEFAULT_BACKEND` - Either `openai` or `local` (default: `openai`)
- `DEFAULT_OUTPUT_FORMAT` - Either `txt`, `srt`, or `json` (default: `txt`)
- `DEFAULT_LANGUAGE` - Language code like `en`, `es`, etc. (default: `en`)

## Examples

### Interactive Mode

```bash
# Start container in interactive mode
docker-compose --profile cpu up utube-transcript-cpu

# Follow the prompts to enter YouTube URL and options
```

### CLI Mode - Multiple Formats

```bash
# Text format
docker-compose run --rm utube-transcript-cli \
  --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --format txt \
  -o transcript.txt

# SRT format with timestamps
docker-compose run --rm utube-transcript-cli \
  --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --format srt \
  -o transcript.srt

# JSON format with segment data
docker-compose run --rm utube-transcript-cli \
  --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --format json \
  -o transcript.json
```

### GPU Usage

```bash
# Verify GPU is accessible
docker-compose --profile gpu run --rm utube-transcript-gpu python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Run with local Whisper model on GPU
docker-compose --profile gpu run --rm utube-transcript-gpu \
  utube-transcript \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --backend local \
  -o transcript.txt
```

## Troubleshooting

### GPU not detected

1. Install nvidia-docker: https://github.com/NVIDIA/nvidia-docker
2. Verify: `docker run --rm --gpus all nvidia/cuda:12.8.0-base-ubuntu22.04 nvidia-smi`

### Permission issues with output directory

```bash
chmod 777 output/
```

### Container exits immediately

Make sure you're using the correct profile:

```bash
docker-compose --profile cpu up utube-transcript-cpu  # For CPU
docker-compose --profile gpu up utube-transcript-gpu  # For GPU
```
