"""
Smart Speed Control System - Audio Manager Module
================================================

Handles non-blocking audio playback for warning and regulation sounds.
Uses Panda3D audio capabilities for sound effects.

Author: IoT Development Team
Version: 1.0
"""

import config


class AudioManager:
    """
    Manages audio playback for system states.
    
    Attributes:
        enabled (bool): Whether audio is enabled
        warning_sound (AudioSound): Warning sound instance
        regulating_sound (AudioSound): Regulating sound instance
        current_playing (str): Currently playing sound state
    """
    
    def __init__(self, base=None):
        """
        Initialize audio manager.
        
        Args:
            base: Panda3D ShowBase instance
        """
        self.base = base
        self.enabled = config.ENABLE_AUDIO
        self.warning_sound = None
        self.regulating_sound = None
        self.current_playing = None
        self._load_sounds()
    
    def _load_sounds(self):
        """Load audio files (if Panda3D base is available)."""
        if not self.enabled or not self.base:
            return
        
        try:
            # Create synthetic warning sound if file not available
            # In production, you would load actual sound files
            pass
        except Exception as e:
            print(f"[Audio] Warning: Could not load sounds: {e}")
            self.enabled = False
    
    def play_warning_sound(self):
        """
        Play warning sound (non-blocking).
        Triggered when speed enters WARNING state.
        """
        if not self.enabled:
            return
        
        try:
            # Generate beep sound effect
            self._beep(frequency=1000, duration=0.2, volume=0.5)
            self.current_playing = "warning"
        except Exception as e:
            print(f"[Audio] Error playing warning sound: {e}")
    
    def play_regulating_sound(self):
        """
        Play regulating sound (non-blocking).
        Triggered when speed enters REGULATING state.
        """
        if not self.enabled:
            return
        
        try:
            # Generate alarm sound effect
            self._beep(frequency=800, duration=0.3, volume=0.7)
            self._beep(frequency=1000, duration=0.3, volume=0.7)
            self.current_playing = "regulating"
        except Exception as e:
            print(f"[Audio] Error playing regulating sound: {e}")
    
    def _beep(self, frequency=1000, duration=0.1, volume=0.5):
        """
        Generate a simple beep sound.
        
        Args:
            frequency (int): Frequency in Hz
            duration (float): Duration in seconds
            volume (float): Volume 0-1
        """
        if self.base and hasattr(self.base, 'sfxManagerFactory'):
            try:
                # This is a placeholder - actual implementation would use
                # Panda3D's audio system or external audio library
                pass
            except Exception as e:
                pass
    
    def stop_sound(self):
        """Stop currently playing sound."""
        if not self.enabled:
            return
        
        try:
            if self.warning_sound:
                self.warning_sound.stop()
            if self.regulating_sound:
                self.regulating_sound.stop()
            self.current_playing = None
        except Exception as e:
            print(f"[Audio] Error stopping sound: {e}")
    
    def set_enabled(self, enabled):
        """
        Enable or disable audio.
        
        Args:
            enabled (bool): Whether audio should be enabled
        """
        self.enabled = enabled and config.ENABLE_AUDIO
    
    def get_status(self):
        """
        Get audio manager status.
        
        Returns:
            dict: Status information including enabled flag and current sound
        """
        return {
            "enabled": self.enabled,
            "currently_playing": self.current_playing
        }
