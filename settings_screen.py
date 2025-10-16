#!/usr/bin/env python3
"""
Scarred Winds - Settings UI
Features ember-themed sliders and toggles
"""

import pygame
import sys
import math
import random
import opensimplex
from theme_config import theme
from mouse_trail import FlameTrail
from sound_manager import play_sound


class ScreenBurnTransition:
    """Handles the full-screen burn transition effect."""
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.burn_progress = 0.0  # 0.0 to 1.0
        self.burn_speed = 2.0  # Fast (0.5s duration)
        self.complete = False
        self.active = False
        self.time = 0.0
        self.reverse_mode = False  # True for inward burn (Escape), False for outward burn (button click)
        self.black_fade_alpha = 0.0  # Black screen fade alpha (0-255)
        self.black_fade_speed = 8.0  # Fast fade speed
        
        # Center-outward burn
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2
        self.max_radius = math.sqrt((screen_width/2)**2 + (screen_height/2)**2)
        
        # Noise generator for organic burn edge
        self.noise = opensimplex.OpenSimplex(seed=42)
        
        # Particle systems
        self.fire_particles = []
        self.smoke_particles = []
        self.ember_sparks = []
        
    def start(self, reverse_mode=False):
        """Start the burn transition."""
        self.active = True
        self.reverse_mode = reverse_mode
        self.burn_progress = 0.0 if not reverse_mode else 1.0  # Start from center for normal, from edge for reverse
        self.complete = False
        self.time = 0.0
        self.black_fade_alpha = 0.0
        self.fire_particles.clear()
        self.smoke_particles.clear()
        self.ember_sparks.clear()
    
    def _generate_organic_burn_points(self, base_radius):
        """Generate organic, noisy burn edge points using opensimplex noise."""
        burn_points = []
        num_points = 120  # More points for smoother, more detailed shape
        
        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            
            # Use noise to vary the radius dynamically
            noise_val = self.noise.noise2(
                math.cos(angle) * 2 + self.time * 0.5, 
                math.sin(angle) * 2 + self.time * 0.5
            )
            
            # The radius varies around the base radius (0.2 controls jaggedness)
            noisy_radius = base_radius * (1 + noise_val * 0.3)
            
            x = self.center_x + math.cos(angle) * noisy_radius
            y = self.center_y + math.sin(angle) * noisy_radius
            burn_points.append((x, y))
        
        return burn_points
        
    def update(self, dt):
        """Update burn animation and particles."""
        if not self.active:
            return
            
        self.time += dt
        
        # Handle black fade after burn completes
        if self.complete:
            self.black_fade_alpha += self.black_fade_speed * dt * 255
            if self.black_fade_alpha >= 255:
                self.black_fade_alpha = 255
                return  # Ready to transition
            else:
                return  # Still fading
        
        # Update burn progress based on mode
        if self.reverse_mode:
            # Reverse mode: burn inward from edges to center
            self.burn_progress -= self.burn_speed * dt
            if self.burn_progress <= 0.0:
                self.burn_progress = 0.0
                self.complete = True
        else:
            # Normal mode: burn outward from center to edges
            self.burn_progress += self.burn_speed * dt
            if self.burn_progress >= 1.0:
                self.burn_progress = 1.0
                self.complete = True
        
        # Calculate current burn radius
        current_radius = self.burn_progress * self.max_radius
        
        # Generate organic burn points for more realistic particle spawning
        burn_points = self._generate_organic_burn_points(current_radius)
        
        # Spawn particles along organic burn edge
        if random.random() < 0.95:  # Very high spawn rate for dramatic effect
            # Pick random point along the organic edge
            if len(burn_points) > 0:
                point_index = random.randint(0, len(burn_points) - 1)
                edge_x, edge_y = burn_points[point_index]
                
                # Calculate perpendicular direction for more realistic ejection
                if point_index < len(burn_points) - 1:
                    next_point = burn_points[point_index + 1]
                else:
                    next_point = burn_points[0]
                
                # Vector perpendicular to edge
                dx = next_point[0] - edge_x
                dy = next_point[1] - edge_y
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0:
                    # Perpendicular vector (rotated 90 degrees)
                    perp_x = -dy / length
                    perp_y = dx / length
                else:
                    perp_x = 1
                    perp_y = 0
                
                # Fire particles with perpendicular ejection
                self.fire_particles.append({
                    'x': edge_x + random.uniform(-3, 3),
                    'y': edge_y + random.uniform(-3, 3),
                    'life': 1.0,
                    'velocity_y': perp_y * random.uniform(60, 100) + random.uniform(-20, -40),
                    'velocity_x': perp_x * random.uniform(60, 100) + random.uniform(-15, 15),
                    'size': random.uniform(4, 8),
                    'color': random.choice([
                        theme.get_color('flame_core'),
                        theme.get_color('flame_mid'),
                        theme.get_color('flame_outer')
                    ])
                })
        
        # Spawn smoke particles inside burn area (increased density)
        if random.random() < 0.8:  # Higher spawn rate for thicker smoke
            # Random point inside burn area
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, current_radius * 0.9)
            smoke_x = self.center_x + math.cos(angle) * distance
            smoke_y = self.center_y + math.sin(angle) * distance
            
            self.smoke_particles.append({
                'x': smoke_x,
                'y': smoke_y,
                'life': 1.0,
                'velocity_y': random.uniform(-25, -45),
                'velocity_x': random.uniform(-8, 8),
                'size': random.uniform(5, 10),
                'color': theme.get_color('smoke')
            })
        
        # Spawn ember sparks with perpendicular ejection
        if random.random() < 0.6:  # Higher spawn rate for more violent effect
            if len(burn_points) > 0:
                point_index = random.randint(0, len(burn_points) - 1)
                edge_x, edge_y = burn_points[point_index]
                
                # Calculate perpendicular direction
                if point_index < len(burn_points) - 1:
                    next_point = burn_points[point_index + 1]
                else:
                    next_point = burn_points[0]
                
                dx = next_point[0] - edge_x
                dy = next_point[1] - edge_y
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0:
                    perp_x = -dy / length
                    perp_y = dx / length
                else:
                    perp_x = 1
                    perp_y = 0
                
                # Sparks fly perpendicular to edge with high velocity
                spark_speed = random.uniform(120, 180)
                
                self.ember_sparks.append({
                    'x': edge_x,
                    'y': edge_y,
                    'life': 1.0,
                    'velocity_y': perp_y * spark_speed + random.uniform(-30, 30),
                    'velocity_x': perp_x * spark_speed + random.uniform(-30, 30),
                    'size': random.uniform(2, 4),
                    'color': theme.get_color('flame_core')
                })
        
        # Update fire particles
        for particle in self.fire_particles[:]:
            particle['life'] -= dt * 2.5
            particle['y'] += particle['velocity_y'] * dt
            particle['x'] += particle['velocity_x'] * dt
            particle['velocity_y'] += 25 * dt  # Gravity
            if particle['life'] <= 0:
                self.fire_particles.remove(particle)
        
        # Update smoke particles
        for particle in self.smoke_particles[:]:
            particle['life'] -= dt * 1.2
            particle['y'] += particle['velocity_y'] * dt
            particle['x'] += particle['velocity_x'] * dt
            particle['velocity_y'] += 8 * dt  # Light gravity
            if particle['life'] <= 0:
                self.smoke_particles.remove(particle)
        
        # Update spark particles
        for particle in self.ember_sparks[:]:
            particle['life'] -= dt * 3.0
            particle['y'] += particle['velocity_y'] * dt
            particle['x'] += particle['velocity_x'] * dt
            particle['velocity_y'] += 40 * dt  # Heavy gravity
            if particle['life'] <= 0:
                self.ember_sparks.remove(particle)
    
    def draw(self, surface):
        """Draw the organic burning effect with charred edge."""
        if not self.active:
            return
        
        # Draw fire particles with enhanced glow
        for particle in self.fire_particles:
            alpha = int(255 * particle['life'])
            size = int(particle['size'] * particle['life'])
            if size > 0:
                # Enhanced glow effect with more layers
                for i in range(4):
                    glow_size = size * (4 - i)
                    glow_alpha = int(alpha * 0.4 / (i + 1))
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*particle['color'], glow_alpha), (glow_size, glow_size), glow_size)
                    surface.blit(glow_surf, (int(particle['x'] - glow_size), int(particle['y'] - glow_size)))
        
        # Draw smoke particles with enhanced size
        for particle in self.smoke_particles:
            alpha = int(220 * particle['life'])
            size = int(particle['size'] * particle['life'])
            if size > 0:
                smoke_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(smoke_surf, (*particle['color'], alpha), (size, size), size)
                surface.blit(smoke_surf, (int(particle['x'] - size), int(particle['y'] - size)))
        
        # Draw spark particles with trail effect
        for particle in self.ember_sparks:
            alpha = int(255 * particle['life'])
            size = int(particle['size'] * particle['life'])
            if size > 0:
                # Draw spark with trail
                for i in range(3):
                    trail_size = size * (3 - i) * 0.7
                    trail_alpha = int(alpha * 0.3 / (i + 1))
                    spark_surf = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(spark_surf, (*particle['color'], trail_alpha), (trail_size, trail_size), trail_size)
                    surface.blit(spark_surf, (int(particle['x'] - trail_size), int(particle['y'] - trail_size)))
        
        # Draw organic burn edge with layered glow (same for both modes)
        if self.burn_progress > 0 and self.burn_progress < 1.0:
            current_radius = self.burn_progress * self.max_radius
            burn_points = self._generate_organic_burn_points(current_radius)
            
            if len(burn_points) > 2:
                # 1. Thick ember glow just outside the burn hole
                ember_color = theme.get_color('ember_glow')
                pygame.draw.polygon(surface, (*ember_color, 100), burn_points, width=20)
                
                # 2. Medium fire line at the edge
                flame_color = theme.get_color('flame_mid')
                pulse = (math.sin(self.time * 12) + 1) / 2
                edge_alpha = int(180 * (0.7 + 0.3 * pulse))
                pygame.draw.polygon(surface, (*flame_color, edge_alpha), burn_points, width=8)
                
                # 3. Bright core line
                core_color = theme.get_color('flame_core')
                core_pulse = (math.sin(self.time * 15) + 1) / 2
                core_alpha = int(220 * (0.8 + 0.2 * core_pulse))
                pygame.draw.polygon(surface, (*core_color, core_alpha), burn_points, width=3)
                
                # 4. White-hot inner edge
                white_hot = (255, 255, 255)
                white_pulse = (math.sin(self.time * 20) + 1) / 2
                white_alpha = int(150 * (0.5 + 0.5 * white_pulse))
                pygame.draw.polygon(surface, (*white_hot, white_alpha), burn_points, width=1)
        
        # Draw black fade overlay when burn is complete
        if self.complete and self.black_fade_alpha > 0:
            fade_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, int(self.black_fade_alpha)))
            surface.blit(fade_surface, (0, 0))


