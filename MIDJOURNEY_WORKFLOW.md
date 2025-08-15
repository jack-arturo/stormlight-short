# 🎨 Midjourney + Video Generation Workflow

## 🎯 Overview

This workflow integrates Midjourney styleframes with Veo 3 video generation to create cinematic, consistent videos with proper visual references.

## 📁 Directory Structure

```
01_styleframes_midjourney/
├── start_frames/          # Opening shots for each scene
│   ├── kaladin_intro/
│   ├── bridge_run/
│   └── highstorm/
├── end_frames/            # Closing shots for each scene  
│   ├── kaladin_intro/
│   ├── bridge_run/
│   └── highstorm/
├── reference/             # General reference images
│   ├── characters/
│   ├── environments/
│   └── props/
└── styleframes_metadata.json  # Organized metadata
```

## 🔄 Complete Workflow

### Step 1: Generate Midjourney Prompts

```bash
# Generate clean prompts optimized for --style raw
python3 tools/styleframe_manager.py prompts kaladin_intro "Kaladin standing on cliff edge storm approaching windswept cloak"
```

**Output:**
```
Start Frame:
Kaladin standing on cliff edge storm approaching windswept cloak stormy dramatic navy gray dramatic lighting Arcane style by Fortiche --style raw --ar 16:9 --q 2

End Frame:
Kaladin standing on cliff edge storm approaching windswept cloak stormy dramatic navy gray dramatic lighting Arcane style by Fortiche --style raw --ar 16:9 --q 2
```

### Step 2: Create Images in Midjourney
1. Copy the generated prompts to Midjourney
2. Generate multiple variations
3. Download your favorites (PNG format recommended)

### Step 3: Organize Styleframes
```bash
# Organize start frame
python3 tools/styleframe_manager.py organize \
  ~/Downloads/kaladin_cliff_start.png \
  kaladin_intro \
  start \
  --description "Kaladin on cliff edge, dramatic pose" \
  --prompt "Opening shot: Kaladin standing on cliff edge..."

# Organize end frame  
python3 tools/styleframe_manager.py organize \
  ~/Downloads/kaladin_cliff_end.png \
  kaladin_intro \
  end \
  --description "Kaladin after storm passes" \
  --prompt "Closing shot: Kaladin standing on cliff edge..."
```

### Step 4: Generate Video with Auto-Reference
```bash
# Video generation now automatically finds and uses your styleframes!
python3 tools/generate_veo3.py \
  "Kaladin stands defiantly on cliff edge as massive storm approaches, wind whipping his cloak, dramatic cinematic shot" \
  --scene kaladin_intro
```

**The tool will:**
- ✅ Auto-discover your organized start frame
- ✅ Use it as reference for video generation
- ✅ Generate consistent, high-quality video

## 🛠️ Styleframe Manager Commands

### Generate Midjourney Prompts
```bash
# Generate clean prompts (optimized for --style raw)
python3 tools/styleframe_manager.py prompts SCENE_NAME "description"

# Save to file for easy access
python3 tools/styleframe_manager.py prompts SCENE_NAME "description" --save
```

### Organize Images
```bash
# Basic organization
python3 tools/styleframe_manager.py organize IMAGE_PATH SCENE_NAME FRAME_TYPE

# With full metadata
python3 tools/styleframe_manager.py organize \
  image.png \
  scene_name \
  start \
  --description "Detailed description" \
  --prompt "Original Midjourney prompt"
```

### View Organized Styleframes
```bash
# List all scenes
python3 tools/styleframe_manager.py list

# View specific scene
python3 tools/styleframe_manager.py list --scene kaladin_intro
```

### Get Reference for Generation
```bash
# Find best reference image for a scene
python3 tools/styleframe_manager.py get-ref kaladin_intro

# Prefer end frames
python3 tools/styleframe_manager.py get-ref kaladin_intro --type end
```

## 🎬 Video Generation Options

### Automatic Reference (Recommended)
```bash
# Uses best available styleframe automatically
python3 tools/generate_veo3.py "Your prompt" --scene scene_name
```

### Manual Reference
```bash
# Specify exact image
python3 tools/generate_veo3.py "Your prompt" --scene scene_name --image path/to/image.png
```

### No Reference
```bash
# Disable auto-discovery
python3 tools/generate_veo3.py "Your prompt" --scene scene_name --no-auto-image
```

## 🎨 Scene-Specific Style Guidelines

### Kaladin Scenes
- **Style**: Windswept, stormy atmosphere, spear and bridge crew
- **Colors**: Dark blues, grays, storm colors
- **Mood**: Determined, defiant, heroic

### Bridge Run Scenes  
- **Style**: Chaotic action, desperate movement, arrows flying
- **Colors**: Earth tones, dust, danger
- **Mood**: Frantic, dangerous, teamwork

### Highstorm Scenes
- **Style**: Massive storm wall, electric blue lightning, overwhelming scale
- **Colors**: Electric blues, dark storm clouds, supernatural energy
- **Mood**: Awe-inspiring, terrifying, otherworldly

### Shattered Plains
- **Style**: Alien landscape, crystalline formations, desolate beauty
- **Colors**: Alien rock, crystal formations, harsh sunlight
- **Mood**: Desolate, alien, vast

## 📊 Best Practices

### Midjourney Settings

#### JSON Format (Recommended)
- **Style**: `--style raw` for maximum control
- **Quality**: `--q 2` for highest quality
- **Aspect Ratio**: `--ar 16:9` for video compatibility
- **Repeat**: `--repeat 1` for single generation
- **Negatives**: Comprehensive `--no` list to avoid unwanted elements

#### Advanced Features
- **Scene-Specific Styling**: Automatic mood, color, and element selection
- **Consistent Technical Settings**: Raw style, high quality, proper aspect ratio
- **Professional Negatives**: Excludes cartoon, anime, low-detail, AI artifacts
- **Arkane Studios Style**: Fantasy realism reference for consistency

### Image Organization
- **Naming**: Use descriptive scene names (`kaladin_intro`, not `scene1`)
- **Types**: Organize as `start`, `end`, or `reference` frames
- **Metadata**: Always add descriptions and original prompts

### Video Generation
- **Consistency**: Use styleframes to maintain visual consistency
- **Iteration**: Generate multiple takes with different styleframes
- **Quality**: Start frames usually work best as references

## 🔍 Troubleshooting

### No Reference Found
```bash
# Check what styleframes exist
python3 tools/styleframe_manager.py list --scene your_scene

# Organize some styleframes first
python3 tools/styleframe_manager.py organize image.png your_scene start
```

### Wrong Reference Used
```bash
# Specify exact image
python3 tools/generate_veo3.py "prompt" --scene scene --image specific/image.png

# Or disable auto-discovery
python3 tools/generate_veo3.py "prompt" --scene scene --no-auto-image
```

---

**🎬 This workflow ensures your videos have consistent, high-quality visual references while maintaining creative flexibility!**
