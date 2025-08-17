# 🌪️ Stormlight Archives: Into the Tempest
> **Complete AI-Powered Animation Pipeline**: Midjourney → Veo 3 → Final Cut

## 🚀 Quick Start

```bash
# 🌪️ Launch the beautiful Control Center (Recommended!)
python3 tools/stormlight_control.py

# Or use individual tools:
# Interactive workflow with AI enhancement
python3 tools/styleframe_manager.py interactive title_sequence "Sweeping aerial shot across alien Roshar landscape"

# Generate video with AI-enhanced cinematic prompts
python3 tools/generate_veo3.py "Sweeping aerial shot" --scene title_sequence --llm-prompt --mood heroic
```

### 🎯 **Enhanced Interactive Workflow (v2.0)**
1. **Launch Interactive Mode** - `python3 tools/generate_veo3.py` (no args = interactive)
2. **Smart Scene Detection** - Auto-detects pending clips from story development
3. **Styleframe Validation** - Shows start/end frame status before generation:
   ```
   ✅ Styleframes available:
      🎬 Start frame: ✓  📸 path/to/start_frame.jpg
      🎯 End frame: ✓   📸 path/to/end_frame.jpg
      💡 Veo3 will generate 8-second transition between these frames
   ```
4. **AI Prompt Enhancement** - Optional GPT-4-mini enhancement with cost transparency
5. **Model & Cost Selection** - Choose between Veo 3 Fast ($3.20) or Standard ($6.00) with audio options
6. **Dual Frame Generation** - Uses Veo 3's `image` + `lastFrame` API for perfect transitions

## ✅ **Production Ready**

- **🤖 AI-Powered Prompt Generation**: GPT-4-mini integration for cinematic prompts and variations
- **🎨 Interactive Styleframe Workflow**: Step-by-step Midjourney integration with AI enhancement
- **🖼️ Auto-Image Optimization**: PNG→JPG conversion, compression, resizing (9MB→1MB)
- **🎬 Veo 3 Generation**: 720p, 8-second clips via Gemini API with AI prompt enhancement
- **🎵 Complete Audio Pipeline**: Aiva + Stable Audio + Manual Foley integration
- **📁 Smart Organization**: Automatic file management with enhanced prompt saving to markdown
- **🚫 Text-Free Prompts**: Clean generation avoiding Midjourney text artifacts
- **🔒 Secure Setup**: Environment-based API key management for both OpenAI and Gemini
- **📊 Pipeline Monitoring**: Real-time status tracking, cost monitoring, and AI status display

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
├── 05_audio/                    # Complete audio pipeline
│   ├── base_scores/             # Aiva API musical compositions
│   ├── ambient_layers/          # Stable Audio atmospheric sounds
│   ├── foley/                   # Manual sound effects
│   └── final_mixes/             # Combined audio tracks
├── 06_final_cut/                # Final edited sequences
├── 07_story_development/        # Story docs & scene breakdowns
└── tools/
    ├── generate_veo3.py         # 🎬 Video generation (Veo 3 via Gemini API)
    ├── styleframe_manager.py    # 🎨 Midjourney workflow & prompt generation
    ├── pipeline_monitor.py      # 📊 Real-time monitoring & cost tracking
    ├── audio_composer.py        # 🎵 Aiva API integration
    ├── stormlight_control.py    # 🌪️ Beautiful Control Center Dashboard
    └── ambient_generator.py     # 🔊 Stable Audio integration
```

## 🌪️ **Control Center Dashboard**

Launch the gorgeous full-screen control center with ASCII branding:

```bash
python3 tools/stormlight_control.py
```

**Features:**
- 🎨 **Beautiful ASCII Logo** - Full Stormlight branding
- 📊 **Real-time Status** - All tools and metrics at a glance  
- 🎮 **Visual Navigation** - Hotkeys to launch any tool
- 📱 **Responsive Design** - Adapts to any terminal size
- ⚡ **Quick Launch** - S/V/M/D/H/R hotkeys for instant access

## 🎨 **Complete Workflow**

### 1. Generate Midjourney Prompts (Now with AI Enhancement!)
```bash
# AI-enhanced prompts with variations (Recommended!)
python3 tools/styleframe_manager.py prompts kaladin_intro "Kaladin on cliff edge storm approaching" --llm-enhance --variations 3

# Traditional prompts (without AI)
python3 tools/styleframe_manager.py prompts bridge_run "Bridge crew charging under arrow fire"

# Interactive workflow with AI option
python3 tools/styleframe_manager.py interactive
```

### 2. Organize Styleframes
```bash
# After creating images in Midjourney
python3 tools/styleframe_manager.py organize image.png kaladin_intro start
python3 tools/styleframe_manager.py organize image.png kaladin_intro end
```

### 3. Generate Videos (Enhanced Interactive Mode!)
```bash
# 🌟 NEW: Interactive mode with full styleframe validation (RECOMMENDED)
python3 tools/generate_veo3.py
# → Shows pending clips from story development
# → Validates start/end frame availability  
# → AI enhancement with cost transparency
# → Model selection (Fast/Standard + Audio options)