class FlameSlider:
    """A slider with flame indicator."""
    def __init__(self, x, y, width, label, min_val, max_val, initial_val, font):
        self.x = x
        self.y = y
        self.width = width
        self.height = 40
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.font = font
        self.dragging = False
        self.hovered = False
        self.time = 0
        
        # Slider dimensions
        self.track_height = 6
        self.handle_radius = 12
        
        # Calculate handle position
        self.track_rect = pygame.Rect(x, y + 30, width, self.track_height)
        self._update_handle_pos()
    
    def _update_handle_pos(self):
        """Update handle position based on value."""
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        self.handle_x = self.track_rect.x + int(ratio * self.track_rect.width)
        self.handle_y = self.track_rect.centery
    
    def handle_event(self, event, mouse_pos):
        """Handle mouse events."""
        handle_rect = pygame.Rect(self.handle_x - self.handle_radius, 
                                  self.handle_y - self.handle_radius,
                                  self.handle_radius * 2, self.handle_radius * 2)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if handle_rect.collidepoint(mouse_pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        
        self.hovered = handle_rect.collidepoint(mouse_pos)
    
    def update(self, dt, mouse_pos):
        """Update slider state."""
        self.time += dt
        
        if self.dragging:
            # Calculate new value based on mouse position
            ratio = (mouse_pos[0] - self.track_rect.x) / self.track_rect.width
            ratio = max(0, min(1, ratio))
            old_value = self.value
            self.value = self.min_val + ratio * (self.max_val - self.min_val)
            self._update_handle_pos()
            
            # Apply volume changes immediately for feedback
            if self.label == "Master Volume" and abs(old_value - self.value) > 1:
                pygame.mixer.music.set_volume(self.value / 100.0)
            elif self.label == "Music Volume" and abs(old_value - self.value) > 1:
                pygame.mixer.music.set_volume(self.value / 100.0)
            elif self.label == "SFX Volume" and abs(old_value - self.value) > 1:
                # Play a test sound to demonstrate SFX volume
                try:
                    import math
                    sample_rate = 22050
                    duration = 0.05
                    frequency = 600
                    
                    frames = int(duration * sample_rate)
                    arr = []
                    for i in range(frames):
                        time = float(i) / sample_rate
                        wave = 2048 * math.sin(frequency * 2 * math.pi * time)
                        arr.append([int(wave), int(wave)])
                    
                    import numpy as np
                    sound = pygame.sndarray.make_sound(np.array(arr, dtype=np.int16))
                    sound.set_volume(self.value / 100.0)
                    sound.play()
                except (pygame.error, ValueError, AttributeError) as e:
                    print(f"SFX sound error: {e}")
                    pass  # Ignore sound errors
    
    def draw(self, surface):
        """Draw the slider."""
        # Label
        label_color = theme.get_color('text_primary')
        label_surf = self.font.render(self.label, True, label_color)
        surface.blit(label_surf, (self.x, self.y))
        
        # Value display
        value_text = f"{int(self.value)}"
        value_surf = self.font.render(value_text, True, theme.get_color('text_highlight'))
        surface.blit(value_surf, (self.x + self.width + 20, self.y))
        
        # Track background
        pygame.draw.rect(surface, theme.get_color('ui_background'), self.track_rect, border_radius=3)
        
        # Filled track (ember glow)
        fill_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.track_rect.width)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.track_rect.x, self.track_rect.y, fill_width, self.track_rect.height)
            
            # Animated ember colors
            pulse = (math.sin(self.time * 3) + 1) / 2
            ember_color = theme.get_color('flame_mid')
            ember_r = int(ember_color[0] * (0.8 + 0.2 * pulse))
            ember_g = int(ember_color[1] * (0.8 + 0.2 * pulse))
            ember_b = int(ember_color[2] * (0.8 + 0.2 * pulse))
            
            pygame.draw.rect(surface, (ember_r, ember_g, ember_b), fill_rect, border_radius=3)
            
            # Glow effect on filled track
            glow_surf = pygame.Surface((fill_width + 20, self.track_rect.height + 20), pygame.SRCALPHA)
            for i in range(10, 0, -1):
                alpha = int(30 * (1 - i / 10))
                pygame.draw.rect(glow_surf, (*theme.get_color('flame_mid'), alpha), 
                               pygame.Rect(10 - i, 10 - i, fill_width, self.track_rect.height), 
                               border_radius=3)
            surface.blit(glow_surf, (fill_rect.x - 10, fill_rect.y - 10))
        
        # Handle (flame-like)
        # Outer glow
        if self.hovered or self.dragging:
            for i in range(5, 0, -1):
                glow_radius = self.handle_radius + i * 3
                alpha = int(60 * (1 - i / 5))
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*theme.get_color('flame_core'), alpha), (glow_radius, glow_radius), glow_radius)
                surface.blit(glow_surf, (self.handle_x - glow_radius, self.handle_y - glow_radius))
        
        # Handle body
        handle_color = theme.get_color('button_bg')
        if self.hovered or self.dragging:
            pulse = (math.sin(self.time * 8) + 1) / 2
            flame_color = theme.get_color('flame_mid')
            handle_color = (
                int(flame_color[0] * pulse + handle_color[0] * (1 - pulse)),
                int(flame_color[1] * pulse + handle_color[1] * (1 - pulse)),
                int(flame_color[2] * pulse + handle_color[2] * (1 - pulse))
            )
        
        pygame.draw.circle(surface, handle_color, (self.handle_x, self.handle_y), self.handle_radius)
        pygame.draw.circle(surface, theme.get_color('flame_core'), (self.handle_x, self.handle_y), self.handle_radius, width=2)
    
    def get_value(self):
        """Return current value."""
        return self.value


