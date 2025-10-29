"""Test Ollama backend - DISABLED.

Note: Ollama backend is not supported as Whisper models are not available in Ollama.
This test file is kept for reference but the tests are disabled.
"""
import pytest

def test_ollama_not_supported():
    """Test that Ollama backend correctly reports as not supported."""
    from utube_transcript.transcriber import Transcriber
    
    # Attempting to use ollama backend should raise an error
    with pytest.raises(ValueError, match="Unsupported backend"):
        Transcriber(backend="ollama")