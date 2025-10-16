#!/usr/bin/env python3
"""
Scarred Winds - Bedroom Scene (Story Part 1)
The player wakes up in their room and explores before Exile Day.
"""

import pygame
import math
from theme_config import theme
from asset_loader import get_scaled_asset, asset_loader
from logger import log_info
from mouse_trail import FlameTrail

class InteractableObject:
    """An object the player can interact with."""
    def __init__(self, rect, name, interaction_text, on_interact=None):
        self.rect = rect
        self.name = name
        self.interaction_text = interaction_text
        self.on_interact = on_interact
        self.highlighted = False
    
    def is_near(self, player_rect, distance=60):
        """Check if player is near enough to interact."""
        return self.rect.colliderect(player_rect.inflate(distance, distance))
    
    def interact(self):
        """Trigger interaction."""
        log_info(f"Interacting with: {self.name}")
        if self.on_interact:
            return self.on_interact()
        return self.interaction_text

class BedroomScene:
    """The player's bedroom - Story Part 1."""
    
    def __init__(self):
        self.SCREEN_WIDTH = 1366
        self.SCREEN_HEIGHT = 768
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN
        )
        pygame.display.set_caption("Scarred Winds - Your Room")
        
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.running = True
        
        # Camera/viewport
        self.camera_x = 0
        self.camera_y = 0
        
        # Room dimensions (larger than screen for exploration)
        self.room_width = 1600
        self.room_height = 1200
        
        # Player (using your sprite animations later)
        self.player_x = self.room_width // 2
        self.player_y = self.room_height // 2
        self.player_width = 48
        self.player_height = 48
        self.player_speed = 200  # pixels per second
        
        # Load assets with appropriate scaling
        self.tile_scale = 2.0  # Scale up tiles
        self.furniture_scale = 1.5  # Scale furniture
        
        self._load_assets()
        self._setup_room()
        self._create_interactables()
        
        # UI
        self.dialogue_font = theme.get_font('ui_medium')
        self.ui_font = theme.get_font('ui_small')
        self.current_dialogue = None
        self.dialogue_timer = 0
        self.dialogue_duration = 3.0
        
        # Flame trail effect
        self.flame_trail = FlameTrail(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, max_particles=15)
        
        # Story flags
        self.has_checked_bed = False
        self.has_checked_photo = False
        self.has_checked_calendar = False
        self.has_checked_chest = False
        
        self.time = 0
    
    def _load_assets(self):
        """Load all bedroom assets."""
        try:
            # Floor tiles
            self.floor_tile = get_scaled_asset("damaged_wood_tile.png", self.tile_scale)
            
            # Furniture
            self.bed = get_scaled_asset("damaged_bed.png", self.furniture_scale)
            self.bookshelf = get_scaled_asset("damaged_bookshelf.png", self.furniture_scale)
            self.chest = get_scaled_asset("wood_chest.png", self.furniture_scale)
            self.calendar = get_scaled_asset("calendar.png", self.furniture_scale)
            
            # Rug
            self.rug = get_scaled_asset("rug_tile.png", self.tile_scale)
            
            log_info("Bedroom assets loaded successfully")
        except Exception as e:
            log_info(f"Some assets failed to load (using placeholders): {e}")
    
    def _setup_room(self):
        """Create the room layout."""
        # Create tiled floor
        tile_width = self.floor_tile.get_width()
        tile_height = self.floor_tile.get_height()
        
        self.floor_surface = pygame.Surface((self.room_width, self.room_height))
        
        # Tile the floor
        for y in range(0, self.room_height, tile_height):
            for x in range(0, self.room_width, tile_width):
                self.floor_surface.blit(self.floor_tile, (x, y))
        
        log_info("Room floor created")
    
    def _create_interactables(self):
        """Create interactable objects in the room."""
        self.interactables = []
        
        # Bed (bottom left area)
        bed_rect = pygame.Rect(200, 800, self.bed.get_width(), self.bed.get_height())
        self.interactables.append(InteractableObject(
            bed_rect, 
            "Bed",
            "A worn bed with torn sheets. You slept here... but you don't remember much.",
            on_interact=self._interact_bed
        ))
        
        # Calendar (on wall, top center)
        calendar_rect = pygame.Rect(700, 150, self.calendar.get_width(), self.calendar.get_height())
        self.interactables.append(InteractableObject(
            calendar_rect,
            "Calendar",
            "The 26th is marked with a red X. Tomorrow is Exile Day...",
            on_interact=self._interact_calendar
        ))
        
        # Empty photo frame (on wall, left side)
        photo_rect = pygame.Rect(300, 200, 80, 60)
        self.interactables.append(InteractableObject(
            photo_rect,
            "Photo Frame",
            "An empty photo frame. No memories... no family. Just emptiness.",
            on_interact=self._interact_photo
        ))
        
        # Chest (bottom right)
        chest_rect = pygame.Rect(1200, 850, self.chest.get_width(), self.chest.get_height())
        self.interactables.append(InteractableObject(
            chest_rect,
            "Chest",
            "A small wooden chest. Inside are a few worn clothes and nothing else.",
            on_interact=self._interact_chest
        ))
        
        # Bookshelf (right wall)
        bookshelf_rect = pygame.Rect(1300, 400, self.bookshelf.get_width(), self.bookshelf.get_height())
        self.interactables.append(InteractableObject(
            bookshelf_rect,
            "Bookshelf",
            "Damaged books about survival in the wilderness. You've read them all.",
            on_interact=None
        ))
        
        log_info(f"Created {len(self.interactables)} interactable objects")
    
    def _interact_bed(self):
        """Player checks the bed."""
        self.has_checked_bed = True
        return "You touch the rough sheets. How many nights have you spent here, staring at nothing?"
    
    def _interact_calendar(self):
        """Player checks the calendar - KEY STORY MOMENT."""
        self.has_checked_calendar = True
        return "Tomorrow is the 26th. Exile Day. One villager chosen by vote... sent away to die."
    
    def _interact_photo(self):
        """Player checks the empty frame - establishes orphan backstory."""
        self.has_checked_photo = True
        return "No photo. No family. No past. You are alone. You have always been alone."
    
    def _interact_chest(self):
        """Player checks their belongings."""
        self.has_checked_chest = True
        return "Just the bare essentials. You own nothing of value. You are no one."
    
    def handle_events(self):
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F12:
                    self.take_screenshot()
                elif event.key == pygame.K_e or event.key == pygame.K_SPACE:
                    # Interaction key
                    self._try_interact()
                elif event.key == pygame.K_RETURN:
                    # Skip to next scene (for testing)
                    if self.has_checked_calendar:
                        log_info("Moving to next scene...")
                        self.running = False
    
    def _try_interact(self):
        """Try to interact with nearby objects."""
        player_rect = pygame.Rect(self.player_x, self.player_y, self.player_width, self.player_height)
        
        for obj in self.interactables:
            if obj.is_near(player_rect):
                text = obj.interact()
                if text:
                    self.show_dialogue(text)
                break
    
    def show_dialogue(self, text):
        """Show dialogue text."""
        self.current_dialogue = text
        self.dialogue_timer = 0
        log_info(f"Dialogue: {text}")
    
    def update(self, dt):
        """Update game state."""
        self.time += dt
        
        # Update flame trail
        mouse_pos = pygame.mouse.get_pos()
        self.flame_trail.update(dt, mouse_pos)
        
        # Player movement
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.player_speed * dt
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.player_speed * dt
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.player_speed * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.player_speed * dt
        
        # Update player position with bounds checking
        self.player_x = max(self.player_width, min(self.room_width - self.player_width, self.player_x + dx))
        self.player_y = max(self.player_height, min(self.room_height - self.player_height, self.player_y + dy))
        
        # Update camera to follow player
        self.camera_x = self.player_x - self.SCREEN_WIDTH // 2
        self.camera_y = self.player_y - self.SCREEN_HEIGHT // 2
        
        # Clamp camera to room bounds
        self.camera_x = max(0, min(self.room_width - self.SCREEN_WIDTH, self.camera_x))
        self.camera_y = max(0, min(self.room_height - self.SCREEN_HEIGHT, self.camera_y))
        
        # Update interactable highlights
        player_rect = pygame.Rect(self.player_x, self.player_y, self.player_width, self.player_height)
        for obj in self.interactables:
            obj.highlighted = obj.is_near(player_rect)
        
        # Update dialogue timer
        if self.current_dialogue:
            self.dialogue_timer += dt
            if self.dialogue_timer >= self.dialogue_duration:
                self.current_dialogue = None
    
    def draw(self):
        """Render the scene."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Draw floor (with camera offset)
        self.screen.blit(self.floor_surface, (-self.camera_x, -self.camera_y))
        
        # Draw furniture (with camera offset)
        for obj in self.interactables:
            # Get the appropriate sprite
            sprite = None
            if obj.name == "Bed":
                sprite = self.bed
            elif obj.name == "Calendar":
                sprite = self.calendar
            elif obj.name == "Chest":
                sprite = self.chest
            elif obj.name == "Bookshelf":
                sprite = self.bookshelf
            
            if sprite:
                draw_x = obj.rect.x - self.camera_x
                draw_y = obj.rect.y - self.camera_y
                self.screen.blit(sprite, (draw_x, draw_y))
                
                # Highlight if near
                if obj.highlighted:
                    highlight_rect = pygame.Rect(draw_x, draw_y, obj.rect.width, obj.rect.height)
                    pygame.draw.rect(self.screen, theme.get_color('flame_mid'), highlight_rect, 2)
        
        # Draw empty photo frame placeholder
        for obj in self.interactables:
            if obj.name == "Photo Frame":
                draw_x = obj.rect.x - self.camera_x
                draw_y = obj.rect.y - self.camera_y
                pygame.draw.rect(self.screen, (80, 70, 60), (draw_x, draw_y, obj.rect.width, obj.rect.height))
                pygame.draw.rect(self.screen, (40, 35, 30), (draw_x, draw_y, obj.rect.width, obj.rect.height), 3)
                if obj.highlighted:
                    pygame.draw.rect(self.screen, theme.get_color('flame_mid'), (draw_x, draw_y, obj.rect.width, obj.rect.height), 2)
        
        # Draw player (placeholder - will use your sprite animations later)
        player_screen_x = self.player_x - self.camera_x
        player_screen_y = self.player_y - self.camera_y
        pygame.draw.rect(self.screen, (200, 180, 160), (player_screen_x, player_screen_y, self.player_width, self.player_height))
        pygame.draw.circle(self.screen, (180, 160, 140), (int(player_screen_x + self.player_width//2), int(player_screen_y + 10)), 8)
        
        # Draw flame trail
        self.flame_trail.draw(self.screen)
        
        # Draw UI
        self._draw_ui()
        
        pygame.display.flip()
    
    def _draw_ui(self):
        """Draw UI elements."""
        # Dialogue box
        if self.current_dialogue:
            # Background
            dialogue_height = 120
            dialogue_rect = pygame.Rect(50, self.SCREEN_HEIGHT - dialogue_height - 50, self.SCREEN_WIDTH - 100, dialogue_height)
            pygame.draw.rect(self.screen, (20, 15, 10, 200), dialogue_rect, border_radius=10)
            pygame.draw.rect(self.screen, theme.get_color('button_border'), dialogue_rect, width=2, border_radius=10)
            
            # Text with wrapping
            words = self.current_dialogue.split(' ')
            lines = []
            current_line = ""
            max_width = dialogue_rect.width - 40
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_surf = self.dialogue_font.render(test_line, True, theme.get_color('text_primary'))
                if test_surf.get_width() < max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)
            
            # Draw lines
            y_offset = dialogue_rect.y + 20
            for line in lines:
                text_surf = self.dialogue_font.render(line, True, theme.get_color('text_primary'))
                self.screen.blit(text_surf, (dialogue_rect.x + 20, y_offset))
                y_offset += 30
        
        # Interaction prompt
        player_rect = pygame.Rect(self.player_x, self.player_y, self.player_width, self.player_height)
        for obj in self.interactables:
            if obj.is_near(player_rect):
                prompt = f"[E] {obj.name}"
                prompt_surf = self.ui_font.render(prompt, True, theme.get_color('text_highlight'))
                prompt_rect = prompt_surf.get_rect(center=(self.SCREEN_WIDTH // 2, 100))
                
                # Background
                bg_rect = prompt_rect.inflate(20, 10)
                pygame.draw.rect(self.screen, (20, 15, 10, 180), bg_rect, border_radius=5)
                pygame.draw.rect(self.screen, theme.get_color('flame_mid'), bg_rect, width=1, border_radius=5)
                
                self.screen.blit(prompt_surf, prompt_rect)
                break
        
        # Instructions (top right)
        instructions = [
            "WASD/Arrows - Move",
            "E/Space - Interact",
            "Enter - Next Scene (after checking calendar)",
            "ESC - Exit"
        ]
        
        y = 20
        for instruction in instructions:
            text_surf = self.ui_font.render(instruction, True, theme.get_color('text_dark'))
            self.screen.blit(text_surf, (self.SCREEN_WIDTH - text_surf.get_width() - 20, y))
            y += 25
    
    def take_screenshot(self):
        """Take a screenshot."""
        import os
        from datetime import datetime
        
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/bedroom_{timestamp}.png"
        pygame.image.save(self.screen, filename)
        log_info(f"Screenshot saved: {filename}")
    
    def run(self):
        """Main game loop."""
        log_info("Bedroom scene started")
        
        # Show opening dialogue
        self.show_dialogue("You slowly open your eyes. Another day in this cold, dark world...")
        
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        
        log_info("Bedroom scene ended")
        
        # Return next scene
        if self.has_checked_calendar:
            return "village_exterior"  # Next scene to implement
        return "main_menu"

if __name__ == "__main__":
    scene = BedroomScene()
    result = scene.run()
    log_info(f"Transitioning to: {result}")
