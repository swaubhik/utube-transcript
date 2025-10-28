"""Transcription module supporting OpenAI Whisper API and local whisper."""
import os
from typing import Literal, Optional, Union

import openai
from .utils import get_env_var

class Transcriber:
    """Handles audio transcription using different backends."""
    
    def __init__(
        self,
        backend: Literal["openai", "local"] = "openai",
        api_key: Optional[str] = None,
        language: Optional[str] = None
    ):
        """Initialize the transcriber.
        
        Args:
            backend: Transcription backend to use ('openai' or 'local')
            api_key: OpenAI API key (required for 'openai' backend)
            language: Optional language code (e.g., 'en', 'es')
        """
        self.backend = backend
        self.language = language
        
        if backend == "openai":
            # Try to get API key from env if not provided
            self.api_key = api_key or get_env_var("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "OpenAI API key required. Set OPENAI_API_KEY env variable "
                    "or pass api_key parameter."
                )
            openai.api_key = self.api_key
            
        elif backend == "local":
            try:
                import faster_whisper
                self.model = faster_whisper.WhisperModel("base")
            except ImportError:
                raise ImportError(
                    "faster-whisper not installed. Install it with: "
                    "pip install faster-whisper"
                )
    
    def transcribe(
        self,
        audio_path: str,
        output_format: Literal["txt", "srt", "json"] = "txt"
    ) -> Union[str, dict]:
        """Transcribe audio file using selected backend.
        
        Args:
            audio_path: Path to audio file
            output_format: Desired output format
            
        Returns:
            Transcription in requested format (str for txt/srt, dict for json)
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        if self.backend == "openai":
            return self._transcribe_openai(audio_path, output_format)
        else:
            return self._transcribe_local(audio_path, output_format)
    
    def _transcribe_openai(
        self,
        audio_path: str,
        output_format: str
    ) -> Union[str, dict]:
        """Transcribe using OpenAI's Whisper API."""
        with open(audio_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                "whisper-1",
                audio_file,
                language=self.language
            )
            
        if output_format == "json":
            return transcript
        
        # For now, just return the text for both txt and srt
        # TODO: Implement proper SRT formatting with timestamps
        return transcript.text
    
    def _transcribe_local(
        self,
        audio_path: str,
        output_format: str
    ) -> Union[str, dict]:
        """Transcribe using local Whisper model."""
        segments, _ = self.model.transcribe(
            audio_path,
            language=self.language
        )
        
        if output_format == "json":
            return {"segments": [
                {
                    "start": s.start,
                    "end": s.end,
                    "text": s.text
                } for s in segments
            ]}
        
        # Simple text output
        text = " ".join(segment.text for segment in segments)
        
        if output_format == "txt":
            return text
            
        # Basic SRT format
        srt_lines = []
        for i, segment in enumerate(segments, 1):
            srt_lines.extend([
                str(i),
                f"{self._format_timestamp(segment.start)} --> "
                f"{self._format_timestamp(segment.end)}",
                segment.text.strip(),
                ""
            ])
        return "\n".join(srt_lines)
    
    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Convert seconds to SRT timestamp format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"