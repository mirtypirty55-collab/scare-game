#!/usr/bin/env python3
"""
Scarred Winds - Character Creation Scene
Features elder NPC dialogue, gender selection, and name input
"""

import pygame
import sys
import math
import random
import time
from theme_config import theme
from mouse_trail import FlameTrail
from sound_manager import play_sound

class EmberTextInput:
    """Ember-themed text input field."""
    def __init__(self, x, y, width, height, font, placeholder="Enter text..."):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0.0
        self.max_length = 12
        self.ember_particles = []
        self.time = 0
        
    def update(self, dt, mouse_pos):
        """Update input field state and animations."""
        self.time += dt
        self.cursor_timer += dt
        
        # Toggle cursor visibility
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0.0
        
        # Spawn ember particles when active
        if self.active and random.random() < 0.1:
            self.ember_particles.append({
                'x': random.uniform(self.rect.left, self.rect.right),
                'y': self.rect.bottom,
                'life': 1.0,
                'velocity_y': random.uniform(-20, -40),
                'velocity_x': random.uniform(-5, 5),
                'size': random.uniform(1, 3),
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
            particle['velocity_y'] += 30 * dt  # Gravity
            if particle['life'] <= 0:
                self.ember_particles.remove(particle)
    
    def handle_event(self, event, mouse_pos):
        """Handle input events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(mouse_pos)
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True  # Indicate completion
            elif len(self.text) < self.max_length:
                self.text += event.unicode
    
    def draw(self, surface):
        """Draw the text input field."""
        # Draw ember particles
        for particle in self.ember_particles:
            alpha = int(255 * particle['life'])
            size = int(2 * particle['life'])
            if size > 0:
                # Glow effect
                for i in range(3):
                    glow_size = size * (3 - i)
                    glow_alpha = int(alpha * 0.3 / (i + 1))
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*particle['color'], glow_alpha), (glow_size, glow_size), glow_size)
                    surface.blit(glow_surf, (int(particle['x'] - glow_size), int(particle['y'] - glow_size)))
        
        # Input field background
        base_color = theme.get_color('button_bg')
        if self.active:
            base_color = theme.get_color('button_bg_hover')
        
        # Ember glow when active
        if self.active:
            glow_size = int(8)
            glow_rect = self.rect.inflate(glow_size * 2, glow_size * 2)
            for i in range(glow_size, 0, -2):
                alpha = int(40 * (1 - i / glow_size))
                glow_color = (*theme.get_color('flame_mid'), alpha)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=8)
                surface.blit(glow_surf, (glow_rect.x, glow_rect.y))
        
        pygame.draw.rect(surface, base_color, self.rect, border_radius=8)
        
        # Border with ember glow
        border_color = theme.get_color('button_border')
        if self.active:
            ember_intensity = (math.sin(self.time * 8) + 1) / 2
            flame_color = theme.get_color('flame_mid')
            border_color = (
                int(flame_color[0] * ember_intensity * 0.6 + border_color[0] * (1 - ember_intensity)),
                int(flame_color[1] * ember_intensity * 0.6 + border_color[1] * (1 - ember_intensity)),
                int(flame_color[2] * ember_intensity * 0.6 + border_color[2] * (1 - ember_intensity))
            )
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=8)
        
        # Text or placeholder
        if self.text:
            text_surf = self.font.render(self.text, True, theme.get_color('text_primary'))
        else:
            text_surf = self.font.render(self.placeholder, True, theme.get_color('text_dark'))
        
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Cursor
        if self.active and self.cursor_visible:
            cursor_x = text_rect.right + 2
            cursor_y = self.rect.centery - 8
            pygame.draw.line(surface, theme.get_color('flame_core'), 
                           (cursor_x, cursor_y), (cursor_x, cursor_y + 16), 2)

class DialogueBox:
    """Dialogue box with typewriter effect."""
    def __init__(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.full_text = ""
        self.displayed_text = ""
        self.typewriter_speed = 0.05  # Seconds per character
        self.typewriter_timer = 0.0
        self.complete = False
        self.waiting_for_input = False
        
    def set_text(self, text):
        """Set new dialogue text and start typewriter effect."""
        self.full_text = text
        self.displayed_text = ""
        self.typewriter_timer = 0.0
        self.complete = False
        self.waiting_for_input = False
    
    def update(self, dt):
        """Update typewriter effect."""
        if not self.complete and len(self.displayed_text) < len(self.full_text):
            self.typewriter_timer += dt
            if self.typewriter_timer >= self.typewriter_speed:
                self.displayed_text = self.full_text[:len(self.displayed_text) + 1]
                self.typewriter_timer = 0.0
                
                # Check if typewriter is complete
                if len(self.displayed_text) >= len(self.full_text):
                    self.complete = True
                    self.waiting_for_input = True
    
    def advance(self):
        """Advance to next dialogue or complete current one."""
        if self.waiting_for_input:
            return True  # Ready for next dialogue
        elif not self.complete:
            # Skip typewriter effect
            self.displayed_text = self.full_text
            self.complete = True
            self.waiting_for_input = True
            return False
        return False
    
    def draw(self, surface):
        """Draw the dialogue box."""
        # Background
        pygame.draw.rect(surface, theme.get_color('button_bg'), self.rect, border_radius=10)
        pygame.draw.rect(surface, theme.get_color('button_border'), self.rect, width=2, border_radius=10)
        
        # --- IMPROVED TEXT WRAPPING LOGIC ---
        words = self.displayed_text.split(' ')
        lines = []
        current_line = ""
        line_height = 28  # Increased for better spacing
        margin = 20

        for word in words:
            # Test if the new word fits on the current line
            test_line = current_line + (" " if current_line else "") + word
            test_surf = self.font.render(test_line, True, theme.get_color('text_primary'))

            if test_surf.get_width() < self.rect.width - (margin * 2):
                current_line = test_line
            else:
                # If the line is too long, push the old line and start a new one
                lines.append(current_line)
                current_line = word

        lines.append(current_line)  # Add the last line

        # Draw the formatted lines
        y_offset = margin
        for line in lines:
            if y_offset + line_height <= self.rect.height - margin:
                line_surf = self.font.render(line, True, theme.get_color('text_primary'))
                surface.blit(line_surf, (self.rect.x + margin, self.rect.y + y_offset))
                y_offset += line_height
        
        # Continue indicator
        if self.waiting_for_input:
            indicator_text = "Click to continue..."
            indicator_surf = self.font.render(indicator_text, True, theme.get_color('text_dark'))
            indicator_rect = indicator_surf.get_rect(bottomright=(self.rect.right - 10, self.rect.bottom - 10))
            surface.blit(indicator_surf, indicator_rect)

class EmberButton:
    """A button that glows like an ember when hovered."""
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hovered = False
        self.selected = False
        self.glow_intensity = 0.0
        self.ember_particles = []
        self.time = 0
        
    def update(self, dt, mouse_pos):
        """Update button state and animations."""
        self.time += dt
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Animate glow intensity
        target_glow = 1.0 if (self.hovered or self.selected) else 0.0
        self.glow_intensity += (target_glow - self.glow_intensity) * 5 * dt
        
        # Spawn ember particles when hovered or selected
        if (self.hovered or self.selected) and random.random() < 0.15:
            self.ember_particles.append({
                'x': random.uniform(self.rect.left, self.rect.right),
                'y': self.rect.bottom,
                'life': 1.0,
                'velocity_y': random.uniform(-40, -80),
                'velocity_x': random.uniform(-15, 15),
                'size': random.uniform(2, 5),
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
        # Draw ember particles
        for particle in self.ember_particles:
            alpha = int(255 * particle['life'])
            size = int(3 * particle['life'])
            if size > 0:
                # Glow layers
                for i in range(3):
                    glow_size = size * (3 - i)
                    glow_alpha = int(alpha * 0.3 / (i + 1))
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    color = theme.get_color('flame_mid') if particle['life'] > 0.5 else theme.get_color('flame_outer')
                    pygame.draw.circle(glow_surf, (*color, glow_alpha), (glow_size, glow_size), glow_size)
                    surface.blit(glow_surf, (int(particle['x'] - glow_size), int(particle['y'] - glow_size)))
        
        # Button background with glow
        if self.glow_intensity > 0:
            # Outer glow
            glow_size = int(10 * self.glow_intensity)
            glow_rect = self.rect.inflate(glow_size * 2, glow_size * 2)
            for i in range(glow_size, 0, -2):
                alpha = int(50 * self.glow_intensity * (1 - i / glow_size))
                glow_color = (*theme.get_color('flame_mid'), alpha)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=15)
                surface.blit(glow_surf, (glow_rect.x, glow_rect.y))
        
        # Main button body
        base_color = theme.get_color('button_bg')
        if self.hovered or self.selected:
            base_color = theme.get_color('button_bg_hover')
        
        # Pulsing effect when hovered or selected
        pulse = math.sin(self.time * 5) * 0.2 * self.glow_intensity
        highlight = tuple(min(255, int(c * (1 + pulse))) for c in base_color)
        
        pygame.draw.rect(surface, highlight, self.rect, border_radius=10)
        
        # Border with ember glow
        border_color = theme.get_color('button_border')
        if self.hovered or self.selected:
            ember_intensity = (math.sin(self.time * 8) + 1) / 2
            flame_color = theme.get_color('flame_mid')
            border_color = (
                int(flame_color[0] * ember_intensity * 0.6 + border_color[0] * (1 - ember_intensity)),
                int(flame_color[1] * ember_intensity * 0.6 + border_color[1] * (1 - ember_intensity)),
                int(flame_color[2] * ember_intensity * 0.6 + border_color[2] * (1 - ember_intensity))
            )
        pygame.draw.rect(surface, border_color, self.rect, width=3, border_radius=10)
        
        # Text with glow effect
        text_color = theme.get_color('text_primary')
        if self.hovered or self.selected:
            text_color = theme.get_color('text_highlight')
        
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        
        # Text shadow
        shadow_surf = self.font.render(self.text, True, theme.get_color('text_shadow'))
        shadow_rect = shadow_surf.get_rect(center=(self.rect.centerx + 2, self.rect.centery + 2))
        surface.blit(shadow_surf, shadow_rect)
        
        # Main text
        surface.blit(text_surf, text_rect)

class CharacterCreationScene:
    """Character creation scene with elder dialogue and character setup."""
    def __init__(self):
        # Pygame is initialized by main.py
        
        self.SCREEN_WIDTH = 1366
        self.SCREEN_HEIGHT = 768
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN)
        pygame.display.set_caption("Scarred Winds - Character Creation")
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.running = True
        
        # Fonts from theme
        self.title_font = theme.get_font('title_medium')
        self.dialogue_font = theme.get_font('ui_medium')
        self.button_font = theme.get_font('ui_large')
        
        # Background colors from theme
        self.BG_TOP = theme.get_color('bg_dark')
        self.BG_BOTTOM = theme.get_color('bg_light')
        
        # Flame trail mouse effect
        self.flame_trail = FlameTrail(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, max_particles=20)
        
        # Load elder sprite
        try:
            self.elder_sprite = pygame.image.load('assets/sprites/elder.png').convert_alpha()
            # Scale elder sprite to very large size
            self.elder_sprite = pygame.transform.scale(self.elder_sprite, (750, 900))
        except pygame.error:
            print("Warning: Could not load elder.png, using placeholder")
            self.elder_sprite = pygame.Surface((750, 900), pygame.SRCALPHA)
            pygame.draw.rect(self.elder_sprite, (100, 100, 100), self.elder_sprite.get_rect())
        
        # Elder animation variables
        self.elder_bob_offset = 0.0
        self.elder_bob_speed = 1.5  # Slow bobbing speed
        self.elder_bob_amplitude = 8.0  # Small vertical movement
        
        # Dialogue system - repositioned to bottom, longer and taller
        self.dialogue_box = DialogueBox(
            (self.SCREEN_WIDTH - 1200) // 2,  # Centered
            self.SCREEN_HEIGHT - 220,         # 220px from the bottom
            1200,                             # Longer width
            200,                              # Taller height
            self.dialogue_font
        )
        self.dialogue_index = 0
        self.dialogue_complete = False
        
        # Elder dialogue sequence
        self.dialogue_sequence = [
            "Greetings, young one. I am the Elder of this village.",
            "You were born into a world of eternal winter, where the sun is but a distant memory.",
            "Our people have learned to survive through strength, cunning, and the sacred bond with the creatures of this frozen land.",
            "Tomorrow, you will face your Exile Day - the rite of passage that has defined our people for generations.",
            "You will venture into the wilderness alone, and only by proving your worth may you return.",
            "But first... tell me, what is your name?"
        ]
        
        # Character creation state - simplified to dialogue only
        self.creation_state = "dialogue"
        
        # Initialize first dialogue
        self.dialogue_box.set_text(self.dialogue_sequence[0])
        
        self.time = 0
    
    
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
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.creation_state == "dialogue":
                    # Play subtle click sound for dialogue advancement
                    play_sound('button_click', volume=0.3)
                    
                    # Advance dialogue
                    if self.dialogue_box.advance():
                        self.dialogue_index += 1
                        if self.dialogue_index < len(self.dialogue_sequence):
                            self.dialogue_box.set_text(self.dialogue_sequence[self.dialogue_index])
                        else:
                            # Dialogue is complete, trigger the transition
                            self.running = False
    
    def _setup_gender_selection(self):
        """Setup gender selection buttons."""
        button_width = 150
        button_height = 60
        button_spacing = 20
        total_width = button_width * 2 + button_spacing
        start_x = (self.SCREEN_WIDTH - total_width) // 2
        y = 400
        
        self.gender_buttons = [
            EmberButton(start_x, y, button_width, button_height, "Male", self.button_font),
            EmberButton(start_x + button_width + button_spacing, y, button_width, button_height, "Female", self.button_font)
        ]
    
    def _setup_name_input(self):
        """Setup name input field."""
        input_width = 300
        input_height = 50
        x = (self.SCREEN_WIDTH - input_width) // 2
        y = 400
        
        self.name_input = EmberTextInput(x, y, input_width, input_height, self.button_font, "Enter your name...")
        self.name_input.active = True
    
    def _setup_continue_button(self):
        """Setup continue button."""
        button_width = 200
        button_height = 60
        x = (self.SCREEN_WIDTH - button_width) // 2
        y = 500
        
        self.continue_button = EmberButton(x, y, button_width, button_height, "Continue", self.button_font)
    
    def update(self, dt):
        """Update scene state."""
        self.time += dt
        mouse_pos = pygame.mouse.get_pos()
        
        # Update elder bobbing animation
        self.elder_bob_offset += self.elder_bob_speed * dt
        if self.elder_bob_offset >= 2 * math.pi:
            self.elder_bob_offset -= 2 * math.pi
        
        # Update flame trail mouse effect
        self.flame_trail.update(dt, mouse_pos)
        
        # Update dialogue box
        if self.creation_state == "dialogue":
            self.dialogue_box.update(dt)
    
    def draw(self):
        """Draw the character creation scene."""
        # Clear screen first to prevent artifacts
        self.screen.fill((0, 0, 0))
        
        # Gradient background
        for y in range(self.SCREEN_HEIGHT):
            ratio = y / self.SCREEN_HEIGHT
            r = int(self.BG_TOP[0] * (1 - ratio) + self.BG_BOTTOM[0] * ratio)
            g = int(self.BG_TOP[1] * (1 - ratio) + self.BG_BOTTOM[1] * ratio)
            b = int(self.BG_TOP[2] * (1 - ratio) + self.BG_BOTTOM[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.SCREEN_WIDTH, y))
        
        # Draw elder sprite with bobbing animation
        # Position elder much more to the right
        elder_x = self.SCREEN_WIDTH - self.elder_sprite.get_width() + 200  # Much more to the right
        # Position elder so only his bottom touches the bottom of the screen
        # Screen height is 768, elder height is 900, so position at -132 to show only bottom
        elder_y = self.SCREEN_HEIGHT - self.elder_sprite.get_height()  # Bottom just touches screen bottom
        # Add bobbing animation
        bob_y = elder_y + math.sin(self.elder_bob_offset) * self.elder_bob_amplitude
        self.screen.blit(self.elder_sprite, (elder_x, bob_y))
        
        # Draw dialogue box
        if self.creation_state == "dialogue":
            self.dialogue_box.draw(self.screen)
        
        # Draw flame trail mouse effect
        self.flame_trail.draw(self.screen)
        
        # Vignette removed for cleaner look
        
        pygame.display.flip()
    
    def _draw_vignette(self):
        """Draw dark vignette effect."""
        vignette = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2
        max_radius = min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) // 2
        
        for i in range(max_radius, 0, -2):
            distance_ratio = 1 - (i / max_radius)
            alpha = int(255 * (distance_ratio ** 1.5) * 0.9)
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (center_x, center_y), i)
        
        self.screen.blit(vignette, (0, 0))
    
    def run(self):
        """Main loop."""
        print("Character Creation running...")
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        
        print("Elder dialogue complete. Transitioning to name/gender entry.")
        return "name_gender_entry"  # This tells main.py which scene to load next
    
    def take_screenshot(self):
        """Take a screenshot of the current screen."""
        import os
        from datetime import datetime
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/character_creation_{timestamp}.png"
        
        # Save screenshot
        pygame.image.save(self.screen, filename)
        print(f"Screenshot saved: {filename}")


if __name__ == "__main__":
    scene = CharacterCreationScene()
    result = scene.run()
    # Pygame cleanup handled by main.py
    print(f"Character creation result: {result}")
