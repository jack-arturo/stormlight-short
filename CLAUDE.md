# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Stormlight Archives short film project using Google's Veo 3 video generation model, Flow, Vertex AI, and Midjourney for creative asset generation. The project involves AI-driven content creation with a focus on reproducibility and cloud-based asset management.

## Environment Setup

- **Python**: 3.9+ (uses google-cloud-storage and google-cloud-aiplatform)
- **Google Cloud SDK**: Required for authentication and GCS operations
- **Authentication**: Uses Application Default Credentials (ADC)
  ```bash
  gcloud auth application-default login
  ```

## Project Structure

```
stormlight_short/
├── 00_docs/               # Documentation and sync logs
│   └── sync_logs/        # Automated sync operation logs
├── 01_styleframes_midjourney/  # Midjourney style references
├── 02_prompts/           # Prompt templates and ledgers
├── 03_vertex_jobs/       # Vertex AI job organization
│   └── [scene_name]/    # Per-scene job folders
│       └── [job_id]/    # Individual job with inputs/outputs/metadata
├── 04_flow_exports/      # Flow editing exports
├── 05_audio/            # Audio assets
├── 06_final_cut/        # Final cut exports
└── tools/               # Automation scripts
    ├── sync_to_gcs.py.py     # GCS sync utility
    └── vertex_manager.py      # Vertex AI job management
```

## Common Development Commands

### Sync to Google Cloud Storage
```bash
# Basic sync (uploads new/changed files)
python3 tools/sync_to_gcs.py.py \
  --local ~/Projects/OpenAI/stormlight_short \
  --bucket stormlight_short

# Sync with deletion of removed files
python3 tools/sync_to_gcs.py.py \
  --local ~/Projects/OpenAI/stormlight_short \
  --bucket stormlight_short \
  --delete

# Dry run to preview changes
python3 tools/sync_to_gcs.py.py \
  --local ~/Projects/OpenAI/stormlight_short \
  --bucket stormlight_short \
  --dry-run
```

### Vertex AI Video Generation
```bash
# Submit a Veo 3 generation job
python3 tools/vertex_manager.py \
  --project-id YOUR_PROJECT_ID \
  --scene "opening_kaladin" \
  --prompt "Kaladin standing on shattered plains at sunset..." \
  --duration 5 \
  --resolution 1280x720

# Test with dry run
python3 tools/vertex_manager.py \
  --project-id YOUR_PROJECT_ID \
  --scene "test_scene" \
  --prompt "Test prompt" \
  --dry-run
```

## Key Development Patterns

### Vertex AI Job Organization
Each Vertex job creates a structured folder with:
- `inputs/` - Request payloads and configuration
- `outputs/` - Generated video files
- `metadata/` - Job metadata and tracking
- `README.md` - Human-readable job summary

### Sync Strategy
The sync tool uses MD5 hashing to avoid re-uploading unchanged files. It:
- Skips common temporary files (*.DS_Store, *.tmp)
- Creates detailed logs in `00_docs/sync_logs/`
- Supports incremental updates and full synchronization
- Can optionally delete remote files not present locally

### Prompt Management
Store reusable prompts in `02_prompts/` with:
- Template files for consistent scene generation
- Seed values for reproducibility
- Negative prompts for quality control
- Scene-specific parameters

## Important Considerations

1. **GCS Path Note**: The sync tool has a duplicate `.py` extension (`sync_to_gcs.py.py`) - be aware when calling it
2. **Shell Configuration**: The system shows zprofile errors for Google Cloud SDK paths - these can be ignored or fixed by updating shell configuration
3. **Vertex AI Integration**: The vertex_manager.py currently has placeholder code for actual Vertex AI submission - implementation needed for production use
4. **Authentication**: Ensure Google Cloud ADC is configured before running any cloud operations