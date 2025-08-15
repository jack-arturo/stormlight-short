# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered animation pipeline for creating Stormlight Archives animated content using Midjourney for styleframes and Google's Veo 3 API for video generation.

## Key Commands

### Running the Pipeline

```bash
# Launch control center dashboard
python3 tools/stormlight_control.py

# Generate styleframes with interactive workflow
python3 tools/styleframe_manager.py interactive title_sequence "Scene description"

# Generate video from prompt
python3 tools/generate_veo3.py "Scene description" --scene scene_name

# Monitor pipeline status
python3 tools/pipeline_monitor.py --dashboard
```

### Development & Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup (creates directories, configures GCP)
python3 setup.py

# Check system health
python3 tools/pipeline_monitor.py --health-check
```

## Architecture

### Directory Structure
- `01_styleframes_midjourney/` - Organized Midjourney images (start/end frames per scene)
- `02_prompts/` - Generation metadata and prompt tracking (ledger.jsonl)
- `04_flow_exports/` - Generated MP4 videos from Veo 3
- `07_story_development/` - Story breakdown by acts
- `tools/` - Core pipeline scripts
- `config/pipeline_config.yaml` - Scene definitions and settings

### Core Components

**StyleframeManager** (`tools/styleframe_manager.py`)
- Interactive Midjourney workflow with step-by-step guidance
- Automatic image optimization (PNG→JPG, 9MB→1MB)
- Organizes frames by scene and type (start/end/reference)
- Tracks metadata for all styleframes

**Veo3Generator** (`tools/generate_veo3.py`)
- Interfaces with Gemini API for Veo 3 video generation
- Auto-discovers matching styleframes for scene consistency
- Tracks all generations in ledger with cost estimation
- Supports 720p, 8-second clips

**StormlightControl** (`tools/stormlight_control.py`)
- Beautiful ASCII-branded control center dashboard
- Hotkey navigation (S/V/M/D/H/R) for tool launching
- Real-time status monitoring across all components

**PipelineMonitor** (`tools/pipeline_monitor.py`)
- Tracks generation costs and pipeline health
- Live dashboard with progress tracking
- Validates API connectivity and resource availability

### Key Patterns

1. **Environment Configuration**: Uses `.env` file for API keys (GEMINI_API_KEY required)
2. **Scene Organization**: All content organized by scene name (e.g., kaladin_intro, bridge_run)
3. **Metadata Tracking**: JSONL ledger tracks all generations with timestamps, costs, and parameters
4. **Image Optimization**: Automatic compression and format conversion for API compatibility
5. **Style Consistency**: Arcane animation style prompts with --style raw --ar 16:9 --q 2

## API Integration

- **Gemini API**: Used for Veo 3 video generation via REST endpoint
- **Cost Tracking**: ~$0.15 per 8-second clip (720p)
- **Rate Limiting**: Built-in retry logic with exponential backoff

## Scene Types

Predefined in `config/pipeline_config.yaml`:
- `opening_kaladin` - Heroic character introduction
- `bridge_run` - Action sequences
- `spren_encounter` - Mystical/magical moments
- `stormwall` - Environmental/storm scenes

Each scene has style descriptors and default prompts for consistency.

## Dependencies

Key Python packages:
- `google-generativeai` - Gemini API client
- `Pillow` - Image processing and optimization
- `rich` - Terminal UI components
- `pyyaml` - Configuration management
- `python-dotenv` - Environment variable loading