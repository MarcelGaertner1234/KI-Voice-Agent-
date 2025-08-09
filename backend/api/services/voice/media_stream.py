"""
Media Stream Service
Handles real-time audio streaming from Twilio WebSocket connections
"""
import asyncio
import base64
import json
import logging
from typing import Dict, Optional, Any
from collections import deque
from datetime import datetime
import uuid

from api.utils.logger import setup_logger

logger = setup_logger(__name__)


class MediaStreamBuffer:
    """Buffer for managing audio chunks from media stream"""
    
    def __init__(self, max_size: int = 100):
        self.buffer = deque(maxlen=max_size)
        self.stream_sid = None
        self.call_sid = None
        self.is_active = False
        self.metadata = {}
        
    def add_chunk(self, chunk: bytes):
        """Add audio chunk to buffer"""
        self.buffer.append(chunk)
    
    def get_chunks(self, count: int = None) -> list:
        """Get chunks from buffer"""
        if count is None:
            chunks = list(self.buffer)
            self.buffer.clear()
        else:
            chunks = []
            for _ in range(min(count, len(self.buffer))):
                chunks.append(self.buffer.popleft())
        return chunks
    
    def clear(self):
        """Clear the buffer"""
        self.buffer.clear()
    
    @property
    def size(self) -> int:
        """Get current buffer size"""
        return len(self.buffer)


