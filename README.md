# 🌪️ Stormlight Archives: Into the Tempest
> **Complete AI-Powered Animation Pipeline**: Midjourney → Veo 3 → Final Cut

## 🚀 Quick Start

```bash
# 1. Generate Midjourney styleframes
python3 tools/styleframe_manager.py prompts kaladin_intro "Kaladin on cliff edge storm approaching"

# 2. Create images in Midjourney, organize them
python3 tools/styleframe_manager.py organize downloaded_image.png kaladin_intro start

# 3. Generate video (automatically uses your styleframe!)
python3 tools/generate_veo3.py "Kaladin stands defiantly as storm approaches" --scene kaladin_intro
```

## ✅ **Production Ready**

- **🎨 Midjourney Integration**: Automated prompt generation with Arcane-style references
- **🎬 Veo 3 Generation**: 720p, 8-second clips via Gemini API (~2-5 min generation)
- **📁 Auto-Organization**: Styleframes → Videos → Metadata tracking
- **🔒 Secure Setup**: Environment-based API key management
- **📊 Pipeline Monitoring**: Real-time status tracking and cost monitoring

## 🎭 **Arcane Animation Style**

All prompts are optimized for **Arcane animation style by Fortiche** with:
- Painterly realism and dramatic lighting
- Scene-specific color palettes (storm grays, electric blues, earth tones)
- Cinematic composition and professional quality
- `--style raw --ar 16:9 --q 2` for maximum control

## 📁 **Project Structure**

```
stormlight_short/
├── 01_styleframes_midjourney/    # Organized Midjourney styleframes
│   ├── start_frames/             # Opening shots by scene
│   ├── end_frames/               # Closing shots by scene
│   └── reference/                # General reference images
├── 02_prompts/
│   ├── ledger.jsonl             # Video generation metadata
│   └── midjourney/              # Generated Midjourney prompts
├── 04_flow_exports/             # Generated videos (MP4)
├── 07_story_development/        # Story docs & scene breakdowns
└── tools/
    ├── generate_veo3.py         # Video generation (Veo 3)
    ├── styleframe_manager.py    # Midjourney workflow
    └── pipeline_monitor.py      # Status & cost tracking
```

## 🎨 **Complete Workflow**

### 1. Generate Midjourney Prompts
```bash
# Scene-specific prompts with Arcane styling
python3 tools/styleframe_manager.py prompts kaladin_intro "Kaladin on cliff edge storm approaching"
python3 tools/styleframe_manager.py prompts bridge_run "Bridge crew charging under arrow fire"
python3 tools/styleframe_manager.py prompts highstorm "Massive storm wall approaching"
```

### 2. Organize Styleframes
```bash
# After creating images in Midjourney
python3 tools/styleframe_manager.py organize image.png kaladin_intro start
python3 tools/styleframe_manager.py organize image.png kaladin_intro end
```

### 3. Generate Videos
```bash
# Automatically uses organized styleframes as reference
python3 tools/generate_veo3.py "Kaladin stands defiantly as storm approaches" --scene kaladin_intro
python3 tools/generate_veo3.py "Bridge crew charges across chasm" --scene bridge_run
```

### 4. Monitor Pipeline
```bash
# Real-time dashboard
python3 tools/pipeline_monitor.py --dashboard

# Quick status check
python3 tools/pipeline_monitor.py

# Health check
python3 tools/pipeline_monitor.py --health-check
```

## 🎯 **Key Features**

- **🤖 Automated Prompts**: Scene-specific Midjourney prompts with Arcane styling
- **📸 Smart References**: Auto-discovery of styleframes for video generation
- **💰 Cost Tracking**: Real-time monitoring of generation costs
- **🔄 Take Management**: Automatic versioning and iteration tracking
- **📊 Pipeline Health**: Comprehensive monitoring and status reporting
- **🔒 Secure Setup**: Environment-based API key management

## 📚 **Documentation**

- **[MIDJOURNEY_WORKFLOW.md](MIDJOURNEY_WORKFLOW.md)** - Complete styleframe workflow
- **[COMMANDS.md](COMMANDS.md)** - Command reference with examples
- **[SECURITY.md](SECURITY.md)** - API key security setup

## 🛠️ **Setup**

1. **Get API Key**: https://aistudio.google.com/app/apikey
2. **Set Environment**: `export GEMINI_API_KEY='your-key-here'`
3. **Install Dependencies**: `pip install -r requirements.txt`
4. **Test Setup**: `python3 tools/pipeline_monitor.py --health-check`

## 🎬 **Scene Types**

- **kaladin_intro**: Heroic defiance, storm grays, windswept atmosphere
- **bridge_run**: Desperate action, earth tones, chaotic movement
- **highstorm**: Overwhelming power, electric blues, massive scale
- **shattered_plains**: Alien desolation, crystal formations
- **spren**: Mystical wonder, ethereal glows, otherworldly magic

---

**Ready to create epic Stormlight videos with professional Arcane-style animation!** ⚡🌪️