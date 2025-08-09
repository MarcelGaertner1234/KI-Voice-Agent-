"""
Integration tests for Voice Pipeline
Tests audio processing, VAD, STT/TTS, and WebSocket streaming
"""
import pytest
import asyncio
import json
import base64
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from api.services.voice.media_stream import MediaStreamHandler, MediaStreamBuffer
from api.services.voice.audio_buffer import AudioBuffer, StreamingAudioProcessor
from api.services.voice.vad import VoiceActivityDetector, VADConfig, VADMode
from api.services.voice.stt import STTService
from api.services.voice.tts import TTSService


class TestMediaStreamBuffer:
    """Test MediaStreamBuffer functionality"""
    
    def test_buffer_initialization(self):
        """Test buffer initialization"""
        buffer = MediaStreamBuffer(max_size=50)
        
        assert buffer.size == 0
        assert buffer.stream_sid is None
        assert buffer.call_sid is None
        assert not buffer.is_active
    
    def test_add_and_get_chunks(self):
        """Test adding and retrieving chunks"""
        buffer = MediaStreamBuffer()
        
        # Add chunks
        chunk1 = b"audio_data_1"
        chunk2 = b"audio_data_2"
        chunk3 = b"audio_data_3"
        
        buffer.add_chunk(chunk1)
        buffer.add_chunk(chunk2)
        buffer.add_chunk(chunk3)
        
        assert buffer.size == 3
        
        # Get specific number of chunks
        chunks = buffer.get_chunks(2)
        assert len(chunks) == 2
        assert chunks[0] == chunk1
        assert chunks[1] == chunk2
        assert buffer.size == 1
        
        # Get all remaining chunks
        chunks = buffer.get_chunks()
        assert len(chunks) == 1
        assert chunks[0] == chunk3
        assert buffer.size == 0
    
    def test_buffer_max_size(self):
        """Test buffer max size constraint"""
        buffer = MediaStreamBuffer(max_size=2)
        
        buffer.add_chunk(b"1")
        buffer.add_chunk(b"2")
        buffer.add_chunk(b"3")  # Should evict "1"
        
        chunks = buffer.get_chunks()
        assert len(chunks) == 2
        assert chunks[0] == b"2"
        assert chunks[1] == b"3"


class TestAudioBuffer:
    """Test AudioBuffer with VAD"""
    
    def generate_audio_samples(self, frequency=440, duration_ms=100, sample_rate=8000, amplitude=0.5):
        """Generate test audio samples"""
        duration_seconds = duration_ms / 1000
        num_samples = int(sample_rate * duration_seconds)
        t = np.linspace(0, duration_seconds, num_samples)
        
        # Generate sine wave
        audio = amplitude * np.sin(2 * np.pi * frequency * t)
        
        # Convert to 16-bit PCM
        audio_int16 = (audio * 32767).astype(np.int16)
        return audio_int16.tobytes()
    
    def test_buffer_initialization(self):
        """Test audio buffer initialization"""
        buffer = AudioBuffer(
            sample_rate=8000,
            chunk_duration_ms=20,
            silence_threshold=0.01
        )
        
        assert buffer.sample_rate == 8000
        assert buffer.chunk_duration_ms == 20
        assert not buffer.is_speaking
        assert buffer.total_audio_duration == 0
    
    def test_voice_activity_detection(self):
        """Test VAD in audio buffer"""
        buffer = AudioBuffer(
            sample_rate=8000,
            chunk_duration_ms=20,
            silence_threshold=0.01,
            silence_duration_ms=500
        )
        
        # Generate speech-like audio (higher amplitude)
        speech_audio = self.generate_audio_samples(
            frequency=200,
            duration_ms=100,
            amplitude=0.5
        )
        
        # Generate silence (low amplitude)
        silence_audio = self.generate_audio_samples(
            frequency=100,
            duration_ms=600,  # Longer than silence threshold
            amplitude=0.001
        )
        
        # Add speech
        result = buffer.add_audio(speech_audio)
        assert result is None  # Still speaking
        assert buffer.is_speaking
        
        # Add silence to trigger end of speech
        result = buffer.add_audio(silence_audio)
        assert result is not None  # Utterance complete
        assert not buffer.is_speaking
    
    def test_buffer_statistics(self):
        """Test buffer statistics tracking"""
        buffer = AudioBuffer(sample_rate=8000)
        
        # Add some audio
        audio = self.generate_audio_samples(duration_ms=1000)
        buffer.add_audio(audio)
        
        status = buffer.get_buffer_status()
        
        assert "buffer_size" in status
        assert "is_speaking" in status
        assert "total_audio_duration" in status
        assert "speech_ratio" in status


