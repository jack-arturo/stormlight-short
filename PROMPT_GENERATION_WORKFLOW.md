# 🎬 Prompt Generation Workflow

## Overview
We're ready to convert our story beats into Vertex AI prompts for video generation.

## ✅ What's Ready
1. **Act 1 Template**: `02_prompts/act1_clips_template.yaml` (9 clips, 60 seconds)
2. **Prompt Generator**: `tools/prompt_generator.py` - Converts templates to batch jobs
3. **Vertex Manager**: Ready to submit jobs to Veo 3

## 🎯 Next Steps

### 1. Create Templates for Acts 2 & 3
We need to create similar YAML templates for:
- Act 2: 10 clips, 67 seconds
- Act 3: 10 clips, 66 seconds

### 2. Test Individual Clips
Before running full batches:
```bash
# Test single clip (dry run)
python3 tools/vertex_manager.py \
  --project-id stormlight-short \
  --scene "test_clip_01" \
  --prompt "Your test prompt..." \
  --duration 6 \
  --dry-run

# Test single clip (real - costs money!)
# Remove --dry-run when ready
```

### 3. Submit Act 1 Batch
```bash
# Preview prompts
python3 tools/prompt_generator.py \
  --template 02_prompts/act1_clips_template.yaml \
  --preview

# Generate batch file
python3 tools/prompt_generator.py \
  --template 02_prompts/act1_clips_template.yaml \
  --batch

# Submit batch (dry run first!)
python3 tools/vertex_manager.py \
  --batch-config 02_prompts/act1_world_introduction_batch_[timestamp].json \
  --project-id stormlight-short \
  --dry-run

# Monitor progress
python3 tools/pipeline_monitor.py --dashboard
```

## 📊 Cost Breakdown
- Act 1: 60 seconds × $0.0375 = $2.25
- Act 2: 67 seconds × $0.0375 = $2.51  
- Act 3: 66 seconds × $0.0375 = $2.48
- **Total First Pass**: $7.24

## 🎨 Prompt Tips
1. **Be Specific**: Include camera movements, lighting, mood
2. **Avoid Banned Content**: No violence, gore, explicit content
3. **Consistent Style**: Maintain "Attack on Titan meets Studio Ghibli"
4. **Character Consistency**: Describe characters the same way each time
5. **World Building**: Emphasize alien/otherworldly elements

## 📝 Example Enhanced Prompt Structure
```
[Main action/subject], [character description], [environment details], 
[lighting/mood], [camera movement], [style notes]
```

## ⚠️ Important Reminders
- Always use **--dry-run** first
- Monitor costs in dashboard
- Save generated videos immediately
- Document any prompt adjustments
- Test clips individually before batch processing

## 🔄 Iteration Process
1. Generate first pass
2. Review results
3. Adjust prompts based on output
4. Re-generate specific clips as needed
5. Document successful prompts in ledger

---

Ready to start with Act 1? The template is complete and tested!
