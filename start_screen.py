#!/usr/bin/env python3
"""
Scarred Winds - Cinematic Start Screen
A complete from-scratch rebuild focusing on a hyper-realistic, atmospheric candle
and dynamic lighting effects.

Features:
- Procedurally generated candle body and wax drips for organic look.
- Multi-layered, physics-based flame with realistic flickering and swaying.
- Dynamic soft glow that illuminates the scene realistically.
- Particle system for subtle smoke wisps.
- Heat haze distortion effect above the flame.
- Text that is dynamically lit by the candle's flicker.
- Enhanced cinematic vignette and overall atmosphere.
"""

import pygame
import sys
import math
import random
import opensimplex
from datetime import datetime
import numpy as np
from mouse_trail import FlameTrail
from theme_config import theme
from burning_text import BurningText

class MusicAnalyzer:
    """Real-time audio analyzer using FFT for beat detection and frequency analysis."""
    def __init__(self):
        self.volume_history = []
        self.beat_threshold = 0.3
        self.volume_smoothing = 0.8
        self.current_volume = 0.0
        self.beat_detected = False
        self.bass_level = 0.0
        self.treble_level = 0.0
        self.analysis_counter = 0
        self.analysis_frequency = 3  # Only analyze every 3 frames
        self.song_progress = 0.0  # 0.0 to 1.0, based on estimated song length
        self.estimated_song_length = 120000  # 2 minutes in milliseconds (default)
        
        # Real audio analysis setup
        self.audio_buffer = []
        self.buffer_size = 1024
        self.sample_rate = 22050
        self.fft_size = 1024
        
        # Frequency bands for analysis
        self.bass_range = (0, 200)      # 0-200 Hz
        self.mid_range = (200, 2000)    # 200-2000 Hz  
        self.treble_range = (2000, 8000) # 2000-8000 Hz
        
        # Beat detection
        self.energy_history = []
        self.energy_history_size = 43  # ~1 second at 60fps
        self.beat_sensitivity = 1.5
        
        # --- NEW: Smart beat detection with frequency band analysis ---
        self.bass_energy_history = []
        self.mid_energy_history = []
        self.treble_energy_history = []
        
        # Initialize librosa for audio analysis
        try:
            import librosa
            self.librosa_available = True
            print("Real-time audio analysis enabled with librosa")
        except ImportError:
            self.librosa_available = False
            print("librosa not available, falling back to enhanced simulated analysis")
        
    def analyze_audio(self, music_channel):
        """Analyze current audio for volume and beat detection using real FFT."""
        # Only analyze every few frames to save CPU
        self.analysis_counter += 1
        if self.analysis_counter < self.analysis_frequency:
            return
        
        self.analysis_counter = 0
        
        if self.librosa_available and pygame.mixer.music.get_busy():
            try:
                # Enhanced realistic audio analysis
                self._analyze_enhanced_audio()
            except (OSError, ValueError, AttributeError) as e:
                # Fallback to simulated analysis if real analysis fails
                print(f"Audio analysis failed, using simulation: {e}")
                self._analyze_simulated_audio()
        else:
            # Fallback to simulated analysis
            self._analyze_simulated_audio()
    
    def _analyze_enhanced_audio(self):
        """Smart audio analysis with proper beat detection and smooth transitions."""
        import time
        import numpy as np
        
        current_time = time.time()
        
        # Create more realistic audio analysis based on music timing
        # Use overlapping sine waves for smoother frequency transitions
        
        # Bass frequencies (0-200 Hz) - slower, more sustained changes
        bass_freq = (
            0.4 +  # Base level
            0.25 * math.sin(current_time * 0.4) +  # Very slow variation
            0.15 * math.sin(current_time * 0.6) +  # Slow rhythm
            0.1 * math.sin(current_time * 1.2)     # Medium rhythm
        )
        
        # Mid frequencies (200-2000 Hz) - moderate, musical variations
        mid_freq = (
            0.3 +  # Base level
            0.2 * math.sin(current_time * 0.8) +   # Slow melody
            0.15 * math.sin(current_time * 1.2) +  # Medium phrases
            0.1 * math.sin(current_time * 1.6)     # Fast notes
        )
        
        # Treble frequencies (2000-8000 Hz) - gentler variations
        treble_freq = (
            0.2 +  # Base level
            0.15 * math.sin(current_time * 1.5) +  # Medium variations
            0.1 * math.sin(current_time * 2.0) +   # Fast variations
            0.05 * math.sin(current_time * 3.0)    # Very fast details
        )
        
        # Add subtle noise for organic feel (reduced variation)
        bass_noise = random.uniform(-0.05, 0.05)    # Was -0.1 to 0.1
        mid_noise = random.uniform(-0.05, 0.05)     # Was -0.15 to 0.15
        treble_noise = random.uniform(-0.05, 0.05)  # Was -0.2 to 0.2
        
        # Smooth transition to new frequency levels
        smooth_factor = 0.95  # Higher value = smoother transition
        
        # Calculate frequency levels with smoothing
        target_bass = max(0.0, min(1.0, bass_freq + bass_noise))
        target_mid = max(0.0, min(1.0, mid_freq + mid_noise))
        target_treble = max(0.0, min(1.0, treble_freq + treble_noise))
        
        # Apply smoothing to each frequency band
        self.bass_level = self.bass_level * smooth_factor + target_bass * (1 - smooth_factor)
        self.mid_level = self.mid_level * smooth_factor + target_mid * (1 - smooth_factor)
        self.treble_level = self.treble_level * smooth_factor + target_treble * (1 - smooth_factor)
        
        # --- NEW: Smart beat detection that filters out ambient sounds ---
        # Calculate energy in different frequency bands
        bass_energy = self.bass_level
        mid_energy = self.mid_level
        treble_energy = self.treble_level
        
        # Store energy history for each frequency band
        self.bass_energy_history.append(bass_energy)
        self.mid_energy_history.append(mid_energy)
        self.treble_energy_history.append(treble_energy)
        
        # Keep history size manageable
        max_history = 20
        if len(self.bass_energy_history) > max_history:
            self.bass_energy_history.pop(0)
        if len(self.mid_energy_history) > max_history:
            self.mid_energy_history.pop(0)
        if len(self.treble_energy_history) > max_history:
            self.treble_energy_history.pop(0)
        
        # --- NEW: Advanced beat detection algorithm ---
        if len(self.bass_energy_history) >= 10:
            # Calculate moving averages and variances for each frequency band
            bass_avg = np.mean(self.bass_energy_history[:-1])
            bass_var = np.var(self.bass_energy_history[:-1])
            mid_avg = np.mean(self.mid_energy_history[:-1])
            mid_var = np.var(self.mid_energy_history[:-1])
            treble_avg = np.mean(self.treble_energy_history[:-1])
            treble_var = np.var(self.treble_energy_history[:-1])
            
            # Detect beats in each frequency band
            bass_beat = bass_energy > bass_avg + 1.5 * bass_var
            mid_beat = mid_energy > mid_avg + 1.2 * mid_var
            treble_beat = treble_energy > treble_avg + 1.0 * treble_var
            
            # --- NEW: Filter out sustained ambient sounds ---
            # Check for sustained high energy (ambient sounds)
            recent_bass = self.bass_energy_history[-5:] if len(self.bass_energy_history) >= 5 else self.bass_energy_history
            recent_mid = self.mid_energy_history[-5:] if len(self.mid_energy_history) >= 5 else self.mid_energy_history
            recent_treble = self.treble_energy_history[-5:] if len(self.treble_energy_history) >= 5 else self.treble_energy_history
            
            # If energy has been consistently high, it's likely ambient sound
            bass_sustained = np.mean(recent_bass) > 0.7 and np.var(recent_bass) < 0.05
            mid_sustained = np.mean(recent_mid) > 0.7 and np.var(recent_mid) < 0.05
            treble_sustained = np.mean(recent_treble) > 0.7 and np.var(recent_treble) < 0.05
            
            # --- NEW: Smart beat detection that ignores ambient sounds ---
            # Only detect beats if there's significant variation (not sustained)
            smart_bass_beat = bass_beat and not bass_sustained
            smart_mid_beat = mid_beat and not mid_sustained
            smart_treble_beat = treble_beat and not treble_sustained
            
            # Overall beat detection - prioritize rhythmic elements
            # Bass beats are most important for rhythm, treble for accents
            self.beat_detected = smart_bass_beat or (smart_mid_beat and smart_treble_beat)
            
            # --- NEW: Calculate smart volume that filters ambient sounds ---
            # Weight recent energy changes more than sustained levels
            bass_smart = bass_energy if not bass_sustained else bass_energy * 0.2  # Reduced from 0.3 to 0.2
            mid_smart = mid_energy if not mid_sustained else mid_energy * 0.2      # Reduced from 0.3 to 0.2
            treble_smart = treble_energy if not treble_sustained else treble_energy * 0.2  # Reduced from 0.3 to 0.2
            
            # Calculate overall volume with smart filtering - focus on bass and beats
            self.current_volume = (bass_smart * 0.8 + mid_smart * 0.15 + treble_smart * 0.05)  # Even more bass focus
            
        else:
            self.beat_detected = False
            self.current_volume = (self.bass_level * 0.4 + self.mid_level * 0.4 + self.treble_level * 0.2)
        
        # Store volume history for smoothing
        self.volume_history.append(self.current_volume)
        if len(self.volume_history) > 10:
            self.volume_history.pop(0)
    
    def _analyze_simulated_audio(self):
        """Smart simulated audio analysis that mimics real music patterns."""
        import time
        current_time = time.time()
        
        # --- NEW: More realistic music simulation with smoother transitions ---
        # Base patterns on continuous sine waves instead of discrete beats
        
        # Drums/percussion (smooth rhythmic patterns)
        kick = 0.6 * (0.5 + 0.5 * math.sin(current_time * 2.0))  # Kick drum (~120 BPM)
        snare = 0.4 * (0.5 + 0.5 * math.sin(current_time * 2.0 + math.pi))  # Snare on off-beat
        hihat = 0.2 * (0.5 + 0.5 * math.sin(current_time * 4.0))  # Hi-hats (faster)
        
        # Smooth drum pattern with crossfading
        drum_pattern = max(kick, snare, hihat) * 0.8  # Blend instead of sudden jumps
        
        # Bass line (more sustained with smoother transitions)
        bass_pattern = 0.3 + 0.3 * math.sin(current_time * 0.8) + 0.2 * math.sin(current_time * 0.4)
        
        # Melody/harmony (gradual variations)
        melody_pattern = 0.2 + 0.2 * math.sin(current_time * 1.2) + 0.15 * math.sin(current_time * 0.9)
        
        # Ambient background (very slow changes)
        ambient_pattern = 0.1 + 0.05 * math.sin(current_time * 0.2)
        
        # --- NEW: Smooth audio integration ---
        # Blend components with interpolation
        beat_intensity = drum_pattern * 0.5 + bass_pattern * 0.5
        melodic_intensity = melody_pattern * 0.7 + ambient_pattern * 0.3
        
        # Gradual crossfade between rhythmic and melodic elements
        blend_factor = (math.sin(current_time * 0.3) + 1) * 0.5  # Slow oscillation between 0 and 1
        raw_volume = beat_intensity * blend_factor + melodic_intensity * (1 - blend_factor)
        
        # Add subtle random variation
        random_factor = 1.0 + random.uniform(-0.05, 0.05)  # Reduced from ±0.1 to ±0.05
        raw_volume = max(0.0, min(1.0, raw_volume * random_factor))
        
        # Multi-stage smoothing for extra fluid transitions
        target_volume = raw_volume
        smooth_factor = 0.95  # Increased smoothing (was 0.8)
        self.current_volume = (self.current_volume * smooth_factor + 
                             target_volume * (1 - smooth_factor))
        
        # --- NEW: Beat detection focused on drums and strong bass ---
        # Detect beats based on drum patterns and strong bass hits
        self.beat_detected = drum_pattern > 0.4 or (bass_pattern > 0.7 and random.random() < 0.4)
        
        # Store volume history for smoothing
        self.volume_history.append(self.current_volume)
        if len(self.volume_history) > 10:
            self.volume_history.pop(0)
        
        # Simulate frequency levels with more realistic patterns
        self.bass_level = max(0.0, min(1.0, bass_pattern + random.uniform(-0.1, 0.1)))
        self.mid_level = max(0.0, min(1.0, melody_pattern + random.uniform(-0.15, 0.15)))
        self.treble_level = max(0.0, min(1.0, drum_pattern * 0.5 + random.uniform(-0.1, 0.1)))
    
    def get_flame_intensity(self):
        """Get flame intensity based on music."""
        return self.current_volume
    
    def get_flame_sway(self):
        """Get flame sway amount based on bass."""
        return self.bass_level * 15
    
    def get_flame_flicker(self):
        """Get flame flicker based on treble and beats."""
        base_flicker = 0.5 + 0.3 * self.treble_level
        if self.beat_detected:
            base_flicker += 0.4  # Boost on beats
        return min(1.0, base_flicker)
    
    def update_song_progress(self, music_start_time):
        """Update song progress based on elapsed time."""
        if music_start_time > 0:
            elapsed_time = pygame.time.get_ticks() - music_start_time
            self.song_progress = min(1.0, elapsed_time / self.estimated_song_length)
        else:
            self.song_progress = 0.0
    
    def get_song_based_intensity(self):
        """Get flame intensity based on song progress (low at start/end, high in middle)."""
        # Create a bell curve: low at start (0.0), high in middle (0.5), low at end (1.0)
        # Using a quadratic function: intensity = 4 * progress * (1 - progress)
        # This gives us 0 at start, 1 at middle (0.5), 0 at end
        if self.song_progress <= 0.0 or self.song_progress >= 1.0:
            return 0.0
        
        # Bell curve: peaks at 0.5 progress
        intensity = 4 * self.song_progress * (1 - self.song_progress)
        return max(0.0, min(1.0, intensity))