class MediaStreamHandler:
    """Handler for Twilio Media Stream WebSocket connections"""
    
    def __init__(self):
        self.active_streams: Dict[str, MediaStreamBuffer] = {}
        self.stream_processors: Dict[str, asyncio.Task] = {}
        
    async def handle_websocket(self, websocket, path):
        """
        Main WebSocket handler for Twilio Media Streams
        
        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        stream_sid = None
        buffer = None
        
        try:
            logger.info(f"New WebSocket connection from {websocket.remote_address}")
            
            async for message in websocket:
                data = json.loads(message)
                event_type = data.get("event")
                
                if event_type == "start":
                    stream_sid = await self._handle_start(data)
                    buffer = self.active_streams.get(stream_sid)
                    
                elif event_type == "media":
                    if buffer:
                        await self._handle_media(data, buffer)
                        
                elif event_type == "stop":
                    await self._handle_stop(stream_sid)
                    break
                    
                elif event_type == "mark":
                    await self._handle_mark(data, websocket)
                    
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            if stream_sid:
                await self._cleanup_stream(stream_sid)
            logger.info("WebSocket connection closed")
    
    async def _handle_start(self, data: Dict) -> str:
        """
        Handle stream start event
        
        Args:
            data: Start event data
            
        Returns:
            Stream SID
        """
        start_data = data.get("start", {})
        stream_sid = start_data.get("streamSid")
        call_sid = start_data.get("callSid")
        account_sid = start_data.get("accountSid")
        
        # Custom parameters passed from Twilio
        custom_params = start_data.get("customParameters", {})
        agent_id = custom_params.get("agent_id")
        from_number = custom_params.get("from_number")
        
        logger.info(f"Stream started - SID: {stream_sid}, Call: {call_sid}")
        
        # Create buffer for this stream
        buffer = MediaStreamBuffer()
        buffer.stream_sid = stream_sid
        buffer.call_sid = call_sid
        buffer.is_active = True
        buffer.metadata = {
            "account_sid": account_sid,
            "agent_id": agent_id,
            "from_number": from_number,
            "start_time": datetime.utcnow().isoformat()
        }
        
        self.active_streams[stream_sid] = buffer
        
        # Start audio processor for this stream
        processor_task = asyncio.create_task(
            self._process_audio_stream(stream_sid)
        )
        self.stream_processors[stream_sid] = processor_task
        
        return stream_sid
    
    async def _handle_media(self, data: Dict, buffer: MediaStreamBuffer):
        """
        Handle media event with audio data
        
        Args:
            data: Media event data
            buffer: Stream buffer
        """
        media_data = data.get("media", {})
        
        # Extract audio payload (base64 encoded mulaw/8000)
        payload = media_data.get("payload")
        if payload:
            # Decode base64 audio data
            audio_bytes = base64.b64decode(payload)
            
            # Add to buffer for processing
            buffer.add_chunk(audio_bytes)
            
            # Track statistics
            chunk_number = media_data.get("chunk")
            timestamp = media_data.get("timestamp")
            
            if chunk_number and chunk_number % 100 == 0:
                logger.debug(f"Received chunk {chunk_number} at {timestamp}")
    
    async def _handle_stop(self, stream_sid: str):
        """
        Handle stream stop event
        
        Args:
            stream_sid: Stream SID
        """
        logger.info(f"Stream stopped: {stream_sid}")
        
        if stream_sid in self.active_streams:
            self.active_streams[stream_sid].is_active = False
    
    async def _handle_mark(self, data: Dict, websocket):
        """
        Handle mark event (custom event markers)
        
        Args:
            data: Mark event data
            websocket: WebSocket connection
        """
        mark_data = data.get("mark", {})
        name = mark_data.get("name")
        
        logger.debug(f"Mark event received: {name}")
        
        # Send acknowledgment if needed
        if name == "audio_complete":
            response = {
                "event": "clear",
                "streamSid": data.get("streamSid")
            }
            await websocket.send(json.dumps(response))
    
    async def _process_audio_stream(self, stream_sid: str):
        """
        Process audio stream in real-time
        
        Args:
            stream_sid: Stream SID
        """
        buffer = self.active_streams.get(stream_sid)
        if not buffer:
            return
        
        logger.info(f"Starting audio processor for stream {stream_sid}")
        
        # Import services
        from api.services.voice import stt_service, tts_service, audio_processor
        from api.services.ai import conversation_service
        
        accumulated_audio = bytearray()
        silence_threshold = 1500  # ms of silence before processing
        last_activity = datetime.utcnow()
        
        try:
            while buffer.is_active:
                # Check for audio chunks
                if buffer.size > 0:
                    chunks = buffer.get_chunks(10)  # Get up to 10 chunks
                    
                    for chunk in chunks:
                        accumulated_audio.extend(chunk)
                    
                    last_activity = datetime.utcnow()
                
                # Check for silence timeout
                silence_duration = (datetime.utcnow() - last_activity).total_seconds() * 1000
                
                if len(accumulated_audio) > 0 and silence_duration > silence_threshold:
                    # Process accumulated audio
                    logger.info(f"Processing {len(accumulated_audio)} bytes of audio")
                    
                    # Convert mulaw to WAV for STT
                    wav_audio = await self._convert_mulaw_to_wav(accumulated_audio)
                    
                    if wav_audio:
                        # Transcribe audio
                        transcript = await stt_service.transcribe_audio(
                            wav_audio,
                            language="en"
                        )
                        
                        if transcript:
                            logger.info(f"Transcribed: {transcript}")
                            
                            # TODO: Generate response and synthesize speech
                            # This will be implemented in the next step
                            
                    # Clear accumulated audio
                    accumulated_audio = bytearray()
                
                # Small delay to prevent busy loop
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error processing audio stream: {e}")
        finally:
            logger.info(f"Audio processor stopped for stream {stream_sid}")
    
    async def _convert_mulaw_to_wav(self, mulaw_data: bytes) -> Optional[bytes]:
        """
        Convert mulaw audio to WAV format
        
        Args:
            mulaw_data: Mulaw encoded audio
            
        Returns:
            WAV audio bytes
        """
        try:
            import audioop
            import wave
            import io
            
            # Convert μ-law to linear PCM
            pcm_data = audioop.ulaw2lin(mulaw_data, 2)
            
            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(8000)  # 8kHz (Twilio standard)
                wav_file.writeframes(pcm_data)
            
            return wav_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error converting mulaw to WAV: {e}")
            return None
    
    async def _cleanup_stream(self, stream_sid: str):
        """
        Clean up stream resources
        
        Args:
            stream_sid: Stream SID
        """
        # Cancel processor task
        if stream_sid in self.stream_processors:
            task = self.stream_processors[stream_sid]
            if not task.done():
                task.cancel()
            del self.stream_processors[stream_sid]
        
        # Remove buffer
        if stream_sid in self.active_streams:
            del self.active_streams[stream_sid]
        
        logger.info(f"Cleaned up stream {stream_sid}")
    
    async def send_audio_to_stream(self, stream_sid: str, audio_data: bytes, websocket):
        """
        Send audio data back to Twilio stream
        
        Args:
            stream_sid: Stream SID
            audio_data: Audio data to send
            websocket: WebSocket connection
        """
        try:
            # Convert audio to mulaw if needed
            mulaw_audio = await self._convert_to_mulaw(audio_data)
            
            # Base64 encode
            encoded_audio = base64.b64encode(mulaw_audio).decode('utf-8')
            
            # Create media message
            message = {
                "event": "media",
                "streamSid": stream_sid,
                "media": {
                    "payload": encoded_audio
                }
            }
            
            await websocket.send(json.dumps(message))
            
        except Exception as e:
            logger.error(f"Error sending audio to stream: {e}")
    
    async def _convert_to_mulaw(self, audio_data: bytes) -> bytes:
        """
        Convert audio to mulaw format for Twilio
        
        Args:
            audio_data: Input audio data
            
        Returns:
            Mulaw encoded audio
        """
        try:
            import audioop
            
            # Assuming input is 16-bit PCM
            # Convert to μ-law
            mulaw_data = audioop.lin2ulaw(audio_data, 2)
            
            return mulaw_data
            
        except Exception as e:
            logger.error(f"Error converting to mulaw: {e}")
            return audio_data
    
    def get_active_streams(self) -> Dict[str, Dict]:
        """
        Get information about active streams
        
        Returns:
            Dictionary of active stream information
        """
        return {
            sid: {
                "call_sid": buffer.call_sid,
                "is_active": buffer.is_active,
                "buffer_size": buffer.size,
                "metadata": buffer.metadata
            }
            for sid, buffer in self.active_streams.items()
        }


# Singleton instance
media_stream_handler = MediaStreamHandler()