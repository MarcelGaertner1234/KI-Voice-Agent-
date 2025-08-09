"""
Text-to-Speech Service
Handles speech synthesis using ElevenLabs API
"""
import httpx
import logging
from typing import Optional, Dict
from api.config import settings

logger = logging.getLogger(__name__)


class TTSService:
    """Service for Text-to-Speech conversion"""
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.voice_id = settings.ELEVENLABS_VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
        self.model_id = settings.TTS_MODEL or "eleven_multilingual_v2"
        self.timeout_ms = settings.TTS_TIMEOUT_MS or 30000
        self.base_url = "https://api.elevenlabs.io/v1"
    
    async def synthesize_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        voice_settings: Optional[Dict] = None,
        output_format: str = "mp3_44100_128"
    ) -> bytes:
        """
        Convert text to speech using ElevenLabs API
        
        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID override
            voice_settings: Optional voice settings (stability, similarity_boost, etc.)
            output_format: Audio format (mp3_44100_128, pcm_16000, etc.)
            
        Returns:
            Audio data in bytes or empty bytes on error
        """
        if not text:
            logger.warning("No text provided for TTS")
            return b""
        
        if not self.api_key:
            logger.error("ElevenLabs API key not configured")
            return b""
        
        # Use provided voice_id or default
        voice = voice_id or self.voice_id
        url = f"{self.base_url}/text-to-speech/{voice}"
        
        # Default voice settings for natural speech
        if voice_settings is None:
            voice_settings = {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        
        try:
            timeout = self.timeout_ms / 1000.0
            headers = {
                "xi-api-key": self.api_key,
                "accept": "audio/mpeg",
                "content-type": "application/json",
            }
            
            payload = {
                "text": text,
                "model_id": self.model_id,
                "voice_settings": voice_settings
            }
            
            # Add output format if not default
            if output_format != "mp3_44100_128":
                payload["output_format"] = output_format
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    audio_data = response.content
                    logger.info(f"Synthesized {len(text)} chars to {len(audio_data)} bytes")
                    return audio_data
                else:
                    logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                    return b""
                    
        except httpx.TimeoutException:
            logger.error(f"ElevenLabs API timeout after {timeout}s")
            return b""
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            return b""
    
    async def get_voices(self) -> Dict:
        """
        Get available voices from ElevenLabs
        
        Returns:
            Dictionary with voice information
        """
        if not self.api_key:
            return {"error": "API key not configured"}
        
        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            return {"error": str(e)}
    
    async def clone_voice(
        self,
        name: str,
        files: list,
        description: Optional[str] = None
    ) -> Dict:
        """
        Clone a voice from audio samples
        
        Args:
            name: Name for the cloned voice
            files: List of audio file paths
            description: Optional voice description
            
        Returns:
            Voice clone response
        """
        # TODO: Implement voice cloning
        # This requires handling file uploads and voice training
        pass
    
    async def stream_speech(
        self,
        text: str,
        voice_id: Optional[str] = None
    ):
        """
        Stream TTS audio for real-time playback
        Future implementation for streaming TTS
        """
        # TODO: Implement streaming TTS
        # This would use WebSockets for real-time audio streaming
        pass


# Singleton instance
tts_service = TTSService()