# Manual generation with AI enhancement
python3 tools/generate_veo3.py "Kaladin stands defiantly" --scene kaladin_intro --llm-prompt --camera "slow push-in" --mood "heroic"

# Cost-controlled generation
python3 tools/generate_veo3.py "Bridge crew charges" --scene bridge_run --fast --with-audio  # $3.20
python3 tools/generate_veo3.py "Epic battle scene" --scene combat --standard --no-audio      # $4.00
```

### 4. Generate Audio Components
```bash
# Base musical score
python3 tools/audio_composer.py --scene kaladin_intro --length 8s --style "80bpm orchestral minor key crescendo"

# Atmospheric layers
python3 tools/ambient_generator.py --type highstorm --duration 8s --intensity crescendo
python3 tools/ambient_generator.py --type spren --duration 8s --style mystical_chimes

# Combine all layers
python3 tools/audio_composer.py --mix kaladin_intro
```

### 5. Monitor Pipeline
```bash
# Real-time dashboard
python3 tools/pipeline_monitor.py --dashboard

# Quick status check
python3 tools/pipeline_monitor.py

# Health check
python3 tools/pipeline_monitor.py --health-check
```

## 🎯 **Key Features**

### **AI-Powered Features (NEW!)**
- **🤖 GPT-4-mini Integration**: Intelligent prompt generation at ~$0.01-0.02 per generation
- **🎨 Cinematic Prompt Enhancement**: Professional film language with camera movements
- **🎬 Multiple Variations**: Generate 3-5 variations per scene for creative options
- **📝 Automatic Documentation**: AI prompts saved to markdown with metadata
- **💾 Smart Caching**: Reduce costs with intelligent response caching
- **🎯 Context-Aware**: Stormlight and Arcane style specialization

### **Core Pipeline Features**
- **🎭 Dual Frame System**: Uses Veo 3's `image` + `lastFrame` API for precise start→end transitions
- **✅ Styleframe Validation**: Pre-generation checks with clear status display
- **📸 Smart References**: Auto-discovery and validation of scene styleframes
- **💰 Cost Tracking**: Real-time monitoring with transparent pricing ($3.20 Fast, $6.00 Standard)
- **🔄 Take Management**: Automatic versioning and iteration tracking
- **📊 Pipeline Health**: Comprehensive monitoring and status reporting
- **🔒 Secure Setup**: Environment-based API key management (OpenAI + Gemini)

## 📚 **Documentation**

- **[MIDJOURNEY_WORKFLOW.md](MIDJOURNEY_WORKFLOW.md)** - Complete styleframe workflow
- **[COMMANDS.md](COMMANDS.md)** - Command reference with examples
- **[SECURITY.md](SECURITY.md)** - API key security setup

## 🛠️ **Setup & Requirements**

### 📋 **Required Tools**
- **Python 3.8+** - Core runtime environment
- **Midjourney** - Styleframe generation (Discord subscription required)
- **Google AI Studio** - Veo 3 video generation via Gemini API
- **Terminal/Command Line** - Pipeline execution
- **Image Editor** (optional) - Fine-tuning styleframes

### 🚀 **Installation Steps**

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd stormlight_short
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get API Keys**
   - **Gemini API** (Required for video generation):
     - Visit: https://aistudio.google.com/app/apikey
     - Create new API key
   - **OpenAI API** (Optional for AI enhancement):
     - Visit: https://platform.openai.com/api-keys
     - Create new API key

4. **Configure Environment**
   ```bash
   # Create environment file
   cp .env.template .env
   
   # Edit .env with your API keys
   nano .env
   # Add: GEMINI_API_KEY=your_gemini_key_here
   # Add: OPENAI_API_KEY=your_openai_key_here (optional)
   
   # Add to shell profile for persistence
   echo 'export GEMINI_API_KEY=your_key_here' >> ~/.zshrc
   echo 'export OPENAI_API_KEY=your_key_here' >> ~/.zshrc  # Optional
   source ~/.zshrc
   ```

5. **Verify Setup**
   ```bash
   python3 tools/pipeline_monitor.py --health-check
   ```

### 💰 **Cost Estimates**

#### **Current Pipeline Costs (Updated Pricing)**
- **Veo 3 Fast + Audio**: $3.20 per 8-second clip (720p, recommended)
- **Veo 3 Fast, Video Only**: $2.00 per 8-second clip (720p)
- **Veo 3 Standard + Audio**: $6.00 per 8-second clip (720p, highest quality)
- **Veo 3 Standard, Video Only**: $4.00 per 8-second clip (720p)
- **GPT-4-mini Enhancement**: ~$0.01-0.02 per prompt generation (with variations)
- **Midjourney**: $10-30/month subscription (unlimited generations)
- **Storage**: Minimal (local files, optional cloud backup)

#### **Audio Pipeline Costs**
- **AIVA API**: €15/month (~$17) Standard plan (15 downloads/month) or €49/month (~$55) Pro plan (300 downloads/month)
- **Stable Audio Open**: Free tier available (limited generations), paid tiers for higher usage
- **Manual Foley**: 
  - Professional studios: $50-140 per film minute
  - Freelance artists: $45-60/hour or $5+ per effect
  - Stock libraries: $8-50 per pack (100+ effects)
  - Self-recorded: Free (equipment costs $200-2000 initial setup)

#### **Total Project Estimate**
- **Short Film (3-5 minutes)**: $35-120 total (including monthly subscriptions)
- **Full Trailer (1-2 minutes)**: $25-75 total (including monthly subscriptions)  
- **Single Scene Test**: $20-40 total (including monthly subscriptions)
- **Budget Option**: Use free tiers + stock libraries for $5-15 per project

*Costs scale with iterations and complexity. Monitor real-time costs with `python3 tools/pipeline_monitor.py --dashboard`*

## 🎬 **Scene Types**

- **kaladin_intro**: Heroic defiance, storm grays, windswept atmosphere
- **bridge_run**: Desperate action, earth tones, chaotic movement
- **highstorm**: Overwhelming power, electric blues, massive scale
- **shattered_plains**: Alien desolation, crystal formations
- **spren**: Mystical wonder, ethereal glows, otherworldly magic

## 🎵 **Audio Pipeline Integration**

### **Three-Layer Audio Architecture**

#### 1. **Aiva API - Base Musical Score**
- **Purpose**: Primary orchestral composition for each scene
- **Input**: Clip length + style parameters (BPM, key, crescendo timing)
- **Output**: High-quality WAV files per cue
- **Integration**: `python3 tools/audio_composer.py --scene kaladin_intro --length 8s --style "80bpm orchestral minor key"`

#### 2. **Stable Audio API - Atmospheric Layers**
- **Purpose**: Stormlight-specific ambience and sound design
- **Specialties**: 
  - Highstorm wind crescendos
  - Spren chimes and mystical tones
  - Shardblade activation sounds
  - Cut-point stingers and risers
- **Integration**: `python3 tools/ambient_generator.py --type highstorm --duration 8s --intensity crescendo`

#### 3. **Manual Foley Layer**
- **Purpose**: Key sound effects and environmental audio
- **Sources**: 
  - Self-recorded Highstorm rumble (low-end focus)
  - Stock library effects for combat/movement
  - Custom Roshar-specific environmental sounds
- **Integration**: Manual editing in Final Cut Pro with auto-sync markers

### **Workflow Integration**
```bash
# Complete scene with audio
python3 tools/generate_veo3.py "Storm approaches Kaladin" --scene kaladin_intro --with-audio
# → Automatically triggers: video generation → audio composition → ambient layers → final mix
```

**Complete audio pipeline with automatic synchronization to video cuts and scene transitions!** 🎼⚡

## 🔧 **Troubleshooting**

### **Common Issues**

#### **API Key Problems**
```bash
# Check if key is set
echo $GEMINI_API_KEY

