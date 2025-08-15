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

## 🛠️ Key Commands

```bash
# Generate with notes
python3 tools/generate_veo3.py "Prompt" --scene name --notes "iteration notes"

# Generate with reference image  
python3 tools/generate_veo3.py "Prompt" --scene name --image path/to/ref.jpg

# List all scenes from story
python3 tools/web_workflow_helper.py scenes
```