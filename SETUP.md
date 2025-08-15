# Stormlight Archives Short Film - Setup Guide

Quick setup guide for the Stormlight Archives short film project environment.

## ✅ Shell Configuration Fixed

The Google Cloud SDK shell configuration has been fixed with the following improvements:

### What was fixed:
- **Incorrect paths**: Changed from `google-cloud-sdk` to `gcloud-cli` (correct Homebrew package)
- **Hardcoded versions**: Replaced with version-agnostic auto-detection
- **Missing error handling**: Added file existence checks before sourcing
- **Poor maintenance**: Created robust configuration that survives SDK updates

### Current configuration:
- ✅ Google Cloud SDK properly detected at: `/opt/homebrew/Caskroom/gcloud-cli/534.0.0/google-cloud-sdk`
- ✅ Shell integration (path and completion) loaded automatically
- ✅ `gcloud` command available and working (version 534.0.0)
- ✅ Authentication configured for `johngarturo@gmail.com`

## 🚀 Quick Start

1. **Environment Setup** (Required):
   ```bash
   cp .env.template .env
   # Edit .env with your actual values (GCP project ID, bucket name, etc.)
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Google Cloud Setup**:
   ```bash
   gcloud --version
   gcloud config get-value project
   gcloud auth application-default login  # If needed
   ```

4. **Test the Pipeline**:
   ```bash
   python tools/test_pipeline.py
   ```

## 🔧 Tools Available

### Shell Configuration Fix Script
```bash
# Check what the script would do (safe to run)
./tools/fix_shell_config.sh --dry-run

# Apply fixes if needed (creates backups first)
./tools/fix_shell_config.sh
```

### Google Cloud Storage Sync
```bash
# Sync local files to GCS (dry run first)
python tools/sync_to_gcs.py --local . --bucket your-bucket-name --dry-run

# Actual sync
python tools/sync_to_gcs.py --local . --bucket your-bucket-name
```

## 📋 Environment Variables

Key variables to set in your `.env` file:

```bash
# Required
GCP_PROJECT_ID=your-actual-project-id
GCS_BUCKET=your-bucket-name
GCP_LOCATION=us-central1

# Optional but recommended
COST_WARNING_THRESHOLD=10.0
DEFAULT_DRY_RUN=true
DEBUG=false
```

## 🔍 Verification Commands

Test everything is working:

```bash
# Shell configuration
echo $GCLOUD_SDK_DIR
gcloud --version

# Project configuration
gcloud config get-value project
gcloud auth list

# Python environment
python -c "import google.cloud.storage; print('GCS client available')"
python -c "import google.cloud.aiplatform; print('Vertex AI client available')"

# Tool functionality
./tools/fix_shell_config.sh --dry-run
python tools/test_pipeline.py --help
```

## 🆘 Troubleshooting

### Shell Issues
- **Command not found**: Run `./tools/fix_shell_config.sh` then restart your shell
- **Path errors**: Ensure you're in the project root directory

### GCP Issues  
- **Auth errors**: Run `gcloud auth application-default login`
- **Project not set**: Run `gcloud config set project YOUR_PROJECT_ID`
- **Permission denied**: Check your GCP IAM permissions

### Python Issues
- **Import errors**: Run `pip install -r requirements.txt`
- **Permission errors**: Check file permissions with `ls -la`

## 📁 Project Structure

```
stormlight_short/
├── .env.template          # Environment variables template
├── SETUP.md              # This file
├── config/               # Configuration files
├── tools/                # Automation scripts
│   ├── README.md         # Tools documentation
│   ├── fix_shell_config.sh  # Shell configuration fix
│   └── *.py              # Python automation tools
├── 00_docs/              # Documentation and logs
├── 01_styleframes_midjourney/  # Midjourney assets
├── 02_prompts/           # Generated prompts
├── 03_vertex_jobs/       # Vertex AI job outputs
├── 04_flow_exports/      # Flow video exports
├── 05_audio/             # Audio assets
└── 06_final_cut/         # Final Cut Pro projects
```

## ✨ Next Steps

1. Configure your `.env` file with actual values
2. Test the sync functionality with a dry run
3. Generate your first style frames in Midjourney
4. Create video clips with Vertex AI
5. Import and edit in Flow/Final Cut Pro

For detailed tool documentation, see `tools/README.md`.