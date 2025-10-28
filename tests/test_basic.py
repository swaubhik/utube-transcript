"""Basic test cases for the package."""
import os
import pytest
from utube_transcript.utils import check_ffmpeg_installed
from utube_transcript.downloader import YouTubeDownloader
from utube_transcript.transcriber import Transcriber

def test_ffmpeg_check():
    """Test ffmpeg installation check."""
    assert check_ffmpeg_installed() is True

def test_downloader_init():
    """Test downloader initialization."""
    downloader = YouTubeDownloader()
    assert downloader.output_dir is not None

def test_transcriber_openai_no_key():
    """Test transcriber fails without API key."""
    with pytest.raises(ValueError):
        Transcriber(backend="openai", api_key=None)

def test_transcriber_local_import():
    """Test local transcriber import check."""
    try:
        import faster_whisper
        Transcriber(backend="local")
    except ImportError:
        pytest.skip("faster-whisper not installed")