class EmberToggle:
    """A toggle switch with ember effect."""
    def __init__(self, x, y, label, initial_state, font):
        self.x = x
        self.y = y
        self.label = label
        self.state = initial_state
        self.font = font
        self.hovered = False
        self.time = 0
        
        self.toggle_width = 60
        self.toggle_height = 30
        self.toggle_rect = pygame.Rect(x + 250, y, self.toggle_width, self.toggle_height)
    
    def handle_event(self, event, mouse_pos):
        """Handle mouse events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.toggle_rect.collidepoint(mouse_pos):
                # Play button click sound
                play_sound('button_click', volume=0.6)
                
                self.state = not self.state
                # Play a test sound when toggling
                try:
                    import math
                    sample_rate = 22050
                    duration = 0.1
                    frequency = 800 if self.state else 400
                    
                    frames = int(duration * sample_rate)
                    arr = []
                    for i in range(frames):
                        time = float(i) / sample_rate
                        wave = 4096 * math.sin(frequency * 2 * math.pi * time)
                        arr.append([int(wave), int(wave)])
                    
                    import numpy as np
                    sound = pygame.sndarray.make_sound(np.array(arr, dtype=np.int16))
                    sound.set_volume(0.3)
                    sound.play()
                except (pygame.error, ValueError, AttributeError) as e:
                    print(f"Sound error: {e}")
                    pass  # Ignore sound errors
        
        self.hovered = self.toggle_rect.collidepoint(mouse_pos)
    
    def update(self, dt):
        """Update toggle animation."""
        self.time += dt
    
    def draw(self, surface):
        """Draw the toggle."""
        # Label
        label_color = theme.get_color('text_primary')
        label_surf = self.font.render(self.label, True, label_color)
        surface.blit(label_surf, (self.x, self.y + 5))
        
        # Toggle background
        bg_color = theme.get_color('ui_background') if not self.state else theme.get_color('flame_outer')
        pygame.draw.rect(surface, bg_color, self.toggle_rect, border_radius=15)
        
        # Ember glow when on
        if self.state:
            glow_rect = self.toggle_rect.inflate(10, 10)
            for i in range(5, 0, -1):
                alpha = int(40 * (1 - i / 5))
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*theme.get_color('flame_mid'), alpha), glow_surf.get_rect(), border_radius=15)
                surface.blit(glow_surf, (glow_rect.x, glow_rect.y))
        
        # Toggle circle
        circle_x = self.toggle_rect.x + 15 if not self.state else self.toggle_rect.x + self.toggle_width - 15
        circle_y = self.toggle_rect.centery
        circle_radius = 10
        
        # Circle glow
        if self.state:
            pulse = (math.sin(self.time * 5) + 1) / 2
            for i in range(3):
                glow_radius = circle_radius + (3 - i) * 2
                alpha = int(80 * (1 - i / 3) * pulse)
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*theme.get_color('flame_core'), alpha), (glow_radius, glow_radius), glow_radius)
                surface.blit(glow_surf, (circle_x - glow_radius, circle_y - glow_radius))
        
        # Circle body
        circle_color = theme.get_color('button_border') if not self.state else theme.get_color('flame_core')
        pygame.draw.circle(surface, circle_color, (circle_x, circle_y), circle_radius)
        pygame.draw.circle(surface, theme.get_color('ui_border'), (circle_x, circle_y), circle_radius, width=2)
    
    def get_state(self):
        """Return current state."""
        return self.state


class SettingsScreen:
    """Settings screen with ember-themed controls and fire effects."""
    def __init__(self):
        # Pygame is initialized by main.py

        self.SCREEN_WIDTH = 1366
        self.SCREEN_HEIGHT = 768
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN)
        pygame.display.set_caption("Scarred Winds - Settings")
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.running = True

        # Fonts from theme
        self.title_font = theme.get_font('title_medium')
        self.label_font = theme.get_font('ui_medium')

        # Background colors from theme
        self.BG_TOP = theme.get_color('bg_dark')
        self.BG_BOTTOM = theme.get_color('bg_light')

        # Screen burn transition for returning to main menu
        self.screen_burn = ScreenBurnTransition(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.transitioning = False

        # Add ember particles for atmosphere
        self.ember_particles = []
        for _ in range(15):
            self.ember_particles.append({
                'x': random.uniform(0, self.SCREEN_WIDTH),
                'y': random.uniform(0, self.SCREEN_HEIGHT),
                'life': random.uniform(0, 1),
                'velocity_y': random.uniform(-5, -15),
                'velocity_x': random.uniform(-2, 2),
                'size': random.uniform(1, 3),
                'color': random.choice([
                    theme.get_color('flame_outer'),
                    theme.get_color('flame_mid'),
                    theme.get_color('flame_core')
                ])
            })

        # Create UI elements with fire theme
        start_x = 300
        start_y = 200
        spacing = 100

        self.sliders = [
            FlameSlider(start_x, start_y, 400, "Master Volume", 0, 100, 70, self.label_font),
            FlameSlider(start_x, start_y + spacing, 400, "Music Volume", 0, 100, 60, self.label_font),
            FlameSlider(start_x, start_y + spacing * 2, 400, "SFX Volume", 0, 100, 80, self.label_font),
        ]

        self.toggles = [
            EmberToggle(start_x, start_y + spacing * 3, "Fullscreen", True, self.label_font),
            EmberToggle(start_x, start_y + spacing * 3 + 60, "V-Sync", True, self.label_font),
        ]

        self.time = 0

        # Add flame trail mouse effect
        self.flame_trail = FlameTrail(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, max_particles=20)
    
    def handle_events(self):
        """Handle input events."""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                # Take screenshot
                self.take_screenshot()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if not self.transitioning:
                    # Start reverse burn transition (burn inward)
                    self.transitioning = True
                    self.screen_burn.start(reverse_mode=True)
                    print("Settings screen burning inward (reverse mode) to return to main menu...")
            
            for slider in self.sliders:
                slider.handle_event(event, mouse_pos)
            
            for toggle in self.toggles:
                toggle.handle_event(event, mouse_pos)
    
    def update(self, dt):
        """Update settings state."""
        self.time += dt
        mouse_pos = pygame.mouse.get_pos()

        # Update screen burn transition
        if self.transitioning:
            self.screen_burn.update(dt)
            if self.screen_burn.complete and self.screen_burn.black_fade_alpha >= 255:
                print("Settings burn complete, returning to main menu...")
                self.running = False  # Exit settings screen

        # Update ember particles for atmosphere
        for particle in self.ember_particles:
            particle['life'] -= dt * 0.3
            particle['y'] += particle['velocity_y'] * dt
            particle['x'] += particle['velocity_x'] * dt
            particle['velocity_y'] += 8 * dt  # Gravity

            if particle['life'] <= 0:
                particle['x'] = random.uniform(0, self.SCREEN_WIDTH)
                particle['y'] = self.SCREEN_HEIGHT + 10
                particle['life'] = 1.0
                particle['velocity_y'] = random.uniform(-5, -15)
                particle['velocity_x'] = random.uniform(-2, 2)

        for slider in self.sliders:
            slider.update(dt, mouse_pos)

        for toggle in self.toggles:
            toggle.update(dt)

        # Update flame trail mouse effect
        mouse_pos = pygame.mouse.get_pos()
        self.flame_trail.update(dt, mouse_pos)
    
    def draw(self):
        """Draw the settings screen."""
        if self.transitioning:
            # Create a surface for the settings content
            settings_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            self._draw_settings_content(settings_surface)
            
            # Apply burn mask to make content disappear as flame burns inward
            # Always apply mask during transition (even when burn_progress is 0)
            mask = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 255))  # Solid black
            
            # In reverse mode, burn inward from edges - cut out the burnt outer area
            burn_radius = self.screen_burn.burn_progress * self.screen_burn.max_radius
            if burn_radius > 0:
                burn_points = self.screen_burn._generate_organic_burn_points(burn_radius)
                if len(burn_points) > 2:
                    pygame.draw.polygon(mask, (0, 0, 0, 0), burn_points)
            # If burn_radius is 0, no cutout is made, so entire screen is masked (hidden)
            
            # Apply mask to settings surface
            settings_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Draw the masked settings content
            self.screen.blit(settings_surface, (0, 0))
            
            # Draw burn effect on top
            self.screen_burn.draw(self.screen)
        else:
            # Normal settings rendering
            self._draw_settings_content(self.screen)

        pygame.display.flip()
    
    def _draw_settings_content(self, surface):
        """Draw the settings content on the given surface."""
        # Gradient background
        for y in range(self.SCREEN_HEIGHT):
            ratio = y / self.SCREEN_HEIGHT
            r = int(self.BG_TOP[0] * (1 - ratio) + self.BG_BOTTOM[0] * ratio)
            g = int(self.BG_TOP[1] * (1 - ratio) + self.BG_BOTTOM[1] * ratio)
            b = int(self.BG_TOP[2] * (1 - ratio) + self.BG_BOTTOM[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.SCREEN_WIDTH, y))

        # Draw ember particles for atmosphere
        for particle in self.ember_particles:
            alpha = int(180 * particle['life'])
            size = int(particle['size'] * particle['life'])
            if size > 0:
                # Glow effect for particles
                for i in range(3):
                    glow_size = size * (3 - i)
                    glow_alpha = int(alpha * 0.4 / (i + 1))
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*particle['color'], glow_alpha), (glow_size, glow_size), glow_size)
                    surface.blit(glow_surf, (int(particle['x'] - glow_size), int(particle['y'] - glow_size)))

        # Title with ember glow effect
        title_pulse = (math.sin(self.time * 2) + 1) / 2
        title_color = theme.get_color('text_primary')
        title_glow = tuple(int(c * (0.8 + 0.2 * title_pulse)) for c in title_color)
        title_surf = self.title_font.render("SETTINGS", True, title_glow)
        title_rect = title_surf.get_rect(center=(self.SCREEN_WIDTH // 2, 100))
        surface.blit(title_surf, title_rect)

        # UI elements
        for slider in self.sliders:
            slider.draw(surface)

        for toggle in self.toggles:
            toggle.draw(surface)

        # Back instruction with subtle glow
        back_pulse = (math.sin(self.time * 1.5) + 1) / 2
        back_color = theme.get_color('text_dark')
        back_glow = tuple(int(c * (0.7 + 0.3 * back_pulse)) for c in back_color)
        back_text = self.label_font.render("Press ESC to return", True, back_glow)
        back_rect = back_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 50))
        surface.blit(back_text, back_rect)

        # Draw flame trail mouse effect (only if not transitioning)
        if not self.transitioning:
            self.flame_trail.draw(surface)

        # Vignette removed for cleaner look
    
    def _draw_vignette(self, surface):
        """Draw vignette effect."""
        vignette = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2
        max_radius = min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) // 2
        
        for i in range(max_radius, 0, -2):
            distance_ratio = 1 - (i / max_radius)
            alpha = int(255 * (distance_ratio ** 1.5) * 0.9)
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (center_x, center_y), i)
        
        surface.blit(vignette, (0, 0))
    
    def take_screenshot(self):
        """Take a screenshot of the current screen."""
        import os
        from datetime import datetime
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/settings_{timestamp}.png"
        
        # Save screenshot
        pygame.image.save(self.screen, filename)
        print(f"Screenshot saved: {filename}")
    
    def run(self):
        """Main loop."""
        print("Settings screen running...")
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        
        # Return settings
        return {
            'master_volume': self.sliders[0].get_value(),
            'music_volume': self.sliders[1].get_value(),
            'sfx_volume': self.sliders[2].get_value(),
            'fullscreen': self.toggles[0].get_state(),
            'vsync': self.toggles[1].get_state(),
        }


if __name__ == "__main__":
    settings = SettingsScreen()
    result = settings.run()
    # Pygame cleanup handled by main.py
    print(f"Settings: {result}")
