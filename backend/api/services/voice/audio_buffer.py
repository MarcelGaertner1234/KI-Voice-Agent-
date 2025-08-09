"""
Real-time Audio Buffer System
Optimized buffering for streaming audio with Voice Activity Detection
"""
import asyncio
import numpy as np
from collections import deque
from typing import Optional, Tuple, List
from datetime import datetime, timedelta
import logging

from api.utils.logger import setup_logger

logger = setup_logger(__name__)


class AudioBuffer:
    """
    Circular buffer for real-time audio streaming
    Handles chunking, silence detection, and VAD
    """
    
    def __init__(
        self,
        sample_rate: int = 8000,
        chunk_duration_ms: int = 20,
        buffer_duration_ms: int = 2000,
        silence_threshold: float = 0.01,
        silence_duration_ms: int = 1500
    ):
        """
        Initialize audio buffer
        
        Args:
            sample_rate: Audio sample rate in Hz
            chunk_duration_ms: Duration of each audio chunk in ms
            buffer_duration_ms: Total buffer duration in ms
            silence_threshold: RMS threshold for silence detection
            silence_duration_ms: Duration of silence before triggering
        """
        self.sample_rate = sample_rate
        self.chunk_duration_ms = chunk_duration_ms
        self.buffer_duration_ms = buffer_duration_ms
        self.silence_threshold = silence_threshold
        self.silence_duration_ms = silence_duration_ms
        
        # Calculate sizes
        self.chunk_size = int(sample_rate * chunk_duration_ms / 1000)
        self.buffer_size = int(sample_rate * buffer_duration_ms / 1000)
        self.silence_chunks = int(silence_duration_ms / chunk_duration_ms)
        
        # Initialize buffer
        self.buffer = deque(maxlen=self.buffer_size)
        self.chunk_buffer = bytearray()
        
        # State tracking
        self.is_speaking = False
        self.silence_counter = 0
        self.speech_start_time = None
        self.last_speech_time = None
        
        # Statistics
        self.total_audio_duration = 0
        self.total_speech_duration = 0
        
    def add_audio(self, audio_bytes: bytes) -> Optional[bytes]:
        """
        Add audio to buffer and return complete utterance when detected
        
        Args:
            audio_bytes: Raw audio bytes
            
        Returns:
            Complete utterance bytes when silence is detected, None otherwise
        """
        # Add to chunk buffer
        self.chunk_buffer.extend(audio_bytes)
        
        # Process complete chunks
        utterance = None
        while len(self.chunk_buffer) >= self.chunk_size * 2:  # 16-bit audio
            # Extract chunk
            chunk = self.chunk_buffer[:self.chunk_size * 2]
            self.chunk_buffer = self.chunk_buffer[self.chunk_size * 2:]
            
            # Convert to numpy array (16-bit PCM)
            audio_array = np.frombuffer(chunk, dtype=np.int16)
            
            # Add to circular buffer
            self.buffer.extend(audio_array)
            
            # Detect voice activity
            is_speech = self._detect_voice_activity(audio_array)
            
            # Handle state transitions
            if is_speech:
                if not self.is_speaking:
                    # Speech started
                    self.is_speaking = True
                    self.speech_start_time = datetime.utcnow()
                    self.silence_counter = 0
                    logger.debug("Speech started")
                
                self.last_speech_time = datetime.utcnow()
                self.silence_counter = 0
                
            else:
                if self.is_speaking:
                    self.silence_counter += 1
                    
                    # Check if silence duration exceeded
                    if self.silence_counter >= self.silence_chunks:
                        # Speech ended, return utterance
                        self.is_speaking = False
                        utterance = self._get_utterance()
                        
                        # Update statistics
                        if self.speech_start_time:
                            duration = (datetime.utcnow() - self.speech_start_time).total_seconds()
                            self.total_speech_duration += duration
                            logger.info(f"Speech ended, duration: {duration:.2f}s")
                        
                        self.speech_start_time = None
            
            # Update total duration
            self.total_audio_duration += self.chunk_duration_ms / 1000
        
        return utterance
    
    def _detect_voice_activity(self, audio_chunk: np.ndarray) -> bool:
        """
        Detect voice activity in audio chunk
        
        Args:
            audio_chunk: Audio samples as numpy array
            
        Returns:
            True if voice detected, False otherwise
        """
        # Calculate RMS (Root Mean Square) energy
        rms = np.sqrt(np.mean(audio_chunk.astype(float) ** 2))
        
        # Normalize to 0-1 range (16-bit audio max is 32767)
        normalized_rms = rms / 32767.0
        
        # Check against threshold
        is_speech = normalized_rms > self.silence_threshold
        
        # Advanced VAD using zero-crossing rate
        if not is_speech and len(audio_chunk) > 0:
            # Calculate zero-crossing rate
            zero_crossings = np.sum(np.diff(np.sign(audio_chunk)) != 0)
            zcr = zero_crossings / len(audio_chunk)
            
            # Speech typically has higher ZCR than silence
            if zcr > 0.1:  # Threshold for zero-crossing rate
                is_speech = True
        
        return is_speech
    
    def _get_utterance(self) -> bytes:
        """
        Get the complete utterance from buffer
        
        Returns:
            Audio bytes of the utterance
        """
        # Convert buffer to bytes
        audio_array = np.array(self.buffer, dtype=np.int16)
        return audio_array.tobytes()
    
    def get_buffer_status(self) -> dict:
        """
        Get current buffer status
        
        Returns:
            Dictionary with buffer statistics
        """
        return {
            "buffer_size": len(self.buffer),
            "is_speaking": self.is_speaking,
            "silence_counter": self.silence_counter,
            "total_audio_duration": self.total_audio_duration,
            "total_speech_duration": self.total_speech_duration,
            "speech_ratio": self.total_speech_duration / max(self.total_audio_duration, 1)
        }
    
    def clear(self):
        """Clear the buffer"""
        self.buffer.clear()
        self.chunk_buffer = bytearray()
        self.is_speaking = False
        self.silence_counter = 0
        self.speech_start_time = None