class TestVoiceActivityDetector:
    """Test VAD service"""
    
    def generate_frame(self, is_speech=True, sample_rate=8000, duration_ms=30):
        """Generate test audio frame"""
        num_samples = int(sample_rate * duration_ms / 1000)
        
        if is_speech:
            # Generate speech-like signal
            frequency = 200 + np.random.randint(-50, 50)
            t = np.linspace(0, duration_ms/1000, num_samples)
            audio = 0.3 * np.sin(2 * np.pi * frequency * t)
            # Add some noise
            audio += 0.05 * np.random.randn(num_samples)
        else:
            # Generate silence/noise
            audio = 0.001 * np.random.randn(num_samples)
        
        audio_int16 = (audio * 32767).astype(np.int16)
        return audio_int16.tobytes()
    
    def test_vad_initialization(self):
        """Test VAD initialization"""
        config = VADConfig(
            mode=VADMode.AGGRESSIVE,
            sample_rate=8000,
            frame_duration_ms=30
        )
        vad = VoiceActivityDetector(config)
        
        assert vad.config.mode == VADMode.AGGRESSIVE
        assert vad.config.sample_rate == 8000
        assert not vad.is_speech
    
    def test_speech_detection(self):
        """Test speech detection"""
        vad = VoiceActivityDetector()
        
        # Test with speech frame
        speech_frame = self.generate_frame(is_speech=True)
        is_speech, utterance = vad.process_frame(speech_frame)
        
        # May or may not detect speech immediately
        # depending on thresholds
        
        # Test with silence frame
        silence_frame = self.generate_frame(is_speech=False)
        is_speech, utterance = vad.process_frame(silence_frame)
        
        assert not is_speech or vad.silence_frames > 0
    
    def test_utterance_detection(self):
        """Test complete utterance detection"""
        config = VADConfig(
            min_speech_duration_ms=100,
            max_silence_duration_ms=200,
            frame_duration_ms=20
        )
        vad = VoiceActivityDetector(config)
        
        # Generate speech frames
        for _ in range(10):  # 200ms of speech
            speech_frame = self.generate_frame(is_speech=True)
            is_speech, utterance = vad.process_frame(speech_frame)
            assert utterance is None  # Still in speech
        
        # Generate silence frames to end speech
        for i in range(15):  # 300ms of silence
            silence_frame = self.generate_frame(is_speech=False)
            is_speech, utterance = vad.process_frame(silence_frame)
            
            if i >= 10:  # After max_silence_duration_ms
                assert utterance is not None
                break


@pytest.mark.asyncio
class TestStreamingAudioProcessor:
    """Test streaming audio processor"""
    
    async def test_processor_initialization(self):
        """Test processor initialization"""
        processor = StreamingAudioProcessor()
        
        assert len(processor.audio_buffers) == 0
        assert len(processor.processing_tasks) == 0
    
    async def test_start_stop_stream(self):
        """Test starting and stopping stream"""
        processor = StreamingAudioProcessor()
        
        stream_id = "test_stream_123"
        call_sid = "call_456"
        agent_id = "agent_789"
        
        # Start stream
        await processor.start_stream(stream_id, call_sid, agent_id)
        
        assert stream_id in processor.audio_buffers
        assert stream_id in processor.processing_tasks
        
        # Stop stream
        await processor.stop_stream(stream_id)
        
        assert stream_id not in processor.audio_buffers
        assert stream_id not in processor.processing_tasks
    
    @patch('api.services.voice.stt.stt_service.transcribe_audio')
    async def test_audio_transcription(self, mock_transcribe):
        """Test audio transcription flow"""
        mock_transcribe.return_value = "Hello, this is a test"
        
        processor = StreamingAudioProcessor()
        stream_id = "test_stream"
        
        await processor.start_stream(stream_id, "call_123", "agent_456")
        
        # Generate test audio that triggers utterance
        audio_data = np.random.bytes(1000)
        
        # Mock the buffer to return utterance
        with patch.object(processor.audio_buffers[stream_id], 'add_audio', return_value=audio_data):
            result = await processor.add_audio(stream_id, audio_data)
            
            assert result is not None
            assert result["transcript"] == "Hello, this is a test"
            assert result["stream_id"] == stream_id
        
        await processor.stop_stream(stream_id)


