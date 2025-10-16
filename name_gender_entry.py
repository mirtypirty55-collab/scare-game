#!/usr/bin/env python3
"""
Scarred Winds - Name & Gender Entry Scene
A dedicated screen for character data input, styled after classic Pokémon games.
"""

import pygame
import sys
import math
import random
from theme_config import theme
from sound_manager import play_sound

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
        self.glow_intensity += (target_glow - self.glow_intensity) * 8 * dt  # Faster (was 5)
        
        # Spawn ember particles when hovered or selected
        if (self.hovered or self.selected) and random.random() < 0.25:  # More frequent (was 0.15)
            self.ember_particles.append({
                'x': random.uniform(self.rect.left, self.rect.right),
                'y': self.rect.bottom,
                'life': 1.0,
                'velocity_y': random.uniform(-50, -90),  # Faster (was -40 to -80)
                'velocity_x': random.uniform(-20, 20),  # Wider (was -15 to 15)
                'size': random.uniform(3, 6),  # Larger (was 2-5)
                'color': random.choice([
                    theme.get_color('flame_core'),
                    theme.get_color('flame_mid'),
                    theme.get_color('flame_outer')
                ])
            })
        
        # Update ember particles
        for particle in self.ember_particles[:]:
            particle['life'] -= dt * 0.8
            particle['y'] += particle['velocity_y'] * dt
            particle['x'] += particle['velocity_x'] * dt
            particle['velocity_y'] += 50 * dt  # Gravity
            if particle['life'] <= 0:
                self.ember_particles.remove(particle)
    
    def draw(self, surface):
        """Draw the button with ember effects."""
        # Draw ember particles
        for particle in self.ember_particles:
            alpha = int(255 * particle['life'])
            size = int(3 * particle['life'])
            if size > 0:
                # Glow effect for particles
                for i in range(3):
                    glow_size = size * (3 - i)
                    glow_alpha = int(alpha * 0.3 / (i + 1))
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    color = theme.get_color('flame_mid') if particle['life'] > 0.5 else theme.get_color('flame_outer')
                    pygame.draw.circle(glow_surf, (*color, glow_alpha), (glow_size, glow_size), glow_size)
                    surface.blit(glow_surf, (int(particle['x'] - glow_size), int(particle['y'] - glow_size)))
        
        # Draw button glow
        if self.glow_intensity > 0:
            glow_size = int(10 * self.glow_intensity)
            glow_rect = self.rect.inflate(glow_size * 2, glow_size * 2)
            for i in range(glow_size, 0, -2):
                alpha = int(50 * self.glow_intensity * (1 - i / glow_size))
                glow_color = (*theme.get_color('flame_mid'), alpha)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=15)
                surface.blit(glow_surf, (glow_rect.x, glow_rect.y))
        
        # Draw button background
        base_color = theme.get_color('button_bg')
        if self.hovered or self.selected:
            base_color = theme.get_color('button_bg_hover')
        
        # Add pulsing effect
        pulse = math.sin(self.time * 5) * 0.2 * self.glow_intensity
        highlight = tuple(min(255, int(c * (1 + pulse))) for c in base_color)
        pygame.draw.rect(surface, highlight, self.rect, border_radius=8)
        
        # Draw button border
        border_color = theme.get_color('button_border')
        if self.hovered or self.selected:
            ember_intensity = (math.sin(self.time * 8) + 1) / 2
            flame_color = theme.get_color('flame_mid')
            border_color = (
                int(flame_color[0] * ember_intensity * 0.6 + border_color[0] * (1 - ember_intensity)),
                int(flame_color[1] * ember_intensity * 0.6 + border_color[1] * (1 - ember_intensity)),
                int(flame_color[2] * ember_intensity * 0.6 + border_color[2] * (1 - ember_intensity))
            )
        pygame.draw.rect(surface, border_color, self.rect, width=3, border_radius=8)
        
        # Draw button text
        text_color = theme.get_color('text_primary')
        if self.hovered or self.selected:
            text_color = theme.get_color('text_highlight')
        
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        
        # Draw text shadow
        shadow_surf = self.font.render(self.text, True, theme.get_color('text_shadow'))
        shadow_rect = shadow_surf.get_rect(center=(self.rect.centerx + 2, self.rect.centery + 2))
        surface.blit(shadow_surf, shadow_rect)
        surface.blit(text_surf, text_rect)

