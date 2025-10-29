"""Test Ollama transcription functionality."""
import os
import pytest
from utube_transcript.transcriber import Transcriber
from utube_transcript.downloader import YouTubeDownloader

def test_ollama_transcription(tmp_path):
    """Test transcription using Ollama backend."""
    # Use a short test video
    # Using test video from Wikimedia Commons
    video_url = "https://www.youtube.com/watch?v=EngW7tLk6R8"  # Creative Commons Test Video
    output_dir = str(tmp_path)
    
    # Download video
    downloader = YouTubeDownloader(output_dir)
    audio_path = downloader.download_audio(video_url, "mp3")
    assert os.path.exists(audio_path)
    
    # Create transcriber with ollama backend
    transcriber = Transcriber(backend="ollama")
    
    # Test different output formats
    text = transcriber.transcribe(audio_path, output_format="txt")
    assert isinstance(text, str)
    assert len(text) > 0
    
    json_output = transcriber.transcribe(audio_path, output_format="json")
    assert isinstance(json_output, dict)
    assert "segments" in json_output
    assert len(json_output["segments"]) > 0
    
    srt = transcriber.transcribe(audio_path, output_format="srt")
    assert isinstance(srt, str)
    assert len(srt) > 0