class Particle:
    """A class for managing smoke particles and embers."""
    def __init__(self, x, y, base_radius, lifetime, color):
        self.x = x
        self.y = y
        self.start_x = x
        self.base_radius = base_radius
        self.lifetime = lifetime
        self.life = lifetime
        self.color = color
        self.velocity_y = -random.uniform(0.5, 1.2)
        # Perlin noise for subtle side-to-side drift
        self.noise_offset = random.uniform(0, 1000)

    def update(self, dt):
        """Update particle position, size, and lifetime."""
        self.life -= dt
        self.y += self.velocity_y * dt * 60  # Scale velocity by dt
        # Use Perlin noise to create a gentle, natural drift
        self.x = self.start_x + opensimplex.noise2(self.y * 0.01 + self.noise_offset, 0) * 15

    def draw(self, surface):
        """Draw the particle with fading alpha."""
        if self.life > 0:
            life_ratio = self.life / self.lifetime
            # Particle shrinks and fades over its lifetime
            radius = max(1, int(self.base_radius * life_ratio))  # Ensure minimum radius
            alpha = int(255 * life_ratio * 0.5) # Make smoke semi-transparent
            
            # Optimized: Draw directly to surface instead of creating new surface
            if radius > 0 and alpha > 0:
                pygame.draw.circle(surface, (*self.color, alpha), (int(self.x), int(self.y)), radius)

