#!/usr/bin/env python3
"""
Scarred Winds - Centralized Pygame Resource Manager
Manages pygame initialization and cleanup to prevent resource conflicts.
"""

import pygame
import sys
import atexit
from typing import Optional
from logger import log_info, log_error

class PygameManager:
    """Centralized manager for pygame resources to prevent conflicts."""
    
    _instance: Optional['PygameManager'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._pygame_initialized = False
            self._display_created = False
            self._mixer_initialized = False
            self._font_initialized = False
            
            # Register cleanup function
            atexit.register(self.cleanup)
    
    def initialize_pygame(self, 
                         init_mixer: bool = True, 
                         init_font: bool = True,
                         create_display: bool = False,
                         display_size: tuple = (1366, 768),
                         display_flags: int = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN) -> bool:
        """
        Initialize pygame subsystems safely.
        
        Args:
            init_mixer: Whether to initialize the mixer for audio
            init_font: Whether to initialize the font system
            create_display: Whether to create a display surface
            display_size: Size of display if creating one
            display_flags: Display flags for pygame.display.set_mode
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            if not self._pygame_initialized:
                pygame.init()
                self._pygame_initialized = True
                log_info("Pygame core initialized")
            
            if init_mixer and not self._mixer_initialized:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self._mixer_initialized = True
                log_info("Pygame mixer initialized")
            
            if init_font and not self._font_initialized:
                pygame.font.init()
                self._font_initialized = True
                log_info("Pygame font initialized")
            
            if create_display and not self._display_created:
                pygame.display.set_mode(display_size, display_flags)
                self._display_created = True
                log_info(f"Pygame display created: {display_size}")
            
            return True
            
        except pygame.error as e:
            log_error(f"Pygame initialization error: {e}")
            return False
        except Exception as e:
            log_error(f"Unexpected error during pygame initialization: {e}")
            return False
    
    def cleanup(self):
        """Clean up pygame resources."""
        try:
            if self._pygame_initialized:
                pygame.quit()
                self._pygame_initialized = False
                log_info("Pygame cleaned up")
        except Exception as e:
            log_error(f"Error during pygame cleanup: {e}")
    
    def is_initialized(self) -> bool:
        """Check if pygame is initialized."""
        return self._pygame_initialized
    
    def get_display_info(self) -> dict:
        """Get information about the current display."""
        if not self._display_created:
            return {}
        
        try:
            info = pygame.display.Info()
            return {
                'width': info.current_w,
                'height': info.current_h,
                'bitsize': info.bitsize,
                'bytesize': info.bytesize,
                'masks': info.masks,
                'shifts': info.shifts,
                'losses': info.losses
            }
        except pygame.error as e:
            log_error(f"Error getting display info: {e}")
            return {}

# Global instance
pygame_manager = PygameManager()

def safe_pygame_init(**kwargs) -> bool:
    """Safe wrapper for pygame initialization."""
    return pygame_manager.initialize_pygame(**kwargs)

def safe_pygame_quit():
    """Safe wrapper for pygame cleanup."""
    pygame_manager.cleanup()

def is_pygame_ready() -> bool:
    """Check if pygame is ready for use."""
    return pygame_manager.is_initialized()
