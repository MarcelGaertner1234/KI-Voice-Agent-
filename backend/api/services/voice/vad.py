"""
Voice Activity Detection (VAD) Service
Advanced VAD using WebRTC and energy-based detection
"""
import numpy as np
from typing import Optional, Tuple, List
import logging
from dataclasses import dataclass
from enum import Enum

try:
    import webrtcvad
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False
    logging.warning("WebRTC VAD not available. Install with: pip install webrtcvad")

from api.utils.logger import setup_logger

logger = setup_logger(__name__)


class VADMode(Enum):
    """VAD aggressiveness modes"""
    QUALITY = 0      # Least aggressive, best quality
    LOW_BITRATE = 1  # Slightly aggressive
    AGGRESSIVE = 2   # More aggressive
    VERY_AGGRESSIVE = 3  # Most aggressive filtering


@dataclass
class VADConfig:
    """VAD configuration parameters"""
    mode: VADMode = VADMode.AGGRESSIVE
    frame_duration_ms: int = 30  # 10, 20, or 30 ms
    sample_rate: int = 8000  # 8000, 16000, 32000, or 48000 Hz
    
    # Energy-based detection parameters
    energy_threshold: float = 0.01
    zero_crossing_threshold: float = 0.1
    
    # Smoothing parameters
    speech_pad_ms: int = 300  # Pad speech with silence
    min_speech_duration_ms: int = 250  # Minimum speech duration
    max_silence_duration_ms: int = 1500  # Maximum silence in speech
    
    # Advanced parameters
    use_webrtc: bool = True
    use_energy: bool = True
    use_zero_crossing: bool = True


class VoiceActivityDetector:
    """
    Advanced Voice Activity Detection combining multiple methods
    """
    
    def __init__(self, config: Optional[VADConfig] = None):
        """
        Initialize VAD
        
        Args:
            config: VAD configuration
        """
        self.config = config or VADConfig()
        
        # Initialize WebRTC VAD if available
        self.webrtc_vad = None
        if WEBRTC_AVAILABLE and self.config.use_webrtc:
            try:
                self.webrtc_vad = webrtcvad.Vad(self.config.mode.value)
                logger.info(f"WebRTC VAD initialized with mode {self.config.mode.name}")
            except Exception as e:
                logger.error(f"Failed to initialize WebRTC VAD: {e}")
        
        # State tracking
        self.is_speech = False
        self.speech_frames = []
        self.silence_frames = 0
        self.speech_count = 0
        
        # Calculate frame sizes
        self.frame_size = int(
            self.config.sample_rate * self.config.frame_duration_ms / 1000
        )
        self.speech_pad_frames = int(
            self.config.speech_pad_ms / self.config.frame_duration_ms
        )
        self.min_speech_frames = int(
            self.config.min_speech_duration_ms / self.config.frame_duration_ms
        )
        self.max_silence_frames = int(
            self.config.max_silence_duration_ms / self.config.frame_duration_ms
        )
    
    def process_frame(self, audio_frame: bytes) -> Tuple[bool, Optional[bytes]]:
        """
        Process single audio frame
        
        Args:
            audio_frame: Audio frame bytes
            
        Returns:
            Tuple of (is_speech, complete_utterance)
        """
        # Detect speech in frame
        is_speech = self._detect_speech(audio_frame)
        
        # Update state machine
        utterance = self._update_state(audio_frame, is_speech)
        
        return is_speech, utterance
    
    def _detect_speech(self, audio_frame: bytes) -> bool:
        """
        Detect speech in audio frame using multiple methods
        
        Args:
            audio_frame: Audio frame
            
        Returns:
            True if speech detected
        """
        results = []
        
        # WebRTC VAD
        if self.webrtc_vad and self.config.use_webrtc:
            try:
                # WebRTC VAD expects specific frame sizes
                if len(audio_frame) == self.frame_size * 2:  # 16-bit audio
                    webrtc_result = self.webrtc_vad.is_speech(
                        audio_frame, self.config.sample_rate
                    )
                    results.append(webrtc_result)
            except Exception as e:
                logger.debug(f"WebRTC VAD error: {e}")
        
        # Energy-based detection
        if self.config.use_energy:
            energy_result = self._detect_by_energy(audio_frame)
            results.append(energy_result)
        
        # Zero-crossing rate detection
        if self.config.use_zero_crossing:
            zcr_result = self._detect_by_zero_crossing(audio_frame)
            results.append(zcr_result)
        
        # Combine results (majority vote or any positive)
        if results:
            # If WebRTC is available, give it more weight
            if self.webrtc_vad and len(results) > 1:
                return results[0]  # Trust WebRTC primarily
            else:
                # Otherwise, use majority vote
                return sum(results) > len(results) / 2
        
        return False
    
    def _detect_by_energy(self, audio_frame: bytes) -> bool:
        """
        Detect speech using energy threshold
        
        Args:
            audio_frame: Audio frame
            
        Returns:
            True if energy exceeds threshold
        """
        # Convert to numpy array
        audio_array = np.frombuffer(audio_frame, dtype=np.int16)
        
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_array.astype(float) ** 2))
        normalized_rms = rms / 32767.0  # Normalize for 16-bit audio
        
        return normalized_rms > self.config.energy_threshold
    
    def _detect_by_zero_crossing(self, audio_frame: bytes) -> bool:
        """
        Detect speech using zero-crossing rate
        
        Args:
            audio_frame: Audio frame
            
        Returns:
            True if ZCR indicates speech
        """
        # Convert to numpy array
        audio_array = np.frombuffer(audio_frame, dtype=np.int16)
        
        if len(audio_array) == 0:
            return False
        
        # Calculate zero-crossing rate
        zero_crossings = np.sum(np.diff(np.sign(audio_array)) != 0)
        zcr = zero_crossings / len(audio_array)
        
        # Speech typically has moderate ZCR (not too low, not too high)
        return 0.02 < zcr < 0.5
    
    def _update_state(self, audio_frame: bytes, is_speech: bool) -> Optional[bytes]:
        """
        Update VAD state machine
        
        Args:
            audio_frame: Audio frame
            is_speech: Whether speech was detected
            
        Returns:
            Complete utterance if speech ended
        """
        utterance = None
        
        if is_speech:
            if not self.is_speech:
                # Speech started
                self.is_speech = True
                self.speech_count = 0
                logger.debug("Speech started")
            
            # Add frame to speech buffer
            self.speech_frames.append(audio_frame)
            self.speech_count += 1
            self.silence_frames = 0
            
        else:
            if self.is_speech:
                # Possible end of speech
                self.silence_frames += 1
                
                # Add silence frame (for padding)
                if self.silence_frames <= self.speech_pad_frames:
                    self.speech_frames.append(audio_frame)
                
                # Check if silence duration exceeded
                if self.silence_frames >= self.max_silence_frames:
                    # Check if speech was long enough
                    if self.speech_count >= self.min_speech_frames:
                        # Return complete utterance
                        utterance = b''.join(self.speech_frames)
                        logger.info(f"Speech ended: {len(self.speech_frames)} frames")
                    
                    # Reset state
                    self.is_speech = False
                    self.speech_frames = []
                    self.speech_count = 0
                    self.silence_frames = 0
        
        return utterance
    
    def reset(self):
        """Reset VAD state"""
        self.is_speech = False
        self.speech_frames = []
        self.silence_frames = 0
        self.speech_count = 0
    
    def get_status(self) -> dict:
        """Get current VAD status"""
        return {
            "is_speech": self.is_speech,
            "speech_frames": len(self.speech_frames),
            "silence_frames": self.silence_frames,
            "config": {
                "mode": self.config.mode.name,
                "sample_rate": self.config.sample_rate,
                "frame_duration_ms": self.config.frame_duration_ms,
                "webrtc_enabled": self.webrtc_vad is not None
            }
        }


