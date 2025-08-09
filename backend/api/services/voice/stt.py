"""
Speech-to-Text Service
Handles audio transcription using OpenAI Whisper API
"""
from typing import Optional
import httpx
import logging
from api.config import settings

logger = logging.getLogger(__name__)


class STTService:
    """Service for Speech-to-Text conversion"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.STT_MODEL or "whisper-1"
        self.max_audio_mb = settings.MAX_AUDIO_MB or 25
        self.timeout_ms = settings.STT_TIMEOUT_MS or 30000
    
    def _bytes_to_mb(self, length_bytes: int) -> float:
        """Convert bytes to megabytes"""
        return length_bytes / (1024 * 1024)
    
    async def transcribe_audio(
        self, 
        audio_bytes: bytes,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        Transcribe audio to text using OpenAI Whisper
        
        Args:
            audio_bytes: Audio data in bytes
            language: Optional language code (e.g., 'de', 'en')
            prompt: Optional prompt to guide transcription
            
        Returns:
            Transcribed text or empty string on error
        """
        if not audio_bytes:
            logger.warning("No audio data provided")
            return ""
        
        # Check audio size
        audio_size_mb = self._bytes_to_mb(len(audio_bytes))
        if audio_size_mb > self.max_audio_mb:
            logger.error(f"Audio too large: {audio_size_mb:.2f}MB (max: {self.max_audio_mb}MB)")
            return ""
        
        if not self.api_key:
            logger.error("OpenAI API key not configured")
            return ""
        
        try:
            timeout = self.timeout_ms / 1000.0
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            data = {"model": self.model}
            if language:
                data["language"] = language
            if prompt:
                data["prompt"] = prompt
            
            files = {
                "file": ("audio.webm", audio_bytes, "application/octet-stream"),
            }
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers=headers,
                    data=data,
                    files=files,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get("text", "")
                    logger.info(f"Transcribed {audio_size_mb:.2f}MB audio: {len(text)} chars")
                    return text
                else:
                    logger.error(f"Whisper API error: {response.status_code} - {response.text}")
                    return ""
                    
        except httpx.TimeoutException:
            logger.error(f"Whisper API timeout after {timeout}s")
            return ""
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    async def transcribe_stream(
        self,
        audio_stream,
        language: Optional[str] = None
    ):
        """
        Transcribe audio stream in chunks
        Future implementation for streaming transcription
        """
        # TODO: Implement streaming transcription
        # This would use WebSockets or Server-Sent Events
        # to provide real-time transcription
        pass


# Singleton instance
stt_service = STTService()