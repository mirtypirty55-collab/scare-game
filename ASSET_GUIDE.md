# Asset Integration & Bedroom Scene - Quick Start Guide

## 🎮 What I Just Built For You

### 1. **Asset Loader System** (`asset_loader.py`)
- Centralized asset loading with caching
- Automatic scaling support
- Handles missing assets gracefully with magenta placeholders
- Memory efficient with caching

### 2. **Bedroom Scene** (`bedroom_scene.py`)
- First actual gameplay scene!
- Implements Story Part 1 from your story.txt
- Top-down exploration with camera following
- Interactive objects (bed, calendar, photo frame, chest, bookshelf)
- Dialogue system with text wrapping
- Uses your actual asset images

### 3. **Burning Text State Manager** (`burning_text_state.py`)
- Fixes the missing import crash
- Saves/restores letter burn states between scenes

## 🚀 How To Test It

### Option 1: Direct Test (Fastest)
```bash
python bedroom_scene.py
```

### Option 2: Through Main Menu
1. Run the game: `python main.py`
2. In main.py, temporarily modify line 49 to start at bedroom:
   ```python
   current_scene_name = "bedroom"  # Change from "start_screen"
   ```

## 🎨 Your Assets In Action

The bedroom scene uses these assets:
- **damaged_wood_tile.png** - Floor tiles (tiled across room)
- **damaged_bed.png** - Player's bed (bottom left)
- **calendar.png** - The Exile Day calendar (top center, KEY STORY ITEM)
- **damaged_bookshelf.png** - Bookshelf (right wall)
- **wood_chest.png** - Storage chest (bottom right)
- **rug_tile.png** - Decorative rug (currently just floor, but loaded)

**Note**: Photo frame uses a placeholder since you don't have that asset yet.

## 🎯 Controls

- **WASD / Arrow Keys** - Move around
- **E or Space** - Interact with highlighted objects
- **Enter** - Go to next scene (only works after checking the calendar)
- **ESC** - Exit
- **F12** - Screenshot

## 📝 What Happens In The Scene

1. Player wakes up in their bedroom
2. Can explore and interact with:
   - **Bed** - Reflects on sleeping there
   - **Calendar** - Discovers tomorrow is Exile Day (KEY MOMENT)
   - **Photo Frame** - Empty frame, no family memories
   - **Chest** - Few belongings, nothing of value
   - **Bookshelf** - Survival books
3. After checking the calendar, can press Enter to move to next scene
4. Establishes the orphan backstory and the impending threat

## 🔧 Adjusting Asset Scales

If assets look too big/small, edit `bedroom_scene.py` lines 46-47:
```python
self.tile_scale = 2.0  # Change this for floor tiles
self.furniture_scale = 1.5  # Change this for furniture
```

Recommended scales for your assets:
- **Too small?** Increase values (2.5, 3.0, etc.)
- **Too large?** Decrease values (1.0, 0.8, etc.)
- **Pixel perfect?** Use 1.0 for no scaling

## 🐛 Common Issues & Fixes

### Assets showing as magenta squares?
- Check file paths in `assets/images/` folder
- Verify filenames match exactly (case-sensitive on Linux)
- Check console logs for "Failed to load" messages

### Player moves too fast/slow?
- Edit line 36 in bedroom_scene.py: `self.player_speed = 200`

### Camera feels wrong?
- The camera automatically follows the player
- Room is larger than screen (1600x1200) for exploration feel

### Dialogue disappears too fast?
- Edit line 58: `self.dialogue_duration = 3.0` (increase for longer display)

## 📦 Asset Naming Reference

Your assets vs. code names:
```
Images you shared:
1. Wooden planks → damaged_wood_tile.png
2. Calendar → calendar.png
3. Campfire → campfire.png
4. Cave entrance → cave_entrance.png
5. Bed → damaged_bed.png
6. Bookshelf → damaged_bookshelf.png
7. Floor tiles → damaged_wood_tile.png (variants: 2, 3)
8. House → exterior_house.png
9. Dead man → dead_old_man.png (Dorian!)
10. Dirt → (needs naming)
11. Chest → wood_chest.png
12. Rug/frame → rug_tile.png
```

## 🎯 Next Steps - Building The Game

### Immediate (Week 1):
1. **Test the bedroom scene** - Make sure assets load correctly
2. **Adjust scales** - Get everything looking right
3. **Add player sprite** - Replace placeholder with your walk animations
4. **Create village exterior** - Use exterior_house.png and grass tiles
5. **Add more interactables** - Door to leave room, etc.

### Priority (Week 2):
6. **Implement Story Part 2-3** - Exile day cutscene with Elders
7. **Add the village scene** - 5 houses, villagers, assembly area
8. **Create the ravine** - Scavenging mini-game for berries
9. **Build the cave entrance** - Use your awesome cave_entrance.png!

