#!/usr/bin/env python3
"""
Scarred Winds - Main Menu UI
Features ember-glowing buttons and cinematic design
"""

import pygame
import sys
import math
import random
import opensimplex
from theme_config import theme
from mouse_trail import FlameTrail
from burning_text import BurningText
from sound_manager import play_sound
class FadeTransition:
    """Simple fade to black transition for exit."""
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.fade_alpha = 0.0  # 0-255
        self.fade_speed = 3.0  # Fade speed
        self.complete = False
        self.active = False
    
    def start(self):
        """Start the fade transition."""
        self.active = True
        self.complete = False
        self.fade_alpha = 0.0
    
    def update(self, dt):
        """Update fade animation."""
        if not self.active:
            return
        
        self.fade_alpha += self.fade_speed * dt * 255
        if self.fade_alpha >= 255:
            self.fade_alpha = 255
            self.complete = True
    
    def draw(self, surface):
        """Draw the fade overlay."""
        if not self.active:
            return
        
        fade_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, int(self.fade_alpha)))
        surface.blit(fade_surface, (0, 0))

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
        if self._update_black_fade(dt):
            return
        
        # Update burn progress
        self._update_burn_progress(dt)
        
        # Calculate current burn radius and generate burn points
        current_radius = self.burn_progress * self.max_radius
        burn_points = self._generate_organic_burn_points(current_radius)
        
        # Spawn particles
        self._spawn_fire_particles(burn_points)
        self._spawn_smoke_particles(current_radius)
        self._spawn_ember_sparks(burn_points)
        
        # Update existing particles
        self._update_fire_particles(dt)
        self._update_smoke_particles(dt)
        self._update_spark_particles(dt)
    
    def _update_black_fade(self, dt):
        """Update black fade after burn completes. Returns True if still fading."""
        if not self.complete:
            return False
        
        self.black_fade_alpha += self.black_fade_speed * dt * 255
        if self.black_fade_alpha >= 255:
            self.black_fade_alpha = 255
        return True  # Still fading
    
    def _update_burn_progress(self, dt):
        """Update burn progress based on mode."""
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
    
    def _spawn_fire_particles(self, burn_points):
        """Spawn fire particles along organic burn edge."""
        if random.random() >= 0.95 or len(burn_points) == 0:
            return
        
        point_index = random.randint(0, len(burn_points) - 1)
        edge_x, edge_y = burn_points[point_index]
        perp_x, perp_y = self._calculate_perpendicular_direction(burn_points, point_index)
        
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
    
    def _spawn_smoke_particles(self, current_radius):
        """Spawn smoke particles inside burn area."""
        if random.random() >= 0.8:
            return
        
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
    
    def _spawn_ember_sparks(self, burn_points):
        """Spawn ember sparks with perpendicular ejection."""
        if random.random() >= 0.6 or len(burn_points) == 0:
            return
        
        point_index = random.randint(0, len(burn_points) - 1)
        edge_x, edge_y = burn_points[point_index]
        perp_x, perp_y = self._calculate_perpendicular_direction(burn_points, point_index)
        
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
    
    def _calculate_perpendicular_direction(self, burn_points, point_index):
        """Calculate perpendicular direction for particle ejection."""
        edge_x, edge_y = burn_points[point_index]
        
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
        
        return perp_x, perp_y
    
    def _update_fire_particles(self, dt):
        """Update fire particles with gravity."""
        for particle in self.fire_particles[:]:
            particle['life'] -= dt * 2.5
            particle['y'] += particle['velocity_y'] * dt
            particle['x'] += particle['velocity_x'] * dt
            particle['velocity_y'] += 25 * dt  # Gravity
            if particle['life'] <= 0:
                self.fire_particles.remove(particle)
    
    def _update_smoke_particles(self, dt):
        """Update smoke particles with light gravity."""
        for particle in self.smoke_particles[:]:
            particle['life'] -= dt * 1.2
            particle['y'] += particle['velocity_y'] * dt
            particle['x'] += particle['velocity_x'] * dt
            particle['velocity_y'] += 8 * dt  # Light gravity
            if particle['life'] <= 0:
                self.smoke_particles.remove(particle)
    
    def _update_spark_particles(self, dt):
        """Update spark particles with heavy gravity."""
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


