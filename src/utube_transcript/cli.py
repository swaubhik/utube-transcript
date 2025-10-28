"""CLI interface for YouTube transcript generator."""
import argparse
import os
import sys
from typing import Literal, Optional

from .downloader import YouTubeDownloader
from .transcriber import Transcriber
from .utils import check_ffmpeg_installed

def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Generate transcripts from YouTube videos"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="YouTube video URL"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: transcript.<format>)"
    )
    parser.add_argument(
        "--backend",
        choices=["openai", "local"],
        default="openai",
        help="Transcription backend to use (default: openai)"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["txt", "srt", "json"],
        default="txt",
        help="Output format (default: txt)"
    )
    parser.add_argument(
        "--language",
        "-l",
        help="Language code (e.g., en, es) - optional"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (can also use OPENAI_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    try:
        # Ensure ffmpeg is available
        check_ffmpeg_installed()
        
        # Set up downloader
        downloader = YouTubeDownloader()
        
        # Download audio
        print("Downloading audio...", file=sys.stderr)
        audio_path = downloader.download_audio(args.url)
        
        # Initialize transcriber
        print("Transcribing...", file=sys.stderr)
        transcriber = Transcriber(
            backend=args.backend,
            api_key=args.api_key,
            language=args.language
        )
        
        # Generate transcript
        transcript = transcriber.transcribe(
            audio_path,
            output_format=args.format
        )
        
        # Clean up downloaded audio
        downloader.cleanup(audio_path)
        
        # Determine output path
        output_path = args.output or f"transcript.{args.format}"
        
        # Write output
        if args.format == "json":
            import json
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(transcript, f, ensure_ascii=False, indent=2)
        else:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(transcript)
                
        print(f"Transcript saved to: {output_path}", file=sys.stderr)
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()