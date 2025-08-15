#!/usr/bin/env python3
"""
Test script for LLM integration in Stormlight pipeline
Tests all the new OpenAI-powered features
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from llm_generator import LLMGenerator
    from prompt_enhancer import PromptEnhancer
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("❌ LLM modules not available. Please ensure OpenAI is installed:")
    print("   pip install openai")
    sys.exit(1)

console = Console()

def test_llm_generator():
    """Test basic LLM generator functionality"""
    console.print(Panel.fit("🧪 Testing LLM Generator", style="bold cyan"))
    
    try:
        generator = LLMGenerator()
        console.print("✅ LLM Generator initialized successfully", style="green")
        
        # Test basic generation
        test_prompt = "Kaladin standing on cliff during storm"
        console.print(f"\n📝 Test prompt: {test_prompt}")
        
        response = generator.generate(
            prompt=f"Enhance this scene description for cinematic impact: {test_prompt}",
            system_prompt="You are a cinematic prompt specialist. Enhance the given description with visual details.",
            max_tokens=100,
            temperature=0.7
        )
        
        console.print(f"✨ Enhanced: {response['content'][:200]}...")
        console.print(f"💰 Cost: ${response['cost']:.6f}")
        console.print(f"📊 Tokens: {response['total_tokens']}")
        
        return True
        
    except Exception as e:
        console.print(f"❌ LLM Generator test failed: {e}", style="red")
        return False

def test_prompt_enhancer():
    """Test prompt enhancer for Midjourney and Veo"""
    console.print(Panel.fit("🎨 Testing Prompt Enhancer", style="bold cyan"))
    
    try:
        enhancer = PromptEnhancer()
        console.print("✅ Prompt Enhancer initialized successfully", style="green")
        
        # Test Midjourney enhancement
        console.print("\n📸 Testing Midjourney enhancement...")
        midjourney_result = enhancer.enhance_midjourney_prompt(
            "Kaladin on cliff edge",
            "kaladin_intro",
            frame_type="start",
            use_llm=True
        )
        
        console.print(f"Start frame prompt: {midjourney_result.get('simple', '')[:100]}...")
        
        # Test Veo enhancement
        console.print("\n🎬 Testing Veo 3 enhancement...")
        veo_result = enhancer.enhance_veo_prompt(
            "Bridge crew running across chasm",
            "bridge_run",
            camera_movement="tracking shot",
            mood="desperate",
            use_llm=True
        )
        
        console.print(f"Video prompt: {veo_result.get('prompt', '')[:100]}...")
        
        # Show total cost
        if enhancer.llm:
            stats = enhancer.llm.get_usage_stats()
            console.print(f"\n💰 Total cost: ${stats['total_cost']:.4f}")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Prompt Enhancer test failed: {e}", style="red")
        return False

def test_styleframe_integration():
    """Test styleframe manager integration"""
    console.print(Panel.fit("🖼️ Testing Styleframe Manager Integration", style="bold cyan"))
    
    try:
        from styleframe_manager import StyleframeManager
        
        manager = StyleframeManager()
        console.print("✅ StyleframeManager initialized", style="green")
        
        # Test prompt generation with LLM
        console.print("\n🎨 Generating enhanced Midjourney prompts...")
        prompts = manager.generate_midjourney_prompts(
            "kaladin_intro",
            "Kaladin standing defiantly",
            use_llm=True,
            num_variations=2
        )
        
        if "start_frame" in prompts:
            console.print(f"✅ Start frame: {prompts['start_frame'][:80]}...")
        
        if "variations" in prompts and prompts["variations"]:
            console.print(f"✅ Generated {len(prompts['variations'])} variations")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Styleframe integration test failed: {e}", style="red")
        return False

def test_veo_integration():
    """Test Veo 3 generator integration"""
    console.print(Panel.fit("🎬 Testing Veo 3 Integration", style="bold cyan"))
    
    try:
        from generate_veo3 import Veo3Generator
        
        generator = Veo3Generator()
        console.print("✅ Veo3Generator initialized", style="green")
        
        # Note: We won't actually generate a video (costs money)
        # Just test that the enhancement works
        
        if generator.prompt_enhancer:
            console.print("✅ Prompt enhancer available in Veo3Generator")
            
            # Test enhancement without actual generation
            enhanced = generator.prompt_enhancer.enhance_veo_prompt(
                "Test scene with action",
                "test_scene",
                camera_movement="tracking shot",
                mood="intense",
                use_llm=True
            )
            
            console.print(f"✅ Video prompt enhanced: {enhanced.get('prompt', '')[:80]}...")
        else:
            console.print("⚠️  Prompt enhancer not available in Veo3Generator")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Veo integration test failed: {e}", style="red")
        return False

def check_api_key():
    """Check if OpenAI API key is configured"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        console.print("\n❌ OPENAI_API_KEY not found in environment", style="red")
        console.print("\n📝 To set up your API key:")
        console.print("1. Create or edit .env file in project root")
        console.print("2. Add: OPENAI_API_KEY=your_key_here")
        console.print("3. Never commit the .env file to git")
        return False
    
    # Check if it looks valid (basic check)
    if not api_key.startswith('sk-'):
        console.print("⚠️  API key doesn't look like a valid OpenAI key", style="yellow")
        return False
    
    console.print("✅ OpenAI API key configured", style="green")
    return True

def main():
    """Run all integration tests"""
    console.print(Panel.fit(
        "🚀 [bold cyan]Stormlight LLM Integration Test Suite[/bold cyan]\n"
        "Testing OpenAI GPT-4-mini integration",
        style="bold"
    ))
    
    # Check API key first
    if not check_api_key():
        console.print("\n⚠️  Please configure your OpenAI API key first", style="yellow")
        return
    
    # Run tests
    tests = [
        ("LLM Generator", test_llm_generator),
        ("Prompt Enhancer", test_prompt_enhancer),
        ("Styleframe Integration", test_styleframe_integration),
        ("Veo 3 Integration", test_veo_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        console.print(f"\n{'='*60}")
        success = test_func()
        results[test_name] = success
        
    # Summary
    console.print(f"\n{'='*60}")
    console.print(Panel.fit("📊 Test Results Summary", style="bold"))
    
    all_passed = True
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        style = "green" if success else "red"
        console.print(f"{test_name}: {status}", style=style)
        if not success:
            all_passed = False
    
    if all_passed:
        console.print("\n🎉 All tests passed! LLM integration is working.", style="bold green")
        console.print("\n📚 Example commands to try:")
        console.print("  # Enhanced Midjourney prompts with variations")
        console.print("  python3 tools/styleframe_manager.py prompts kaladin_intro \"Kaladin on cliff\" --llm-enhance --variations 5")
        console.print("\n  # Enhanced Veo 3 video generation")
        console.print("  python3 tools/generate_veo3.py \"Bridge crew running\" --scene bridge_run --llm-prompt --mood desperate")
    else:
        console.print("\n⚠️  Some tests failed. Please check the errors above.", style="yellow")

if __name__ == "__main__":
    main()