# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered animation pipeline for creating Stormlight Archives animated content using Midjourney for styleframes, Google's Veo 3 API for video generation, and OpenAI GPT-4-mini for intelligent prompt enhancement.

## Key Commands

### Running the Pipeline

```bash
# Launch control center dashboard (shows AI status)
python3 tools/stormlight_control.py

# Generate styleframes with interactive workflow (AI enhancement offered)
python3 tools/styleframe_manager.py interactive title_sequence "Scene description"

# Generate AI-enhanced prompts with variations
python3 tools/styleframe_manager.py prompts scene_name "Description" --llm-enhance --variations 3

# Generate video with AI-enhanced cinematic prompt
python3 tools/generate_veo3.py "Scene description" --scene scene_name --llm-prompt --camera "sweeping aerial" --mood "heroic"

# Monitor pipeline status (includes AI costs)
python3 tools/pipeline_monitor.py --dashboard
```

### Development & Testing

```bash
# Install dependencies (includes OpenAI SDK)
pip install -r requirements.txt

# Run setup (creates directories, configures GCP)
python3 setup.py

# Check system health (verifies AI configuration)
python3 tools/pipeline_monitor.py --health-check

# Test AI integration
bash test_integrated_workflow.sh
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
- AI-powered prompt enhancement with GPT-4-mini integration
- Automatic image optimization (PNG→JPG, 9MB→1MB)
- Organizes frames by scene and type (start/end/reference)
- Tracks metadata for all styleframes
- Saves enhanced prompts to both 02_prompts/ and 07_story_development/

**Veo3Generator** (`tools/generate_veo3.py`)
- Interfaces with Gemini API for Veo 3 video generation
- AI-enhanced cinematic prompts with camera movements and mood
- Auto-discovers matching styleframes for scene consistency
- Tracks all generations in ledger with cost estimation
- Supports 720p, 8-second clips

**StormlightControl** (`tools/stormlight_control.py`)
- Beautiful ASCII-branded control center dashboard
- Hotkey navigation (S/V/M/D/H/R) for tool launching
- Real-time status monitoring across all components
- Shows AI enhancement availability and status

**PipelineMonitor** (`tools/pipeline_monitor.py`)
- Tracks generation costs (video + AI) and pipeline health
- Live dashboard with progress tracking
- Validates API connectivity and resource availability
- Monitors AI token usage and costs

### Key Patterns

1. **Environment Configuration**: Uses `.env` file for API keys (GEMINI_API_KEY required, OPENAI_API_KEY optional)
2. **Scene Organization**: All content organized by scene name (e.g., kaladin_intro, bridge_run)
3. **Metadata Tracking**: JSONL ledger tracks all generations with timestamps, costs, and parameters
4. **Image Optimization**: Automatic compression and format conversion for API compatibility
5. **Style Consistency**: Arcane animation style prompts with --style raw --ar 16:9 --q 2
6. **AI Integration**: Seamless GPT-4-mini integration with caching and cost tracking
7. **Prompt Documentation**: Enhanced prompts saved to markdown with metadata

## API Integration

### Core APIs
- **Gemini API**: Used for Veo 3 video generation via REST endpoint
- **OpenAI API**: GPT-4-mini for intelligent prompt enhancement

### Cost Tracking
- **Video Generation**: ~$0.15 per 8-second clip (720p)
- **AI Enhancement**: ~$0.01-0.02 per prompt generation with variations
- **Total per Scene**: ~$0.16-0.17 with full AI enhancement

### Reliability Features
- **Rate Limiting**: Built-in retry logic with exponential backoff
- **Response Caching**: Reduces redundant AI calls and costs
- **Error Handling**: Graceful fallback when AI unavailable

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
- `openai` - OpenAI GPT-4-mini integration
- `Pillow` - Image processing and optimization
- `rich` - Terminal UI components
- `pyyaml` - Configuration management
- `python-dotenv` - Environment variable loading

## AI Enhancement Components

**LLMGenerator** (`tools/llm_generator.py`)
- Core OpenAI integration with GPT-4-mini
- Retry logic with exponential backoff
- Cost tracking and token counting
- Response caching to minimize API costs

**PromptEnhancer** (`tools/prompt_enhancer.py`)
- Specialized prompt generation for Midjourney and Veo 3
- Stormlight-specific visual elements
- Arcane animation style descriptors
- Camera movement and mood options
- Multiple variation generation