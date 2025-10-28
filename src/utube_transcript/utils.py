"""Utility functions for the utube-transcript package."""
import os
import shutil
import subprocess
from typing import Optional

def check_ffmpeg_installed() -> bool:
    """Check if ffmpeg is installed and accessible.
    
    Returns:
        bool: True if ffmpeg is installed, raises RuntimeError otherwise
    
    Raises:
        RuntimeError: If ffmpeg is not found
    """
    if not shutil.which('ffmpeg'):
        raise RuntimeError(
            "ffmpeg not found. Please install it first:\n"
            "macOS: brew install ffmpeg\n"
            "Ubuntu/Debian: sudo apt-get install ffmpeg\n"
            "Windows: https://ffmpeg.org/download.html"
        )
    return True

def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get an environment variable, checking .env file if present.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        str: Environment variable value or default
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    return os.getenv(key, default)