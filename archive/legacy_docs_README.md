# Stormlight Short - AI Video Production Pipeline

A comprehensive automation pipeline for creating the *Stormlight Archives* short film using Veo 3, Flow, Vertex AI, and Midjourney.

## 🎬 Project Overview

This project creates a seamless, reproducible pipeline for AI-generated video content, managing the entire workflow from style frame generation to final video production.

### Key Features

- **Automated GCS Sync**: Bidirectional sync between local project and Google Cloud Storage
- **Vertex AI Integration**: Automated Veo 3 video generation with metadata tracking
- **Flow Management**: Organized exports with take numbering and seed references
- **Midjourney Organization**: Style frame validation, naming, and batch processing
- **Reproducibility**: Complete metadata tracking for all generations
- **Safety Systems**: Confirmation prompts and backup systems for destructive operations
- **Automation**: Scheduled sync operations and batch processing

## 📁 Project Structure

```
stormlight_short/
├── 00_docs/                    # Documentation and logs
│   ├── sync_logs/              # GCS sync operation logs
│   ├── safety_logs/            # Safety operation logs
│   └── backups/                # Automated backups
├── 01_styleframes_midjourney/  # Midjourney style frames (16:9, ≥1280×720)
├── 02_prompts/                 # Prompt ledgers and templates
├── 03_vertex_jobs/             # Vertex AI job folders with metadata
├── 04_flow_exports/            # Flow creative assembly exports
├── 05_audio/                   # Audio assets and tracks
├── 06_final_cut/               # Final editing and output files
├── config/                     # Pipeline configuration
├── tools/                      # Automation scripts
└── .cursor/rules/              # Development agent instructions
```

## 🚀 Quick Start

### 1. Setup

```bash
# Install dependencies
pip3 install -r requirements.txt

# Configure your GCP project
gcloud init
gcloud auth application-default login

# Update configuration
vim config/pipeline_config.yaml
```

### 2. Basic Operations

```bash
# Sync to GCS (dry run first)
python3 tools/sync_to_gcs.py.py --local . --bucket your-bucket --dry-run

# Process Midjourney style frames
python3 tools/midjourney_manager.py --source /path/to/images --scene opening_kaladin --descriptor windswept --prompt "Kaladin on stormy plains"

# Create Vertex AI job
python3 tools/vertex_manager.py --scene bridge_run --prompt "Warriors carrying bridge across chasm" --project-id your-project

# Full automation orchestration
python3 tools/automation_orchestrator.py --sync-only --dry-run
```

## 🛠 Tools Overview

### Core Scripts

- **`sync_to_gcs.py.py`**: Bidirectional sync with GCS, MD5 checking, logging
- **`vertex_manager.py`**: Vertex AI job creation, metadata tracking, Veo 3 integration
- **`flow_manager.py`**: Flow export organization, take numbering, prompt ledgers
- **`midjourney_manager.py`**: Style frame validation, batch processing, naming conventions
- **`automation_orchestrator.py`**: Master automation controller
- **`safety_manager.py`**: Safety confirmations, permissions, backups

### Usage Examples

#### Sync Operations
```bash
# Dry run sync
python3 tools/sync_to_gcs.py.py --local . --bucket stormlight-short --dry-run

# Full sync with deletions (requires confirmation)
python3 tools/sync_to_gcs.py.py --local . --bucket stormlight-short --delete

# Exclude specific patterns
python3 tools/sync_to_gcs.py.py --local . --bucket stormlight-short --exclude "*.tmp" --exclude "*.DS_Store"
```

#### Vertex AI Jobs
```bash
# Create video generation job
python3 tools/vertex_manager.py \
  --scene opening_kaladin \
  --prompt "Kaladin Stormblessed standing on the Shattered Plains, windswept cloak, dramatic storm lighting" \
  --duration 5 \
  --resolution 1280x720 \
  --project-id your-gcp-project

# Dry run (no actual submission)
python3 tools/vertex_manager.py --scene test --prompt "test prompt" --project-id your-project --dry-run
```

#### Midjourney Processing
```bash
# Process single style frame
python3 tools/midjourney_manager.py \
  --source image.png \
  --scene opening_kaladin \
  --descriptor windswept \
  --prompt "Kaladin on stormy plains"

# Validate image requirements
python3 tools/midjourney_manager.py --source image.png --validate-only

# Resize to meet requirements
python3 tools/midjourney_manager.py --source image.png --resize
```

