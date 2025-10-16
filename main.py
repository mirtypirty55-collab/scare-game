#!/usr/bin/env python3
"""
Viking Creature Game - Main Entry Point
Simple launcher for the start screen
"""

import pygame
import sys
from pygame_manager import safe_pygame_init, safe_pygame_quit, is_pygame_ready
from logger import log_info, log_error, log_warning
from start_screen import StartScreen
from main_menu import MainMenu
from settings_screen import SettingsScreen
from character_creation import CharacterCreationScene
from name_gender_entry import NameGenderEntryScene
from bedroom_scene import BedroomScene

# Scene mapping for scalable scene management
SCENE_MAP = {
    "start_screen": StartScreen,
    "main_menu": MainMenu,
    "settings": SettingsScreen,
    "character_creation": CharacterCreationScene,
    "name_gender_entry": NameGenderEntryScene,
    "bedroom": BedroomScene,
    # Future scenes can be added here:
    # "village_exterior": VillageExteriorScene,
    # "battle": BattleUI,
    # "cave": CaveScene,
    # "inventory": InventoryScreen,
}

def main():
    """Main entry point for Scarred Winds."""
    log_info("Starting Scarred Winds...")
    
    try:
        # Initialize pygame safely
        if not safe_pygame_init(init_mixer=True, init_font=True):
            log_error("Failed to initialize pygame. Exiting.")
            return

        # Scene flow system with scalable scene mapping
        current_scene_name = "start_screen"
        
        while current_scene_name:
            # Look up the scene class from the map
            scene_class = SCENE_MAP.get(current_scene_name)
            
            if scene_class:
                log_info(f"Loading {current_scene_name}...")
                # Create an instance of the scene and run it
                current_scene = scene_class()
                next_scene_name = current_scene.run()  # .run() should return the name of the next scene
                
                # Special logic for menu selections
                if current_scene_name == "main_menu":
                    if next_scene_name == "Settings":
                        log_info("Loading settings screen...")
                        settings_screen = SettingsScreen()
                        settings_result = settings_screen.run()
                        log_info(f"Settings updated: {settings_result}")
                        next_scene_name = "main_menu"  # Return to main menu
                    elif next_scene_name == "New Game":
                        log_info("New Game selected - loading character creation...")
                        next_scene_name = "character_creation"  # Go to character creation
                    elif next_scene_name == "Continue":
                        log_info("Continue selected - placeholder for save loading")
                        next_scene_name = None  # For now, just exit
                    elif next_scene_name == "Exit":
                        next_scene_name = None
                
                current_scene_name = next_scene_name
            else:
                log_error(f"Unknown scene: {current_scene_name}")
                current_scene_name = None

        log_info("Game ended.")
        
    except KeyboardInterrupt:
        log_info("Game interrupted by user")
    except pygame.error as e:
        log_error(f"Pygame error: {e}")
        import traceback
        traceback.print_exc()
    except ImportError as e:
        log_error(f"Missing dependency: {e}")
        log_error("Please ensure all required packages are installed.")
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        safe_pygame_quit()
        sys.exit()

if __name__ == "__main__":
    main()
