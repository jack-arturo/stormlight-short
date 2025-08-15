# 🔑 Gemini API Setup for Veo 3 Video Generation

## Quick Setup (2 minutes)

### 1. Get Your Gemini API Key
1. Go to: **https://aistudio.google.com/app/apikey**
2. Click **"Create API Key"**
3. Select your `stormlight-short` project (or any project with billing enabled)
4. Copy the generated API key

### 2. Set Environment Variable
```bash
# Add to your shell profile (~/.zshrc or ~/.bash_profile)
export GEMINI_API_KEY='your-api-key-here'

# Or set for current session
export GEMINI_API_KEY='your-api-key-here'
```

### 3. Test the Setup
```bash
# Test with a simple generation
python3 tools/generate_veo3.py "A windswept cliffside fortress at sunset, banners whipping in the storm, cinematic lighting" --scene test_fortress

# Check status
python3 tools/web_workflow_helper.py status
```

## 🎬 Generate Your First Stormlight Video

Once set up, generate the title sequence:

```bash
python3 tools/generate_veo3.py \
  "Epic fantasy title sequence: Sweeping aerial cinematography over the alien world of Roshar. Strange crystalline rock formations jutting from barren ground, no grass only glowing alien moss and crystal plants. Stormy dark clouds gathering overhead with supernatural blue-violet lightning. Otherworldly atmosphere, epic fantasy film opening sequence." \
  --scene title_sequence \
  --notes "First Stormlight video using Gemini API"
```

## 🎯 Available Commands

```bash
# Basic generation
python3 tools/generate_veo3.py "Your prompt here" --scene scene_name

# With reference image
python3 tools/generate_veo3.py "Your prompt here" --scene scene_name --image path/to/reference.jpg

# Specific take number
python3 tools/generate_veo3.py "Your prompt here" --scene scene_name --take 2

# With notes
python3 tools/generate_veo3.py "Your prompt here" --scene scene_name --notes "Special notes about this generation"
```

## 📊 What You Get

- **Quality**: 720p, 8-second videos with native audio
- **Speed**: ~2-5 minutes generation time
- **Organization**: Automatically saved to `04_flow_exports/`
- **Tracking**: All prompts logged to `02_prompts/ledger.jsonl`
- **Integration**: Ready for Flow assembly and audio work

## 🚀 Priority Scenes to Generate

1. **title_sequence** - Establish the alien world
2. **kaladin_intro** - Main character introduction  
3. **shattered_plains** - Central location
4. **bridge_run** - Key action sequence
5. **highstorm** - Environmental spectacle

## 💰 Cost Estimates

- **Per video**: ~$0.10-0.30 (8 seconds, 720p)
- **Full trailer**: ~$3-9 for 29 clips
- **Much cheaper** than expected!

---

**Ready to generate? Set your API key and start creating!** ⚡🌪️
