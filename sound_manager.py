#!/usr/bin/env python3
"""
Sound Effects Helper
Centralized sound effect loading and playing for consistent audio across the game.
"""

import pygame
import os

class SoundManager:
    """Manages loading and playing sound effects."""
    
    def __init__(self):
        """Initialize the sound manager."""
        self.sounds = {}
        self.enabled = True
        
        # Try to initialize mixer if not already initialized
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                print("Sound mixer initialized")
            except pygame.error as e:
                print(f"Could not initialize sound mixer: {e}")
                self.enabled = False
        
        # Load sounds
        self._load_sounds()
    
    def _load_sounds(self):
        """Load all sound effects."""
        if not self.enabled:
            return
        
        sound_files = {
            'button_click': 'assets/audio/sfx/button_click.wav',
            # Add more sounds here as needed
        }
        
        for name, path in sound_files.items():
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    print(f"Loaded sound: {name}")
                except pygame.error as e:
                    print(f"Could not load sound {name}: {e}")
            else:
                print(f"Sound file not found: {path}")
    
    def play(self, sound_name, volume=1.0):
        """Play a sound effect."""
        if not self.enabled or sound_name not in self.sounds:
            return
        
        try:
            sound = self.sounds[sound_name]
            sound.set_volume(volume)
            sound.play()
        except pygame.error as e:
            print(f"Could not play sound {sound_name}: {e}")
    
    def stop(self, sound_name):
        """Stop a playing sound effect."""
        if not self.enabled or sound_name not in self.sounds:
            return
        
        try:
            self.sounds[sound_name].stop()
        except pygame.error as e:
            print(f"Could not stop sound {sound_name}: {e}")
    
    def set_volume(self, sound_name, volume):
        """Set volume for a specific sound (0.0 to 1.0)."""
        if not self.enabled or sound_name not in self.sounds:
            return
        
        try:
            self.sounds[sound_name].set_volume(max(0.0, min(1.0, volume)))
        except pygame.error as e:
            print(f"Could not set volume for sound {sound_name}: {e}")

# Global sound manager instance
_sound_manager = None

def get_sound_manager():
    """Get the global sound manager instance."""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager

def play_sound(sound_name, volume=1.0):
    """Convenience function to play a sound."""
    get_sound_manager().play(sound_name, volume)
