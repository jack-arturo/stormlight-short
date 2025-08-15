# Web-First Workflow for Stormlight Short

## Current Status: Web Interface Priority

The project has been cleaned up and optimized for a web-interface-first workflow while awaiting Veo 3 API opt-in approval.

## Key Changes Made

### 1. Cleanup Completed
- Moved all API experiment files to `archive/api_experiments/`
- Removed simulated test data and redundant scripts
- Cleaned up vertex job directories
- Added `archive/` to .gitignore

### 2. Web Workflow Implementation
- Created `README_vertex_ai_workflow.md` with complete instructions
- Added `tools/web_workflow_helper.py` for clip organization
- Implemented `02_prompts/ledger.jsonl` for prompt tracking
- Established clean file naming conventions

### 3. Directory Structure
```
stormlight_short/
├── 04_flow_exports/           # Downloaded MP4 clips go here
├── 02_prompts/ledger.jsonl    # Prompt metadata tracking
├── tools/web_workflow_helper.py # Organization automation
├── README_vertex_ai_workflow.md # Complete workflow guide
└── archive/api_experiments/   # Archived experimental code
```

## Current Workflow

### For Video Generation:
1. Use Vertex AI Media Studio web interface
2. Generate with `veo-3.0-generate-preview` at 720p, 8 seconds
3. Download MP4 files manually
4. Use `tools/web_workflow_helper.py` to organize and log

### For Development:
- Focus on story development and prompt refinement
- Maintain existing pipeline tools for future API integration
- Use web workflow helper for clip management
- Keep all metadata for reproducibility

## Commands Available

```bash
# Organize a downloaded clip
python3 tools/web_workflow_helper.py organize \
  --source ~/Downloads/video.mp4 \
  --scene title_sequence \
  --prompt "Epic fantasy title sequence..." \
  --notes "Good alien landscape"

# Check generation status
python3 tools/web_workflow_helper.py status

# List all scenes
python3 tools/web_workflow_helper.py scenes

# View prompts for a scene
python3 tools/web_workflow_helper.py prompts --scene-name title_sequence
```

## API Transition Plan

When Veo 3 API opt-in is approved:
1. Existing clips remain valid (high quality)
2. Update `tools/vertex_manager.py` for API calls
3. Batch generate remaining clips
4. Maintain same file organization and metadata

## Priority Scenes

Generate in this order:
1. Title sequence (establish world)
2. Kaladin introduction (main character)
3. Shattered Plains (central location)
4. Bridge run action (key sequence)
5. Highstorm approach (environmental spectacle)

The web workflow ensures continuous progress while maintaining project organization and preparing for seamless API integration.
