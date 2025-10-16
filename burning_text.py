#!/usr/bin/env python3
"""
Scarred Winds - Advanced Burning Text Effect
A complete rewrite of the letter burning mechanic focusing on heat simulation,
realistic fire spread, multiple particle types, and procedural charcoal textures.
"""

import pygame
import math
import random
import numpy as np
from burning_text_state import burning_state_manager

# --- Configuration Constants ---
# Heat Simulation
HEAT_RATE = 400.0          # How quickly the mouse applies heat
COOL_RATE = 50.0           # How quickly letters cool down
IGNITION_POINT = 200.0     # Heat level required to ignite
HEAT_TRANSFER_RATE = 800.0 # How fast heat spreads between burning pixels (faster spread)

# Fire & Fuel Physics
FUEL_CONSUMPTION_RATE = 0.5 # How quickly burning pixels lose fuel per second
FIRE_SPREAD_CHANCE = 0.95   # Chance for a burning pixel to spread heat (faster spread)

# Particle Physics
PARTICLE_LIFETIME_FLAME = 0.8
PARTICLE_LIFETIME_SPARK = 0.5
PARTICLE_LIFETIME_SMOKE = 2.5
PARTICLE_SPAWN_RATE_FLAME = 3  # Reduced flame particles
PARTICLE_SPAWN_RATE_SPARK = 2  # Reduced spark particles  
PARTICLE_SPAWN_RATE_SMOKE = 1  # Reduced smoke particles
SPARK_VELOCITY = 150.0

# Ember Effect (from previous version, integrated)
PULSE_SPEED = 6.0
PULSE_INTENSITY_MIN = 0.05
PULSE_INTENSITY_MAX = 0.8
CHARCOAL_TEXTURE_VARIATION = 25
CHARCOAL_BASE_COLOR = np.array([20, 15, 15])
CHARCOAL_GLOW_COLOR = np.array([255, 140, 40])