# Re-source your shell config
source ~/.zshrc

# Verify API access
python3 tools/pipeline_monitor.py --health-check
```

#### **Generation Failures**
```bash
# Check recent logs
python3 tools/pipeline_monitor.py --dashboard

# Verify styleframes exist
ls -la 01_styleframes_midjourney/start_frames/your_scene/

# Test with simple prompt
python3 tools/generate_veo3.py "simple test scene" --scene test
```

#### **Image Optimization Issues**
```bash
# Check tmp directory
ls -la tmp/

# Manually optimize image
python3 tools/styleframe_manager.py optimize tmp/your_image.png
```

#### **Cost Monitoring**
```bash
# Real-time cost tracking
python3 tools/pipeline_monitor.py --dashboard

# Check generation history
cat 02_prompts/ledger.jsonl | tail -10
```

### **Performance Tips**
- **Batch generations**: Process multiple scenes together for efficiency
- **Reuse styleframes**: Organize reference images for consistent style
- **Monitor costs**: Use dashboard to track spending in real-time
- **Optimize images**: Always use the auto-optimization (PNG→JPG, 9MB→1MB)

### **Getting Help**
- **Health Check**: `python3 tools/pipeline_monitor.py --health-check`
- **Verbose Logging**: Add `--verbose` flag to any command
- **Configuration**: Check `config/pipeline_config.yaml` for settings

---

**Ready to create epic Stormlight videos with professional Arcane-style animation!** ⚡🌪️