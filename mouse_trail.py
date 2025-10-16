#!/usr/bin/env python3
"""
Scarred Winds - Flame Trail Mouse Effect
Reusable mouse trail system with ember particles
"""

import pygame
import math
import random
import opensimplex

class FlameTrail:
    """Creates a flame trail effect that follows the mouse cursor."""

    def __init__(self, screen_width=1366, screen_height=768, max_particles=25):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_particles = max_particles
        self.particles = []
        self.last_mouse_pos = (0, 0)
        self.trail_intensity = 1.0
        self.audio_reactive = True
        self.time = 0

        # Trail configuration
        self.particle_types = {
            'ember': {
                'colors': [(255, 150, 50), (255, 200, 100), (255, 100, 30)],
                'size_range': (2, 5),
                'lifetime': (1.0, 2.0),
                'velocity_range': (-30, 30),
                'gravity': 25,
                'air_resistance': 0.97
            },
            'spark': {
                'colors': [(255, 255, 200)],
                'size_range': (1, 3),
                'lifetime': (0.5, 1.0),
                'velocity_range': (-50, 50),
                'gravity': 40,
                'air_resistance': 0.95
            },
            'glow_ember': {
                'colors': [(255, 180, 100), (255, 200, 150)],
                'size_range': (2, 4),
                'lifetime': (1.5, 3.0),
                'velocity_range': (-20, 20),
                'gravity': 15,
                'air_resistance': 0.98
            }
        }

        self.current_particle_type = 'ember'

    def set_particle_type(self, particle_type):
        """Set the type of particles for the trail."""
        if particle_type in self.particle_types:
            self.current_particle_type = particle_type

    def set_audio_reactive(self, reactive, audio_intensity=0.0):
        """Set audio-reactive behavior."""
        self.audio_reactive = reactive
        if reactive:
            # Adjust trail intensity based on audio
            self.trail_intensity = 0.5 + (audio_intensity * 0.8)
        else:
            self.trail_intensity = 1.0

    def update(self, dt, mouse_pos, audio_intensity=0.0):
        """Update trail particles."""
        self.time += dt

        # Update audio reactivity
        if self.audio_reactive:
            self.trail_intensity = 0.5 + (audio_intensity * 0.8)

        # Add new particles when mouse moves significantly
        if mouse_pos != self.last_mouse_pos:
            distance = math.sqrt((mouse_pos[0] - self.last_mouse_pos[0])**2 +
                               (mouse_pos[1] - self.last_mouse_pos[1])**2)

            if distance > 3:  # Minimum movement threshold
                # Spawn multiple particles based on movement speed and audio intensity
                particle_count = max(1, int(distance / 10 * self.trail_intensity))
                particle_count = min(particle_count, 5)  # Limit per frame

                for _ in range(particle_count):
                    self._add_trail_particle(mouse_pos[0], mouse_pos[1])

        self.last_mouse_pos = mouse_pos

        # Update existing particles
        for particle in self.particles[:]:
            particle['life'] -= dt * 2
            particle['x'] += particle['velocity_x'] * dt
            particle['y'] += particle['velocity_y'] * dt
            particle['velocity_y'] += particle['gravity'] * dt
            particle['velocity_x'] *= particle['air_resistance']
            particle['velocity_y'] *= particle['air_resistance']

            # Add subtle noise for organic movement
            try:
                noise_x = opensimplex.noise2(particle['y'] * 0.01, self.time) * 5
                noise_y = opensimplex.noise2(particle['x'] * 0.01, self.time * 0.7) * 3
                particle['x'] += noise_x * dt
                particle['y'] += noise_y * dt
            except ImportError:
                # Simple fallback if opensimplex not available
                particle['x'] += math.sin(self.time + particle['offset']) * 2 * dt
                particle['y'] += math.cos(self.time * 0.7 + particle['offset']) * 1 * dt

            if particle['life'] <= 0:
                self.particles.remove(particle)

        # Limit particle count
        if len(self.particles) > self.max_particles:
            # Remove oldest particles first
            self.particles.sort(key=lambda p: p['spawn_time'])
            excess = len(self.particles) - self.max_particles
            self.particles = self.particles[excess:]

    def _add_trail_particle(self, x, y):
        """Add a new trail particle at the specified position."""
        config = self.particle_types[self.current_particle_type]

        # Create particle with slight random offset
        offset_x = random.uniform(-5, 5)
        offset_y = random.uniform(-5, 5)

        particle = {
            'x': x + offset_x,
            'y': y + offset_y,
            'life': 1.0,
            'spawn_time': self.time,
            'offset': random.uniform(0, 1000),
            'color': random.choice(config['colors']),
            'size': random.uniform(*config['size_range']),
            'lifetime': random.uniform(*config['lifetime']),
            'velocity_x': random.uniform(*config['velocity_range']) * 0.3,
            'velocity_y': random.uniform(*config['velocity_range']) * 0.3,
            'gravity': config['gravity'],
            'air_resistance': config['air_resistance']
        }

        self.particles.append(particle)

    def draw(self, surface):
        """Draw all trail particles."""
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            size = int(particle['size'] * particle['life'])

            if size > 0 and alpha > 0:
                # Draw glow effect
                for i in range(3):
                    glow_size = size * (2 - i * 0.5)
                    glow_alpha = int(alpha * 0.4 / (i + 1))
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    glow_color = (*particle['color'], glow_alpha)
                    pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), int(glow_size))
                    surface.blit(glow_surf, (int(particle['x'] - glow_size), int(particle['y'] - glow_size)))

                # Draw main particle
                particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                particle_color = (*particle['color'], alpha)
                pygame.draw.circle(particle_surf, particle_color, (size, size), size)
                surface.blit(particle_surf, (int(particle['x'] - size), int(particle['y'] - size)))

    def clear(self):
        """Clear all trail particles."""
        self.particles.clear()

    def set_intensity(self, intensity):
        """Set trail intensity (0.0 to 2.0)."""
        self.trail_intensity = max(0.0, min(2.0, intensity))

# Global flame trail instance for easy access
global_flame_trail = None

def get_flame_trail(screen_width=1366, screen_height=768):
    """Get or create the global flame trail instance."""
    global global_flame_trail
    if global_flame_trail is None:
        global_flame_trail = FlameTrail(screen_width, screen_height)
    return global_flame_trail
