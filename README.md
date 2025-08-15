# 🎬 Stormlight Archives Short Film - AI Production Pipeline

An end-to-end AI-powered video generation pipeline for creating a Stormlight Archives short film using Google's Veo 3, Vertex AI, Midjourney, and Flow.

## 🚀 Quick Start

```bash
# Launch the interactive pipeline manager
./launch.sh
```

## 📋 Project Status

### ✅ Completed Features
- **Shell Configuration**: Fixed Google Cloud SDK paths
- **Vertex AI Integration**: Complete Veo 3 API integration with cost tracking
- **Prompt Template System**: YAML-based scene prompts with variations
- **Asset Pipeline**: Automated Midjourney and Flow export processing
- **Workflow Orchestration**: End-to-end scene-to-video automation
- **Monitoring Dashboard**: Real-time pipeline monitoring with Rich UI
- **Testing Framework**: Comprehensive test coverage
- **Cost Management**: Per-job and cumulative cost tracking with warnings

### 🔧 Configuration Required
1. Update `config/pipeline_config.yaml` with your GCP project ID
2. Copy `.env.template` to `.env` and fill in your values
3. Ensure GCP authentication: `gcloud auth application-default login`

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Midjourney    │────▶│   Prompts    │────▶│  Vertex AI  │
│   Styleframes   │     │   Templates  │     │   (Veo 3)   │
└─────────────────┘     └──────────────┘     └─────────────┘
         │                      │                     │
         └──────────────────────┼─────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Master Pipeline    │
                    │    Orchestrator     │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┼─────────────┐
                 │             │             │
         ┌───────▼──────┐ ┌───▼────┐ ┌──────▼──────┐
         │     Flow     │ │  GCS   │ │  Monitoring │
         │   Exports    │ │  Sync  │ │  Dashboard  │
         └──────────────┘ └────────┘ └─────────────┘
```

## 📁 Project Structure

```
stormlight_short/
├── 00_docs/                    # Documentation and logs
│   ├── sync_logs/              # GCS sync operation logs
│   └── vertex_logs/            # Vertex AI job logs
├── 01_styleframes_midjourney/  # Midjourney reference images
├── 02_prompts/                 # Prompt templates and configurations
│   ├── opening_kaladin_template.yaml
│   ├── bridge_run_template.yaml
│   └── batch_example.json
├── 03_vertex_jobs/             # Vertex AI job outputs
│   └── [scene_name]/
│       └── [job_id]/
│           ├── inputs/         # Request payloads
│           ├── outputs/        # Generated videos
│           └── metadata/       # Job metadata
├── 04_flow_exports/            # Flow editing exports
├── 05_audio/                   # Audio assets
├── 06_final_cut/              # Final rendered videos
├── config/                     # Configuration files
│   └── pipeline_config.yaml
├── tools/                      # Automation scripts
│   ├── vertex_manager.py       # Vertex AI integration
│   ├── flow_manager.py         # Flow export processing
│   ├── midjourney_manager.py   # Midjourney asset management
│   ├── automation_orchestrator.py  # Pipeline orchestration
│   ├── pipeline_monitor.py     # Monitoring dashboard
│   ├── master_pipeline.py      # Master controller
│   ├── safety_manager.py       # Safety and permissions
│   ├── test_pipeline.py        # Test suite
│   └── sync_to_gcs.py.py      # GCS synchronization
├── launch.sh                   # Interactive launcher
├── requirements.txt            # Python dependencies
├── .env.template              # Environment variables template
├── CLAUDE.md                  # Claude Code instructions
├── SETUP.md                   # Setup guide
└── README.md                  # This file
```

## 🎯 Key Commands

### Interactive Mode
```bash
./launch.sh  # Launch interactive menu
```

### Direct Commands
```bash
# Monitor dashboard
python3 tools/pipeline_monitor.py --dashboard

# Validate configuration
python3 tools/master_pipeline.py --validate

# Test single scene
python3 tools/master_pipeline.py --test-scene opening_kaladin

# Run full pipeline
python3 tools/master_pipeline.py --full-pipeline

# Sync to GCS
python3 tools/sync_to_gcs.py.py --local . --bucket stormlight-short

# Submit Vertex AI job
python3 tools/vertex_manager.py \
  --project-id YOUR_PROJECT_ID \
  --scene "opening_kaladin" \
  --prompt "Kaladin on the Shattered Plains..." \
  --duration 5
```

## 🎬 Scene Definitions

### Configured Scenes
1. **opening_kaladin**: Kaladin on the Shattered Plains
2. **bridge_run**: Bridge Four carrying bridge under fire
3. **spren_encounter**: First meeting with Sylphrena
4. **stormwall**: The approaching highstorm

Each scene includes:
- Multiple prompt variations
- Style references
- Technical specifications
- Production notes

## 💰 Cost Management

### Vertex AI (Veo 3) Pricing
- **720p**: $0.0375/second
- **1080p**: $0.075/second
- **4K**: $0.15/second

### Cost Controls
- Warning at $50 USD
- Approval required at $200 USD
- Per-job and cumulative tracking
- Dry-run mode for testing

## 🔒 Safety Features

- **Dry-run mode**: Test without API calls
- **Cost warnings**: Automatic thresholds
- **Backup before sync**: Automatic backups
- **Permission checks**: Safety manager validation
- **Error recovery**: Comprehensive error handling

## 🧪 Testing

```bash
# Run all tests
python3 tools/test_pipeline.py

# Test specific component
python3 tools/test_pipeline.py TestVertexManager

# Validate pipeline
python3 tools/master_pipeline.py --validate
```

## 📊 Monitoring

The pipeline includes a real-time monitoring dashboard showing:
- Active Vertex AI jobs
- Asset inventory
- GCS sync status
- Cost summary
- Pipeline health

Launch with: `python3 tools/pipeline_monitor.py --dashboard`

## 🚁 Troubleshooting

### Common Issues

1. **Shell errors about Google Cloud SDK paths**
   ```bash
   bash tools/fix_shell_config.sh
   ```

2. **GCP authentication issues**
   ```bash
   gcloud auth application-default login
   ```

3. **Missing dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Configuration not found**
   - Update `config/pipeline_config.yaml` with your GCP project ID
   - Copy `.env.template` to `.env` and configure

## 📚 Documentation

- **CLAUDE.md**: Instructions for Claude Code AI assistant
- **SETUP.md**: Detailed setup guide
- **tools/README.md**: Documentation for all automation tools
- **.cursor/rules/**: Cursor AI configuration

## 🤝 Contributing

This project uses AI-driven development with Claude Code and Cursor. When contributing:
1. Follow existing patterns in the codebase
2. Update tests for new features
3. Document changes in relevant files
4. Test with dry-run mode first

## 📄 License

Private project for Stormlight Archives short film production.

## 🙏 Acknowledgments

- Brandon Sanderson for the Stormlight Archives universe
- Google Veo 3 for AI video generation
- Midjourney for style frame generation
- Claude Code for development assistance

---

**Project Status**: Production Ready with Configuration Required
**Last Updated**: August 2025
**Version**: 1.0.0