@pytest.mark.asyncio
class TestMediaStreamHandler:
    """Test media stream handler"""
    
    async def test_websocket_start_event(self):
        """Test handling start event"""
        handler = MediaStreamHandler()
        
        # Create mock websocket
        mock_ws = AsyncMock()
        
        # Simulate start event
        start_data = {
            "event": "start",
            "start": {
                "streamSid": "stream_123",
                "callSid": "call_456",
                "accountSid": "account_789",
                "customParameters": {
                    "agent_id": "agent_001",
                    "from_number": "+1234567890"
                }
            }
        }
        
        stream_sid = await handler._handle_start(start_data)
        
        assert stream_sid == "stream_123"
        assert stream_sid in handler.active_streams
        
        buffer = handler.active_streams[stream_sid]
        assert buffer.call_sid == "call_456"
        assert buffer.metadata["agent_id"] == "agent_001"
    
    async def test_websocket_media_event(self):
        """Test handling media event"""
        handler = MediaStreamHandler()
        
        # Create buffer
        buffer = MediaStreamBuffer()
        buffer.stream_sid = "stream_123"
        handler.active_streams["stream_123"] = buffer
        
        # Simulate media event
        audio_payload = base64.b64encode(b"test_audio_data").decode()
        media_data = {
            "event": "media",
            "media": {
                "payload": audio_payload,
                "chunk": 1,
                "timestamp": "123456"
            }
        }
        
        await handler._handle_media(media_data, buffer)
        
        assert buffer.size > 0
        chunks = buffer.get_chunks()
        assert base64.b64decode(audio_payload) in chunks
    
    async def test_mulaw_conversion(self):
        """Test mulaw audio conversion"""
        handler = MediaStreamHandler()
        
        # Generate test PCM data
        pcm_data = np.array([0, 1000, -1000, 5000, -5000], dtype=np.int16).tobytes()
        
        # Convert to mulaw
        mulaw_data = await handler._convert_to_mulaw(pcm_data)
        
        assert mulaw_data is not None
        assert len(mulaw_data) > 0
        
        # Convert back to WAV
        wav_data = await handler._convert_mulaw_to_wav(mulaw_data)
        
        assert wav_data is not None
        assert len(wav_data) > 0


@pytest.mark.asyncio
class TestSTTService:
    """Test Speech-to-Text service"""
    
    @patch('httpx.AsyncClient.post')
    async def test_transcribe_audio(self, mock_post):
        """Test audio transcription"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"text": "Test transcription"}
        mock_post.return_value = mock_response
        
        service = STTService()
        service.api_key = "test_key"
        
        audio_data = b"test_audio_data"
        result = await service.transcribe_audio(audio_data)
        
        assert result == "Test transcription"
        mock_post.assert_called_once()
    
    async def test_transcribe_without_api_key(self):
        """Test transcription without API key"""
        service = STTService()
        service.api_key = None
        
        result = await service.transcribe_audio(b"test_audio")
        assert result == ""


@pytest.mark.asyncio
class TestTTSService:
    """Test Text-to-Speech service"""
    
    @patch('httpx.AsyncClient.post')
    async def test_synthesize_speech(self, mock_post):
        """Test speech synthesis"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"synthesized_audio_data"
        mock_post.return_value = mock_response
        
        service = TTSService()
        service.api_key = "test_key"
        
        text = "Hello, this is a test"
        result = await service.synthesize_speech(text)
        
        assert result == b"synthesized_audio_data"
        mock_post.assert_called_once()
    
    async def test_synthesize_without_api_key(self):
        """Test synthesis without API key"""
        service = TTSService()
        service.api_key = None
        
        result = await service.synthesize_speech("Test text")
        assert result == b""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])