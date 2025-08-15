# 🎬 Vertex AI Media Studio Workflow - Stormlight: Into the Tempest

## Overview
This document describes the clean, web-interface-first workflow for generating Veo 3 video clips while awaiting API opt-in approval. This approach uses Vertex AI's Media Studio for high-quality generation with manual download and integration into our project structure.

## 🎯 Current Veo 3 Status
- **Available Model**: `veo-3.0-generate-preview`
- **Quality**: High (720p maximum in preview)
- **Duration**: 8 seconds maximum
- **Access**: Via Vertex AI Media Studio web interface
- **API Status**: Requires opt-in approval (pending)

---

## 📋 Step-by-Step Workflow

### 1. Access Vertex AI Media Studio
1. Navigate to: https://console.cloud.google.com/vertex-ai/generative/multimodal/create/video
2. Ensure you're in the `stormlight-short` project
3. Select **Veo 3.0 Generate Preview** model
4. Set quality to **High** and resolution to **720p**

### 2. Generate Video Clips

#### Prompt Preparation
Use clean, cinematic prompts without MidJourney parameters:

**Example - Title Sequence:**
```
Epic fantasy title sequence: Sweeping aerial cinematography over the alien world of Roshar. Strange crystalline rock formations jutting from barren ground, no grass only glowing alien moss and crystal plants. Stormy dark clouds gathering overhead with supernatural blue-violet lightning. Otherworldly atmosphere, epic fantasy film opening sequence.
```

**Key Prompt Guidelines:**
- Focus on cinematic language
- Describe camera movements and lighting
- Emphasize the alien, otherworldly nature of Roshar
- Avoid technical parameters (--ar, --v, etc.)
- Keep under 500 characters for best results

#### Generation Settings
- **Model**: veo-3.0-generate-preview
- **Quality**: High
- **Resolution**: 720p
- **Duration**: 6-8 seconds (maximum available)
- **Aspect Ratio**: 16:9 (widescreen)

### 3. Download and Organize

#### File Naming Convention
Download files using this naming pattern:
```
<scene_name>_take<##>_<YYYYMMDD_HHMMSS>.mp4
```

**Examples:**
- `title_sequence_take01_20250815_143022.mp4`
- `kaladin_intro_take01_20250815_143156.mp4`
- `bridge_run_take02_20250815_144312.mp4`

#### Directory Structure
Save downloaded files to:
```
stormlight_short/04_flow_exports/
├── title_sequence_take01_20250815_143022.mp4
├── kaladin_intro_take01_20250815_143156.mp4
├── bridge_run_take02_20250815_144312.mp4
└── ...
```

### 4. Prompt Logging

After each generation, append metadata to the prompt ledger:

**File**: `stormlight_short/02_prompts/ledger.jsonl`

**Format** (one JSON object per line):
```json
{"timestamp": "2025-08-15T14:30:22", "scene": "title_sequence", "take": 1, "prompt": "Epic fantasy title sequence: Sweeping aerial cinematography...", "duration": 8, "resolution": "720p", "model": "veo-3.0-generate-preview", "quality": "high", "filename": "title_sequence_take01_20250815_143022.mp4", "notes": "Good alien landscape, could use more spren"}
```

**Required Fields:**
- `timestamp`: ISO 8601 format
- `scene`: Scene identifier
- `take`: Take number
- `prompt`: Full prompt text used
- `duration`: Video duration in seconds
- `resolution`: Video resolution
- `model`: Veo model version
- `quality`: Quality setting
- `filename`: Downloaded filename
- `notes`: Optional generation notes

### 5. Version Control Integration

After downloading and logging each clip:

```bash
# Add new files to git
git add 04_flow_exports/<new_file>.mp4
git add 02_prompts/ledger.jsonl

# Commit with descriptive message
git commit -m "feat: Add <scene_name> take <##> - <brief_description>"

# Example:
git commit -m "feat: Add title_sequence take01 - Alien Roshar landscape with crystalline formations"
```

---

## 🎨 Scene Priority List

Generate clips in this order for maximum impact:

### Phase 1: Core Scenes (Week 1)
1. **Title Sequence** - Establish the alien world
2. **Kaladin Introduction** - Our main character
3. **The Shattered Plains** - Central location
4. **Bridge Run Action** - Key action sequence
5. **Highstorm Approach** - Environmental spectacle

### Phase 2: Character Development (Week 2)
6. **Adolin Introduction** - Noble warrior prince
7. **Dalinar's Command** - Military leader
8. **Spren Encounter** - Magic system introduction
9. **Kaladin's Leadership** - Character growth
10. **Parshendi Warriors** - The alien enemy

### Phase 3: Magic and Climax (Week 3)
11. **First Surgebinding** - Unconscious magic
12. **Syl's True Form** - Spren revelation
13. **The First Oath** - Transformation sequence
14. **Knights Radiant Rising** - Epic finale
15. **Series Hook** - Promise of more

---

## 📊 Quality Control Checklist

For each generated clip, verify:

- [ ] **Duration**: 6-8 seconds (optimal for editing)
- [ ] **Resolution**: 720p minimum
- [ ] **Aspect Ratio**: 16:9 widescreen
- [ ] **Content Quality**: Matches prompt description
- [ ] **Visual Consistency**: Fits established art style
- [ ] **File Size**: Reasonable for project storage
- [ ] **Audio**: Check if audio is present/needed

### Regeneration Criteria
Regenerate a clip if:
- Visual quality is poor or blurry
- Content doesn't match the prompt
- Duration is too short (< 5 seconds)
- Aspect ratio is incorrect
- Contains unwanted modern elements

---

## 🔄 Integration with Existing Pipeline

### Flow Assembly
Once clips are downloaded:
1. Import MP4 files into Flow
2. Arrange according to story structure in `07_story_development/`
3. Apply transitions and timing adjustments
4. Export for audio integration

### Audio Integration
1. Use clips as video base in audio editing software
2. Add orchestral score and sound effects
3. Sync with visual beats and transitions
4. Export final trailer

### Final Output
Target specifications:
- **Duration**: 3:13 (191 seconds total)
- **Resolution**: 1080p (upscaled from 720p clips)
- **Frame Rate**: 24fps
- **Audio**: Stereo, 48kHz
- **Format**: MP4 (H.264)

---

## 🚀 Transition to API Workflow

When API opt-in is approved:

1. **Keep existing clips** - They're already high quality
2. **Update tools** - Modify `tools/vertex_manager.py` for API calls
3. **Batch processing** - Generate remaining clips via API
4. **Cost optimization** - Use API for iterations and variations

The manual workflow ensures we maintain momentum while building a library of high-quality clips that will integrate seamlessly with the automated pipeline.

---

## 📝 Notes and Tips

### Prompt Optimization
- **Specific is better**: "crystalline rock formations" vs "rocks"
- **Camera language**: Use cinematic terms (aerial, close-up, tracking shot)
- **Lighting**: Specify mood lighting (dramatic, ethereal, storm lighting)
- **Movement**: Describe camera and subject movement

### Common Issues
- **Blurry results**: Try shorter, more focused prompts
- **Wrong aspect ratio**: Explicitly mention "cinematic widescreen 16:9"
- **Modern elements**: Add negative prompts if available
- **Short duration**: Request "8-second sequence" in prompt

### Storage Management
- Each 720p 8-second clip ≈ 15-25MB
- Budget ~500MB for complete 29-clip library
- Use git LFS if files become too large for standard git

---

*This workflow ensures high-quality video generation while maintaining project organization and preparing for seamless API integration when available.*