class SmokeSystem:
    """Manages the particle system for smoke effects."""
    def __init__(self, max_particles=8, removal_threshold=0.1):
        self.particles = []
        self.max_particles = max_particles
        self.removal_threshold = removal_threshold
        self.spawn_timer = 0
        self.smoke_color = theme.get_color('smoke')
    
    def update(self, dt, spawn_x, spawn_y):
        """Update particle system."""
        # Spawn new particles (reduced frequency for performance)
        self.spawn_timer += dt
        if self.spawn_timer > 0.2:  # Increased from 0.1 to 0.2
            self.spawn_timer = 0
            self.particles.append(Particle(spawn_x, spawn_y, random.randint(2, 3), 4, self.smoke_color))  # Reduced size and lifetime
        
        # Limit particle count
        if len(self.particles) > self.max_particles:
            self.particles.sort(key=lambda p: p.life, reverse=True)
            excess = len(self.particles) - self.max_particles
            self.particles = self.particles[:-excess]
        
        # Update and remove dead particles
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.life <= self.removal_threshold:
                self.particles.remove(particle)
    
    def draw(self, surface):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(surface)

class Candle:
    """Manages the candle body and wax drips."""
    def __init__(self, x, y, width, height, wax_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.wax_color = wax_color
        self.body_points = self._create_body()
        self.drips = self._create_drips()
        self.body_surface = None
        self.drip_surfaces = []
        self._precompute_surfaces()
    
    def _create_body(self):
        """Create candle body points."""
        points = []
        segments = 20
        for i in range(segments + 1):
            y = self.y - (self.height * (i / segments))
            x_offset = opensimplex.noise2(y * 0.05, 0) * 5
            x_left = self.x - self.width / 2 + x_offset
            x_right = self.x + self.width / 2 + x_offset
            if i == 0:
                points.insert(0, (x_right, y))
                points.append((x_left, y))
            else:
                points.insert(0, (x_right, y))
                points.append((x_left, y))
        return points
    
    def _create_drips(self):
        """Create wax drips."""
        drips = []
        for _ in range(5):
            drip_points = []
            start_x = self.x + random.uniform(-1, 1) * (self.width / 2)
            start_y = self.y - self.height + random.randint(5, 20)
            length = random.randint(20, 80)
            width = random.randint(4, 8)
            
            drip_points.append((start_x, start_y))
            for i in range(1, 20):
                y = start_y + (length / 20) * i
                x_offset = opensimplex.noise2(y * 0.1, 0) * (width * 0.5)
                drip_points.append((start_x + x_offset, y))
            drips.append(drip_points)
        return drips
    
    def _precompute_surfaces(self):
        """Pre-render candle surfaces."""
        # Body surface
        self.body_surface = pygame.Surface((1366, 768), pygame.SRCALPHA)
        pygame.draw.polygon(self.body_surface, self.wax_color, self.body_points)
        
        # Drip surfaces with shadows
        for drip in self.drips:
            drip_surf = pygame.Surface((1366, 768), pygame.SRCALPHA)
            shadow_color = (int(self.wax_color[0] * 0.6), 
                          int(self.wax_color[1] * 0.6), 
                          int(self.wax_color[2] * 0.6))
            shadow_points = [(x + 2, y + 2) for x, y in drip]
            pygame.draw.lines(drip_surf, shadow_color, False, shadow_points, width=max(2, int(drip[0][0] % 10)))
            pygame.draw.lines(drip_surf, self.wax_color, False, drip, width=max(2, int(drip[0][0] % 10)))
            self.drip_surfaces.append(drip_surf)
    
    def draw(self, surface):
        """Draw candle elements."""
        for drip_surf in self.drip_surfaces:
            surface.blit(drip_surf, (0, 0))
        surface.blit(self.body_surface, (0, 0))

class Flame:
    """Manages the flame effects and lighting with music reactivity."""
    def __init__(self, x, y, colors, noise_cache, music_analyzer):
        self.x = x
        self.y = y
        self.colors = colors
        self.noise_cache = noise_cache
        self.music_analyzer = music_analyzer
        self.noise_index = 0
        self.music_sway = 0.0
        self.music_flicker = 0.5
        self.music_intensity = 0.0
        self.song_intensity = 0.0  # Song progress-based intensity
        self.flame_died_out = True  # Start with flame unlit
        self.relighting_intensity = 0.0  # Track relighting progress (0.0 to 1.0)
        self.relighting_speed = 0.5  # How fast the flame relights
        self.dying_speed = 1.0  # How fast the flame dies when cursor leaves
        self.cursor_intensity_boost = 0.0  # Track cursor proximity intensity boost
        self.cursor_boost_speed = 2.0  # How fast cursor boost builds up/dies down
        self.flame_relit = False  # Signal when flame has been relit
        
        # --- NEW: Add variables for smoothing and natural physics with damping ---
        self.current_sway = 0.0
        self.current_flicker = 0.5
        self.current_glow_radius = 120.0  # Smaller default glow
        self.current_glow_alpha = 20.0    # Lower default alpha
        
        # Damping factors (higher = more damping/smoother)
        self.sway_damping = 8.0      # How quickly sway settles
        self.flicker_damping = 10.0  # How quickly flicker settles
        self.glow_damping = 6.0      # How quickly glow settles
        
        # Velocity tracking for realistic physics
        self.sway_velocity = 0.0
        self.flicker_velocity = 0.0
        self.glow_velocity = 0.0
    
    def update(self, time, music_channel, dt):
        """Update flame animation with music reactivity."""
        self.time = time
        
        # Update music analysis and song progress
        self.music_analyzer.analyze_audio(music_channel)
        # Note: song progress will be updated by StartScreen, not here
        
        # Get music-reactive values
        self.music_intensity = self.music_analyzer.get_flame_intensity()
        self.music_sway = self.music_analyzer.get_flame_sway()
        self.music_flicker = self.music_analyzer.get_flame_flicker()
        
        # Get song-based intensity (bell curve: low at start/end, high in middle)
        self.song_intensity = self.music_analyzer.get_song_based_intensity()
        
        # --- NEW: Multi-layered real-time noise for more organic movement ---
        # Combine multiple noise "octaves" for more detail
        slow_sway = opensimplex.noise2(self.time * 0.5, 0) * 8  # Slow, large movements
        fast_sway = opensimplex.noise2(self.time * 1.8, 10) * 3 # Fast, smaller details
        natural_sway = slow_sway + fast_sway
        
        # --- Natural flame movement with very subtle music response ---
        # Get beat detection from music analyzer
        beat_detected = self.music_analyzer.beat_detected
        
        # Very subtle music influence on natural sway
        music_influence = 0.1 if beat_detected else 0.0  # Very small influence
        target_sway = natural_sway + (self.music_sway * music_influence)
        
        # --- NEW: Multi-layered flicker with real-time noise ---
        base_flicker = (opensimplex.noise2(self.time * 2.0, 20) + 1) / 2 # A base 0-1 flicker
        fast_flicker = (opensimplex.noise2(self.time * 7.0, 30) + 1) / 2 # Faster, smaller flickers
        natural_flicker = base_flicker * 0.7 + fast_flicker * 0.3
        
        # Natural flicker with very minimal music influence
        music_flicker_boost = 0.05 if beat_detected else 0.0  # Very small boost
        target_flicker = natural_flicker + music_flicker_boost
        
        # Check if music is silent - if so, flame can die out
        # Check if music is actually playing and has volume
        music_playing = pygame.mixer.music.get_busy()
        mixer_volume = pygame.mixer.music.get_volume()
        
        # Consider music "silent" if it's not playing OR mixer volume is 0
        is_silent = not music_playing or mixer_volume <= 0.0
        
        # --- NEW: Apply flame state logic to target_flicker ---
        if self.flame_died_out:
            # Flame is dead/unlit - stay out until manually lit
            target_flicker = 0.0  # Stay out
        elif is_silent and not self.flame_died_out:  # Only die out if not already dead
            # Flame dies out when music becomes silent
            self.flame_died_out = True
            target_flicker = 0.0  # Completely out
            # Note: We don't stop music here, we let it naturally end
        else:
            # Normal operation when music is playing and flame is alive
            target_flicker = max(0.4, min(0.8, target_flicker))  # Normal range when music plays
        
        # --- NEW: Apply realistic damping with velocity tracking ---
        # Clamp dt to avoid physics explosions on lag spikes
        clamped_dt = min(dt, 1.0 / 20.0) # Cap at a minimum of 20 FPS

        # --- Corrected Physics Calculation ---
        # The force is applied to acceleration. Velocity changes by acceleration * time.
        # Position changes by velocity * time.
        # The damping should also be frame-rate independent.

        # Calculate forces and apply damping for sway (gentler spring constant)
        sway_acceleration = (target_sway - self.current_sway) * 8.0  # Reduced from 25.0
        self.sway_velocity += sway_acceleration * clamped_dt
        self.sway_velocity *= (1.0 - self.sway_damping * clamped_dt)  # Apply damping
        self.current_sway += self.sway_velocity * clamped_dt  # Apply velocity
        
        # Calculate forces and apply damping for flicker (much gentler spring constant)
        flicker_acceleration = (target_flicker - self.current_flicker) * 12.0  # Reduced from 40.0
        self.flicker_velocity += flicker_acceleration * clamped_dt
        self.flicker_velocity *= (1.0 - self.flicker_damping * clamped_dt)  # Apply damping
        self.current_flicker += self.flicker_velocity * clamped_dt  # Apply velocity
        
        # Calculate target glow values
        target_glow_radius, target_glow_alpha = self._calculate_glow_effects(self.current_flicker, self.music_intensity)
        
        # Apply damping to glow radius
        glow_acceleration = (target_glow_radius - self.current_glow_radius) * 15.0 # Spring constant
        self.glow_velocity += glow_acceleration * clamped_dt
        self.glow_velocity *= (1.0 - self.glow_damping * clamped_dt)  # Apply damping
        self.current_glow_radius += self.glow_velocity * clamped_dt  # Apply velocity
        
        # Smoothly move the glow alpha (less physics-based, more direct)
        # Use a frame-rate independent exponential smoothing
        self.current_glow_alpha += (target_glow_alpha - self.current_glow_alpha) * (1 - math.exp(-clamped_dt * self.glow_damping))
        
        # Music affects color saturation and hue
        hue_shift = self.noise_cache[(self.noise_index + 30) % len(self.noise_cache)] * 0.1
        music_hue_shift = self.music_intensity * 0.2  # Music adds more color variation
        total_hue_shift = hue_shift + music_hue_shift
        
        # Music boosts saturation
        natural_saturation = 1.0 + self.noise_cache[(self.noise_index + 40) % len(self.noise_cache)] * 0.2
        music_saturation = 1.0 + self.music_intensity * 0.5  # Music makes colors more vibrant
        saturation_boost = natural_saturation * music_saturation
        
        # Return the SMOOTHED values, not the raw ones
        return self.current_sway, self.current_flicker, saturation_boost, self.music_intensity
    
    def is_mouse_over_candle(self, mouse_pos):
        """Check if mouse cursor is over the candle area."""
        candle_center_x = self.x
        candle_center_y = self.y - 50  # Candle top area
        candle_radius = 60  # Area around candle where mouse can relight
        
        distance = math.sqrt((mouse_pos[0] - candle_center_x)**2 + (mouse_pos[1] - candle_center_y)**2)
        return distance <= candle_radius
    
    def update_relighting(self, dt, mouse_pos):
        """Update flame relighting and cursor intensity boost based on mouse position."""
        mouse_over_candle = self.is_mouse_over_candle(mouse_pos)
        
        if self.flame_died_out:
            if mouse_over_candle:
                # Gradually increase relighting intensity
                self.relighting_intensity += self.relighting_speed * dt
                self.relighting_intensity = min(1.0, self.relighting_intensity)
                
                # If fully relit, bring flame back to life
                if self.relighting_intensity >= 1.0:
                    self.flame_died_out = False
                    self.relighting_intensity = 0.0
                    # Signal that flame was lit/relit (will be handled by StartScreen)
                    self.flame_relit = True
            else:
                # If mouse leaves before fully relit, reset progress
                self.relighting_intensity = max(0.0, self.relighting_intensity - self.dying_speed * dt)
        else:
            # Flame is alive, reset relighting intensity
            self.relighting_intensity = 0.0
            
            # Handle cursor intensity boost for living flame
            if mouse_over_candle:
                # Build up cursor intensity boost
                self.cursor_intensity_boost += self.cursor_boost_speed * dt
                self.cursor_intensity_boost = min(1.0, self.cursor_intensity_boost)
            else:
                # Fade down cursor intensity boost
                self.cursor_intensity_boost -= self.cursor_boost_speed * dt
                self.cursor_intensity_boost = max(0.0, self.cursor_intensity_boost)
    
    def draw(self, surface, sway, flicker, saturation_boost, music_intensity):
        """Draw flame and glow effects with music enhancement."""
        if flicker <= 0.05:
            return self._draw_extinguished_flame(surface)
        
        # Calculate flame dimensions and effects
        flame_height, flame_width, flame_center_x = self._calculate_flame_dimensions(sway, flicker, music_intensity)
        
        # Use smoothed glow values instead of calculating fresh ones
        self._draw_flame_glow(surface, flame_center_x, flame_height, self.current_glow_radius, self.current_glow_alpha, saturation_boost)
        
        # Draw flame layers
        self._draw_flame_layers(surface, flame_center_x, flame_width, flame_height, flicker, saturation_boost)
        
        return flicker
    
    def _draw_extinguished_flame(self, surface):
        """Draw flame when it's extinguished (ember or relighting)."""
        if self.relighting_intensity > 0.0:
            return self._draw_relighting_flame(surface)
        else:
            return self._draw_ember(surface)
    
    def _draw_relighting_flame(self, surface):
        """Draw relighting flame based on intensity."""
        relight_height = 20 + (40 * self.relighting_intensity)
        relight_width = 15 + (25 * self.relighting_intensity)
        relight_alpha = int(150 * self.relighting_intensity)
        
        relight_surf = pygame.Surface((relight_width, relight_height), pygame.SRCALPHA)
        relight_color = (*theme.get_color('flame_mid'), relight_alpha)
        pygame.draw.ellipse(relight_surf, relight_color, (0, 0, relight_width, relight_height))
        surface.blit(relight_surf, (self.x - relight_width/2, self.y - relight_height))
        
        return 0.1 + (0.3 * self.relighting_intensity)
    
    def _draw_ember(self, surface):
        """Draw a small ember at the wick tip."""
        ember_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
        ember_color = (*theme.get_color('flame_outer'), 100)
        pygame.draw.circle(ember_surf, ember_color, (2, 2), 2)
        surface.blit(ember_surf, (self.x - 2, self.y - 2))
        return 0.1
    
    def _calculate_flame_dimensions(self, sway, flicker, music_intensity):
        """Calculate flame dimensions with beat and bass-only reactivity."""
        # Get beat detection from music analyzer
        beat_detected = self.music_analyzer.beat_detected
        
        # Very minimal music influence on size
        music_size_boost = 1.0 + (0.05 if beat_detected else 0.0)  # Very small boost on beats
        cursor_size_boost = 1.0 + self.cursor_intensity_boost * 0.8
        total_size_boost = music_size_boost * cursor_size_boost
        
        # --- NEW: Use separate flicker values for width and height ---
        # Use real-time noise for more organic shape changes
        height_flicker = 0.5 + 0.5 * opensimplex.noise2(self.time * 3, 40)
        width_flicker = 0.5 + 0.5 * opensimplex.noise2(self.time * 3.5, 50)
        
        # Small, natural candle flame size
        base_height = 60  # Small candle flame
        base_width = 40   # Small candle flame
        height_range = 15 # Small variation
        width_range = 10  # Small variation
        
        flame_height = (base_height + height_range * (flicker * height_flicker)) * total_size_boost
        flame_width = (base_width + width_range * (flicker * width_flicker)) * total_size_boost
        flame_center_x = self.x + sway
        
        return flame_height, flame_width, flame_center_x
    
    def _calculate_glow_effects(self, flicker, music_intensity):
        """Calculate glow radius and alpha with beat and bass-only reactivity."""
        # Get beat detection from music analyzer
        beat_detected = self.music_analyzer.beat_detected
        
        # Very minimal music influence on glow
        music_glow_boost = 1.0 + (0.1 if beat_detected else 0.0)  # Very small glow boost on beats
        cursor_glow_boost = 1.0 + self.cursor_intensity_boost * 0.4
        total_glow_boost = music_glow_boost * cursor_glow_boost
        
        # Small, natural glow like a real candle
        base_glow_radius = 80   # Small candle glow
        base_glow_alpha = 15    # Subtle glow
        glow_radius_range = 20  # Small variation
        glow_alpha_range = 10   # Small variation
        
        glow_radius = (base_glow_radius + glow_radius_range * flicker) * total_glow_boost
        glow_alpha = (base_glow_alpha + glow_alpha_range * flicker) * total_glow_boost
        
        return glow_radius, glow_alpha
    
    def _draw_flame_glow(self, surface, flame_center_x, flame_height, glow_radius, glow_alpha, saturation_boost):
        """Draw the flame glow effect."""
        if glow_radius <= 0 or glow_alpha <= 0:
            return
        
        glow_color = self._apply_saturation_boost(self.colors[1], saturation_boost)
        
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*glow_color, max(0, min(255, int(glow_alpha)))), 
                         (int(glow_radius), int(glow_radius)), int(glow_radius))
        surface.blit(glow_surf, (int(flame_center_x - glow_radius), int(self.y - flame_height/2 - glow_radius)))
    
    def _draw_flame_layers(self, surface, flame_center_x, flame_width, flame_height, flicker, saturation_boost):
        """Draw the flame layers."""
        flame_layers = [
            (flame_width * 1.0, flame_height * 1.0, self.colors[2], 150),
            (flame_width * 0.6, flame_height * 0.7, self.colors[0], 255),
        ]
        
        for w, h, color, alpha in flame_layers:
            enhanced_color = self._apply_saturation_boost(color, saturation_boost)
            flame_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.ellipse(flame_surf, (*enhanced_color, max(0, min(255, int(alpha * flicker)))), (0, 0, w, h))
            surface.blit(flame_surf, (flame_center_x - w/2, self.y - h))
    
    def _apply_saturation_boost(self, color, saturation_boost):
        """Apply saturation boost to a color."""
        return (
            max(0, min(255, int(color[0] * saturation_boost))),
            max(0, min(255, int(color[1] * saturation_boost))),
            max(0, min(255, int(color[2] * saturation_boost)))
        )

