"""Ollama integration for audio transcription."""
import base64
import json
import requests
from typing import Dict, List, Optional, Tuple

class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, host: str = "http://localhost:11434"):
        """Initialize Ollama client.
        
        Args:
            host: Ollama API host URL
        """
        self.host = host.rstrip('/')
        
    def transcribe(
        self,
        audio_path: str,
        model: str = "llava",
        language: Optional[str] = None
    ) -> List[Dict]:
        """Transcribe audio using Ollama.
        
        Note: Ollama doesn't have native Whisper models. This uses llava as a workaround,
        which may not provide accurate transcriptions. Consider using OpenAI or local backend
        for production use.
        
        Args:
            audio_path: Path to the audio file
            model: Name of the model to use (default: llava)
            language: Optional language code
            
        Returns:
            List of segments with timestamps and text
        """
        raise NotImplementedError(
            "Ollama backend is not currently supported as Ollama does not have "
            "native audio transcription models (Whisper is not available in Ollama). "
            "Please use 'openai' or 'local' backend instead.\n\n"
            "Available options:\n"
            "  - openai: Uses OpenAI Whisper API (requires API key)\n"
            "  - local: Uses faster-whisper locally (requires GPU, not available on M1/M2 Macs)"
        )
            
    @staticmethod
    def _time_to_seconds(time_str: str) -> float:
        """Convert time string (MM:SS) to seconds."""
        try:
            parts = time_str.split(':')
            if len(parts) == 2:
                minutes, seconds = parts
                return float(minutes) * 60 + float(seconds)
            return float(time_str)
        except (ValueError, IndexError):
            return 0.0
    
    def check_availability(self) -> Tuple[bool, str]:
        """Check if Ollama is available.
        
        Note: Ollama doesn't have native Whisper models for audio transcription.
        This method only checks if the Ollama service is running.
        
        Returns:
            Tuple of (is_available, error_message)
        """
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                return False, (
                    "Ollama is running but does not support audio transcription. "
                    "Whisper models are not available in Ollama. "
                    "Please use 'openai' or 'local' backend instead."
                )
            return False, f"Ollama returned status code {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"Failed to connect to Ollama: {str(e)}"