class StreamingAudioProcessor:
    """
    Process audio stream with real-time transcription and synthesis
    """
    
    def __init__(self):
        self.audio_buffers: dict = {}  # Buffer per stream
        self.processing_tasks: dict = {}  # Processing tasks per stream
        
    async def start_stream(self, stream_id: str, call_sid: str, agent_id: str):
        """
        Start processing audio stream
        
        Args:
            stream_id: Unique stream identifier
            call_sid: Call SID
            agent_id: Agent handling the call
        """
        # Create audio buffer for this stream
        self.audio_buffers[stream_id] = AudioBuffer()
        
        # Start processing task
        self.processing_tasks[stream_id] = asyncio.create_task(
            self._process_stream(stream_id, call_sid, agent_id)
        )
        
        logger.info(f"Started audio processing for stream {stream_id}")
    
    async def add_audio(self, stream_id: str, audio_bytes: bytes) -> Optional[dict]:
        """
        Add audio to stream buffer
        
        Args:
            stream_id: Stream identifier
            audio_bytes: Audio data
            
        Returns:
            Transcription result if utterance complete
        """
        if stream_id not in self.audio_buffers:
            logger.warning(f"Unknown stream: {stream_id}")
            return None
        
        buffer = self.audio_buffers[stream_id]
        utterance = buffer.add_audio(audio_bytes)
        
        if utterance:
            # Process complete utterance
            from api.services.voice import stt_service
            
            # Transcribe utterance
            transcript = await stt_service.transcribe_audio(utterance)
            
            if transcript:
                logger.info(f"Transcribed: {transcript}")
                return {
                    "stream_id": stream_id,
                    "transcript": transcript,
                    "timestamp": datetime.utcnow().isoformat(),
                    "duration": len(utterance) / (buffer.sample_rate * 2)  # 16-bit audio
                }
        
        return None
    
    async def _process_stream(self, stream_id: str, call_sid: str, agent_id: str):
        """
        Process audio stream continuously
        
        Args:
            stream_id: Stream identifier
            call_sid: Call SID
            agent_id: Agent ID
        """
        from api.services.ai import conversation_service
        from api.services.voice import tts_service
        from api.services.websocket import websocket_manager
        
        try:
            while stream_id in self.audio_buffers:
                # Wait for audio processing
                await asyncio.sleep(0.1)
                
                # Check buffer status
                buffer = self.audio_buffers.get(stream_id)
                if buffer:
                    status = buffer.get_buffer_status()
                    
                    # Send status update to dashboard
                    await websocket_manager.broadcast_to_dashboards({
                        "type": "stream_status",
                        "stream_id": stream_id,
                        "call_sid": call_sid,
                        "status": status,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
        except Exception as e:
            logger.error(f"Error processing stream {stream_id}: {e}")
        finally:
            logger.info(f"Stream processing ended for {stream_id}")
    
    async def stop_stream(self, stream_id: str):
        """
        Stop processing audio stream
        
        Args:
            stream_id: Stream identifier
        """
        # Cancel processing task
        if stream_id in self.processing_tasks:
            task = self.processing_tasks[stream_id]
            if not task.done():
                task.cancel()
            del self.processing_tasks[stream_id]
        
        # Remove buffer
        if stream_id in self.audio_buffers:
            del self.audio_buffers[stream_id]
        
        logger.info(f"Stopped audio processing for stream {stream_id}")
    
    def get_active_streams(self) -> List[str]:
        """Get list of active stream IDs"""
        return list(self.audio_buffers.keys())
    
    def get_stream_status(self, stream_id: str) -> Optional[dict]:
        """Get status of specific stream"""
        if stream_id in self.audio_buffers:
            return self.audio_buffers[stream_id].get_buffer_status()
        return None


# Singleton instance
streaming_processor = StreamingAudioProcessor()