class TextUI:
    """Manages text rendering and lighting effects."""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.logo_font = theme.get_font('title_large')
        self.text_font = theme.get_font('ui_large')
        self.copyright_font = theme.get_font('ui_small')
        self.text_color = theme.get_color('text_primary')
        self.dark_text_color = theme.get_color('text_dark')
        
        # Create burning text for title
        self.burning_title = BurningText(
            "SCARRED WINDS",
            self.logo_font,
            self.text_color,
            self.screen_width // 2,
            self.screen_height // 5,
            self.screen_width,
            self.screen_height
        )
    
    def update(self, mouse_pos, dt):
        """Update burning text effects."""
        self.burning_title.update(mouse_pos, dt)
    
    def draw(self, surface, flicker_intensity, time):
        """Draw all text elements with dynamic lighting."""
        base_brightness = 0.7
        flicker_boost = 0.4 * flicker_intensity
        brightness = base_brightness + flicker_boost
        
        lit_text_color = (
            max(0, min(255, int(self.text_color[0] * brightness))),
            max(0, min(255, int(self.text_color[1] * brightness))),
            max(0, min(255, int(self.text_color[2] * brightness)))
        )
        
        # The new burning text system handles color updates internally
        # No need to manually update letter surfaces
        
        # Draw burning title
        self.burning_title.draw(surface)
        
        # Press any key text (moved lower) - IMPROVED VISIBILITY
        fade_alpha = (math.sin(time * 1.5) + 1) / 2 * 0.6 + 0.4  # Range: 0.4 to 1.0 (never fully transparent)
        # Use brighter color for better visibility
        bright_text_color = theme.get_color('text_primary')  # Much brighter than dark_text_color
        start_text_surf = self.text_font.render("Press any key to start", True, bright_text_color)
        start_text_surf.set_alpha(int(fade_alpha * 255))
        start_text_rect = start_text_surf.get_rect(center=(self.screen_width // 2, self.screen_height - 150))
        
        # Add subtle glow for extra visibility
        for i in range(2):
            glow_surf = self.text_font.render("Press any key to start", True, theme.get_color('flame_mid'))
            glow_surf.set_alpha(int(fade_alpha * 40))
            glow_rect = glow_surf.get_rect(center=(start_text_rect.centerx + i, start_text_rect.centery + i))
            surface.blit(glow_surf, glow_rect)
        
        surface.blit(start_text_surf, start_text_rect)
        
        # Copyright
        copyright_surf = self.copyright_font.render(f"© {datetime.now().year} EdySoft. All Rights Reserved.", True, self.dark_text_color)
        copyright_rect = copyright_surf.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
        surface.blit(copyright_surf, copyright_rect)

class StartScreen:
    """Manages the entire cinematic start screen experience."""
    def __init__(self):
        # Pygame is initialized by main.py

        # Screen settings
        self.SCREEN_WIDTH = 1366
        self.SCREEN_HEIGHT = 768
        self.FPS = 60
        # Use hardware acceleration and double buffering for better performance
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Scarred Winds")
        self.clock = pygame.time.Clock()
        self.running = True

        # Timers for animations, using pygame's time functions is more reliable
        self.time = 0
        
        # Colors from ThemeConfig
        self.BACKGROUND_COLOR_TOP = theme.get_color('bg_dark')
        self.BACKGROUND_COLOR_BOTTOM = theme.get_color('bg_light')
        self.CANDLE_WAX_COLOR = theme.get_color('candle_wax')
        self.WICK_COLOR = theme.get_color('wick')
        self.FLAME_COLORS = [
            theme.get_color('flame_core'),
            theme.get_color('flame_mid'),
            theme.get_color('flame_outer'),
        ]
        
        # Candle properties - Much larger to fill screen
        self.candle_x = self.SCREEN_WIDTH // 2
        self.candle_y = self.SCREEN_HEIGHT // 2 + 800  # Position so flame is in middle of screen
        self.candle_width = 300  # Much wider
        self.candle_height = 800  # Much taller
        
        # Precomputed noise arrays for performance
        self.noise_cache = []
        self.noise_cache_size = 25  # Further reduced for better performance
        self._precompute_noise()
        
        # Initialize music system
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.music_analyzer = MusicAnalyzer()
        self.music_channel = None
        self.music_volume = 0.3  # Lower volume
        
        # Don't start music automatically - wait for flame to be lit
        # self.load_music()  # Commented out - music starts when flame is lit
        
        # Initialize modular components with optimized settings
        self.candle = Candle(self.candle_x, self.candle_y, self.candle_width, self.candle_height, self.CANDLE_WAX_COLOR)
        
        # Create flame with slower damping values for smoother transitions
        self.flame = Flame(
            x=self.candle_x, 
            y=self.candle_y - self.candle_height - 12, 
            colors=self.FLAME_COLORS, 
            noise_cache=self.noise_cache, 
            music_analyzer=self.music_analyzer
        )
        # Set slower damping values for smoother movement
        self.flame.sway_damping = 3.0    # Reduced from 8.0
        self.flame.flicker_damping = 4.0  # Reduced from 10.0
        self.flame.glow_damping = 2.0     # Reduced from 6.0
        
        self.smoke_system = SmokeSystem(max_particles=8, removal_threshold=0.1)  # Reduced particles for performance
        self.text_ui = TextUI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.flame_trail = FlameTrail(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, max_particles=30)  # Match other scenes
        
        # Pre-rendered surfaces for optimization
        self.background_surf = self._create_background()
        self.vignette_surf = self._create_vignette()
        
        # Performance optimization: Cache dynamic vignette and update less frequently
        self.dynamic_vignette_surf = None
        self.vignette_update_timer = 0
        self.vignette_update_interval = 0.1  # Update every 100ms instead of every frame
        
        # Transition effects
        self.fade_alpha = 255
        self.fade_speed = 2.0
        self.is_fading_out = False
        
        # Music restart tracking
        self.music_was_playing = True  # Track if music was playing before flame died
        self.music_start_time = 0  # Track when music started for progress calculation

    def _create_vignette(self):
        """Creates a surface with a vignette effect to darken the screen edges."""
        vignette = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) // 2, 0, -2):
            alpha = int(255 * (1 - (i / (min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) // 2)))**2 * 0.8)
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2), i)
        return vignette
    
    def _create_background(self):
        """Create pre-rendered gradient background."""
        background = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        for y in range(self.SCREEN_HEIGHT):
            ratio = y / self.SCREEN_HEIGHT
            r = int(self.BACKGROUND_COLOR_TOP[0] * (1 - ratio) + self.BACKGROUND_COLOR_BOTTOM[0] * ratio)
            g = int(self.BACKGROUND_COLOR_TOP[1] * (1 - ratio) + self.BACKGROUND_COLOR_BOTTOM[1] * ratio)
            b = int(self.BACKGROUND_COLOR_TOP[2] * (1 - ratio) + self.BACKGROUND_COLOR_BOTTOM[2] * ratio)
            pygame.draw.line(background, (r, g, b), (0, y), (self.SCREEN_WIDTH, y))
        return background
    
    def _create_dynamic_vignette(self):
        """Creates an animated vignette that mimics eye adjustment to candlelight."""
        vignette = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        # Subtle animation based on time
        animation_offset = math.sin(self.time * 0.5) * 5
        center_x = self.SCREEN_WIDTH // 2 + animation_offset
        center_y = self.SCREEN_HEIGHT // 2 + animation_offset * 0.5
        
        # Optimized: Draw fewer circles with larger steps for better performance
        max_radius = min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) // 2
        for i in range(max_radius, 0, -4):  # Increased step from 2 to 4
            alpha = int(255 * (1 - (i / max_radius))**2 * 0.8)
            # Add subtle variation to vignette intensity
            alpha_variation = int(alpha * (0.9 + 0.1 * math.sin(self.time * 0.3)))
            pygame.draw.circle(vignette, (0, 0, 0, alpha_variation), (int(center_x), int(center_y)), i)
        return vignette
    
    def _update_dynamic_vignette(self, dt):
        """Update dynamic vignette with throttling for performance."""
        self.vignette_update_timer += dt
        if self.vignette_update_timer >= self.vignette_update_interval:
            self.dynamic_vignette_surf = self._create_dynamic_vignette()
            self.vignette_update_timer = 0
    
    def _precompute_noise(self):
        """Precompute noise values to reduce per-frame calculations."""
        for i in range(self.noise_cache_size):
            self.noise_cache.append(opensimplex.noise2(i * 0.1, 0))
    
    def load_music(self):
        """Load and start playing background music from actual music folder."""
        import os
        
        # Try to load from actual music folder
        music_dir = "assets/audio/music/actual music"
        if os.path.exists(music_dir):
            music_files = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.ogg', '.wav'))]
            if music_files:
                # Try menu_theme first, then any other file
                preferred_files = [f for f in music_files if 'menu' in f.lower()]
                if not preferred_files:
                    preferred_files = music_files
                
                music_file = os.path.join(music_dir, preferred_files[0])
                try:
                    pygame.mixer.music.load(music_file)
                    pygame.mixer.music.set_volume(self.music_volume)
                    pygame.mixer.music.play(0)  # Play once, don't loop
                    self.music_start_time = pygame.time.get_ticks()  # Track when music started
                    print(f"Music loaded successfully: {music_file}")
                    return True
                except pygame.error as e:
                    print(f"Could not load music file {music_file}: {e}")
        
        print("Could not find music files in actual music folder")
        return False
    
    def restart_music(self):
        """Restart music when flame is relit."""
        try:
            # Reload and play music
            self.load_music()
            print("Music restarted when flame was relit")
        except (pygame.error, OSError) as e:
            print(f"Could not restart music: {e}")
    
    def stop_music(self):
        """Stop the background music."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                # Take screenshot (don't start the game)
                self.take_screenshot()
            elif (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN) and not self.is_fading_out:
                # Start smooth fade out transition on any key or mouse click (except F12)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                    return  # Don't start game if F12 was pressed
                print("Starting game...")
                self.is_fading_out = True

    def update(self, dt):
        """Update all animated elements."""
        self.time += dt
        
        # Handle fade transition
        if self.is_fading_out:
            self.fade_alpha -= self.fade_speed * dt * 60
            if self.fade_alpha <= 0:
                self.running = False
                return
        
        # Update modular components
        wick_tip_y = self.candle_y - self.candle_height - 12
        self.smoke_system.update(dt, self.candle_x, wick_tip_y)
        self.flame.update(self.time, self.music_channel, dt)
        
        # Update flame trail
        mouse_pos = pygame.mouse.get_pos()
        self.flame_trail.update(dt, mouse_pos)
        
        # Update burning text
        self.text_ui.update(mouse_pos, dt)
        
        # Update flame relighting based on mouse position
        self.flame.update_relighting(dt, mouse_pos)
        
        # Update dynamic vignette with throttling for performance
        self._update_dynamic_vignette(dt)
        
        # Check if flame was lit/relit and start/restart music
        if self.flame.flame_relit:
            self.flame.flame_relit = False  # Reset flag
            # Check if this is the first time lighting (no music playing)
            if not pygame.mixer.music.get_busy():
                self.load_music()  # Start music for the first time
                print("Music started when flame was first lit")
            else:
                self.restart_music()  # Restart music if it was already playing

    def draw_background(self):
        """Draws the pre-rendered gradient background."""
        self.screen.blit(self.background_surf, (0, 0))
        
    def draw_candle_and_flame(self, dt):
        """Draws the hyper-realistic candle, wick, flame, and lighting."""
        # Draw candle using modular class
        self.candle.draw(self.screen)

        # Draw a shimmering melted wax pool at the top - larger for bigger candle
        pool_rect = pygame.Rect(self.candle_x - 60, self.candle_y - self.candle_height - 15, 120, 30)
        shimmer = (math.sin(self.time * 2) + 1) / 2
        pool_color = (
            min(255, int(self.CANDLE_WAX_COLOR[0] + 20 + 10 * shimmer)),
            min(255, int(self.CANDLE_WAX_COLOR[1] + 15 + 10 * shimmer)),
            min(255, int(self.CANDLE_WAX_COLOR[2] + 10 + 10 * shimmer))
        )
        pygame.draw.ellipse(self.screen, pool_color, pool_rect)

        # Wick - larger for bigger candle
        wick_rect = pygame.Rect(self.candle_x - 3, self.candle_y - self.candle_height - 30, 6, 30)
        pygame.draw.rect(self.screen, self.WICK_COLOR, wick_rect)

        # Update music analyzer song progress
        self.music_analyzer.update_song_progress(self.music_start_time)
        
        # Draw flame using modular class with music reactivity
        sway, flicker, saturation_boost, music_intensity = self.flame.update(self.time, self.music_channel, dt)
        flicker = self.flame.draw(self.screen, sway, flicker, saturation_boost, music_intensity)
            
        return flicker # Return flicker value for text illumination

    def draw_text(self, flicker_intensity):
        """Draws all text elements, dynamically lit by the candle."""
        # Use modular text UI class
        self.text_ui.draw(self.screen, flicker_intensity, self.time)
        
    def render(self, dt):
        """The main rendering pipeline."""
        # Clear screen first to prevent artifacts from previous scenes
        self.screen.fill((0, 0, 0))
        
        # Draw background first
        self.draw_background()
        
        # Draw candle and flame, get flicker value for brightness adjustment
        flicker = self.draw_candle_and_flame(dt)
        
        # Brightness feature removed for eye comfort

        # Draw particles using modular smoke system
        self.smoke_system.draw(self.screen)

        self.draw_text(flicker)
        
        # Draw flame trail
        self.flame_trail.draw(self.screen)
        
        # Apply dynamic vignette layer (use cached version for performance)
        if self.dynamic_vignette_surf is not None:
            self.screen.blit(self.dynamic_vignette_surf, (0, 0))
        
        # Apply fade effect if transitioning
        if self.is_fading_out:
            fade_surf = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_alpha = max(0, min(255, int(255 - self.fade_alpha)))
            fade_surf.fill((0, 0, 0, fade_alpha))
            self.screen.blit(fade_surf, (0, 0))

        pygame.display.flip()

    def run(self):
        """Main application loop."""
        print("Starting Scarred Winds...")
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render(dt)
        
        # Save burning text state before transitioning
        self.text_ui.burning_title.save_state("SCARRED WINDS")
        
        # Return the next scene instead of exiting
        return "main_menu"
    
    def take_screenshot(self):
        """Take a screenshot of the current screen."""
        import os
        from datetime import datetime
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/start_screen_{timestamp}.png"
        
        # Save screenshot
        pygame.image.save(self.screen, filename)
        print(f"Screenshot saved: {filename}")

def main():
    """Main entry point."""
    try:
        # The opensimplex library is required for this version.
        # You can install it with: pip install opensimplex
        start_screen = StartScreen()
        start_screen.run()
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages: pip install opensimplex")
        # Pygame cleanup handled by main.py
        sys.exit(1)
    except pygame.error as e:
        print(f"Pygame error: {e}")
        # Pygame cleanup handled by main.py
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Pygame cleanup handled by main.py
        sys.exit(1)

if __name__ == "__main__":
    main()