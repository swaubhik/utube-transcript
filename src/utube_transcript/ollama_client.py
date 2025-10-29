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
        """Transcribe audio using Ollama's Whisper model.
        
        Args:
            audio_path: Path to the audio file
            model: Name of the Whisper model to use
            language: Optional language code
            
        Returns:
            List of segments with timestamps and text
        """
        # Prepare the API endpoint
        url = f"{self.host}/api/chat"
        
        # Convert audio to WAV first
        import subprocess
        import tempfile
        
        # Create temp WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            subprocess.run([
                'ffmpeg', '-y', '-i', audio_path, 
                '-acodec', 'pcm_s16le',  # Standard WAV format
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',  # Mono
                temp_wav.name
            ], check=True, capture_output=True)
        
        try:
            # Read the WAV file
            with open(temp_wav.name, 'rb') as f:
                audio_data = f.read()
                
            # Prepare the request
            headers = {'Content-Type': 'application/json'}
            data = {
                'model': model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an audio transcription assistant. Your task is to convert speech to text accurately ' + 
                                  'and provide the transcription with proper timing information. ' +
                                  'Respond with only the transcription in JSON format with start and end times.' +
                                  (' The audio is in ' + language + ' language.' if language else '')
                    },
                    {
                        'role': 'user',
                        'content': 'Please transcribe this audio and provide a complete word-for-word transcription with precise ' + 
                                  'timing information. Structure the response as JSON with a "transcription" array containing objects ' +
                                  'with "text", "start_time", and "end_time" fields. Use MM:SS format for times.'
                    }
                ],
                'stream': False,
                'images': ['data:audio/wav;base64,' + base64.b64encode(audio_data).decode('utf-8')],  # Audio data as base64
                'options': {
                    'temperature': 0.1  # Low temperature for more accurate transcription
                }
            }
        finally:
            # Clean up temp file
            import os
            try:
                os.unlink(temp_wav.name)
            except:
                pass  # Ignore cleanup errors
        
        # Make the request
        try:
            response = requests.post(url, headers=headers, json=data)
            # Print response for debugging
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
            response.raise_for_status()
            result = response.json()
            
            # Parse the response
            segments = []
            if 'message' in result and 'content' in result['message']:
                content = result['message']['content']
                # Remove markdown code block markers if present
                content = content.strip('`').strip()
                if content.startswith('json'):
                    content = content[4:].strip()
                    
                try:
                    # Try to parse the response as JSON
                    parsed = json.loads(content)
                    if 'transcription' in parsed:
                        segments = [
                            {
                                'text': segment['text'],
                                'start': self._time_to_seconds(segment['start_time']),
                                'end': self._time_to_seconds(segment['end_time'])
                            }
                            for segment in parsed['transcription']
                        ]
                except json.JSONDecodeError:
                    # If not JSON, treat as plain text
                    segments = [{
                        'text': content,
                        'start': 0,
                        'end': 0
                    }]
                    
            return segments
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to communicate with Ollama: {str(e)}")
            
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
        """Check if Ollama is available and has Whisper model.
        
        Returns:
            Tuple of (is_available, error_message)
        """
        try:
            response = requests.get(f"{self.host}/api/tags")
            if response.status_code == 200:
                try:
                    # First check if we have any models for transcription
                    models = response.json().get('models', [])
                    if any(m['name'].startswith(('whisper:', 'whisper/', 'llava:', 'llava/')) for m in models):
                        return True, ""
                        
                    # If not, try to pull llava which has audio transcription capability
                    print("No transcription model found, pulling llava...")
                    pull_response = requests.post(
                        f"{self.host}/api/pull",
                        json={"name": "llava"}
                    )
                    if pull_response.status_code == 200:
                        return True, ""
                    return False, "Failed to pull llava model"
                except Exception as e:
                    return False, f"Error checking/pulling model: {str(e)}"
            return False, f"Ollama returned status code {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"Failed to connect to Ollama: {str(e)}"