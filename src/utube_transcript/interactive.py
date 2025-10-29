#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import argparse
from .cli import main as cli_main

def prompt_for_input():
    print("\n=== YouTube Transcript Generator ===\n")
    
    # Get video URL
    url = input("Enter YouTube video URL: ").strip()
    
    # Get output format
    print("\nAvailable output formats:")
    print("1. txt (plain text)")
    print("2. srt (with timestamps)")
    print("3. json")
    format_choice = input("Choose format [1-3] (default: 1): ").strip()
    format_map = {"1": "txt", "2": "srt", "3": "json"}
    output_format = format_map.get(format_choice, "txt")
    
    # Get output filename
    default_filename = f"transcript.{output_format}"
    output_file = input(f"Enter output filename (default: {default_filename}): ").strip()
    if not output_file:
        output_file = default_filename
    
    # Get transcription backend
    print("\nAvailable transcription backends:")
    print("1. OpenAI Whisper API (requires API key)")
    print("2. Local Whisper model (uses GPU)")
    print("3. Ollama Whisper (using Docker)")
    backend_choice = input("Choose backend [1-3] (default: 3): ").strip()
    if backend_choice == "1":
        backend = "openai"
    elif backend_choice == "2":
        backend = "local"
    else:
        backend = "ollama"
    
    # Get language (optional)
    language = input("\nEnter language code (e.g., 'en' for English, leave empty for auto-detect): ").strip()
    
    api_key = None
    # If using OpenAI backend, check for API key
    if backend == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("\nOpenAI API key not found in .env file")
            api_key = input("Enter your OpenAI API key: ").strip()
            # Update .env file with the new API key
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            with open(env_path, 'w') as f:
                for line in lines:
                    if line.startswith('OPENAI_API_KEY='):
                        f.write(f'OPENAI_API_KEY={api_key}\n')
                    else:
                        f.write(line)
            os.environ["OPENAI_API_KEY"] = api_key
    
    return {
        "url": url,
        "format": output_format,
        "output": output_file,
        "backend": backend,
        "language": language if language else None,
        "api_key": api_key
    }

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    try:
        # Get user input
        args = prompt_for_input()
        
        # Convert to argparse.Namespace for compatibility with existing cli.py
        namespace_args = argparse.Namespace(**args)
        
        # Run the main CLI function with our arguments
        cli_main(args=namespace_args)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"\nError: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())