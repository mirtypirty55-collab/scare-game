#!/usr/bin/env python3
"""
Scarred Winds - Burning Text State Manager
Saves and restores the state of burning text between scenes.
"""

import pickle
import os
from logger import log_info, log_warning

class BurningStateManager:
    """Manages persistent state for burning text effects."""
    
    def __init__(self):
        self.states = {}
        self.save_dir = "temp"
        
        # Create temp directory if it doesn't exist
        if not os.path.exists(self.save_dir):
            try:
                os.makedirs(self.save_dir)
            except OSError:
                log_warning("Could not create temp directory for burning text states")
    
    def save_state(self, identifier, burning_text_obj):
        """Save the state of a burning text object."""
        try:
            state_data = {
                'text': burning_text_obj.text,
                'letters_state': []
            }
            
            # Save state of each letter
            for letter in burning_text_obj.letters:
                if letter is None:
                    state_data['letters_state'].append(None)
                else:
                    letter_state = {
                        'char': letter.char,
                        'pos': letter.pos,
                        'fuel_map': letter.fuel_map.tolist() if hasattr(letter.fuel_map, 'tolist') else None,
                        'heat_map': letter.heat_map.tolist() if hasattr(letter.heat_map, 'tolist') else None,
                    }
                    state_data['letters_state'].append(letter_state)
            
            self.states[identifier] = state_data
            log_info(f"Saved burning text state: {identifier}")
            
        except Exception as e:
            log_warning(f"Failed to save burning text state: {e}")
    
    def restore_state(self, identifier, burning_text_obj):
        """Restore the state to a burning text object."""
        if identifier not in self.states:
            log_info(f"No saved state found for: {identifier}")
            return False
        
        try:
            state_data = self.states[identifier]
            
            # Restore letter states
            for i, letter_state in enumerate(state_data['letters_state']):
                if letter_state is None or burning_text_obj.letters[i] is None:
                    continue
                
                letter = burning_text_obj.letters[i]
                
                # Restore fuel and heat maps if available
                if letter_state['fuel_map'] is not None:
                    import numpy as np
                    letter.fuel_map = np.array(letter_state['fuel_map'])
                if letter_state['heat_map'] is not None:
                    import numpy as np
                    letter.heat_map = np.array(letter_state['heat_map'])
            
            log_info(f"Restored burning text state: {identifier}")
            return True
            
        except Exception as e:
            log_warning(f"Failed to restore burning text state: {e}")
            return False
    
    def clear_state(self, identifier):
        """Clear a saved state."""
        if identifier in self.states:
            del self.states[identifier]
            log_info(f"Cleared burning text state: {identifier}")
    
    def clear_all_states(self):
        """Clear all saved states."""
        self.states.clear()
        log_info("Cleared all burning text states")

# Global instance
burning_state_manager = BurningStateManager()
