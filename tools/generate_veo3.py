#!/usr/bin/env python3
"""
WORKING Gemini API Veo 3 Video Generation for Stormlight Archives
Uses the correct REST API format with instances array
"""

import os
import time
import json
import sys
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import argparse
import base64
import re

try:
    from prompt_enhancer import PromptEnhancer
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️  LLM enhancement not available. Install with: pip install openai")

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

class ScriptParser:
    """Parse story development scripts to extract clip information"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.story_dir = project_root / "07_story_development"
        self.ledger_file = project_root / "02_prompts" / "ledger.jsonl"
    
    def get_all_clips(self) -> List[Dict[str, Any]]:
        """Extract all clips from all story development files"""
        clips = []
        
        if not self.story_dir.exists():
            return clips
        
        # Process all act files in order
        act_files = sorted([f for f in self.story_dir.glob("act*.md")])
        
        for act_file in act_files:
            act_clips = self._parse_act_file(act_file)
            clips.extend(act_clips)
        
        return clips
    
    def _parse_act_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse a single act file to extract clip information"""
        clips = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all clip sections using regex
            clip_pattern = r'### Clip (\d+): ([^(]+)\(([^)]+)\)'
            clip_matches = re.finditer(clip_pattern, content)
            
            for match in clip_matches:
                clip_num = int(match.group(1))
                clip_title = match.group(2).strip()
                timing = match.group(3).strip()
                
                # Extract the full clip section
                start_pos = match.start()
                
                # Find the next clip or end of file
                next_match = None
                for next_clip in re.finditer(clip_pattern, content[start_pos + 1:]):
                    next_match = next_clip
                    break
                
                if next_match:
                    end_pos = start_pos + 1 + next_match.start()
                    clip_content = content[start_pos:end_pos]
                else:
                    # Find next major section (##) or end of file
                    next_section = re.search(r'\n## ', content[start_pos + 1:])
                    if next_section:
                        end_pos = start_pos + 1 + next_section.start()
                        clip_content = content[start_pos:end_pos]
                    else:
                        clip_content = content[start_pos:]
                
                # Extract prompts and details
                clip_data = self._extract_clip_details(clip_content, clip_num, clip_title, timing, file_path.stem)
                if clip_data:
                    clips.append(clip_data)
        
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
        
        return clips
    
    def _extract_clip_details(self, content: str, clip_num: int, title: str, timing: str, act: str) -> Optional[Dict[str, Any]]:
        """Extract detailed information from a clip section"""
        try:
            # Generate scene name from title
            scene_name = re.sub(r'[^\w\s-]', '', title.lower())
            scene_name = re.sub(r'[-\s]+', '_', scene_name).strip('_')
            
            # Extract simple prompts
            start_prompt = None
            end_prompt = None
            
            # Look for "Simple Prompts" section
            simple_prompts_match = re.search(r'\*\*Simple Prompts\*\*:\s*\n(.*?)(?=\n\*\*|\n---|\Z)', content, re.DOTALL)
            if simple_prompts_match:
                prompts_section = simple_prompts_match.group(1)
                
                # Extract start and end prompts
                start_match = re.search(r'- Start: "([^"]+)"', prompts_section)
                end_match = re.search(r'- End: "([^"]+)"', prompts_section)
                
                if start_match:
                    start_prompt = start_match.group(1)
                if end_match:
                    end_prompt = end_match.group(1)
            
            # If no simple prompts, look for single prompt
            if not start_prompt:
                single_prompt_match = re.search(r'\*\*Simple Prompt\*\*: "([^"]+)"', content)
                if single_prompt_match:
                    start_prompt = single_prompt_match.group(1)
            
            # Extract camera movement
            camera_movement = None
            camera_match = re.search(r'\*\*Camera Movement\*\*: ([^\n]+)', content)
            if camera_match:
                camera_movement = camera_match.group(1).strip()
            
            # Extract mood
            mood = None
            mood_match = re.search(r'\*\*Mood\*\*: ([^\n]+)', content)
            if mood_match:
                mood = mood_match.group(1).strip()
            
            # Extract audio info for mood fallback
            if not mood:
                audio_match = re.search(r'\*\*Audio\*\*: ([^\n]+)', content)
                if audio_match:
                    mood = audio_match.group(1).strip()
            
            return {
                'clip_number': clip_num,
                'title': title,
                'scene_name': scene_name,
                'timing': timing,
                'act': act,
                'start_prompt': start_prompt,
                'end_prompt': end_prompt,
                'camera_movement': camera_movement,
                'mood': mood,
                'full_content': content
            }
        
        except Exception as e:
            print(f"⚠️  Error extracting clip details: {e}")
            return None
    
    def get_completed_clips(self) -> List[str]:
        """Get list of scene names that have been completed"""
        completed = []
        
        if not self.ledger_file.exists():
            return completed
        
        try:
            with open(self.ledger_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        scene = entry.get('scene', '')
                        if scene and scene != 'example':
                            completed.append(scene)
        except Exception as e:
            print(f"⚠️  Error reading ledger: {e}")
        
        return completed
    
    def get_pending_clips(self) -> List[Dict[str, Any]]:
        """Get clips that haven't been generated yet"""
        all_clips = self.get_all_clips()
        completed = set(self.get_completed_clips())
        
        pending = []
        for clip in all_clips:
            if clip['scene_name'] not in completed:
                pending.append(clip)
        
        return pending

class Veo3Generator:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.flow_exports_dir = self.project_root / "04_flow_exports"
        self.prompts_dir = self.project_root / "02_prompts"
        self.ledger_file = self.prompts_dir / "ledger.jsonl"
        self.styleframes_dir = self.project_root / "01_styleframes_midjourney"
        
        # Ensure directories exist
        self.flow_exports_dir.mkdir(exist_ok=True)
        self.prompts_dir.mkdir(exist_ok=True)
        
        # Initialize prompt enhancer if available
        if LLM_AVAILABLE:
            self.prompt_enhancer = PromptEnhancer(project_root=self.project_root)
        else:
            self.prompt_enhancer = None
        
        # Initialize script parser
        self.script_parser = ScriptParser(self.project_root)
        
        # Set up API
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            print("❌ Error: GEMINI_API_KEY environment variable not set")
            print("Get your API key from: https://aistudio.google.com/app/apikey")
            print("Then set it with: export GEMINI_API_KEY='your-api-key-here'")
            sys.exit(1)
        
        self.headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        print("✅ Gemini API configured successfully")
    
    def calculate_cost(self, duration_seconds: int = 8, use_fast_model: bool = True, generate_audio: bool = True) -> float:
        """Calculate cost based on official Veo 3 pricing"""
        # Official Veo 3 pricing per second
        if use_fast_model:
            cost_per_second = 0.40 if generate_audio else 0.25  # Veo 3 Fast
        else:
            cost_per_second = 0.75 if generate_audio else 0.50  # Veo 3 Standard
        
        return duration_seconds * cost_per_second
    
    def generate_video(self, 
                      prompt: str, 
                      scene_name: str = "scene",
                      take_number: int = None,
                      reference_image: Optional[Path] = None,
                      notes: str = "",
                      auto_discover_styleframes: bool = True,
                      use_llm: bool = False,
                      camera_movement: str = None,
                      mood: str = None,
                      use_fast_model: bool = True,
                      generate_audio: bool = True) -> Dict[str, Any]:
        """
        Generate a video using Veo 3 via Gemini REST API
        
        Args:
            prompt: Text description for video generation
            scene_name: Scene identifier (e.g., 'title_sequence')
            take_number: Take number (auto-incremented if None)
            reference_image: Optional reference image path
            notes: Optional notes about the generation
            auto_discover_styleframes: Whether to auto-discover styleframes
            use_llm: Whether to use LLM enhancement for the prompt
            camera_movement: Specific camera movement for LLM enhancement
            mood: Desired mood for LLM enhancement
            use_fast_model: Whether to use Veo 3 Fast (cheaper) vs standard (default: True)
            generate_audio: Whether to generate audio with video (default: True)
            
        Returns:
            Dictionary with generation results
        """
        # Enhance prompt with LLM if requested
        if use_llm and self.prompt_enhancer:
            print("🤖 Enhancing prompt with LLM...")
            enhanced = self.prompt_enhancer.enhance_veo_prompt(
                prompt,
                scene_name,
                duration=8,  # Veo 3 generates 8-second clips
                camera_movement=camera_movement,
                mood=mood,
                use_llm=True
            )
            
            # Use the enhanced prompt and display it
            original_prompt = prompt
            prompt = enhanced.get("detailed", prompt)
            print(f"✨ Enhanced prompt: {prompt[:100]}...")
            
            # Display cost if available
            if "cost" in enhanced:
                print(f"💰 LLM cost: ${enhanced['cost']:.4f}")
        
        # Calculate and display cost
        estimated_cost = self.calculate_cost(8, use_fast_model, generate_audio)
        model_type = "Veo 3 Fast" if use_fast_model else "Veo 3 Standard"
        audio_status = "with Audio" if generate_audio else "Video Only"
        
        print(f"🎬 Generating video for scene: {scene_name}")
        print(f"🎥 Model: {model_type} ({audio_status})")
        print(f"💰 Estimated cost: ${estimated_cost:.2f} (8 seconds)")
        print(f"📝 Prompt: {prompt}")
        
        # Auto-increment take number if not provided
        if take_number is None:
            take_number = self._get_next_take_number(scene_name)
        
        # Generate timestamp and filename
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{scene_name}_take{take_number:02d}_{timestamp_str}.mp4"
        output_path = self.flow_exports_dir / filename
        
        try:
            print("🚀 Starting video generation...")
            
            # Prepare the payload
            payload = {
                "instances": [
                    {
                        "prompt": prompt
                    }
                ]
            }
            
            # Auto-discover reference image if not provided
            if not reference_image and auto_discover_styleframes:
                # For V7 Style References workflow: prefer current scene's start frame
                # but fall back to previous clip's end frame for continuity
                reference_image = self._find_best_reference_image(scene_name)
                
                # If no current scene frames, try previous clip's end frame
                if not reference_image:
                    reference_image = self._get_previous_clip_end_frame(scene_name)
                    if reference_image:
                        print(f"🔗 Using previous clip's end frame for continuity: {reference_image.name}")
            
            # Add reference image if available
            if reference_image and reference_image.exists():
                print(f"🖼️  Using reference image: {reference_image}")
                # Read and encode the image
                with open(reference_image, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                # Determine MIME type from file extension
                mime_type = "image/jpeg"
                if reference_image.suffix.lower() in ['.png']:
                    mime_type = "image/png"
                elif reference_image.suffix.lower() in ['.webp']:
                    mime_type = "image/webp"
                
                payload["instances"][0]["image"] = {
                    "bytesBase64Encoded": img_data,
                    "mimeType": mime_type
                }
            elif auto_discover_styleframes:
                print(f"💡 No reference image found for scene '{scene_name}' - generating without reference")
            
            # Choose model based on settings
            model_name = "veo-3.0-fast-generate-preview" if use_fast_model else "veo-3.0-generate-preview"
            
            # Start the generation
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:predictLongRunning"
            
            print("⏳ Submitting generation request...")
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
            
            result = response.json()
            operation_name = result.get("name")
            
            if not operation_name:
                raise Exception("No operation name returned from API")
            
            print(f"🔄 Operation started: {operation_name}")
            
            # Poll for completion
            video_data = self._poll_operation(operation_name)
            
            # Save the video
            with open(output_path, 'wb') as f:
                f.write(video_data)
            
            file_size = output_path.stat().st_size
            print(f"💾 Video saved: {filename} ({file_size / 1024 / 1024:.1f} MB)")
            
            # Create ledger entry with accurate cost tracking
            ledger_entry = {
                "timestamp": timestamp.isoformat(),
                "scene": scene_name,
                "take": take_number,
                "prompt": prompt,
                "duration": 8,  # Veo 3 generates 8-second clips
                "resolution": "720p",
                "model": model_name,
                "use_fast_model": use_fast_model,
                "generate_audio": generate_audio,
                "estimated_cost": estimated_cost,
                "quality": "high",
                "filename": filename,
                "file_size_bytes": file_size,
                "reference_image": str(reference_image) if reference_image else None,
                "notes": notes,
                "operation_name": operation_name
            }
            
            # Append to ledger
            self._append_to_ledger(ledger_entry)
            
            print(f"📝 Added to ledger: {scene_name} take {take_number}")
            
            return {
                "success": True,
                "output_path": output_path,
                "ledger_entry": ledger_entry,
                "take_number": take_number
            }
            
        except Exception as e:
            print(f"❌ Video generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "scene": scene_name,
                "take_number": take_number
            }
    
    def _poll_operation(self, operation_name: str) -> bytes:
        """Poll the long-running operation until completion"""
        operation_url = f"https://generativelanguage.googleapis.com/v1beta/{operation_name}"
        
        max_wait_time = 600  # 10 minutes
        wait_time = 0
        poll_interval = 15  # Check every 15 seconds
        
        print("⏳ Polling for completion...")
        
        while wait_time < max_wait_time:
            try:
                response = requests.get(operation_url, headers=self.headers)
                
                if response.status_code != 200:
                    raise Exception(f"Polling failed: {response.status_code} - {response.text}")
                
                operation_result = response.json()
                
                if operation_result.get("done", False):
                    print("✅ Video generation completed!")
                    
                    # Extract the video data
                    if "response" in operation_result:
                        response_data = operation_result["response"]
                        
                        # Check for the new generateVideoResponse format
                        if "generateVideoResponse" in response_data:
                            video_response = response_data["generateVideoResponse"]
                            if "generatedSamples" in video_response:
                                samples = video_response["generatedSamples"]
                                if samples and len(samples) > 0:
                                    sample = samples[0]
                                    if "video" in sample and "uri" in sample["video"]:
                                        video_uri = sample["video"]["uri"]
                                        print(f"📥 Downloading video from: {video_uri}")
                                        return self._download_video(video_uri)
                        
                        # Fallback: Look for older prediction format
                        elif "predictions" in response_data:
                            predictions = response_data["predictions"]
                            if predictions and len(predictions) > 0:
                                prediction = predictions[0]
                                
                                # Look for base64 encoded video data
                                if "bytesBase64Encoded" in prediction:
                                    video_b64 = prediction["bytesBase64Encoded"]
                                    return base64.b64decode(video_b64)
                                elif "videoData" in prediction:
                                    video_b64 = prediction["videoData"]
                                    return base64.b64decode(video_b64)
                    
                    # If we get here, the operation completed but we couldn't find video data
                    print(f"⚠️  Operation completed but no video data found")
                    print(f"Response structure: {json.dumps(operation_result, indent=2)}")
                    raise Exception("Video generation completed but no video data found in response")
                
                else:
                    # Still processing
                    time.sleep(poll_interval)
                    wait_time += poll_interval
                    print(f"⏳ Still generating... ({wait_time}s elapsed)")
                
            except Exception as e:
                if "Video generation completed but no video data found" in str(e):
                    raise  # Re-raise this specific error
                print(f"⚠️  Polling error: {e}")
                time.sleep(poll_interval)
                wait_time += poll_interval
        
        raise TimeoutError("Video generation timed out after 10 minutes")
    
    def _download_video(self, video_uri: str) -> bytes:
        """Download video from the provided URI"""
        try:
            # The URI should be downloadable with the same API key
            response = requests.get(video_uri, headers=self.headers)
            
            if response.status_code != 200:
                raise Exception(f"Video download failed: {response.status_code} - {response.text}")
            
            return response.content
            
        except Exception as e:
            raise Exception(f"Failed to download video: {e}")
    
    def _get_next_take_number(self, scene_name: str) -> int:
        """Get the next take number for a scene"""
        existing_takes = []
        
        # Check existing files
        for file_path in self.flow_exports_dir.glob(f"{scene_name}_take*.mp4"):
            try:
                # Extract take number from filename
                parts = file_path.stem.split('_')
                for part in parts:
                    if part.startswith('take'):
                        take_num = int(part[4:])  # Remove 'take' prefix
                        existing_takes.append(take_num)
                        break
            except (ValueError, IndexError):
                continue
        
        return max(existing_takes, default=0) + 1
    
    def _find_best_reference_image(self, scene_name: str) -> Optional[Path]:
        """Find the best reference image for a scene from organized styleframes"""
        # Check for organized styleframes first
        metadata_file = self.styleframes_dir / "styleframes_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                scene_data = metadata.get(scene_name, {})
                
                # For V7 Style References workflow: prioritize start frame for current scene
                # (End frame from previous clip should be handled separately)
                for frame_type in ["start", "reference", "end"]:
                    if frame_type in scene_data and scene_data[frame_type]:
                        # Get the most recent one
                        latest = max(scene_data[frame_type], key=lambda x: x["timestamp"])
                        ref_path = self.project_root / latest["path"]
                        if ref_path.exists():
                            return ref_path
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Fallback: look for images in the old flat structure
        for pattern in [f"{scene_name}*", f"*{scene_name}*"]:
            matches = list(self.styleframes_dir.glob(pattern))
            if matches:
                # Return the most recently modified
                return max(matches, key=lambda p: p.stat().st_mtime)
        
        return None
    
    def _get_previous_clip_end_frame(self, scene_name: str) -> Optional[Path]:
        """Get the end frame from the previous clip for visual continuity"""
        # Scene sequence from Act I - using actual styleframe names for consistency
        act1_sequence = [
            "title_sequence",
            "shattered_plains_reveal",  # or "the_shattered_plains" 
            "kaladin_introduction",
            "adolin_introduction", 
            "the_magic_system",  # matches styleframes
            "dalinar_introduction",
            "spren_bonds",
            "the_parshendi",  # matches styleframes
            "highstorm_approaching"
        ]
        
        try:
            current_index = act1_sequence.index(scene_name)
            if current_index > 0:  # Not the first clip
                prev_scene = act1_sequence[current_index - 1]
                
                # Look for the previous scene's end frame
                metadata_file = self.styleframes_dir / "styleframes_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    prev_scene_data = metadata.get(prev_scene, {})
                    if prev_scene_data.get('end'):
                        latest = max(prev_scene_data['end'], key=lambda x: x["timestamp"])
                        ref_path = self.project_root / latest["path"]
                        if ref_path.exists():
                            return ref_path
        except (ValueError, json.JSONDecodeError, KeyError):
            pass
        
        return None
    
    def list_pending_clips(self) -> List[Dict[str, Any]]:
        """List all pending clips from story development scripts"""
        return self.script_parser.get_pending_clips()
    
    def run_interactive_mode(self) -> Dict[str, Any]:
        """Run interactive mode - show pending clips and let user choose with cost estimates"""
        try:
            from rich.console import Console
            from rich.prompt import Prompt, Confirm
            from rich.table import Table
            from rich.panel import Panel
            console = Console()
        except ImportError:
            # Fallback to basic terminal interaction
            return self._run_basic_interactive_mode()
        
        console.clear()
        
        # Show header
        console.print("🌪️✨ [bold cyan]STORMLIGHT VIDEO GENERATOR[/bold cyan] ✨🌪️\n")
        
        # Get pending clips
        pending_clips = self.list_pending_clips()
        
        if not pending_clips:
            console.print("🎉 [bold green]All clips completed![/bold green] No pending clips found.")
            console.print("💡 All clips from your story development scripts have been generated.")
            return {"success": True, "message": "No pending clips"}
        
        # Show pending clips in a beautiful table
        console.print(f"📋 [bold yellow]Found {len(pending_clips)} pending clips[/bold yellow]\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("🎬 Title", style="bold cyan", min_width=20)
        table.add_column("📍 Act", style="yellow", width=12)
        table.add_column("⏰ Timing", style="green", width=10)
        table.add_column("📝 Prompt Preview", style="dim", min_width=40)
        
        for i, clip in enumerate(pending_clips[:10], 1):  # Show first 10
            prompt_preview = clip.get('start_prompt', 'No prompt')[:40] + "..." if clip.get('start_prompt') else "No prompt"
            table.add_row(
                str(i),
                clip['title'],
                clip['act'].replace('_', ' ').title(),
                clip['timing'],
                prompt_preview
            )
        
        if len(pending_clips) > 10:
            table.add_row("...", f"... and {len(pending_clips) - 10} more", "", "", "")
        
        console.print(table)
        console.print()
        
        # Interactive options
        while True:
            console.print("🎯 [bold]What would you like to do?[/bold]")
            console.print("1️⃣  Choose a specific clip to generate")
            console.print("2️⃣  View full details of a clip")
            console.print("3️⃣  Exit")
            
            choice = Prompt.ask("\n🎮 Enter your choice", choices=["1", "2", "3"], default="1")
            
            if choice == "1":
                # Choose specific clip
                console.print(f"\n📋 Choose a clip (1-{min(10, len(pending_clips))}):")
                try:
                    clip_choice = int(Prompt.ask("🎬 Clip number")) - 1
                    if 0 <= clip_choice < len(pending_clips):
                        selected_clip = pending_clips[clip_choice]
                        console.print(f"\n✨ Selected: [bold cyan]{selected_clip['title']}[/bold cyan]")
                        
                        # Step 0: Check for styleframes and warn if missing
                        scene_name = selected_clip['scene_name']
                        styleframes_status = self._check_styleframes_status(scene_name)
                        if not styleframes_status['has_any']:
                            console.print(f"\n⚠️  [bold yellow]WARNING: No styleframes found for '{scene_name}'[/bold yellow]")
                            console.print("🎨 [dim]This video will be generated without reference images[/dim]")
                            console.print("💡 [dim]Consider running the Styleframe Manager first: python3 tools/styleframe_manager.py interactive[/dim]")
                            
                            if not Confirm.ask("Continue without styleframes?", default=True):
                                continue
                        else:
                            console.print(f"\n✅ [bold green]Styleframes available:[/bold green]")
                            if styleframes_status['has_start']:
                                console.print(f"   🎬 Start frame: [green]✓[/green]")
                            else:
                                console.print(f"   🎬 Start frame: [yellow]✗[/yellow]")
                            if styleframes_status['has_end']:
                                console.print(f"   🎯 End frame: [green]✓[/green]")
                            else:
                                console.print(f"   🎯 End frame: [yellow]✗[/yellow]")
                            
                            # Show reference images being used
                            if styleframes_status['reference_path']:
                                console.print(f"   📸 Current scene: [dim cyan]{styleframes_status['reference_path']}[/dim cyan]")
                            
                            # Check for previous clip's end frame for V7 continuity
                            if styleframes_status['has_previous_end']:
                                console.print(f"   🔗 Previous clip: [dim cyan]{styleframes_status['previous_end_path']}[/dim cyan]")
                                if styleframes_status['has_start'] or styleframes_status['has_end']:
                                    console.print(f"   [dim yellow]💡 V7 Style References: Using both current + previous frames for continuity[/dim yellow]")
                                else:
                                    console.print(f"   [dim yellow]💡 Will use previous clip's end frame for continuity[/dim yellow]")
                            else:
                                console.print(f"   🔗 Previous clip: [yellow]✗[/yellow] [dim](first clip or missing)[/dim]")
                        
                        # Step 1: Show the storyboard prompt
                        original_prompt = selected_clip.get('start_prompt')
                        if not original_prompt:
                            console.print("❌ [red]No prompt found for this clip[/red]")
                            continue
                        
                        console.print(f"\n📝 [bold]Original storyboard prompt:[/bold]")
                        console.print(f"[dim cyan]{original_prompt}[/dim cyan]")
                        
                        # Step 2: Ask about AI enhancement
                        use_llm = Confirm.ask("\n🤖 Use AI to enhance the prompt?", default=True)
                        
                        final_prompt = original_prompt
                        if use_llm and self.prompt_enhancer:
                            # Step 3: AI enhancement with confirmation loop
                            while True:
                                console.print("\n🤖 [yellow]Enhancing prompt with AI...[/yellow]")
                                enhanced = self.prompt_enhancer.enhance_veo_prompt(
                                    original_prompt,
                                    selected_clip['scene_name'],
                                    duration=8,
                                    camera_movement=selected_clip.get('camera_movement'),
                                    mood=selected_clip.get('mood'),
                                    use_llm=True
                                )
                                
                                enhanced_prompt = enhanced.get("detailed", original_prompt)
                                console.print(f"\n✨ [bold]AI-enhanced prompt:[/bold]")
                                console.print(f"[dim green]{enhanced_prompt}[/dim green]")
                                
                                if "cost" in enhanced:
                                    console.print(f"💰 LLM cost: ${enhanced['cost']:.4f}")
                                
                                # Confirmation options
                                console.print("\n🎯 [bold]What would you like to do?[/bold]")
                                console.print("1️⃣  Use this enhanced prompt")
                                console.print("2️⃣  Enhance again with feedback")
                                console.print("3️⃣  Use original prompt instead")
                                
                                prompt_choice = Prompt.ask("Choose option", choices=["1", "2", "3"], default="1")
                                
                                if prompt_choice == "1":
                                    final_prompt = enhanced_prompt
                                    break
                                elif prompt_choice == "2":
                                    feedback = Prompt.ask("💬 What changes would you like?")
                                    original_prompt = f"{original_prompt}\n\nUser feedback: {feedback}"
                                    continue
                                else:
                                    final_prompt = original_prompt
                                    break
                        
                        # Step 4: Model and cost selection
                        console.print(f"\n🎬 [bold]Choose model and cost option:[/bold]")
                        
                        # Calculate costs for all options
                        fast_audio_cost = self.calculate_cost(8, True, True)
                        fast_video_cost = self.calculate_cost(8, True, False)
                        std_audio_cost = self.calculate_cost(8, False, True)
                        std_video_cost = self.calculate_cost(8, False, False)
                        
                        console.print(f"1️⃣  [green]Veo 3 Fast + Audio[/green] - Best value ([bold red]${fast_audio_cost:.2f}[/bold red])")
                        console.print(f"2️⃣  [yellow]Veo 3 Fast, Video Only[/yellow] - Cheapest ([bold red]${fast_video_cost:.2f}[/bold red])")
                        console.print(f"3️⃣  [blue]Veo 3 Standard + Audio[/blue] - Highest quality ([bold red]${std_audio_cost:.2f}[/bold red])")
                        console.print(f"4️⃣  [magenta]Veo 3 Standard, Video Only[/magenta] - High quality, no audio ([bold red]${std_video_cost:.2f}[/bold red])")
                        
                        cost_choice = Prompt.ask("🎯 Select option", choices=["1", "2", "3", "4"], default="1")
                        
                        # Set parameters based on choice
                        if cost_choice == "1":
                            use_fast_model, generate_audio = True, True
                            cost_desc = f"Veo 3 Fast + Audio (${fast_audio_cost:.2f})"
                        elif cost_choice == "2":
                            use_fast_model, generate_audio = True, False
                            cost_desc = f"Veo 3 Fast, Video Only (${fast_video_cost:.2f})"
                        elif cost_choice == "3":
                            use_fast_model, generate_audio = False, True
                            cost_desc = f"Veo 3 Standard + Audio (${std_audio_cost:.2f})"
                        else:
                            use_fast_model, generate_audio = False, False
                            cost_desc = f"Veo 3 Standard, Video Only (${std_video_cost:.2f})"
                        
                        console.print(f"\n🚀 [bold green]Generating: {cost_desc}[/bold green]")
                        
                        # Step 5: Generate the video
                        return self.generate_video(
                            prompt=final_prompt,
                            scene_name=selected_clip['scene_name'],
                            notes=f"Interactive: {selected_clip['title']} - {cost_desc}",
                            use_llm=False,  # Already enhanced above
                            camera_movement=selected_clip.get('camera_movement'),
                            mood=selected_clip.get('mood'),
                            use_fast_model=use_fast_model,
                            generate_audio=generate_audio
                        )
                    else:
                        console.print("❌ [red]Invalid clip number[/red]")
                except (ValueError, IndexError):
                    console.print("❌ [red]Please enter a valid number[/red]")
                    
            elif choice == "2":
                # View clip details
                try:
                    clip_choice = int(Prompt.ask(f"🔍 View details for clip (1-{min(10, len(pending_clips))})")) - 1
                    if 0 <= clip_choice < len(pending_clips):
                        clip = pending_clips[clip_choice]
                        
                        details = f"""
[bold cyan]🎬 {clip['title']}[/bold cyan]
📍 Act: {clip['act'].replace('_', ' ').title()}
🎯 Clip #{clip['clip_number']} | ⏰ {clip['timing']}
🎭 Scene: {clip['scene_name']}

📝 [bold]Start Prompt:[/bold]
{clip.get('start_prompt', 'No start prompt found')}

📝 [bold]End Prompt:[/bold]
{clip.get('end_prompt', 'No end prompt found')}

🎥 [bold]Camera Movement:[/bold] {clip.get('camera_movement', 'Not specified')}
🎭 [bold]Mood:[/bold] {clip.get('mood', 'Not specified')}
                        """
                        
                        console.print(Panel(details.strip(), title="📋 Clip Details", border_style="cyan"))
                        console.print("\nPress Enter to continue...")
                        input()
                    else:
                        console.print("❌ [red]Invalid clip number[/red]")
                except (ValueError, IndexError):
                    console.print("❌ [red]Please enter a valid number[/red]")
                    
            elif choice == "3":
                console.print("👋 [bold green]Goodbye![/bold green]")
                return {"success": False, "message": "User exit"}
            
            console.print()  # Add spacing
    
    def _run_basic_interactive_mode(self) -> Dict[str, Any]:
        """Fallback interactive mode without rich formatting"""
        print("🌪️ STORMLIGHT VIDEO GENERATOR 🌪️\n")
        
        pending_clips = self.list_pending_clips()
        
        if not pending_clips:
            print("🎉 All clips completed! No pending clips found.")
            return {"success": True, "message": "No pending clips"}
        
        print(f"📋 Found {len(pending_clips)} pending clips:\n")
        
        for i, clip in enumerate(pending_clips[:5], 1):
            print(f"{i:2d}. 🎬 {clip['title']}")
            print(f"    📍 {clip['act']} | Clip #{clip['clip_number']} | ⏰ {clip['timing']}")
            if clip.get('start_prompt'):
                print(f"    📝 {clip['start_prompt'][:50]}...")
            print()
        
        if len(pending_clips) > 5:
            print(f"    ... and {len(pending_clips) - 5} more clips\n")
        
        print("🎯 Options:")
        print("1. Generate a specific clip")
        print("2. Exit")
        
        try:
            choice = input("\n🎮 Enter choice (1-2): ").strip()
            
            if choice == "1":
                clip_num = int(input("Enter clip number: ")) - 1
                if 0 <= clip_num < len(pending_clips):
                    selected_clip = pending_clips[clip_num]
                    prompt = selected_clip.get('start_prompt', 'No prompt')
                    
                    # Simple cost selection
                    print(f"\nCost options for 8-second video:")
                    print(f"1. Fast + Audio: ${self.calculate_cost(8, True, True):.2f}")
                    print(f"2. Fast, Video Only: ${self.calculate_cost(8, True, False):.2f}")
                    print(f"3. Standard + Audio: ${self.calculate_cost(8, False, True):.2f}")
                    print(f"4. Standard, Video Only: ${self.calculate_cost(8, False, False):.2f}")
                    
                    cost_choice = input("Choose option (1-4): ").strip()
                    
                    if cost_choice == "1":
                        use_fast, audio = True, True
                    elif cost_choice == "2":
                        use_fast, audio = True, False
                    elif cost_choice == "3":
                        use_fast, audio = False, True
                    else:
                        use_fast, audio = False, False
                    
                    return self.generate_video(
                        prompt=prompt,
                        scene_name=selected_clip['scene_name'],
                        notes=f"Interactive: {selected_clip['title']}",
                        use_fast_model=use_fast,
                        generate_audio=audio
                    )
                else:
                    print("❌ Invalid clip number")
            else:
                print("👋 Goodbye!")
                return {"success": False, "message": "User exit"}
                
        except (KeyboardInterrupt, ValueError):
            print("\n👋 Goodbye!")
            return {"success": False, "message": "User exit"}
    
    def _check_styleframes_status(self, scene_name: str) -> Dict[str, Any]:
        """Check if styleframes exist for a scene and return detailed status"""
        metadata_file = self.styleframes_dir / "styleframes_metadata.json"
        
        status = {
            'has_any': False,
            'has_start': False,
            'has_end': False,
            'reference_path': None,
            'has_previous_end': False,
            'previous_end_path': None
        }
        
        if not metadata_file.exists():
            return status
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            scene_data = metadata.get(scene_name, {})
            
            # Check for start frames
            if scene_data.get('start'):
                status['has_start'] = True
                status['has_any'] = True
            
            # Check for end frames
            if scene_data.get('end'):
                status['has_end'] = True
                status['has_any'] = True
            
            # Check for reference frames
            if scene_data.get('reference'):
                status['has_any'] = True
            
            # Get best reference path (same logic as _find_best_reference_image)
            for frame_type in ["start", "reference", "end"]:
                if frame_type in scene_data and scene_data[frame_type]:
                    latest = max(scene_data[frame_type], key=lambda x: x["timestamp"])
                    ref_path = self.project_root / latest["path"]
                    if ref_path.exists():
                        status['reference_path'] = str(ref_path.relative_to(self.project_root))
                        break
            
            # Check for previous clip's end frame for V7 continuity
            prev_end_frame = self._get_previous_clip_end_frame(scene_name)
            if prev_end_frame:
                status['has_previous_end'] = True
                status['previous_end_path'] = str(prev_end_frame.relative_to(self.project_root))
                status['has_any'] = True  # Previous end frame counts as available reference
        
        except (json.JSONDecodeError, KeyError):
            pass
        
        return status
    
    def _append_to_ledger(self, entry: Dict[str, Any]):
        """Append entry to the JSONL ledger file"""
        with open(self.ledger_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

def main():
    """Command line interface for Veo 3 generation"""
    parser = argparse.ArgumentParser(
        description="Generate Veo 3 videos using Gemini API",
        epilog="""
Examples:
  # Interactive mode (DEFAULT - shows pending clips and cost options)
  %(prog)s
  
  # Manual generation with cost control
  %(prog)s "Kaladin on stormy battlefield" --scene kaladin_intro --fast --with-audio
  %(prog)s "Bridge crew running" --scene bridge_run --standard --no-audio
  
  # List pending clips from story scripts
  %(prog)s --list-pending
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("prompt", nargs='?',
                       help="Video description prompt (use quotes for multi-word prompts)")
    parser.add_argument("--scene",
                       help="Scene identifier (use underscores not spaces)")
    parser.add_argument("--take", type=int, 
                       help="Take number (optional, auto-increments if not provided)")
    parser.add_argument("--image", type=Path, 
                       help="Reference image path (optional, auto-discovers if not provided)")
    parser.add_argument("--notes", default="", 
                       help="Production notes (optional, use quotes)")
    parser.add_argument("--no-auto-image", action="store_true",
                       help="Disable automatic styleframe discovery")
    parser.add_argument("--llm-prompt", action="store_true",
                       help="Use LLM to enhance the prompt with cinematic details")
    parser.add_argument("--camera", 
                       help="Camera movement (e.g., 'tracking shot', 'slow push in')")
    parser.add_argument("--mood",
                       help="Desired mood (e.g., 'heroic', 'desperate', 'mystical')")
    parser.add_argument("--list-pending", action="store_true",
                       help="List all pending clips from story development scripts")
    parser.add_argument("--fast", action="store_true",
                       help="Use Veo 3 Fast model (cheaper, faster)")
    parser.add_argument("--standard", action="store_true",
                       help="Use Veo 3 Standard model (higher quality, more expensive)")
    parser.add_argument("--with-audio", action="store_true",
                       help="Generate audio with video")
    parser.add_argument("--no-audio", action="store_true",
                       help="Generate video only (no audio)")
    
    args = parser.parse_args()
    
    # Create generator
    generator = Veo3Generator()
    
    # Interactive mode by default - show pending clips and let user choose
    if not any([args.list_pending, args.prompt]):
        result = generator.run_interactive_mode()
        return
    
    # Handle list pending clips
    if args.list_pending:
        pending_clips = generator.list_pending_clips()
        if not pending_clips:
            print("✅ No pending clips found! All clips from story scripts have been generated.")
        else:
            print(f"📋 Found {len(pending_clips)} pending clips:\n")
            for i, clip in enumerate(pending_clips, 1):
                print(f"{i:2d}. 🎬 {clip['title']}")
                print(f"    📍 {clip['act']} | Clip #{clip['clip_number']} | ⏰ {clip['timing']}")
                print(f"    🎭 Scene: {clip['scene_name']}")
                if clip.get('start_prompt'):
                    print(f"    📝 Prompt: {clip['start_prompt'][:60]}...")
                print()
        return
    
    # Manual generation mode
    if not args.prompt or not args.scene:
        print("❌ Error: --prompt and --scene are required for manual generation")
        print("💡 Tip: Run without arguments for interactive mode")
        sys.exit(1)
    
    # Determine model and audio settings
    if args.standard:
        use_fast_model = False
    else:
        use_fast_model = True  # Default to fast
    
    if args.no_audio:
        generate_audio = False
    else:
        generate_audio = True  # Default to audio
    
    # Show cost estimate
    estimated_cost = generator.calculate_cost(8, use_fast_model, generate_audio)
    model_type = "Veo 3 Fast" if use_fast_model else "Veo 3 Standard"
    audio_status = "with Audio" if generate_audio else "Video Only"
    print(f"💰 Cost estimate: ${estimated_cost:.2f} ({model_type}, {audio_status})")
    
    # Generate video
    result = generator.generate_video(
        prompt=args.prompt,
        scene_name=args.scene,
        take_number=args.take,
        reference_image=args.image,
        notes=args.notes,
        auto_discover_styleframes=not args.no_auto_image,
        use_llm=args.llm_prompt,
        camera_movement=args.camera,
        mood=args.mood,
        use_fast_model=use_fast_model,
        generate_audio=generate_audio
    )
    
    if result["success"]:
        print(f"\n🎉 SUCCESS! Video generated:")
        print(f"📁 File: {result['output_path']}")
        print(f"🎬 Scene: {result['ledger_entry']['scene']}")
        print(f"🎯 Take: {result['take_number']}")
    else:
        print(f"\n❌ FAILED: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
