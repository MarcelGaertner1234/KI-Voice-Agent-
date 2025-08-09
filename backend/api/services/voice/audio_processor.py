"""
Audio Processing Service
Handles audio format conversion, streaming, and buffering
"""
import io
import logging
import base64
from typing import Optional, Tuple
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Service for audio processing and format conversion"""
    
    def __init__(self):
        self.supported_formats = ["mp3", "wav", "ogg", "webm", "m4a", "flac"]
        self.target_sample_rate = 16000  # Optimal for speech recognition
        self.target_channels = 1  # Mono for speech
    
    def convert_audio_format(
        self,
        audio_bytes: bytes,
        input_format: str,
        output_format: str = "wav",
        sample_rate: Optional[int] = None,
        channels: Optional[int] = None
    ) -> Optional[bytes]:
        """
        Convert audio from one format to another
        
        Args:
            audio_bytes: Input audio data
            input_format: Input audio format
            output_format: Desired output format
            sample_rate: Optional sample rate override
            channels: Optional channels override (1=mono, 2=stereo)
            
        Returns:
            Converted audio bytes or None on error
        """
        try:
            # Load audio from bytes
            audio = AudioSegment.from_file(
                io.BytesIO(audio_bytes),
                format=input_format
            )
            
            # Apply conversions
            if sample_rate:
                audio = audio.set_frame_rate(sample_rate)
            
            if channels:
                if channels == 1 and audio.channels > 1:
                    audio = audio.set_channels(1)
                elif channels == 2 and audio.channels == 1:
                    audio = audio.set_channels(2)
            
            # Export to desired format
            output_buffer = io.BytesIO()
            audio.export(output_buffer, format=output_format)
            return output_buffer.getvalue()
            
        except CouldntDecodeError:
            logger.error(f"Could not decode audio format: {input_format}")
            return None
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return None
    
    def prepare_for_stt(self, audio_bytes: bytes, input_format: str = "webm") -> bytes:
        """
        Prepare audio for speech-to-text processing
        Converts to optimal format for STT (16kHz, mono, WAV)
        
        Args:
            audio_bytes: Input audio data
            input_format: Input audio format
            
        Returns:
            Optimized audio bytes
        """
        return self.convert_audio_format(
            audio_bytes,
            input_format=input_format,
            output_format="wav",
            sample_rate=self.target_sample_rate,
            channels=self.target_channels
        ) or audio_bytes
    
    def encode_audio_base64(self, audio_bytes: bytes) -> str:
        """
        Encode audio bytes to base64 string
        
        Args:
            audio_bytes: Audio data
            
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(audio_bytes).decode('utf-8')
    
    def decode_audio_base64(self, audio_base64: str) -> bytes:
        """
        Decode base64 string to audio bytes
        
        Args:
            audio_base64: Base64 encoded audio
            
        Returns:
            Audio bytes
        """
        return base64.b64decode(audio_base64)
    
    def get_audio_duration(self, audio_bytes: bytes, format: str) -> float:
        """
        Get duration of audio in seconds
        
        Args:
            audio_bytes: Audio data
            format: Audio format
            
        Returns:
            Duration in seconds
        """
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=format)
            return len(audio) / 1000.0  # Convert ms to seconds
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0
    
    def split_audio_chunks(
        self,
        audio_bytes: bytes,
        format: str,
        chunk_duration_ms: int = 5000
    ) -> list:
        """
        Split audio into chunks for processing
        
        Args:
            audio_bytes: Audio data
            format: Audio format
            chunk_duration_ms: Chunk duration in milliseconds
            
        Returns:
            List of audio chunks
        """
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=format)
            chunks = []
            
            for i in range(0, len(audio), chunk_duration_ms):
                chunk = audio[i:i + chunk_duration_ms]
                chunk_buffer = io.BytesIO()
                chunk.export(chunk_buffer, format=format)
                chunks.append(chunk_buffer.getvalue())
            
            return chunks
        except Exception as e:
            logger.error(f"Error splitting audio: {e}")
            return []
    
    def merge_audio_chunks(
        self,
        chunks: list,
        format: str,
        output_format: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Merge multiple audio chunks into one
        
        Args:
            chunks: List of audio chunks
            format: Input format of chunks
            output_format: Optional output format
            
        Returns:
            Merged audio bytes
        """
        try:
            if not chunks:
                return None
            
            # Load first chunk
            merged = AudioSegment.from_file(io.BytesIO(chunks[0]), format=format)
            
            # Append remaining chunks
            for chunk_bytes in chunks[1:]:
                chunk = AudioSegment.from_file(io.BytesIO(chunk_bytes), format=format)
                merged += chunk
            
            # Export merged audio
            output_buffer = io.BytesIO()
            merged.export(output_buffer, format=output_format or format)
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error merging audio: {e}")
            return None
    
    def apply_noise_reduction(self, audio_bytes: bytes, format: str) -> bytes:
        """
        Apply basic noise reduction to audio
        
        Args:
            audio_bytes: Input audio
            format: Audio format
            
        Returns:
            Processed audio
        """
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=format)
            
            # Basic noise reduction through normalization
            # More advanced noise reduction would require additional libraries
            normalized = audio.normalize()
            
            # Apply basic high-pass filter to remove low-frequency noise
            # This is a simple approach; production would use more sophisticated methods
            filtered = normalized.high_pass_filter(80)
            
            output_buffer = io.BytesIO()
            filtered.export(output_buffer, format=format)
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error applying noise reduction: {e}")
            return audio_bytes
    
    def detect_silence(
        self,
        audio_bytes: bytes,
        format: str,
        silence_threshold_db: float = -40.0,
        min_silence_len_ms: int = 1000
    ) -> list:
        """
        Detect silence periods in audio
        
        Args:
            audio_bytes: Audio data
            format: Audio format
            silence_threshold_db: Silence threshold in dB
            min_silence_len_ms: Minimum silence length in ms
            
        Returns:
            List of (start_ms, end_ms) tuples for silence periods
        """
        try:
            from pydub.silence import detect_silence
            
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=format)
            silence_ranges = detect_silence(
                audio,
                min_silence_len=min_silence_len_ms,
                silence_thresh=silence_threshold_db
            )
            
            return silence_ranges
            
        except Exception as e:
            logger.error(f"Error detecting silence: {e}")
            return []


# Singleton instance
audio_processor = AudioProcessor()