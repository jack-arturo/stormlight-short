# Story Development - Stormlight: Into the Tempest Animated Pilot

This directory contains all story development materials for the 4-minute animated pilot trailer.

## 📁 Directory Structure

```
07_story_development/
├── README.md                    # This file - overview and guidelines
├── pilot_trailer_overview.md    # Complete trailer outline and vision
├── act1_world_introduction.md   # Act I: World & Characters (0:00-1:20)
├── act2_conflict_growth.md      # Act II: Conflict & Growth (1:20-2:40)  
├── act3_revelation_hook.md      # Act III: Revelation & Hook (2:40-4:00)
├── production_notes.md          # Visual style, pacing, technical specs
└── clips/                       # Individual clip breakdowns
    ├── clip_01_title_sequence.md
    ├── clip_02_shattered_plains.md
    └── ... (30 total clip files)
```

## 🎬 Project Overview

**Format**: 4-minute animated pilot trailer for Stormlight: Into the Tempest TV series
**Technical Constraint**: 8-second maximum clips (30 total clips)
**Target**: Generate interest in full TV series production
**Style**: Anime-inspired animation (Attack on Titan/Demon Slayer aesthetic)

## 🔄 Version Control Strategy

- **Modular Files**: Each act and clip in separate files for focused editing
- **Iterative Development**: Easy to refine individual segments without affecting others
- **LLM Collaboration**: Structured for AI-assisted development and refinement
- **Git Tracking**: Clear commit history for each story element

## 🛠 Usage Guidelines

1. **Start with Overview**: Read `pilot_trailer_overview.md` for complete vision
2. **Develop by Act**: Work through acts sequentially for narrative flow
3. **Refine Individual Clips**: Use clip files for detailed prompt development
4. **Reference Production Notes**: Maintain visual/technical consistency

## 🎯 Integration with Pipeline

These story files directly feed into:
- `02_prompts/` - Vertex AI generation prompts
- `01_styleframes_midjourney/` - Visual reference creation
- `03_vertex_jobs/` - Video generation jobs
- `04_flow_exports/` - Final assembly

## 📝 File Naming Convention

- **Acts**: `act{number}_{description}.md`
- **Clips**: `clip_{number:02d}_{description}.md`
- **Support**: `{purpose}_{description}.md`

---

*This structure optimizes for LLM collaboration, version control, and integration with the existing Stormlight Short pipeline.*