### Core Gameplay (Week 3-4):
10. **Cave exploration** - Dark, dangerous, finding Dorian
11. **Pokemon emergence** - The pokeball scene
12. **Basic follower system** - Pokemon follows player
13. **Start veteran system** - Pokemon stats and tracking

## 💡 Tips For Using Your Assets

### Tiling Strategy:
```python
# For repeating tiles (floors, walls, dirt):
for y in range(0, height, tile_height):
    for x in range(0, width, tile_width):
        surface.blit(tile, (x, y))
```

### Layering Order (draw in this order):
1. Floor tiles (bottom layer)
2. Rugs/decorations
3. Furniture that player walks behind
4. Player
5. Furniture that overlaps player (top layer)
6. UI elements

### Collision Detection:
```python
# Simple rect collision for furniture:
furniture_rect = pygame.Rect(x, y, width, height)
if player_rect.colliderect(furniture_rect):
    # Block movement or trigger interaction
```

## 🎨 Scene Template For Future Scenes

Want to create more scenes? Use this template:

```python
class YourNewScene:
    def __init__(self):
        # Setup screen, camera, player
        self._load_assets()
        self._setup_scene()
        
    def _load_assets(self):
        # Load your images with asset_loader
        self.sprite = get_scaled_asset("filename.png", scale)
    
    def handle_events(self):
        # Handle keyboard/mouse input
        
    def update(self, dt):
        # Update game logic (movement, physics, etc.)
        
    def draw(self):
        # Render everything to screen
        
    def run(self):
        # Main game loop
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        return "next_scene_name"
```

## 🔥 Advanced: Using Your Walk Animations

Your sprites folder has walk animations in 4 directions!
To use them:

```python
# In bedroom_scene.py, replace player drawing with:
class Player:
    def __init__(self):
        self.direction = 'south'  # north, south, east, west
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 0.1
        
        # Load animation frames
        self.anims = {
            'south': [get_scaled_asset(f"sprites/animations/walk/south/frame_{i:03d}.png", 2.0) 
                     for i in range(6)],
            # ... load north, east, west similarly
        }
    
    def update(self, dt, moving):
        if moving:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % len(self.anims[self.direction])
    
    def draw(self, surface, x, y):
        frame = self.anims[self.direction][self.anim_frame]
        surface.blit(frame, (x, y))
```

## 🎮 Config File (Recommended)

Create `config.py` for easy tweaking:

```python
# Game configuration
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
FPS = 60

# Player settings
PLAYER_SPEED = 200
PLAYER_SIZE = 48

# Asset scales
TILE_SCALE = 2.0
FURNITURE_SCALE = 1.5
SPRITE_SCALE = 2.0

# Gameplay
INTERACTION_DISTANCE = 60
DIALOGUE_DURATION = 3.0
```

## 📊 Performance Notes

Your assets are high quality but large. If you experience lag:

1. **Pre-scale assets** - Scale once at load time, not every frame
2. **Use convert_alpha()** - Faster blitting (already done in asset_loader)
3. **Limit particles** - Reduce flame trail particles if needed
4. **Cull off-screen** - Don't draw objects outside camera view
5. **Use dirty rect drawing** - Only redraw changed areas

## 🎯 What's Missing For Full Story Part 1

To complete the bedroom scene according to your story:

- [ ] More ambient details (mentioned in story)
- [ ] Calendar interaction shows "day 26 marked with X"
- [ ] Ability to leave room (door interaction)
- [ ] Transition to village/ravine
- [ ] Time of day system (story mentions it's early morning)

## 🚀 Testing Checklist

Before moving forward, verify:
- [ ] All assets load without errors
- [ ] Player can move smoothly
- [ ] Camera follows player correctly
- [ ] Can interact with all objects
- [ ] Dialogue appears and is readable
- [ ] Can transition to next scene
- [ ] No crashes or lag spikes

## 💬 Need Help?

Common questions:

**Q: Assets aren't loading?**
A: Check the console for "Failed to load" messages and verify file paths.

**Q: How do I add more furniture?**
A: Add to `_create_interactables()` method with a new InteractableObject.

**Q: How do I change dialogue?**
A: Edit the strings in `_interact_bed()`, `_interact_calendar()`, etc.

**Q: How do I make the room bigger/smaller?**
A: Change `self.room_width` and `self.room_height` in line 26-27.

## 🎉 You're Ready!

You now have:
✅ A working gameplay scene
✅ Asset integration system
✅ Interactive objects
✅ Dialogue system
✅ Camera system
✅ Story progression

**Next**: Run `python bedroom_scene.py` and see your game come to life!