#### Flow Management
```bash
# Organize Flow export
python3 tools/flow_manager.py \
  --source video.mp4 \
  --scene bridge_run \
  --prompt "Bridge crew running across chasm" \
  --seed 12345
```

## 🔧 Configuration

Edit `config/pipeline_config.yaml` to customize:

- GCP project and bucket settings
- Scene definitions and default prompts
- Vertex AI model configurations
- Safety and automation settings
- File format preferences

## 🛡 Safety Features

### Confirmation System
- Destructive operations require user confirmation
- Dry-run mode for all sync operations
- Automatic backups before destructive changes
- Operation logging for audit trails

### Permission Checks
```bash
# Check GCS bucket permissions
python3 tools/safety_manager.py --check-permissions your-bucket

# Validate bucket safety
python3 tools/safety_manager.py --validate-bucket your-bucket

# View safety log
python3 tools/safety_manager.py --show-log
```

## 📊 Metadata & Reproducibility

Every generation includes:
- **Prompt text**: Complete prompt used
- **Seed**: Random seed for reproducibility
- **Negative prompt**: Exclusion instructions
- **Model version**: Specific AI model used
- **Technical specs**: Resolution, duration, aspect ratio
- **Timestamps**: Creation and modification times
- **File hashes**: Integrity verification

Metadata is stored as:
- JSON files alongside outputs
- Centralized prompt ledgers per scene
- Human-readable README files

## 🔄 Automation

### Scheduled Operations
```bash
# Set up automated hourly sync (macOS)
python3 tools/automation_orchestrator.py --setup-schedule launchd

# Set up cron job (Linux/macOS)
python3 tools/automation_orchestrator.py --setup-schedule cron
```

### Batch Processing
```bash
# Process multiple Flow exports
python3 tools/automation_orchestrator.py --process-flow /path/to/exports

# Process multiple Midjourney images
python3 tools/automation_orchestrator.py --process-midjourney /path/to/images

# Generate prompt ledger summary
python3 tools/automation_orchestrator.py --generate-summary
```

## 🎯 Scene Definitions

Pre-configured scenes in `config/pipeline_config.yaml`:

1. **opening_kaladin**: Kaladin on the Shattered Plains
2. **bridge_run**: Bridge crew action sequence
3. **spren_encounter**: Kaladin meets Sylphrena
4. **stormwall**: Approaching highstorm

Each scene includes:
- Description and style descriptors
- Default prompts for consistency
- Specific generation parameters

## 📝 File Naming Conventions

### Style Frames
`{scene}_{descriptor}_{seed}.png`
- Example: `opening_kaladin_windswept_12345.png`

### Vertex AI Jobs
`{scene}_take{number}_{timestamp}/`
- Example: `bridge_run_take01_20241215_143022/`

### Flow Exports
`{scene}_take{number}_{timestamp}_seed{seed}.mp4`
- Example: `spren_encounter_take03_20241215_143022_seed67890.mp4`

## 🚨 Troubleshooting

### Common Issues

1. **GCS Authentication**: Ensure `gcloud auth application-default login` is run
2. **Permissions**: Check bucket IAM permissions with safety manager
3. **Dependencies**: Install all requirements with `pip3 install -r requirements.txt`
4. **Configuration**: Update `config/pipeline_config.yaml` with your project details

### Logs and Debugging

- Sync logs: `00_docs/sync_logs/`
- Safety logs: `00_docs/safety_logs/`
- Operation backups: `00_docs/backups/`

## 🔮 Advanced Usage

### Custom Automation Workflows
```python
from tools.automation_orchestrator import StormLightOrchestrator

orchestrator = StormLightOrchestrator()

# Custom scene processing
job_id = orchestrator.process_vertex_job(
    "custom_scene", 
    "Your custom prompt here",
    duration=10,
    seed=42
)

# Automated sync after processing
orchestrator.sync_to_gcs(dry_run=False)
```

### Integration with External Tools
The pipeline is designed to integrate with:
- Midjourney Discord bots
- Flow creative tools
- Google Cloud Vertex AI
- Custom video editing workflows

## 📄 License & Credits

This project is part of the Stormlight Archives short film production using:
- Google Cloud Vertex AI (Veo 3)
- Midjourney for style frames
- Flow for creative assembly
- Brandon Sanderson's Stormlight Archive universe

---

*Built with ⚡ by the Stormlight Short development team*
