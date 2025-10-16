#!/usr/bin/env python3
"""
Scarred Winds - Asset Loader
Centralized asset loading and scaling system
"""

import pygame
import os
from logger import log_info, log_error, log_warning

class AssetLoader:
    """Centralized asset loading with caching and scaling."""
    
    def __init__(self):
        self.images = {}
        self.scaled_images = {}
        self.base_path = "assets/images"
        
    def load_image(self, filename, alpha=True):
        """Load an image with caching."""
        if filename in self.images:
            return self.images[filename]
        
        filepath = os.path.join(self.base_path, filename)
        
        try:
            if alpha:
                image = pygame.image.load(filepath).convert_alpha()
            else:
                image = pygame.image.load(filepath).convert()
            
            self.images[filename] = image
            log_info(f"Loaded asset: {filename}")
            return image
        except (pygame.error, FileNotFoundError) as e:
            log_error(f"Failed to load {filename}: {e}")
            # Return a placeholder surface
            placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
            placeholder.fill((255, 0, 255, 128))  # Magenta placeholder
            return placeholder
    
    def get_scaled(self, filename, scale_factor=1.0, alpha=True):
        """Get a scaled version of an image."""
        cache_key = f"{filename}_{scale_factor}"
        
        if cache_key in self.scaled_images:
            return self.scaled_images[cache_key]
        
        original = self.load_image(filename, alpha)
        
        if scale_factor == 1.0:
            return original
        
        new_width = int(original.get_width() * scale_factor)
        new_height = int(original.get_height() * scale_factor)
        
        scaled = pygame.transform.scale(original, (new_width, new_height))
        self.scaled_images[cache_key] = scaled
        
        return scaled
    
    def get_tile(self, filename, scale_factor=1.0):
        """Get a tile asset scaled appropriately for the game."""
        return self.get_scaled(filename, scale_factor, alpha=True)
    
    def get_sprite(self, filename, scale_factor=1.0):
        """Get a sprite asset with transparency."""
        return self.get_scaled(filename, scale_factor, alpha=True)
    
    def clear_cache(self):
        """Clear the asset cache to free memory."""
        self.images.clear()
        self.scaled_images.clear()
        log_info("Asset cache cleared")

# Global asset loader instance
asset_loader = AssetLoader()

# Convenience functions
def load_asset(filename, alpha=True):
    """Load an asset."""
    return asset_loader.load_image(filename, alpha)

def get_scaled_asset(filename, scale_factor=1.0, alpha=True):
    """Get a scaled asset."""
    return asset_loader.get_scaled(filename, scale_factor, alpha)
