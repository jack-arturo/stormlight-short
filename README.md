# 🌪️ Stormlight Archives: Into the Tempest
> AI-Powered Animated Series Pipeline

## 🎯 Quick Start

```bash
# Set API key (one-time setup)
export GEMINI_API_KEY='your-key-here'  # Get from https://aistudio.google.com/app/apikey

# Generate video
python3 tools/generate_veo3.py "Your prompt" --scene scene_name

# Check status
python3 tools/web_workflow_helper.py status
```

## 📋 Current Status

- **Working**: Veo 3 video generation via Gemini API 
- **Output**: 720p, 8-second clips (~60 second generation)
- **Storage**: Videos → `04_flow_exports/`, metadata → `02_prompts/ledger.jsonl`
- **Progress**: 4 clips generated (26.7% of pilot trailer)

## 🎬 For Animated Style (Not CGI)

Add to prompts: "2D animated style, anime-inspired, hand-drawn aesthetic, Studio Ghibli quality"

## 📁 Project Structure

```
stormlight_short/
├── 04_flow_exports/        # Generated videos
├── 02_prompts/ledger.jsonl # Generation metadata
├── 07_story_development/   # Story docs & scene breakdowns
├── tools/
│   ├── generate_veo3.py   # Main generation script
│   └── web_workflow_helper.py # Status tracking
└── GEMINI_API_SETUP.md    # API setup guide
```

## 🛠️ Video Generation Commands

### Basic Usage
```bash
python3 tools/generate_veo3.py "PROMPT" --scene SCENE_NAME
```

### Full Command Options
```bash
python3 tools/generate_veo3.py "Your video description" \
  --scene scene_name \
  --take 2 \
  --image path/to/reference.jpg \
  --notes "Production notes"
```

### Quick Examples
```bash
# Simple generation
python3 tools/generate_veo3.py "Kaladin standing on cliff edge, storm approaching" --scene kaladin_intro

# With reference image
python3 tools/generate_veo3.py "Bridge crew running across chasm" --scene bridge_run --image 01_styleframes_midjourney/bridge-scene.png

# Specific take with notes
python3 tools/generate_veo3.py "Highstorm wall approaching" --scene highstorm --take 3 --notes "Darker, more ominous version"
```

### Other Useful Commands
```bash
# Get detailed help with examples
python3 tools/generate_veo3.py --help

# Check pipeline status
python3 tools/pipeline_monitor.py

# View generation history
python3 tools/web_workflow_helper.py status
```

## 📚 Documentation

- **[COMMANDS.md](COMMANDS.md)** - Complete command reference with examples
- **[MIDJOURNEY_WORKFLOW.md](MIDJOURNEY_WORKFLOW.md)** - Styleframe integration workflow
- **[GEMINI_API_SETUP.md](GEMINI_API_SETUP.md)** - API setup and configuration
- **[SECURITY.md](SECURITY.md)** - API key security best practices

## 🎨 Styleframe Integration

The pipeline now automatically uses Midjourney styleframes as reference images:

```bash
# 1. Generate clean Midjourney prompts
python3 tools/styleframe_manager.py prompts kaladin_intro "Kaladin on cliff edge storm approaching"

# 2. Create images in Midjourney, then organize them
python3 tools/styleframe_manager.py organize image.png kaladin_intro start

# 3. Generate video (automatically uses your styleframe!)
python3 tools/generate_veo3.py "Video prompt" --scene kaladin_intro
```