# 🚀 Stormlight Short - Quick Start Guide

## ✅ Current Status

Your pipeline is **99% ready**! Everything is installed and configured except for one item:

### 🔴 Required: Update GCP Project ID

The only remaining step is to update your Google Cloud Project ID in the configuration.

## 📝 Complete Setup in 2 Minutes

### Step 1: Get Your GCP Project ID

```bash
# List your GCP projects
gcloud projects list

# Or get the current project
gcloud config get-value project
```

### Step 2: Update Configuration

Edit `config/pipeline_config.yaml`:
```yaml
gcp_project_id: "your-actual-project-id-here"  # <-- Change this line
gcs_bucket: "stormlight-short"  # <-- Update bucket name if needed
```

Or use the interactive menu:
```bash
./launch.sh
# Select option 8 (Configure Project)
```

### Step 3: (Optional) Set Up Environment Variables

Copy and configure the environment file:
```bash
cp .env.template .env
# Edit .env with your values
```

## ✨ That's It! You're Ready!

Once you've updated the project ID, you can:

### Test the Pipeline
```bash
# Validate everything is working
python3 tools/master_pipeline.py --validate

# Run a test scene (dry run - no costs)
python3 tools/master_pipeline.py --test-scene opening_kaladin
```

### Launch the Dashboard
```bash
# Interactive menu
./launch.sh

# Or direct dashboard
python3 tools/pipeline_monitor.py --dashboard
```

### Generate Your First Video
```bash
# Single scene test
python3 tools/vertex_manager.py \
  --project-id YOUR_PROJECT_ID \
  --scene "opening_kaladin" \
  --prompt "Kaladin standing on the Shattered Plains at sunset" \
  --duration 5 \
  --dry-run  # Remove --dry-run for actual generation
```

## 🎬 Available Scenes

1. **opening_kaladin** - Hero shot on the Shattered Plains
2. **bridge_run** - Bridge Four in action
3. **spren_encounter** - Meeting Sylphrena
4. **stormwall** - The approaching highstorm

## 💡 Tips

- Always use `--dry-run` first to test without costs
- Monitor costs with the dashboard (option 1 in menu)
- Sync to GCS regularly (option 5 in menu)
- Check health status before major operations (option 6)

## 📊 What's Working

✅ **Shell configuration** - Fixed and operational
✅ **Python dependencies** - All installed
✅ **GCP authentication** - Active and working
✅ **Project structure** - Complete with all directories
✅ **Vertex AI integration** - Ready with Veo 3 API
✅ **Prompt templates** - 2 scenes configured
✅ **Monitoring dashboard** - Real-time pipeline tracking
✅ **Cost management** - Tracking and warnings enabled
✅ **Safety features** - Dry-run mode and validations

## 🔧 What Needs Configuration

❌ **GCP Project ID** - Update in config/pipeline_config.yaml
⚠️ **GCS Bucket Name** - Verify/update in config
⚠️ **Environment Variables** - Optional but recommended

## 🆘 Need Help?

1. Run health check: `./launch.sh` → Option 6
2. View logs: Check `00_docs/sync_logs/` and `00_docs/vertex_logs/`
3. Test components: `python3 tools/test_pipeline.py`
4. View documentation: `./launch.sh` → Option 7

---

**You're just one configuration change away from generating AI videos!**

Update the project ID and start creating your Stormlight Archives short film! 🎬✨