# 🎬 Stormlight Video Generation - Command Reference

## 🚀 Quick Start

```bash
python3 tools/generate_veo3.py "Your video description" --scene scene_name
```

## 📖 Full Command Syntax

```bash
usage: generate_veo3.py [-h] [--scene SCENE] [--take TAKE] [--image IMAGE] [--notes NOTES] prompt

positional arguments:
  prompt                Video description prompt (required, use quotes)

options:
  -h, --help           Show help message
  --scene SCENE        Scene name/identifier (required)
  --take TAKE          Take number (optional, auto-increments if not specified)
  --image IMAGE        Reference image path (optional)
  --notes NOTES        Production notes (optional, use quotes)
```

## 🎯 Examples by Complexity

### Minimal (Required Only)
```bash
python3 tools/generate_veo3.py "Kaladin on stormy battlefield" --scene kaladin_intro
```

### With Take Number
```bash
python3 tools/generate_veo3.py "Bridge crew charging" --scene bridge_run --take 2
```

### With Reference Image
```bash
python3 tools/generate_veo3.py "Shattered Plains landscape" --scene plains_wide --image 01_styleframes_midjourney/plains.png
```

### With Production Notes
```bash
python3 tools/generate_veo3.py "Highstorm approaching" --scene storm_wall --notes "Make it more ominous and darker"
```

### Full Command (All Options)
```bash
python3 tools/generate_veo3.py "Epic battle sequence with spears and shields" \
  --scene bridge_battle \
  --take 3 \
  --image 01_styleframes_midjourney/battle-ref.jpg \
  --notes "Third attempt - focus on dynamic camera movement"
```

## 🎨 Scene Naming Best Practices

### Good Scene Names
- `kaladin_intro` - Character introduction
- `bridge_run_action` - Specific action sequence
- `highstorm_approach` - Environmental event
- `shattered_plains_wide` - Location establishing shot
- `spren_encounter` - Story moment

### Avoid
- `scene1` - Not descriptive
- `test video` - Spaces (use underscores)
- `really-long-scene-name-that-goes-on-forever` - Too long

## 📝 Prompt Writing Tips

### Effective Prompts
```bash
# Good: Specific, cinematic
"Low angle shot of Kaladin holding spear against stormy sky, dramatic lighting, wind-blown hair"

# Good: Action with camera work  
"Tracking shot following bridge crew running across wooden bridge, arrows flying overhead"

# Good: Environmental storytelling
"Wide establishing shot of the Shattered Plains at sunset, broken plateaus stretching to horizon"
```

### Less Effective
```bash
# Too vague
"Kaladin doing something"

# Too complex (multiple scenes)
"Kaladin fights then talks to Syl then looks at storm then runs away"
```

## 🔧 Other Useful Commands

### Check Status
```bash
python3 tools/pipeline_monitor.py                    # Quick status
python3 tools/pipeline_monitor.py --dashboard        # Live dashboard
python3 tools/pipeline_monitor.py --health-check     # System health
```

### File Management
```bash
ls 04_flow_exports/                                  # List generated videos
cat 02_prompts/ledger.jsonl                         # View generation log
```

## 🎬 Typical Workflow

```bash
# 1. Generate main scene
python3 tools/generate_veo3.py "Kaladin stands defiantly on cliff edge as storm approaches" --scene kaladin_intro

# 2. Generate alternate take if needed
python3 tools/generate_veo3.py "Kaladin stands defiantly on cliff edge as storm approaches" --scene kaladin_intro --take 2 --notes "More dramatic pose"

# 3. Check results
python3 tools/pipeline_monitor.py

# 4. Continue with next scene
python3 tools/generate_veo3.py "Bridge crew charges across chasm under arrow fire" --scene bridge_run
```

---

**💡 Remember**: The prompt is the most important part - be specific about camera angles, lighting, mood, and action!
