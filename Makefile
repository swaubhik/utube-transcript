.PHONY: help build build-cpu build-gpu run run-cpu run-gpu test clean

# Default target
help:
	@echo "utube-transcript Docker Commands"
	@echo "================================="
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Create output dir and .env file"
	@echo ""
	@echo "Build:"
	@echo "  make build          - Build both CPU and GPU images"
	@echo "  make build-cpu      - Build CPU-only image"
	@echo "  make build-gpu      - Build GPU image"
	@echo ""
	@echo "Run (Interactive):"
	@echo "  make run            - Run CPU version interactively"
	@echo "  make run-cpu        - Run CPU version interactively"
	@echo "  make run-gpu        - Run GPU version interactively"
	@echo ""
	@echo "CLI Usage:"
	@echo "  make cli URL=<url>  - Transcribe YouTube video (CPU)"
	@echo "  make cli-gpu URL=<url> - Transcribe with GPU"
	@echo ""
	@echo "Example:"
	@echo "  make cli URL='https://youtube.com/watch?v=xxx' FORMAT=srt OUTPUT=transcript.srt"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove all containers and output files"
	@echo "  make clean-output   - Remove only output files"

setup:
	@echo "Creating output directory..."
	@mkdir -p output
	@if [ ! -f .env ]; then \
		echo "Creating .env file from .env.example..."; \
		cp .env.example .env; \
		echo "✓ Please edit .env and add your OPENAI_API_KEY"; \
	else \
		echo "✓ .env file already exists"; \
	fi

build: build-cpu build-gpu

build-cpu:
	@echo "Building CPU image..."
	docker-compose build utube-transcript-cpu

build-gpu:
	@echo "Building GPU image..."
	docker-compose build utube-transcript-gpu

run: run-cpu

run-cpu:
	@echo "Starting interactive CPU mode..."
	docker-compose --profile cpu up utube-transcript-cpu

run-gpu:
	@echo "Starting interactive GPU mode..."
	docker-compose --profile gpu up utube-transcript-gpu

# CLI usage with variables
# Example: make cli URL="https://youtube.com/watch?v=xxx" FORMAT=srt OUTPUT=transcript.srt
URL ?= 
FORMAT ?= txt
OUTPUT ?= transcript.$(FORMAT)
BACKEND ?= openai

cli:
	@if [ -z "$(URL)" ]; then \
		echo "Error: URL is required"; \
		echo "Usage: make cli URL='https://youtube.com/watch?v=xxx'"; \
		exit 1; \
	fi
	docker-compose run --rm utube-transcript-cli \
		--url "$(URL)" \
		--backend $(BACKEND) \
		--format $(FORMAT) \
		-o $(OUTPUT)

cli-gpu:
	@if [ -z "$(URL)" ]; then \
		echo "Error: URL is required"; \
		echo "Usage: make cli-gpu URL='https://youtube.com/watch?v=xxx'"; \
		exit 1; \
	fi
	docker-compose --profile gpu run --rm utube-transcript-gpu \
		utube-transcript \
		--url "$(URL)" \
		--backend local \
		--format $(FORMAT) \
		-o $(OUTPUT)

test-gpu:
	@echo "Testing GPU availability..."
	docker-compose --profile gpu run --rm utube-transcript-gpu \
		python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU count: {torch.cuda.device_count()}')"

clean:
	@echo "Stopping and removing containers..."
	docker-compose --profile cpu down
	docker-compose --profile gpu down
	docker-compose --profile cli down
	@echo "Removing output files..."
	rm -rf output/*.txt output/*.srt output/*.json output/*.mp3 output/*.wav

clean-output:
	@echo "Removing output files..."
	rm -rf output/*.txt output/*.srt output/*.json output/*.mp3 output/*.wav