class AdaptiveVAD:
    """
    Adaptive VAD that adjusts parameters based on environment
    """
    
    def __init__(self):
        self.vad = VoiceActivityDetector()
        self.noise_level = 0.0
        self.adaptation_rate = 0.1
        
    def adapt_to_environment(self, audio_frame: bytes):
        """
        Adapt VAD parameters to current environment
        
        Args:
            audio_frame: Audio frame for analysis
        """
        # Convert to numpy array
        audio_array = np.frombuffer(audio_frame, dtype=np.int16)
        
        # Calculate current noise level
        rms = np.sqrt(np.mean(audio_array.astype(float) ** 2))
        normalized_rms = rms / 32767.0
        
        # Update noise level with exponential smoothing
        self.noise_level = (
            self.adaptation_rate * normalized_rms +
            (1 - self.adaptation_rate) * self.noise_level
        )
        
        # Adjust energy threshold based on noise level
        self.vad.config.energy_threshold = max(
            0.01,  # Minimum threshold
            self.noise_level * 2  # Adaptive threshold
        )
        
        logger.debug(f"Adapted threshold to {self.vad.config.energy_threshold:.4f}")
    
    def process_frame(self, audio_frame: bytes) -> Tuple[bool, Optional[bytes]]:
        """
        Process frame with adaptive VAD
        
        Args:
            audio_frame: Audio frame
            
        Returns:
            Tuple of (is_speech, complete_utterance)
        """
        # Adapt to environment during silence
        if not self.vad.is_speech:
            self.adapt_to_environment(audio_frame)
        
        # Process frame
        return self.vad.process_frame(audio_frame)


# Singleton instances
vad_service = VoiceActivityDetector()
adaptive_vad = AdaptiveVAD()