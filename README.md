# 🎬 Stormlight: Into the Tempest - AI Production Pipeline

An end-to-end AI-powered video generation pipeline for creating a 4-minute animated pilot trailer for the Stormlight Archives, using Google's Veo 3, Vertex AI, Midjourney, and Flow.

## 🚀 Quick Start

```bash
# Launch the interactive pipeline manager
./launch.sh
```

## 📋 Project Status: GEMINI API INTEGRATION READY

### ✅ Pre-Production Complete
- **Story Development**: Full 4-minute pilot trailer structure with 29 clips
- **Character Arcs**: Kaladin (slave→Radiant), Adolin (prince→true knight), Dalinar (warlord→chosen)
- **Dynamic Timing**: 3-8 second clips for natural pacing (total runtime 3:13)
- **Visual Style Guide**: Anime-inspired (Attack on Titan meets Studio Ghibli)
- **Production Notes**: Complete with audio design and technical specifications

### ✅ Gemini API Integration
- **Veo 3 Access**: Direct API access via `veo-3.0-generate-preview` model
- **Programmatic Generation**: Generate videos directly from Cursor/terminal
- **Automated Pipeline**: Full integration with existing asset organization
- **Quality**: 720p, 8-second videos with native audio
- **Cost Effective**: ~$0.10-0.30 per video, ~$3-9 for full trailer

### 🎯 Current Phase: Ready for Production
Active workflow:
1. **Set up API key** following `GEMINI_API_SETUP.md`
2. **Generate clips** using `tools/generate_veo3.py`
3. **Automatic organization** into `04_flow_exports/`
4. **Prompt tracking** in `02_prompts/ledger.jsonl`
5. **Flow assembly** and final production

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
├── 07_story_development/       # Complete story structure
│   ├── pilot_trailer_overview.md    # Master document
│   ├── act1_world_introduction.md   # Act I details (9 clips)
│   ├── act2_conflict_growth.md      # Act II details (10 clips)
│   ├── act3_revelation_hook.md      # Act III details (10 clips)
│   └── production_notes.md          # Visual/audio specifications
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
├── .env                       # Environment variables (configured)
├── .env.template              # Environment variables template
├── CLAUDE.md                  # Claude Code instructions
├── SETUP.md                   # Setup guide
└── README.md                  # This file
```

## 🎯 Key Commands

### Veo 3 Generation (Current)
```bash
# Generate a video clip
python3 tools/generate_veo3.py \
  "Epic fantasy title sequence: Sweeping aerial cinematography over alien world of Roshar..." \
  --scene title_sequence \
  --notes "First Stormlight video"

# Generate with reference image
python3 tools/generate_veo3.py \
  "Your prompt here" \
  --scene scene_name \
  --image path/to/reference.jpg

# Check generation status
python3 tools/web_workflow_helper.py status

# List all scenes
python3 tools/web_workflow_helper.py scenes
```

### Setup & Management
```bash
# Set up Gemini API key (one-time)
export GEMINI_API_KEY='your-api-key-here'

# Interactive mode
./launch.sh

# Monitor dashboard
python3 tools/pipeline_monitor.py --dashboard

# Sync to GCS
python3 tools/sync_to_gcs.py.py --local . --bucket stormlight-short
```

## 🎬 Story Structure: Stormlight: Into the Tempest

### Three-Act Pilot Trailer (3:13 runtime)

**Act I: World Introduction (60s, 9 clips)**
- Title sequence with alien Roshar landscape
- Character introductions: Kaladin, Adolin, Dalinar
- Magic system reveal: Stormlight and spren
- Highstorm approaching

**Act II: Conflict & Growth (67s, 10 clips)**  
- Bridge runs and deadly warfare
- Kaladin's emerging leadership
- Adolin's honor and dueling
- Dalinar's visions and internal conflict
- Sylphrena's appearance

**Act III: Revelation & Hook (66s, 10 clips)**
- Kaladin's first Surgebinding
- Syl reveals her true nature
- First Oath transformation
- Knights Radiant rising
- Series hook: "The Knights Radiant must stand again"

### Visual Style
- **Animation**: Attack on Titan meets Studio Ghibli
- **Color Palette**: Stormy blues, warm golds, alien purples
- **Dynamic Timing**: 3-8 second clips for natural pacing
- **Magic Focus**: Surgebinding and spren bonds (no Shardblades)

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

**Project Status**: ANIMATION READY - Story Development Complete
**Last Updated**: December 2024
**Version**: 2.0.0