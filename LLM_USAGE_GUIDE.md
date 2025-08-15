# 🤖 LLM Integration Usage Guide

## Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Add your OpenAI API key to .env file
echo "OPENAI_API_KEY=your_key_here" >> .env

# Test the integration
python3 tools/test_llm_integration.py
```

## Enhanced Commands

### 🎨 Midjourney Prompt Enhancement

Generate cinematic prompts with AI-powered variations:

```bash
# Basic enhancement
python3 tools/styleframe_manager.py prompts kaladin_intro "Kaladin on cliff" --llm-enhance

# With multiple variations (different moods)
python3 tools/styleframe_manager.py prompts kaladin_intro "Kaladin on cliff" --llm-enhance --variations 5

# Save to files
python3 tools/styleframe_manager.py prompts bridge_run "Bridge crew charging" --llm-enhance --save
```

### 🎬 Veo 3 Video Generation Enhancement

Create professional video prompts with camera movements and mood:

```bash
# Basic LLM enhancement
python3 tools/generate_veo3.py "Kaladin stands defiantly" --scene kaladin_intro --llm-prompt

# With specific camera movement
python3 tools/generate_veo3.py "Bridge crew running" --scene bridge_run --llm-prompt --camera "tracking shot"

# With mood specification
python3 tools/generate_veo3.py "Storm approaching" --scene highstorm --llm-prompt --mood "ominous"

# Full cinematic treatment
python3 tools/generate_veo3.py "Epic battle sequence" --scene battle \
  --llm-prompt \
  --camera "sweeping aerial shot" \
  --mood "desperate heroism"
```

## Features

### 🎯 Automatic Enhancements
- **Cinematic Language**: Adds professional cinematography terms
- **Visual Details**: Enhances with lighting, atmosphere, composition
- **Style Consistency**: Maintains Arcane animation style throughout
- **Scene Awareness**: Adapts to scene type (action, emotional, landscape)

### 💰 Cost Tracking
- **Real-time Cost Display**: Shows cost after each generation
- **Ledger Tracking**: All costs saved to `02_prompts/llm_ledger.jsonl`
- **Typical Costs**:
  - Prompt enhancement: ~$0.01-0.02
  - Scene variations (5): ~$0.05
  - Full workflow: ~$0.10

### 🔄 Variations Generator
Generate multiple creative variations:
```bash
# Generate 5 mood variations
python3 tools/styleframe_manager.py prompts kaladin_intro "Base scene" --llm-enhance --variations 5

# Variations are automatically:
# - Different moods (heroic, desperate, mystical, etc.)
# - Consistent core subject
# - Professionally formatted
```

### 📊 Cost Monitoring
```bash
# Check generation history and costs
cat 02_prompts/llm_ledger.jsonl | tail -10

# Pretty print with jq (if installed)
cat 02_prompts/llm_ledger.jsonl | jq '.'
```

## Example Workflows

### Complete Styleframe Generation
```bash
# 1. Generate enhanced prompts with variations
python3 tools/styleframe_manager.py prompts kaladin_intro \
  "Kaladin standing on cliff as storm approaches" \
  --llm-enhance --variations 3 --save

# 2. Use prompts in Midjourney (copy from saved file)
cat 02_prompts/midjourney/kaladin_intro_prompts.txt

# 3. Generate video with enhanced prompt
python3 tools/generate_veo3.py \
  "Kaladin standing on cliff as storm approaches" \
  --scene kaladin_intro \
  --llm-prompt \
  --camera "slow push in" \
  --mood "heroic defiance"
```

### Batch Scene Processing
```bash
# Generate enhanced prompts for multiple scenes
for scene in kaladin_intro bridge_run highstorm; do
  python3 tools/styleframe_manager.py prompts $scene \
    "Scene description" --llm-enhance --save
done
```

## Advanced Options

### LLM Configuration
The system uses GPT-4-mini by default for cost efficiency. To modify:

```python
# In tools/llm_generator.py
generator = LLMGenerator(
    model="gpt-4o-mini",  # or "gpt-4o" for higher quality
    temperature=0.7,       # 0.0-1.0, higher = more creative
    max_retries=3          # Retry attempts on failure
)
```

### Caching
Responses are cached automatically to save costs:
- Cache location: `.llm_cache/`
- Clear cache: `rm -rf .llm_cache/`
- Disable caching: Set `cache_enabled=False` in LLMGenerator

## Troubleshooting

### API Key Issues
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Verify in .env file
cat .env | grep OPENAI_API_KEY

# Test connection
python3 -c "from openai import OpenAI; client = OpenAI(); print('✅ Connected')"
```

### Cost Management
- Use `--variations 3` instead of higher numbers
- Enable caching (default)
- Use GPT-4-mini (default) instead of GPT-4
- Reuse prompts when possible

### Performance
- First call may be slower (API warmup)
- Cached responses return instantly
- Batch operations for efficiency

## Integration with Control Center

The LLM features integrate seamlessly with the Stormlight Control Center:

```bash
# Launch control center
python3 tools/stormlight_control.py

# Use 'S' for styleframe generation (now with LLM option)
# Use 'V' for video generation (now with LLM enhancement)
```

---

**💡 Pro Tips:**
- Always test prompts with `--llm-enhance` first before generating expensive videos
- Save enhanced prompts with `--save` for reuse
- Monitor costs in real-time during generation
- Use mood and camera parameters for cinematic control