# Stormlight Archives Short Film - Tools Directory

This directory contains automation and utility scripts for the Stormlight Archives short film project.

## Scripts Overview

### `fix_shell_config.sh` - Shell Configuration Fix Script
Fixes common shell configuration issues, particularly with Google Cloud SDK paths.

**Features:**
- Auto-detects Google Cloud SDK installation location
- Creates version-agnostic configuration that survives updates
- Backs up existing configuration before making changes
- Works with Homebrew installations of `gcloud-cli`
- Supports dry-run mode for testing

**Usage:**
```bash
# Test what changes would be made
./tools/fix_shell_config.sh --dry-run

# Apply the fixes
./tools/fix_shell_config.sh
```

**What it fixes:**
- Incorrect Google Cloud SDK paths in `.zprofile`
- Hardcoded version paths that break on updates
- Missing shell completion setup
- Conflicting configurations in multiple shell files

### `sync_to_gcs.py` - Google Cloud Storage Sync
Synchronizes local project files to Google Cloud Storage with intelligent change detection.

**Key Features:**
- MD5-based change detection (only uploads modified files)
- Configurable exclude patterns
- Optional deletion of remote files not present locally
- Detailed sync logging
- Dry-run mode for testing

### `vertex_manager.py` - Vertex AI Video Generation Manager
Complete Veo 3 integration for AI video generation with comprehensive job management.

**Key Features:**
- **Actual Veo 3 API Integration**: Real Vertex AI API calls with proper request formatting
- **Cost Tracking & Warnings**: Real-time cost calculation with user approval for high-cost jobs
- **Comprehensive Error Handling**: Retry logic, quota management, permission checks
- **Job Status Monitoring**: Progress tracking with visual progress bars and timeouts
- **Batch Job System**: Submit multiple jobs with concurrency limits and cost oversight
- **Complete Metadata Tracking**: Full reproducibility with detailed job metadata

**Single Job Usage:**
```bash
# Basic video generation
python3 tools/vertex_manager.py \
  --project-id YOUR_PROJECT_ID \
  --scene "opening_kaladin" \
  --prompt "Kaladin on the Shattered Plains at sunset..." \
  --duration 5 \
  --resolution 1280x720

# Advanced parameters
python3 tools/vertex_manager.py \
  --project-id YOUR_PROJECT_ID \
  --scene "bridge_run" \
  --prompt "Bridge crews running across chasm..." \
  --negative-prompt "blurry, low quality" \
  --seed 12345 \
  --duration 8 \
  --guidance-scale 7.5 \
  --temperature 0.7 \
  --take 2

# Test without submitting
python3 tools/vertex_manager.py \
  --project-id YOUR_PROJECT_ID \
  --scene "test_scene" \
  --prompt "Test prompt" \
  --dry-run
```

**Batch Job Usage:**
```bash
# Submit batch jobs from JSON config
python3 tools/vertex_manager.py \
  --project-id YOUR_PROJECT_ID \
  --batch-config 02_prompts/batch_example.json \
  --max-concurrent 3

# Test batch submission
python3 tools/vertex_manager.py \
  --project-id YOUR_PROJECT_ID \
  --batch-config 02_prompts/batch_example.json \
  --dry-run
```

**Job Monitoring:**
```bash
# List all active jobs
python3 tools/vertex_manager.py --project-id YOUR_PROJECT_ID --list-jobs

# Check specific job status
python3 tools/vertex_manager.py --project-id YOUR_PROJECT_ID --job-status JOB_ID

# Get cost summary
python3 tools/vertex_manager.py --project-id YOUR_PROJECT_ID --cost-summary

# Cancel a job
python3 tools/vertex_manager.py --project-id YOUR_PROJECT_ID --cancel-job JOB_ID
```

**Cost Management:**
- Automatic cost calculation based on duration and resolution
- Warning thresholds: $50 (warning), $200 (critical approval required)
- Session-wide cost tracking
- Detailed cost breakdowns by job
- Batch cost validation before submission

**Error Handling:**
- Exponential backoff retry for transient failures
- Specific handling for quota/permission issues
- Comprehensive logging to `00_docs/vertex_logs/`
- Graceful degradation and status preservation
- User-friendly error messages with troubleshooting guidance

**Job Organization:**
Each job creates structured folders under `03_vertex_jobs/`:
```
03_vertex_jobs/
└── scene_name/
    └── scene_name_take01_20250815_120459/
        ├── README.md              # Human-readable summary
        ├── inputs/
        │   └── request_payload.json
        ├── metadata/
        │   ├── job_metadata.json  # Complete job metadata
        │   ├── job_result.json    # Job results and status
        │   └── job_id.txt        # Job ID for tracking
        └── outputs/              # Generated videos (when complete)
```

### Other Tools
- `automation_orchestrator.py` - Main automation coordinator
- `flow_manager.py` - Flow integration management
- `midjourney_manager.py` - Midjourney API interactions
- `safety_manager.py` - Safety checks and validations
- `test_pipeline.py` - Pipeline testing utilities

## Environment Setup

1. Copy the environment template:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` with your actual configuration values

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure Google Cloud SDK is properly configured:
   ```bash
   ./tools/fix_shell_config.sh
   source ~/.zprofile
   gcloud auth application-default login
   ```

## Common Issues

### Google Cloud SDK Not Found
If you get "gcloud: command not found" errors:
1. Install Google Cloud CLI: `brew install --cask gcloud-cli`
2. Run the fix script: `./tools/fix_shell_config.sh`
3. Restart your shell or: `source ~/.zprofile`

### Authentication Issues
For GCP authentication problems:
1. Set up Application Default Credentials: `gcloud auth application-default login`
2. Verify your project is set: `gcloud config get-value project`
3. Set project if needed: `gcloud config set project YOUR_PROJECT_ID`

### Path Issues
If scripts can't find files or directories:
1. Ensure you're running from the project root directory
2. Check that all paths in `.env` are correct
3. Verify file permissions are set correctly

## Development Notes

- All Python scripts use type hints and follow PEP 8 style guidelines
- Shell scripts follow best practices with `set -euo pipefail`
- All scripts support `--help` flag for usage information
- Logs are written to `00_docs/sync_logs/` for audit trails