class EmberButton:
    """A button that glows like an ember when hovered."""
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hovered = False
        self.glow_intensity = 0.0
        self.ember_particles = []
        self.time = 0
        
    def update(self, dt, mouse_pos):
        """Update button state and animations."""
        self.time += dt
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Animate glow intensity
        target_glow = 1.0 if self.hovered else 0.0
        self.glow_intensity += (target_glow - self.glow_intensity) * 8 * dt  # Faster transition (was 5)
        
        # Spawn ember particles when hovered (MORE particles for better feedback)
        if self.hovered and random.random() < 0.25:  # More frequent (was 0.15)
            self.ember_particles.append({
                'x': random.uniform(self.rect.left, self.rect.right),
                'y': self.rect.bottom,
                'life': 1.0,
                'velocity_y': random.uniform(-50, -90),  # Faster (was -40 to -80)
                'velocity_x': random.uniform(-20, 20),  # Wider spread (was -15 to 15)
                'size': random.uniform(3, 6),  # Larger (was 2-5)
                'color': random.choice([
                    theme.get_color('flame_core'),
                    theme.get_color('flame_mid'),
                    theme.get_color('flame_outer')
                ])
            })
        
        # Update particles
        for particle in self.ember_particles[:]:
            particle['life'] -= dt * 0.8
            particle['y'] += particle['velocity_y'] * dt
            particle['x'] += particle['velocity_x'] * dt
            particle['velocity_y'] += 50 * dt  # Gravity
            if particle['life'] <= 0:
                self.ember_particles.remove(particle)
    
    def draw(self, surface):
        """Draw the button with ember glow effect."""
        self._draw_ember_particles(surface)
        self._draw_button_glow(surface)
        self._draw_button_body(surface)
        self._draw_button_border(surface)
        self._draw_button_text(surface)
    
    def _draw_ember_particles(self, surface):
        """Draw ember particles with glow effect."""
        for particle in self.ember_particles:
            alpha = int(255 * particle['life'])
            size = int(3 * particle['life'])
            if size > 0:
                self._draw_particle_glow(surface, particle, alpha, size)
    
    def _draw_particle_glow(self, surface, particle, alpha, size):
        """Draw glow layers for a single particle."""
        for i in range(3):
            glow_size = size * (3 - i)
            glow_alpha = int(alpha * 0.3 / (i + 1))
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            color = theme.get_color('flame_mid') if particle['life'] > 0.5 else theme.get_color('flame_outer')
            pygame.draw.circle(glow_surf, (*color, glow_alpha), (glow_size, glow_size), glow_size)
            surface.blit(glow_surf, (int(particle['x'] - glow_size), int(particle['y'] - glow_size)))
    
    def _draw_button_glow(self, surface):
        """Draw the outer glow effect around the button."""
        if self.glow_intensity <= 0:
            return
        
        glow_size = int(15 * self.glow_intensity)  # Increased from 10 to 15
        glow_rect = self.rect.inflate(glow_size * 2, glow_size * 2)
        
        for i in range(glow_size, 0, -2):
            alpha = int(80 * self.glow_intensity * (1 - i / glow_size))  # Increased from 50 to 80
            glow_color = (*theme.get_color('flame_mid'), alpha)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=15)
            surface.blit(glow_surface, (glow_rect.x, glow_rect.y))
    
    def _draw_button_body(self, surface):
        """Draw the main button body with pulsing effect."""
        base_color = theme.get_color('button_bg')
        if self.hovered:
            base_color = theme.get_color('button_bg_hover')
        
        # Stronger pulsing effect when hovered
        pulse = math.sin(self.time * 6) * 0.3 * self.glow_intensity  # Increased from 5 to 6, and 0.2 to 0.3
        highlight = tuple(min(255, int(c * (1 + pulse))) for c in base_color)
        
        pygame.draw.rect(surface, highlight, self.rect, border_radius=10)
    
    def _draw_button_border(self, surface):
        """Draw the button border with ember glow effect."""
        border_color = theme.get_color('button_border')
        if self.hovered:
            border_color = self._calculate_ember_border_color()
        
        pygame.draw.rect(surface, border_color, self.rect, width=3, border_radius=10)
    
    def _calculate_ember_border_color(self):
        """Calculate the ember glow color for the border."""
        ember_intensity = (math.sin(self.time * 10) + 1) / 2  # Faster pulse (was 8)
        flame_color = theme.get_color('flame_mid')
        border_color = theme.get_color('button_border')
        
        return (
            int(flame_color[0] * ember_intensity * 0.7 + border_color[0] * (1 - ember_intensity)),  # Stronger blend (was 0.6)
            int(flame_color[1] * ember_intensity * 0.7 + border_color[1] * (1 - ember_intensity)),
            int(flame_color[2] * ember_intensity * 0.7 + border_color[2] * (1 - ember_intensity))
        )
    
    def _draw_button_text(self, surface):
        """Draw the button text with shadow effect."""
        text_color = theme.get_color('text_primary')
        if self.hovered:
            text_color = theme.get_color('text_highlight')
        
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        
        # Text shadow
        shadow_surf = self.font.render(self.text, True, theme.get_color('text_shadow'))
        shadow_rect = shadow_surf.get_rect(center=(self.rect.centerx + 2, self.rect.centery + 2))
        surface.blit(shadow_surf, shadow_rect)
        
        # Main text
        surface.blit(text_surf, text_rect)


