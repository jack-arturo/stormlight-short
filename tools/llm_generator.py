#!/usr/bin/env python3
"""
LLM Generator - Core OpenAI integration for prompt generation and enhancement
Handles all LLM operations with retry logic, cost tracking, and caching
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from functools import wraps
import hashlib

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not installed. Run: pip install openai")

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load .env file at module import
load_env_file()

class LLMGenerator:
    """Core LLM generator for prompt enhancement and creative generation"""
    
    # Pricing per 1M tokens (GPT-4-mini as of Dec 2024)
    PRICING = {
        "gpt-4o-mini": {
            "input": 0.15,   # $0.15 per 1M input tokens
            "output": 0.60   # $0.60 per 1M output tokens
        },
        "gpt-4o": {
            "input": 2.50,   # $2.50 per 1M input tokens
            "output": 10.00  # $10.00 per 1M output tokens
        }
    }
    
    def __init__(self, 
                 project_root: Path = None,
                 model: str = "gpt-4o-mini",
                 temperature: float = 0.7,
                 max_retries: int = 3,
                 cache_enabled: bool = True):
        """
        Initialize the LLM Generator
        
        Args:
            project_root: Project root directory
            model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
            temperature: Creativity level (0.0-1.0)
            max_retries: Maximum number of retry attempts
            cache_enabled: Whether to cache responses
        """
        self.project_root = project_root or Path.cwd()
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.cache_enabled = cache_enabled
        
        # Set up directories
        self.cache_dir = self.project_root / ".llm_cache"
        self.ledger_file = self.project_root / "02_prompts" / "llm_ledger.jsonl"
        
        if self.cache_enabled:
            self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize OpenAI client
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            console.print("❌ Error: OPENAI_API_KEY not set in environment", style="red")
            console.print("Add to .env file: OPENAI_API_KEY=your_key_here", style="yellow")
            raise ValueError("OpenAI API key not configured")
        
        if OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=self.api_key)
        else:
            raise ImportError("OpenAI library not installed")
        
        # Cost tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
    
    def retry_on_failure(func):
        """Decorator for automatic retry with exponential backoff"""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_retries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_exception = e
                    wait_time = 2 ** attempt  # Exponential backoff
                    
                    if attempt < self.max_retries - 1:
                        console.print(f"⚠️  Attempt {attempt + 1} failed: {e}", style="yellow")
                        console.print(f"⏳ Retrying in {wait_time} seconds...", style="dim")
                        time.sleep(wait_time)
                    else:
                        console.print(f"❌ All {self.max_retries} attempts failed", style="red")
                        raise last_exception
            
            return None
        return wrapper
    
    def _get_cache_key(self, prompt: str, **kwargs) -> str:
        """Generate a cache key from prompt and parameters"""
        cache_data = {
            "prompt": prompt,
            "model": self.model,
            "temperature": self.temperature,
            **kwargs
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Load a cached response if available"""
        if not self.cache_enabled:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None
    
    def _save_to_cache(self, cache_key: str, response: Dict):
        """Save a response to cache"""
        if not self.cache_enabled:
            return
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w') as f:
            json.dump(response, f, indent=2)
    
    def _track_usage(self, input_tokens: int, output_tokens: int):
        """Track token usage and costs"""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        
        # Calculate cost
        pricing = self.PRICING.get(self.model, self.PRICING["gpt-4o-mini"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        self.total_cost += total_cost
        
        # Log to ledger
        ledger_entry = {
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "cumulative_cost": round(self.total_cost, 6)
        }
        
        with open(self.ledger_file, 'a') as f:
            f.write(json.dumps(ledger_entry) + '\n')
        
        return total_cost
    
    @retry_on_failure
    def generate(self, 
                 prompt: str,
                 system_prompt: str = None,
                 max_tokens: int = 500,
                 temperature: float = None,
                 use_cache: bool = True) -> Dict[str, Any]:
        """
        Generate a response from the LLM
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            max_tokens: Maximum response length
            temperature: Override default temperature
            use_cache: Whether to use cached responses
        
        Returns:
            Dict with response text, tokens used, and cost
        """
        temperature = temperature or self.temperature
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(prompt, system_prompt=system_prompt)
            cached = self._load_from_cache(cache_key)
            if cached:
                console.print("💾 Using cached response", style="dim")
                return cached
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Make API call
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Extract response data
        content = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        # Track usage
        cost = self._track_usage(input_tokens, output_tokens)
        
        # Prepare result
        result = {
            "content": content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost": round(cost, 6),
            "model": self.model,
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache the result
        if use_cache:
            self._save_to_cache(cache_key, result)
        
        return result
    
    def generate_variations(self,
                           base_prompt: str,
                           num_variations: int = 5,
                           variation_type: str = "creative") -> List[str]:
        """
        Generate multiple variations of a prompt
        
        Args:
            base_prompt: Original prompt to vary
            num_variations: Number of variations to generate
            variation_type: Type of variations (creative, technical, mood, camera)
        
        Returns:
            List of variation prompts
        """
        system_prompt = f"""You are a cinematic prompt specialist for AI animation generation.
        Generate {num_variations} {variation_type} variations of the given prompt.
        
        Guidelines:
        - Maintain the core subject and scene
        - Vary the {variation_type} aspects
        - Use professional cinematography language
        - Keep prompts concise and clear
        - Avoid text/writing in scenes
        
        Return only the variations as a numbered list."""
        
        user_prompt = f"Original prompt: {base_prompt}\n\nGenerate {num_variations} variations:"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task(f"Generating {num_variations} variations...", total=1)
            
            response = self.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=1000,
                temperature=0.8  # Higher creativity for variations
            )
            
            progress.update(task, completed=1)
        
        # Parse variations from response
        variations = []
        for line in response["content"].split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering/bullets
                clean_line = line.lstrip('0123456789.-) ').strip()
                if clean_line:
                    variations.append(clean_line)
        
        return variations[:num_variations]
    
    def enhance_prompt(self,
                      base_prompt: str,
                      style: str = "arcane",
                      scene_type: str = None,
                      mood: str = None,
                      camera_work: bool = True) -> str:
        """
        Enhance a basic prompt with cinematic details
        
        Args:
            base_prompt: Original prompt
            style: Visual style (arcane, realistic, painterly)
            scene_type: Type of scene (action, emotional, landscape)
            mood: Desired mood
            camera_work: Include camera movement suggestions
        
        Returns:
            Enhanced cinematic prompt
        """
        system_prompt = f"""You are a cinematic prompt specialist for Arcane-style animation.
        Enhance prompts with rich visual details while maintaining clarity.
        
        Style: {style}
        Scene Type: {scene_type or 'general'}
        Mood: {mood or 'dramatic'}
        Include Camera Work: {camera_work}
        
        Guidelines:
        - Add specific visual details (lighting, atmosphere, composition)
        - Use professional cinematography terms
        - Maintain original subject and action
        - Keep under 100 words
        - Avoid text/writing in scenes
        - Focus on visual storytelling"""
        
        user_prompt = f"Enhance this prompt: {base_prompt}"
        
        response = self.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=200,
            temperature=0.6  # Balanced creativity
        )
        
        return response["content"].strip()
    
    def analyze_continuity(self,
                          previous_prompt: str,
                          next_prompt: str,
                          suggest_transition: bool = True) -> Dict[str, Any]:
        """
        Analyze continuity between two scenes and suggest transitions
        
        Args:
            previous_prompt: Previous scene prompt
            next_prompt: Next scene prompt
            suggest_transition: Generate transition suggestions
        
        Returns:
            Analysis with continuity notes and suggestions
        """
        system_prompt = """You are a continuity specialist for animation production.
        Analyze scene transitions for visual and narrative continuity.
        
        Provide:
        1. Visual continuity issues (lighting, color, style)
        2. Narrative flow assessment
        3. Suggested adjustments
        4. Transition recommendations (if requested)"""
        
        user_prompt = f"""Previous scene: {previous_prompt}
        Next scene: {next_prompt}
        
        Analyze continuity and suggest improvements."""
        
        response = self.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=500,
            temperature=0.5
        )
        
        return {
            "analysis": response["content"],
            "previous": previous_prompt,
            "next": next_prompt,
            "cost": response["cost"]
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": round(self.total_cost, 4),
            "model": self.model,
            "average_cost_per_request": round(
                self.total_cost / max(1, self.total_input_tokens // 100),
                6
            )
        }
    
    def clear_cache(self):
        """Clear the response cache"""
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            console.print("🧹 Cache cleared", style="green")


def main():
    """Test the LLM generator with sample prompts"""
    generator = LLMGenerator()
    
    # Test basic generation
    console.print(Panel.fit("🧪 Testing LLM Generator", style="bold cyan"))
    
    # Test prompt enhancement
    test_prompt = "Kaladin standing on cliff during storm"
    console.print(f"\n📝 Original: {test_prompt}")
    
    enhanced = generator.enhance_prompt(
        test_prompt,
        style="arcane",
        scene_type="heroic",
        mood="defiant"
    )
    console.print(f"✨ Enhanced: {enhanced}")
    
    # Test variations
    console.print("\n🎨 Generating variations...")
    variations = generator.generate_variations(test_prompt, num_variations=3)
    for i, var in enumerate(variations, 1):
        console.print(f"  {i}. {var}")
    
    # Show usage stats
    stats = generator.get_usage_stats()
    console.print(f"\n💰 Total cost: ${stats['total_cost']:.4f}")
    console.print(f"📊 Tokens used: {stats['total_tokens']:,}")


if __name__ == "__main__":
    main()