class Particle:
    """A versatile particle for flame, sparks, and smoke."""
    def __init__(self, x, y, p_type):
        self.x = x
        self.y = y
        self.type = p_type
        self.age = 0

        if self.type == 'flame':
            self.lifetime = PARTICLE_LIFETIME_FLAME + random.uniform(-0.2, 0.2)
            self.vx = random.uniform(-15, 15)
            self.vy = random.uniform(-40, -60)
            self.gravity = 15
            self.color = random.choice([(255, 180, 100), (255, 100, 30)])
        elif self.type == 'spark':
            self.lifetime = PARTICLE_LIFETIME_SPARK + random.uniform(-0.1, 0.1)
            angle = random.uniform(0, 2 * math.pi)
            speed = SPARK_VELOCITY * (1.0 + random.uniform(-0.2, 0.2))
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.gravity = 100 # Sparks are heavier
            self.color = (255, 255, 200)
        elif self.type == 'smoke':
            self.lifetime = PARTICLE_LIFETIME_SMOKE + random.uniform(-0.5, 0.5)
            self.vx = random.uniform(-8, 8)
            self.vy = random.uniform(-15, -25)
            self.gravity = -5 # Smoke rises
            self.color = (40, 40, 45)
    
    def update(self, dt):
        """Update particle physics."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.age += dt
        return self.age >= self.lifetime

    def draw(self, surface):
        """Draw the particle with appropriate visuals."""
        if self.age >= self.lifetime:
            return
        
        progress = self.age / self.lifetime
        alpha = int(255 * (1 - progress**2))

        if self.type == 'flame':
            radius = max(1, int(5 * (1 - progress)))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius, 1)
        elif self.type == 'spark':
            radius = max(1, int(2 * (1 - progress)))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)
        elif self.type == 'smoke':
            radius = max(1, int(8 * progress)) # Smoke expands
            smoke_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(smoke_surf, (*self.color, int(alpha * 0.3)), (radius, radius), radius)
            surface.blit(smoke_surf, (int(self.x - radius), int(self.y - radius)))

class Letter:
    """Manages the state of a single burnable letter with advanced physics."""
    def __init__(self, char, pos, font, color):
        self.char = char
        self.pos = pos
        self.font = font
        self.color = color

        # Render surfaces
        self.pristine_surface = self.font.render(self.char, True, self.color)
        self.rect = self.pristine_surface.get_rect(topleft=pos)
        self.width, self.height = self.rect.size
        self.mask = pygame.mask.from_surface(self.pristine_surface)

        # State tracking arrays
        self.heat_map = np.zeros(self.rect.size, dtype=float)
        # Create fuel map only for pixels that are part of the letter
        mask_surface = self.mask.to_surface()
        mask_array = pygame.surfarray.array3d(mask_surface)[:, :, 0] > 0
        self.fuel_map = np.full(self.rect.size, 100.0, dtype=float) * mask_array
        
        # Particles
        self.particles = []

        # Cached charcoal texture
        self.charred_texture = None
        self.ember_pulse_offsets = np.random.uniform(0, 2 * math.pi, self.rect.size)
        variation = np.random.randint(-CHARCOAL_TEXTURE_VARIATION, CHARCOAL_TEXTURE_VARIATION, size=(*self.rect.size, 3))
        self.ember_base_colors = np.clip(CHARCOAL_BASE_COLOR + variation, 0, 50)

    def add_heat(self, x, y, radius, dt):
        """Add heat to a circular area on the letter."""
        local_x, local_y = x - self.rect.x, y - self.rect.y
        
        # Create a grid of coordinates and calculate distance from the heat source
        coords_x, coords_y = np.meshgrid(np.arange(self.width), np.arange(self.height), indexing='ij')
        dist_sq = (coords_x - local_x)**2 + (coords_y - local_y)**2
        
        # Apply heat in a circular area, respecting the letter's mask
        heat_mask = (dist_sq < radius**2) & (self.fuel_map > 0)
        self.heat_map[heat_mask] += HEAT_RATE * dt

    def update(self, dt, current_time):
        """Update fire spread, cooling, fuel, and particles."""
        # 1. Cooling
        self.heat_map -= COOL_RATE * dt
        np.clip(self.heat_map, 0, None, out=self.heat_map)

        # 2. Fire spread and fuel consumption
        burning_mask = (self.heat_map >= IGNITION_POINT) & (self.fuel_map > 0)
        if np.any(burning_mask):
            # Consume fuel
            fuel_consumed = FUEL_CONSUMPTION_RATE * 100 * dt
            self.fuel_map[burning_mask] -= fuel_consumed

            # Spread heat
            burning_coords = np.argwhere(burning_mask)
            for x, y in burning_coords:
                if random.random() < FIRE_SPREAD_CHANCE:
                    # Spread heat to neighbors
                    min_x, max_x = max(0, x-1), min(self.width, x+2)
                    min_y, max_y = max(0, y-1), min(self.height, y+2)
                    self.heat_map[min_x:max_x, min_y:max_y] += HEAT_TRANSFER_RATE * dt

                # Spawn particles from burning pixels
                self._spawn_particles(x, y)

        np.clip(self.fuel_map, 0, 100, out=self.fuel_map)

        # 3. Update particles
        self.particles = [p for p in self.particles if not p.update(dt)]

        # 4. Generate charcoal texture if needed
        if self.charred_texture is None and np.any(self.fuel_map < 100):
            # Check if all letter pixels have no fuel (fully burned)
            mask_surface = self.mask.to_surface()
            mask_array = pygame.surfarray.array3d(mask_surface)[:, :, 0] > 0
            if np.all(self.fuel_map[mask_array] == 0):
                self._generate_charred_texture()

    def _spawn_particles(self, x, y):
        """Spawn flame, spark, and smoke particles."""
        px, py = self.rect.x + x, self.rect.y + y
        if random.random() < PARTICLE_SPAWN_RATE_FLAME / 60.0:
            self.particles.append(Particle(px, py, 'flame'))
        if random.random() < PARTICLE_SPAWN_RATE_SPARK / 60.0:
            self.particles.append(Particle(px, py, 'spark'))
        if random.random() < PARTICLE_SPAWN_RATE_SMOKE / 60.0:
            self.particles.append(Particle(px, py, 'smoke'))

    def draw(self, surface, current_time):
        """Draw the letter in its current state."""
        render_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pixels_rgb = pygame.surfarray.pixels3d(render_surface)
        pixels_alpha = pygame.surfarray.pixels_alpha(render_surface)

        # Create a boolean mask from the pygame mask for efficient indexing
        mask_surface = self.mask.to_surface()
        bool_mask = pygame.surfarray.array3d(mask_surface)[:, :, 0] > 0

        # Apply states based on maps
        # 1. Pristine and Heating state
        pristine_mask = (self.fuel_map == 100) & bool_mask
        heating_mask = (self.fuel_map > 0) & (self.fuel_map < 100) & bool_mask
        
        # Draw pristine parts
        pixels_rgb[pristine_mask] = self.color
        pixels_alpha[pristine_mask] = 255

        # Draw heating parts with a glow
        if np.any(heating_mask):
            heat_ratio = np.clip(self.heat_map[heating_mask] / IGNITION_POINT, 0, 1)
            heat_color = np.array([255, 150, 50])  # Orange glow
            original_color = np.array(self.color)
            heated_colors = original_color + (heat_color - original_color) * heat_ratio[:, np.newaxis]
            pixels_rgb[heating_mask] = np.clip(heated_colors, 0, 255)
            pixels_alpha[heating_mask] = 255

        # 2. Charred and Ember state
        charred_mask = (self.fuel_map == 0) & bool_mask
        if np.any(charred_mask):
            if self.charred_texture:
                # Use the cached texture for performance
                charred_pixels = pygame.surfarray.pixels3d(self.charred_texture)
                pixels_rgb[charred_mask] = charred_pixels[charred_mask]
            
            # Pulsing ember effect
            pulse_values = (np.sin(current_time * PULSE_SPEED + self.ember_pulse_offsets[charred_mask]) + 1) / 2
            pulse_intensities = PULSE_INTENSITY_MIN + pulse_values * (PULSE_INTENSITY_MAX - PULSE_INTENSITY_MIN)
            
            ember_colors = self.ember_base_colors[charred_mask] + (CHARCOAL_GLOW_COLOR - self.ember_base_colors[charred_mask]) * pulse_intensities[:, np.newaxis]
            pixels_rgb[charred_mask] = np.clip(ember_colors, 0, 255)
            pixels_alpha[charred_mask] = 255

        del pixels_rgb
        del pixels_alpha
        surface.blit(render_surface, self.rect)

    def draw_particles(self, surface):
        """Draw all associated particles."""
        for p in self.particles:
            p.draw(surface)

    def _generate_charred_texture(self):
        """Generate and cache a procedural cracked charcoal texture."""
        self.charred_texture = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pixels_rgb = pygame.surfarray.pixels3d(self.charred_texture)
        
        # Base charcoal color with noise
        noise = np.random.randint(-15, 15, size=(*self.rect.size, 3))
        pixels_rgb[:,:] = np.clip(CHARCOAL_BASE_COLOR + noise, 0, 40)
        
        # Draw procedural cracks
        num_cracks = 15
        crack_points = (np.random.rand(num_cracks, 2) * np.array([self.width, self.height])).astype(int)
        
        # Simple crack generation without scipy dependency
        for i in range(num_cracks):
            start_x, start_y = crack_points[i]
            # Draw random crack lines
            for j in range(3):  # 3 segments per crack
                end_x = start_x + random.randint(-20, 20)
                end_y = start_y + random.randint(-20, 20)
                end_x = max(0, min(self.width-1, end_x))
                end_y = max(0, min(self.height-1, end_y))
                pygame.draw.line(self.charred_texture, (5, 5, 5), (start_x, start_y), (end_x, end_y), 1)
                start_x, start_y = end_x, end_y

        del pixels_rgb

class BurningText:
    """Creates a burning text effect where individual letters can be heated and burned."""
    def __init__(self, text, font, color, center_x, center_y, screen_width, screen_height):
        self.text = text
        self.font = font
        self.color = color
        
        self.letters = []
        self._initialize_letters(center_x, center_y)
        self.time = 0

    def _initialize_letters(self, center_x, center_y):
        """Render each letter and create a Letter object for it."""
        full_surface = self.font.render(self.text, True, self.color)
        full_rect = full_surface.get_rect(center=(center_x, center_y))
        
        x_offset = full_rect.x
        for char in self.text:
            if char == ' ':
                x_offset += self.font.size(' ')[0]
                self.letters.append(None)
            else:
                letter_obj = Letter(char, (x_offset, full_rect.y), self.font, self.color)
                self.letters.append(letter_obj)
                x_offset += letter_obj.rect.width
    
    def update(self, mouse_pos, dt):
        """Update heat, burn progress, and particles for all letters."""
        self.time += dt
        
        for letter in self.letters:
            if letter is None:
                continue
            
            # Add heat if mouse is over the letter
            if letter.rect.collidepoint(mouse_pos):
                letter.add_heat(mouse_pos[0], mouse_pos[1], 20, dt)
            
            letter.update(dt, self.time)
    
    def draw(self, surface):
        """Draw the burning text with all effects."""
        for letter in self.letters:
            if letter is None:
                continue
            letter.draw(surface, self.time)
        
        for letter in self.letters:
            if letter is None:
                continue
            letter.draw_particles(surface)
    
    def save_state(self, identifier):
        """Save the current state of this burning text instance."""
        burning_state_manager.save_state(identifier, self)
    
    def restore_state(self, identifier):
        """Restore a previously saved state to this burning text instance."""
        return burning_state_manager.restore_state(identifier, self)