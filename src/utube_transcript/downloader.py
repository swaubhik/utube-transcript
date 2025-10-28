"""YouTube video/audio downloader module using yt-dlp."""
import os
import tempfile
from typing import Optional

import yt_dlp
from .utils import check_ffmpeg_installed

class YouTubeDownloader:
    """Handles downloading audio from YouTube videos."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the downloader.
        
        Args:
            output_dir: Directory to save downloaded files. Uses a temp dir if None.
        """
        check_ffmpeg_installed()
        self.output_dir = output_dir or tempfile.gettempdir()
        
    def download_audio(self, url: str, preferred_format: str = "mp3") -> str:
        """Download audio from a YouTube video.
        
        Args:
            url: YouTube video URL
            preferred_format: Audio format to convert to (default: mp3)
            
        Returns:
            Path to the downloaded audio file
        """
        # yt-dlp options for audio extraction
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': preferred_format,
            }],
            'outtmpl': os.path.join(self.output_dir, '%(id)s.%(ext)s'),
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video info first
                info = ydl.extract_info(url, download=False)
                video_id = info['id']
                output_path = os.path.join(
                    self.output_dir, f"{video_id}.{preferred_format}"
                )
                
                # Download if file doesn't exist
                if not os.path.exists(output_path):
                    ydl.download([url])
                
                return output_path
                
        except Exception as e:
            raise RuntimeError(f"Failed to download audio: {str(e)}") from e
            
    def cleanup(self, filepath: str):
        """Remove a downloaded file.
        
        Args:
            filepath: Path to the file to remove
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except OSError as e:
            print(f"Warning: Failed to remove temporary file {filepath}: {e}")