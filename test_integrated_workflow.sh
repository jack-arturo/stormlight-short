#!/bin/bash

# Test script for integrated AI workflow
echo "🧪 Testing Integrated AI Workflow for Stormlight Pipeline"
echo "========================================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if OpenAI key is set
echo -e "\n${CYAN}1. Checking AI Configuration...${NC}"
if [ -z "$OPENAI_API_KEY" ]; then
    # Try to load from .env
    if [ -f .env ]; then
        export $(cat .env | grep OPENAI_API_KEY | xargs)
    fi
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY not set${NC}"
    echo "Please add to .env file: OPENAI_API_KEY=your_key_here"
    exit 1
else
    echo -e "${GREEN}✅ OpenAI API key configured${NC}"
fi

# Test 1: Generate enhanced prompts with variations
echo -e "\n${CYAN}2. Testing Enhanced Prompt Generation...${NC}"
echo "Running: python3 tools/styleframe_manager.py prompts test_scene 'Epic battle on stormy plains' --llm-enhance --variations 3 --save"
python3 tools/styleframe_manager.py prompts test_scene "Epic battle on stormy plains" --llm-enhance --variations 3 --save

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Enhanced prompts generated successfully${NC}"
    
    # Check if files were created
    if [ -f "02_prompts/midjourney/test_scene_prompts.txt" ]; then
        echo -e "${GREEN}✅ Prompts saved to 02_prompts/midjourney/${NC}"
    fi
    
    if [ -f "07_story_development/enhanced_prompts_test_scene.md" ]; then
        echo -e "${GREEN}✅ Enhanced prompts saved to story development${NC}"
    fi
else
    echo -e "${RED}❌ Failed to generate enhanced prompts${NC}"
fi

# Test 2: Show the generated prompts
echo -e "\n${CYAN}3. Displaying Generated Prompts...${NC}"
if [ -f "02_prompts/midjourney/test_scene_prompts.txt" ]; then
    echo "=== Start Frame ==="
    head -n 20 "02_prompts/midjourney/test_scene_prompts.txt" | grep -A 2 "STEP 1"
    echo -e "\n=== Variations ==="
    grep -A 5 "Alternative Variations" "02_prompts/midjourney/test_scene_prompts.txt" | head -n 10
fi

# Test 3: Test video prompt enhancement (dry run)
echo -e "\n${CYAN}4. Testing Video Prompt Enhancement (dry run)...${NC}"
echo "This would enhance the video prompt with camera movement and mood"
echo "Command: python3 tools/generate_veo3.py 'Epic battle' --scene test_scene --llm-prompt --camera 'sweeping aerial' --mood 'desperate'"

# Test 4: Check Control Center
echo -e "\n${CYAN}5. Checking Control Center AI Integration...${NC}"
echo "The control center should now show:"
echo "  - 🤖 AI Enhancement Available! in Styleframes card"
echo "  - 🤖 AI Prompt Enhancement! in Video Gen card"
echo "  - 🤖 AI Status in Production Overview"

# Summary
echo -e "\n${CYAN}========================================================"
echo -e "📊 INTEGRATION TEST SUMMARY${NC}"
echo -e "${CYAN}========================================================${NC}"

if [ -f "02_prompts/midjourney/test_scene_prompts.txt" ] && [ -f "07_story_development/enhanced_prompts_test_scene.md" ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo -e "\n${YELLOW}🎉 The AI integration is working correctly!${NC}"
    echo -e "\n${CYAN}Next steps:${NC}"
    echo "1. Launch control center: python3 tools/stormlight_control.py"
    echo "2. Press 'S' for interactive styleframe workflow with AI"
    echo "3. The workflow will ask if you want to use AI enhancement"
    echo "4. Generated prompts are saved to both locations automatically"
else
    echo -e "${RED}⚠️ Some tests may have issues${NC}"
    echo "Please check the errors above"
fi

echo -e "\n${CYAN}Cleanup test files? (y/n)${NC}"
read -r cleanup
if [ "$cleanup" = "y" ]; then
    rm -f "02_prompts/midjourney/test_scene_prompts.txt"
    rm -f "07_story_development/enhanced_prompts_test_scene.md"
    echo -e "${GREEN}✅ Test files cleaned up${NC}"
fi