class MainMenu:
    """Main menu screen with cinematic design."""
    def __init__(self):
        # Pygame is initialized by main.py
        
        self.SCREEN_WIDTH = 1366
        self.SCREEN_HEIGHT = 768
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN)
        pygame.display.set_caption("Scarred Winds - Main Menu")
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.running = True
        
        # Fonts from theme
        self.title_font = theme.get_font('title_large')
        self.button_font = theme.get_font('ui_large')
        
        # Background colors from theme
        self.BG_TOP = theme.get_color('bg_dark')
        self.BG_BOTTOM = theme.get_color('bg_light')
        
        # Flame trail mouse effect
        self.flame_trail = FlameTrail(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, max_particles=30)
        self.last_mouse_pos = (0, 0)
        
        # Burning text for title
        self.burning_title = BurningText(
            "SCARRED WINDS",
            self.title_font,
            theme.get_color('text_primary'),
            self.SCREEN_WIDTH // 2,
            150,
            self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT
        )
        
        # Try to restore burning text state from StartScreen
        self.burning_title.restore_state("SCARRED WINDS")
        
        # Background particles for atmosphere - embers that fall and die out
        self.background_particles = []
        for _ in range(60):  # Increased from 40 to 60 for more atmosphere
            self.background_particles.append({
                'x': random.uniform(0, self.SCREEN_WIDTH),
                'y': random.uniform(-100, 0),  # Start above screen
                'life': 1.0,  # Start fully lit
                'velocity_y': random.uniform(30, 60),  # Fall downward
                'velocity_x': random.uniform(-10, 10),  # Slight horizontal drift
                'size': random.uniform(3, 7),  # Larger particles (was 2-5)
                'color': random.choice([
                    theme.get_color('flame_outer'),
                    theme.get_color('flame_mid'),
                    theme.get_color('flame_core')
                ]),
                'brightness_boost': 0.0,  # Cursor interaction brightness
                'push_velocity_x': 0.0,  # Push force from cursor
                'push_velocity_y': 0.0   # Push force from cursor
            })
        
        # Screen burn transition
        self.screen_burn = ScreenBurnTransition(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.fade_transition = FadeTransition(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)  # For exit transitions
        self.transitioning = False
        self.next_scene = None
        self.next_scene_surface = None  # Pre-rendered next scene
        
        # Create buttons
        button_width = 400
        button_height = 70
        button_x = (self.SCREEN_WIDTH - button_width) // 2
        start_y = 350
        spacing = 90
        
        self.buttons = [
            EmberButton(button_x, start_y, button_width, button_height, "New Game", self.button_font),
            EmberButton(button_x, start_y + spacing, button_width, button_height, "Continue", self.button_font),
            EmberButton(button_x, start_y + spacing * 2, button_width, button_height, "Settings", self.button_font),
            EmberButton(button_x, start_y + spacing * 3, button_width, button_height, "Exit", self.button_font),
        ]
        
        self.selected_option = None
        self.time = 0
    
    def handle_events(self):
        """Handle input events."""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.selected_option = "Exit"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                # Take screenshot
                self.take_screenshot()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if not self.transitioning:
                    # Start fade transition to exit
                    self.selected_option = "Exit"
                    self.transitioning = True
                    self.fade_transition.start()
                    print("Fade transition to exit...")
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, button in enumerate(self.buttons):
                    if button.hovered and not self.transitioning:
                        # Play button click sound
                        play_sound('button_click', volume=0.6)
                        
                        if button.text == "Exit":
                            # Start fade transition from Exit button
                            self.selected_option = button.text
                            self.transitioning = True
                            self.fade_transition.start()
                            print("Fade transition from Exit button...")
                        else:
                            # Start normal screen burn transition (burn outward)
                            self.selected_option = button.text
                            self.transitioning = True
                            self.screen_burn.start(reverse_mode=False)
                            self.next_scene = self._get_next_scene_name(button.text)
                            print(f"Screen burning outward to reveal: {self.next_scene}")
    
    def _get_next_scene_name(self, button_text):
        """Get the next scene name based on button selection."""
        if button_text == "Settings":
            return "settings"
        elif button_text == "New Game":
            return "new_game"
        elif button_text == "Continue":
            return "continue"
        elif button_text == "Exit":
            return "exit"
        return "main_menu"
    
    def update(self, dt):
        """Update menu state."""
        self.time += dt
        mouse_pos = pygame.mouse.get_pos()
        
        # Update flame trail mouse effect
        self.flame_trail.update(dt, mouse_pos)
        self.last_mouse_pos = mouse_pos
        
        # Update burning text
        self.burning_title.update(mouse_pos, dt)
        
        # Update falling ember particles
        for particle in self.background_particles[:]:
            # Cursor interaction physics
            mouse_x, mouse_y = mouse_pos
            dx = particle['x'] - mouse_x
            dy = particle['y'] - mouse_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Interaction parameters
            interaction_radius = 120
            push_strength = 250
            
            if distance < interaction_radius and distance > 0.1:  # Avoid division by zero
                # Brightness boost (closer = brighter)
                particle['brightness_boost'] = 1.0 - (distance / interaction_radius)
                
                # Push force (gentle breeze effect - repulsion from cursor)
                force = (1.0 - distance / interaction_radius) * push_strength * dt
                particle['push_velocity_x'] += (dx / distance) * force
                particle['push_velocity_y'] += (dy / distance) * force
            elif distance <= 0.1:  # Handle cursor directly on particle
                # Maximum brightness when cursor is directly on particle
                particle['brightness_boost'] = 1.0
                
                # Random push direction to avoid getting stuck
                angle = random.uniform(0, 2 * math.pi)
                force = push_strength * dt * 0.5  # Reduced force for direct contact
                particle['push_velocity_x'] += math.cos(angle) * force
                particle['push_velocity_y'] += math.sin(angle) * force
            else:
                # Decay brightness boost when cursor moves away
                particle['brightness_boost'] *= 0.95
            
            # Apply push velocities to particle position
            particle['x'] += particle['push_velocity_x'] * dt
            particle['y'] += particle['push_velocity_y'] * dt
            
            # Keep particles within screen bounds (with some margin)
            particle['x'] = max(-50, min(self.SCREEN_WIDTH + 50, particle['x']))
            particle['y'] = max(-100, min(self.SCREEN_HEIGHT + 50, particle['y']))
            
            # Damping for push velocities (gentle decay)
            particle['push_velocity_x'] *= 0.9
            particle['push_velocity_y'] *= 0.9
            
            # Clamp velocities to prevent extreme values
            max_velocity = 200
            particle['push_velocity_x'] = max(-max_velocity, min(max_velocity, particle['push_velocity_x']))
            particle['push_velocity_y'] = max(-max_velocity, min(max_velocity, particle['push_velocity_y']))
            
            # Move particle downward (gravity)
            particle['y'] += particle['velocity_y'] * dt
            particle['x'] += particle['velocity_x'] * dt
            
            # Calculate life based on vertical position (dies as it reaches bottom)
            progress = particle['y'] / self.SCREEN_HEIGHT
            particle['life'] = max(0, 1.0 - progress)  # Fades from 1.0 to 0.0 as it falls
            
            # If particle reached bottom or died, respawn at top
            if particle['y'] > self.SCREEN_HEIGHT or particle['life'] <= 0:
                particle['x'] = random.uniform(0, self.SCREEN_WIDTH)
                particle['y'] = random.uniform(-100, -10)  # Spawn above screen
                particle['life'] = 1.0  # Start fully lit
                particle['velocity_y'] = random.uniform(30, 60)
                particle['velocity_x'] = random.uniform(-10, 10)
                particle['size'] = random.uniform(3, 7)  # Reset size (larger range)
                # Reset interaction state for new particles
                particle['brightness_boost'] = 0.0
                particle['push_velocity_x'] = 0.0
                particle['push_velocity_y'] = 0.0
        
        # Update screen burn transition
        if self.transitioning:
            if self.fade_transition.active:
                # Update fade transition
                self.fade_transition.update(dt)
                if self.fade_transition.complete:
                    print(f"Fade complete, transitioning to: {self.selected_option}")
                    self.running = False  # Exit menu for any selection
            else:
                # Update normal screen burn transition
                self.screen_burn.update(dt)
                if self.screen_burn.complete and self.screen_burn.black_fade_alpha >= 255:
                    print(f"Burn complete, transitioning to: {self.selected_option}")
                    self.running = False  # Exit menu for any selection
        
        # Update buttons (only if not transitioning)
        if not self.transitioning:
            for button in self.buttons:
                button.update(dt, mouse_pos)
    
    def draw(self):
        """Draw the menu with burn transition effect."""
        if self.transitioning:
            if self.fade_transition.active:
                # Fade transition
                self._draw_fade_transition()
            elif self.screen_burn.reverse_mode:
                # Reverse mode: burn inward from edges
                self._draw_reverse_burn_transition()
            else:
                # Normal mode: burn outward from center
                self._draw_normal_burn_transition()
        else:
            # Normal menu rendering
            self._draw_menu_content(self.screen)
        
        pygame.display.flip()
    
    def _draw_fade_transition(self):
        """Draw simple fade to black transition."""
        # Draw normal menu content
        self._draw_menu_content(self.screen)
        
        # Draw fade overlay
        self.fade_transition.draw(self.screen)
    
    def _draw_normal_burn_transition(self):
        """Draw normal burn transition (outward from center)."""
        # Create surfaces for layered rendering
        menu_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        next_scene_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        
        # Draw next scene background (placeholder for now)
        next_scene_surface.fill(theme.get_color('bg_dark'))
        
        # Draw current menu on menu surface
        self._draw_menu_content(menu_surface)
        
        # Apply organic burn mask to menu surface
        if self.screen_burn.burn_progress > 0:
            mask = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 255))  # Solid black
            
            # Cut out organic burnt area (make transparent)
            burn_radius = self.screen_burn.burn_progress * self.screen_burn.max_radius
            burn_points = self.screen_burn._generate_organic_burn_points(burn_radius)
            
            if len(burn_points) > 2:
                pygame.draw.polygon(mask, (0, 0, 0, 0), burn_points)
            
            # Apply mask to menu surface
            menu_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Draw next scene first (background)
        self.screen.blit(next_scene_surface, (0, 0))
        
        # Draw menu with burn mask applied
        self.screen.blit(menu_surface, (0, 0))
        
        # Draw burn effect on top
        self.screen_burn.draw(self.screen)
    
    def _draw_reverse_burn_transition(self):
        """Draw reverse burn transition (inward from edges)."""
        # For reverse mode, we draw the menu normally but with a burn overlay
        self._draw_menu_content(self.screen)
        
        # Create a burn overlay that covers the screen and burns inward
        if self.screen_burn.burn_progress > 0:
            burn_overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            burn_overlay.fill((0, 0, 0, 255))  # Solid black overlay
            
            # Cut out the unburnt center area (make transparent)
            unburnt_radius = (1.0 - self.screen_burn.burn_progress) * self.screen_burn.max_radius
            if unburnt_radius > 0:
                unburnt_points = self.screen_burn._generate_organic_burn_points(unburnt_radius)
                if len(unburnt_points) > 2:
                    pygame.draw.polygon(burn_overlay, (0, 0, 0, 0), unburnt_points)
            
            # Apply burn overlay
            self.screen.blit(burn_overlay, (0, 0))
        
        # Draw burn effect on top
        self.screen_burn.draw(self.screen)
    
    def _draw_menu_content(self, surface):
        """Draw the menu content on the given surface."""
        # Clear surface first to prevent artifacts
        surface.fill((0, 0, 0))
        
        # Gradient background
        for y in range(self.SCREEN_HEIGHT):
            ratio = y / self.SCREEN_HEIGHT
            r = int(self.BG_TOP[0] * (1 - ratio) + self.BG_BOTTOM[0] * ratio)
            g = int(self.BG_TOP[1] * (1 - ratio) + self.BG_BOTTOM[1] * ratio)
            b = int(self.BG_TOP[2] * (1 - ratio) + self.BG_BOTTOM[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.SCREEN_WIDTH, y))
        
        # Draw falling ember particles
        for particle in self.background_particles:
            # Apply brightness boost from cursor interaction
            brightness_multiplier = 1.0 + particle['brightness_boost']
            alpha = int(255 * particle['life'] * brightness_multiplier)  # Enhanced by cursor proximity
            # Clamp alpha to valid range (0-255)
            alpha = max(0, min(255, alpha))
            size = int(particle['size'] * particle['life'] * (1.0 + particle['brightness_boost'] * 0.3))  # Slightly larger when bright
            if size > 0 and alpha > 0:
                # Enhanced glow effect for particles (MORE LAYERS for better visibility)
                glow_layers = 5 if particle['brightness_boost'] > 0.5 else 4  # More glow layers (was 3-4)
                for i in range(glow_layers):
                    glow_size = size * (glow_layers - i) * 1.2  # Bigger glow multiplier (was 1.0)
                    glow_alpha = int(alpha * 0.6 / (i + 1) * brightness_multiplier)  # Brighter glow (was 0.5)
                    # Clamp alpha to valid range (0-255)
                    glow_alpha = max(0, min(255, glow_alpha))
                    if glow_alpha > 0:  # Only draw if alpha is positive
                        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                        pygame.draw.circle(glow_surf, (*particle['color'], glow_alpha), (glow_size, glow_size), glow_size)
                        surface.blit(glow_surf, (int(particle['x'] - glow_size), int(particle['y'] - glow_size)))
        
        # Update burning title color based on glow
        title_color = theme.get_color('text_primary')
        glow_intensity = (math.sin(self.time * 2) + 1) / 2
        title_glow = tuple(int(c * (0.8 + 0.2 * glow_intensity)) for c in title_color)
        
        # The new burning text system handles color updates internally
        # No need to manually update letter surfaces
        
        # Draw burning title
        self.burning_title.draw(surface)
        
        # Draw flame trail (only if not transitioning)
        if not self.transitioning:
            self.flame_trail.draw(surface)
        
        # Buttons
        for button in self.buttons:
            button.draw(surface)
        
        # Vignette removed for cleaner look
    
    def _draw_vignette(self, surface):
        """Draw dark vignette effect."""
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
        filename = f"screenshots/main_menu_{timestamp}.png"
        
        # Save screenshot
        pygame.image.save(self.screen, filename)
        print(f"Screenshot saved: {filename}")
    
    def run(self):
        """Main loop."""
        print("Main Menu running...")
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        
        # Save burning text state before transitioning
        self.burning_title.save_state("SCARRED WINDS")
        
        return self.selected_option


if __name__ == "__main__":
    menu = MainMenu()
    selected = menu.run()
    # Pygame cleanup handled by main.py
    print(f"User selected: {selected}")
