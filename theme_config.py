#!/usr/bin/env python3
"""
Viking Creature Game - Theme Configuration
Viking-themed colors and fonts for the start screen
"""

import pygame

class ThemeConfig:
    """Viking-themed configuration for consistent UI."""

    # Font sizes and families
    FONTS = {
        'title_large': {'name': 'georgia', 'size': 120, 'bold': True},
        'title_medium': {'name': 'georgia', 'size': 80, 'bold': True},
        'title_small': {'name': 'georgia', 'size': 60, 'bold': True},
        'ui_large': {'name': 'georgia', 'size': 42, 'bold': False},
        'ui_medium': {'name': 'georgia', 'size': 32, 'bold': False},
        'ui_small': {'name': 'georgia', 'size': 24, 'bold': False},
        'body': {'name': 'georgia', 'size': 18, 'bold': False},
        'caption': {'name': 'georgia', 'size': 14, 'bold': False},
    }

    # Viking-themed color palette
    COLORS = {
        # Flame/Ember colors (warmer for Viking theme)
        'flame_core': (255, 255, 220),
        'flame_mid': (255, 180, 100),
        'flame_outer': (255, 100, 30),
        'ember_primary': (255, 150, 50),
        'ember_secondary': (255, 200, 100),
        'ember_glow': (255, 120, 40),

        # Viking background colors (dark, cold, atmospheric)
        'bg_top': (8, 12, 20),      # Dark blue-gray
        'bg_bottom': (15, 20, 30),  # Slightly lighter blue-gray
        'bg_dark': (5, 8, 15),      # Very dark blue
        'bg_light': (25, 30, 40),   # Lighter blue-gray

        # UI element colors (wooden, metallic)
        'ui_background': (40, 35, 25),    # Dark wood
        'ui_surface': (60, 50, 35),       # Medium wood
        'ui_border': (120, 100, 70),      # Light wood
        'ui_border_hover': (255, 200, 100), # Gold
        'ui_border_selected': (255, 255, 100), # Bright gold
        
        # Button colors
        'button_bg': (40, 35, 30),        # Dark button background
        'button_bg_hover': (60, 45, 35),  # Hovered button background
        'button_border': (100, 80, 60),   # Button border
        'text_highlight': (255, 200, 150), # Highlighted text
        'text_shadow': (20, 15, 10),      # Text shadow

        # Text colors (warm, readable)
        'text_primary': (220, 200, 180),   # Warm white
        'text_secondary': (180, 160, 140), # Muted warm
        'text_dark': (90, 80, 70),         # Dark warm
        'text_light': (255, 255, 200),     # Bright warm
        'text_accent': (255, 200, 150),    # Gold accent

        # State colors
        'success': (100, 255, 100),
        'warning': (255, 255, 100),
        'error': (255, 100, 100),
        'info': (100, 200, 255),

        # Material colors
        'candle_wax': (200, 185, 170),
        'wick': (25, 20, 15),
        'smoke': (60, 60, 70),      # Slightly blue-tinted smoke
        'fog': (40, 45, 55),        # Blue-gray fog
    }

    # Animation timing constants
    ANIMATION = {
        'fast': 8.0,
        'medium': 5.0,
        'slow': 3.0,
        'very_slow': 2.0,
    }

    # Particle system defaults
    PARTICLES = {
        'max_count': 100,
        'spawn_rate': 0.1,
        'lifetime': 2.0,
        'gravity': 30,
        'air_resistance': 0.98,
    }

    @classmethod
    def get_font(cls, font_key):
        """Get a pygame font object for the specified key."""
        if font_key not in cls.FONTS:
            font_key = 'ui_medium'  # Default fallback

        font_info = cls.FONTS[font_key]
        return pygame.font.SysFont(font_info['name'], font_info['size'], bold=font_info['bold'])

    @classmethod
    def get_color(cls, color_key, alpha=None):
        """Get a color tuple, optionally with alpha."""
        if color_key not in cls.COLORS:
            return (255, 255, 255)  # Default fallback

        color = cls.COLORS[color_key]
        if alpha is not None:
            return (*color, alpha)
        return color

    @classmethod
    def get_animation_speed(cls, speed_key):
        """Get animation speed multiplier."""
        return cls.ANIMATION.get(speed_key, cls.ANIMATION['medium'])

# Global theme instance
theme = ThemeConfig()