class EmberTextInput:
    """A text input field with ember effects."""
    def __init__(self, x, y, width, height, font, placeholder="Enter text..."):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.placeholder = placeholder
        self.text = ""
        self.active = True  # Start as active by default
        self.cursor_visible = True
        self.cursor_timer = 0.0
        self.max_length = 10  # Pokémon style names are shorter
        self.ember_particles = []
        self.time = 0

    def update(self, dt):
        """Update input field state and animations."""
        self.time += dt
        self.cursor_timer += dt
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
        
        # Update ember particles
        for particle in self.ember_particles[:]:
            particle['life'] -= dt * 0.8
            particle['y'] += particle['velocity_y'] * dt
            particle['x'] += particle['velocity_x'] * dt
            particle['velocity_y'] += 30 * dt  # Gravity
            if particle['life'] <= 0:
                self.ember_particles.remove(particle)

    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length and event.unicode.isalnum():
                self.text += event.unicode
    
    def draw(self, surface):
        """Draw the text input field with full ember effects."""
        # Draw ember particles
        for particle in self.ember_particles:
            alpha = int(255 * particle['life'])
            size = int(2 * particle['life'])
            if size > 0:
                # Glow effect for particles
                for i in range(3):
                    glow_size = size * (3 - i)
                    glow_alpha = int(alpha * 0.3 / (i + 1))
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*particle['color'], glow_alpha), (glow_size, glow_size), glow_size)
                    surface.blit(glow_surf, (int(particle['x'] - glow_size), int(particle['y'] - glow_size)))
        
        # Draw input field glow when active
        if self.active:
            glow_size = int(8)
            glow_rect = self.rect.inflate(glow_size * 2, glow_size * 2)
            for i in range(glow_size, 0, -2):
                alpha = int(40 * (1 - i / glow_size))
                glow_color = (*theme.get_color('flame_mid'), alpha)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=8)
                surface.blit(glow_surf, (glow_rect.x, glow_rect.y))
        
        # Draw input field background
        base_color = theme.get_color('button_bg')
        if self.active:
            base_color = theme.get_color('button_bg_hover')
        pygame.draw.rect(surface, base_color, self.rect, border_radius=8)
        
        # Draw input field border
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
        
        # Draw text or placeholder
        if self.text:
            text_surf = self.font.render(self.text, True, theme.get_color('text_primary'))
        else:
            text_surf = self.font.render(self.placeholder, True, theme.get_color('text_dark'))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Draw cursor when active
        if self.active and self.cursor_visible:
            # Calculate cursor position based on rendered text width
            text_width = self.font.size(self.text)[0]
            cursor_x = self.rect.x + (self.rect.width - text_width) / 2 + text_width + 5
            cursor_y1 = self.rect.centery - 10
            cursor_y2 = self.rect.centery + 10
            pygame.draw.line(surface, theme.get_color('flame_core'), (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)

class NameGenderEntryScene:
    """Dedicated screen for character name and gender input in Pokémon Platinum style."""
    def __init__(self):
        self.SCREEN_WIDTH = 1366
        self.SCREEN_HEIGHT = 768
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.running = True

        # Fonts
        self.dialogue_font = theme.get_font('ui_medium')
        self.input_font = theme.get_font('ui_large')

        # State machine for the screen
        self.state = "GENDER_SELECT"  # GENDER_SELECT -> NAME_ENTRY
        self.selected_gender = "Male"  # Default selection
        self.player_name = ""

        # Left Panel (Character Display & Dialogue)
        self.left_panel_rect = pygame.Rect(0, 0, self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT)
        self.dialogue_box_rect = pygame.Rect(20, self.SCREEN_HEIGHT - 170, self.left_panel_rect.width - 40, 150)
        
        # Load character sprites - try to load actual sprites, fallback to placeholders
        import os
        
        # Try to load male character sprite
        male_sprite_path = 'assets/sprites/male_character.png'
        if os.path.exists(male_sprite_path):
            try:
                male_sprite_raw = pygame.image.load(male_sprite_path).convert_alpha()
                self.male_sprite = pygame.transform.scale(male_sprite_raw, (150, 300))
                print("Loaded male character sprite")
            except pygame.error as e:
                print(f"Warning: Could not load male_character.png: {e}, using placeholder")
                self.male_sprite = self._create_male_placeholder()
        else:
            print("Warning: male_character.png not found, using placeholder")
            self.male_sprite = self._create_male_placeholder()
        
        # Try to load female character sprite
        female_sprite_path = 'assets/sprites/female_character.png'
        if os.path.exists(female_sprite_path):
            try:
                female_sprite_raw = pygame.image.load(female_sprite_path).convert_alpha()
                self.female_sprite = pygame.transform.scale(female_sprite_raw, (150, 300))
                print("Loaded female character sprite")
            except pygame.error as e:
                print(f"Warning: Could not load female_character.png: {e}, using placeholder")
                self.female_sprite = self._create_female_placeholder()
        else:
            print("Warning: female_character.png not found, using placeholder")
            self.female_sprite = self._create_female_placeholder()

        # Right Panel (Input)
        self.right_panel_rect = pygame.Rect(self.SCREEN_WIDTH // 2, 0, self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT)
        self.name_input = EmberTextInput(self.right_panel_rect.x + 50, 100, 500, 80, self.input_font, "")
        
        # On-screen keyboard buttons
        self.keyboard_buttons = []
        self.create_keyboard()

        # OK and Back buttons
        self.ok_button = EmberButton(self.right_panel_rect.right - 150, 190, 100, 60, "OK", self.dialogue_font)
        self.back_button = EmberButton(self.right_panel_rect.right - 270, 190, 100, 60, "Back", self.dialogue_font)
        
        # Atmospheric effects
        from mouse_trail import FlameTrail
        self.flame_trail = FlameTrail(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, max_particles=20)
        
        # Background particles for atmosphere
        self.background_particles = []
        for _ in range(15):
            self.background_particles.append({
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

    def create_keyboard(self):
        """Create the on-screen keyboard layout - QWERTY style."""
        layout = [
            "q w e r t y u i o p",
            "a s d f g h j k l",
            "z x c v b n m",
            "0 1 2 3 4 5 6 7 8 9"
        ]
        btn_size = 50
        start_x = self.right_panel_rect.x + 40
        start_y = 300
        for row_idx, row_str in enumerate(layout):
            for col_idx, char in enumerate(row_str.split(' ')):
                x = start_x + col_idx * (btn_size + 5)
                y = start_y + row_idx * (btn_size + 5)
                self.keyboard_buttons.append(EmberButton(x, y, btn_size, btn_size, char, self.dialogue_font))
    
    def handle_events(self):
        """Handle input events."""
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return "main_menu"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                # Take screenshot
                self.take_screenshot()

            if self.state == "GENDER_SELECT":
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        play_sound('button_click', volume=0.5)
                        self.selected_gender = "Male"
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        play_sound('button_click', volume=0.5)
                        self.selected_gender = "Female"
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        play_sound('button_click', volume=0.6)
                        self.state = "NAME_ENTRY"
            
            elif self.state == "NAME_ENTRY":
                self.name_input.handle_event(event)  # Handle physical keyboard
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.player_name = self.name_input.text.strip()
                    if self.player_name:
                        return "bedroom"  # Go to bedroom scene

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # On-screen keyboard logic
                    for btn in self.keyboard_buttons:
                        if btn.rect.collidepoint(mouse_pos) and len(self.name_input.text) < self.name_input.max_length:
                            self.name_input.text += btn.text
                            play_sound('button_click', volume=0.4)  # Quieter for keyboard
                    
                    # Back and OK buttons
                    if self.back_button.rect.collidepoint(mouse_pos):
                        play_sound('button_click', volume=0.6)
                        self.state = "GENDER_SELECT"
                    if self.ok_button.rect.collidepoint(mouse_pos):
                        play_sound('button_click', volume=0.6)
                        self.player_name = self.name_input.text.strip()
                        if self.player_name:
                             return "bedroom"  # Go to bedroom scene

    def update(self, dt):
        """Update scene state."""
        mouse_pos = pygame.mouse.get_pos()
        self.name_input.update(dt)
        for btn in self.keyboard_buttons:
            btn.update(dt, mouse_pos)
        self.ok_button.update(dt, mouse_pos)
        self.back_button.update(dt, mouse_pos)
        
        # Update flame trail mouse effect
        self.flame_trail.update(dt, mouse_pos)
        
        # Update background particles
        for particle in self.background_particles[:]:
            particle['life'] -= dt * 0.3
            particle['y'] += particle['velocity_y'] * dt
            particle['x'] += particle['velocity_x'] * dt
            particle['velocity_y'] += 8 * dt  # Light gravity
            if particle['life'] <= 0:
                # Respawn particle at top
                particle['x'] = random.uniform(0, self.SCREEN_WIDTH)
                particle['y'] = self.SCREEN_HEIGHT + 10
                particle['life'] = 1.0
                particle['velocity_y'] = random.uniform(-5, -15)
                particle['velocity_x'] = random.uniform(-2, 2)

    def draw(self):
        """Draw the scene."""
        # Clear screen first to prevent artifacts
        self.screen.fill((0, 0, 0))
        
        # --- NEW: Replace screen.fill with atmospheric background ---
        # Gradient background
        for y in range(self.SCREEN_HEIGHT):
            ratio = y / self.SCREEN_HEIGHT
            top_color = theme.get_color('bg_dark')
            bottom_color = theme.get_color('bg_light')
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.SCREEN_WIDTH, y))

        # --- REPLACE Left and Right Panel Fills with Active/Inactive States ---
        # Left Panel (Character Display)
        left_panel_surf = pygame.Surface(self.left_panel_rect.size, pygame.SRCALPHA)
        if self.state == "GENDER_SELECT":
            # Active panel - brighter
            left_panel_surf.fill((*theme.get_color('button_bg'), 150))
            left_border_color = theme.get_color('flame_mid')  # Ember glow for active
        else:
            # Inactive panel - dimmer
            left_panel_surf.fill((*theme.get_color('button_bg'), 80))  # Much dimmer
            # Add dark overlay for inactive state
            dark_overlay = pygame.Surface(self.left_panel_rect.size, pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 100))  # Dark overlay
            left_panel_surf.blit(dark_overlay, (0, 0))
            left_border_color = theme.get_color('button_border')  # Normal border for inactive
        
        self.screen.blit(left_panel_surf, self.left_panel_rect.topleft)
        pygame.draw.rect(self.screen, left_border_color, self.left_panel_rect, 3, border_radius=10)
        
        # Right Panel (Input)
        right_panel_surf = pygame.Surface(self.right_panel_rect.size, pygame.SRCALPHA)
        if self.state == "NAME_ENTRY":
            # Active panel - brighter
            right_panel_surf.fill((*theme.get_color('button_bg'), 150))
            right_border_color = theme.get_color('flame_mid')  # Ember glow for active
        else:
            # Inactive panel - dimmer
            right_panel_surf.fill((*theme.get_color('button_bg'), 80))  # Much dimmer
            # Add dark overlay for inactive state
            dark_overlay = pygame.Surface(self.right_panel_rect.size, pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 100))  # Dark overlay
            right_panel_surf.blit(dark_overlay, (0, 0))
            right_border_color = theme.get_color('button_border')  # Normal border for inactive
        
        self.screen.blit(right_panel_surf, self.right_panel_rect.topleft)
        pygame.draw.rect(self.screen, right_border_color, self.right_panel_rect, 3, border_radius=10)
        
        # Draw character sprites with better spacing
        male_pos = (self.left_panel_rect.centerx - 200, 150)  # Move male further left
        female_pos = (self.left_panel_rect.centerx + 50, 150)  # Move female further right
        self.screen.blit(self.male_sprite, male_pos)
        self.screen.blit(self.female_sprite, female_pos)
        
        # Add state indicator text
        if self.state == "GENDER_SELECT":
            # Show "SELECT GENDER" indicator on left panel
            indicator_text = "SELECT GENDER"
            indicator_surf = self.dialogue_font.render(indicator_text, True, theme.get_color('flame_core'))
            indicator_rect = indicator_surf.get_rect(center=(self.left_panel_rect.centerx, 100))
            # Add glow effect to active indicator
            for i in range(3):
                glow_surf = self.dialogue_font.render(indicator_text, True, (*theme.get_color('flame_mid'), 50 - i * 15))
                glow_rect = glow_surf.get_rect(center=(indicator_rect.centerx + i, indicator_rect.centery + i))
                self.screen.blit(glow_surf, glow_rect)
            self.screen.blit(indicator_surf, indicator_rect)
        else:
            # Show "ENTER NAME" indicator on right panel
            indicator_text = "ENTER NAME"
            indicator_surf = self.dialogue_font.render(indicator_text, True, theme.get_color('flame_core'))
            indicator_rect = indicator_surf.get_rect(center=(self.right_panel_rect.centerx, 50))
            # Add glow effect to active indicator
            for i in range(3):
                glow_surf = self.dialogue_font.render(indicator_text, True, (*theme.get_color('flame_mid'), 50 - i * 15))
                glow_rect = glow_surf.get_rect(center=(indicator_rect.centerx + i, indicator_rect.centery + i))
                self.screen.blit(glow_surf, glow_rect)
            self.screen.blit(indicator_surf, indicator_rect)
        
        # Highlight selected gender with ember glow
        if self.state == "GENDER_SELECT":
            highlight_rect = pygame.Rect(male_pos, self.male_sprite.get_size()) if self.selected_gender == "Male" else pygame.Rect(female_pos, self.female_sprite.get_size())
            # Ember-style highlight instead of plain red
            for i in range(3):
                glow_size = 20 - i * 5
                alpha = int(100 * (1 - i / 3))
                glow_color = (*theme.get_color('flame_mid'), alpha)
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=5)
                self.screen.blit(glow_surf, (highlight_rect.centerx - glow_size, highlight_rect.centery - glow_size))

        # --- REPLACE Dialogue Box drawing ---
        pygame.draw.rect(self.screen, theme.get_color('button_bg'), self.dialogue_box_rect, border_radius=10)
        pygame.draw.rect(self.screen, theme.get_color('button_border'), self.dialogue_box_rect, 2, border_radius=10)
        
        # Dialogue text based on state
        if self.state == "GENDER_SELECT":
            dialogue_text = "Are you a boy?\nOr are you a girl?"
        else:
            if self.selected_gender == "Male":
                dialogue_text = "So, you're a boy.\nWhat is your name?"
            else:
                dialogue_text = "So, you're a girl.\nWhat is your name?"
        
        # --- REPLACE Dialogue Text drawing ---
        y_offset = self.dialogue_box_rect.y + 30
        for line in dialogue_text.split('\n'):
            text_surf = self.dialogue_font.render(line, True, theme.get_color('text_primary'))  # Use theme color
            self.screen.blit(text_surf, (self.dialogue_box_rect.x + 30, y_offset))
            y_offset += 40
        
        # Draw name input field
        self.name_input.draw(self.screen)
        
        # Draw on-screen keyboard
        for btn in self.keyboard_buttons:
            btn.draw(self.screen)
        
        # Draw OK and Back buttons
        self.ok_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        # Draw flame trail mouse effect
        self.flame_trail.draw(self.screen)
        
        # Draw background particles
        for particle in self.background_particles:
            alpha = int(180 * particle['life'])
            size = int(particle['size'] * particle['life'])
            if size > 0:
                # Glow effect for particles
                for i in range(3):
                    glow_size = size * (3 - i)
                    glow_alpha = int(alpha * 0.4 / (i + 1))
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*particle['color'], glow_alpha), (glow_size, glow_size), glow_size)
                    self.screen.blit(glow_surf, (int(particle['x'] - glow_size), int(particle['y'] - glow_size)))
        
        # Add vignette for cinematic feel
        self._draw_vignette()

        pygame.display.flip()
    
    def run(self):
        """Run the scene."""
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0
            next_scene = self.handle_events()
            if next_scene:
                return next_scene
            self.update(dt)
            self.draw()
        return "main_menu"
    
    def _draw_vignette(self):
        """Draw vignette effect for cinematic feel."""
        vignette = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2
        max_radius = min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) // 2
        
        for i in range(max_radius, 0, -2):
            distance_ratio = 1 - (i / max_radius)
            alpha = int(255 * (distance_ratio ** 1.5) * 0.6)  # Lighter vignette
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (center_x, center_y), i)
        
        self.screen.blit(vignette, (0, 0))
    
    def take_screenshot(self):
        """Take a screenshot of the current screen."""
        import os
        from datetime import datetime
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/name_gender_entry_{timestamp}.png"
        
        # Save screenshot
        pygame.image.save(self.screen, filename)
        print(f"Screenshot saved: {filename}")
    
    def _create_male_placeholder(self):
        """Create a detailed male character placeholder."""
        sprite = pygame.Surface((150, 300), pygame.SRCALPHA)
        # Orange background
        pygame.draw.rect(sprite, (255, 165, 0), (0, 0, 150, 300))
        # Head
        pygame.draw.circle(sprite, (255, 220, 177), (75, 60), 25)
        # Body
        pygame.draw.rect(sprite, (200, 100, 0), (60, 85, 30, 80))
        # Left arm
        pygame.draw.rect(sprite, (200, 100, 0), (40, 90, 20, 60))
        # Right arm
        pygame.draw.rect(sprite, (200, 100, 0), (90, 90, 20, 60))
        # Left leg
        pygame.draw.rect(sprite, (200, 100, 0), (65, 165, 20, 80))
        # Right leg
        pygame.draw.rect(sprite, (200, 100, 0), (85, 165, 20, 80))
        return sprite
    
    def _create_female_placeholder(self):
        """Create a detailed female character placeholder."""
        sprite = pygame.Surface((150, 300), pygame.SRCALPHA)
        # Red background
        pygame.draw.rect(sprite, (255, 0, 0), (0, 0, 150, 300))
        # Head
        pygame.draw.circle(sprite, (255, 220, 177), (75, 60), 25)
        # Body
        pygame.draw.rect(sprite, (180, 0, 0), (60, 85, 30, 80))
        # Left arm
        pygame.draw.rect(sprite, (180, 0, 0), (40, 90, 20, 60))
        # Right arm
        pygame.draw.rect(sprite, (180, 0, 0), (90, 90, 20, 60))
        # Left leg
        pygame.draw.rect(sprite, (180, 0, 0), (65, 165, 20, 80))
        # Right leg
        pygame.draw.rect(sprite, (180, 0, 0), (85, 165, 20, 80))
        return sprite


if __name__ == "__main__":
    # Pygame is initialized by main.py
    screen = pygame.display.set_mode((1366, 768), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN)
    scene = NameGenderEntryScene()
    result = scene.run()
    # Pygame cleanup handled by main.py
    print(f"Name/Gender entry result: {result}")