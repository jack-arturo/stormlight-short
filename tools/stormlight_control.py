#!/usr/bin/env python3
"""
🌪️ Stormlight Control Center - Beautiful Meta Dashboard
The ultimate visual control center for Stormlight: Into the Tempest production pipeline
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import argparse

console = Console()

class StormlightControl:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.console = Console()
        self.current_view = "main"
        self.tools_status = {}
        
    def create_ascii_logo(self) -> Text:
        """Create absolutely gorgeous ASCII art logo with gradients and emojis"""
        logo = Text()
        
        # Animated storm effect with gradients
        logo.append("⚡", style="bold yellow")
        logo.append("🌪️", style="bold cyan")
        logo.append(" ╔══════════════════════════════════════════════════════════════╗ ", style="bold blue")
        logo.append("🌪️", style="bold cyan")
        logo.append("⚡\n", style="bold yellow")
        
        logo.append("⛈️ ", style="bold white")
        logo.append("║ ", style="bold blue")
        logo.append("███████╗████████╗ ██████╗ ██████╗ ███╗   ███╗██╗     ██╗ ██████╗ ██╗  ██╗", style="bold magenta")
        logo.append(" ║", style="bold blue")
        logo.append(" ⛈️\n", style="bold white")
        
        logo.append("🔮 ", style="bold purple")
        logo.append("║ ", style="bold blue")
        logo.append("██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗████╗ ████║██║     ██║██╔════╝ ██║  ██║", style="bold cyan")
        logo.append(" ║", style="bold blue")
        logo.append(" 🔮\n", style="bold purple")
        
        logo.append("✨ ", style="bold yellow")
        logo.append("║ ", style="bold blue")
        logo.append("███████╗   ██║   ██║   ██║██████╔╝██╔████╔██║██║     ██║██║  ███╗███████║", style="bold green")
        logo.append(" ║", style="bold blue")
        logo.append(" ✨\n", style="bold yellow")
        
        logo.append("🎬 ", style="bold red")
        logo.append("║ ", style="bold blue")
        logo.append("╚════██║   ██║   ██║   ██║██╔══██╗██║╚██╔╝██║██║     ██║██║   ██║██╔══██║", style="bold yellow")
        logo.append(" ║", style="bold blue")
        logo.append(" 🎬\n", style="bold red")
        
        logo.append("🌟 ", style="bold white")
        logo.append("║ ", style="bold blue")
        logo.append("███████║   ██║   ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗██║╚██████╔╝██║  ██║", style="bold magenta")
        logo.append(" ║", style="bold blue")
        logo.append(" 🌟\n", style="bold white")
        
        logo.append("⚡ ", style="bold yellow")
        logo.append("║ ", style="bold blue")
        logo.append("╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝", style="bold cyan")
        logo.append(" ║", style="bold blue")
        logo.append(" ⚡\n", style="bold yellow")
        
        logo.append("🌪️", style="bold cyan")
        logo.append(" ╚══════════════════════════════════════════════════════════════╝ ", style="bold blue")
        logo.append("🌪️\n", style="bold cyan")
        
        # Subtitle with more emojis - more compact
        logo.append("      ✨🎭 ", style="bold yellow")
        logo.append("I N T O   T H E   T E M P E S T", style="bold white on blue")
        logo.append(" 🎭✨", style="bold yellow")
        
        return logo
    
    def get_tool_status(self) -> Dict[str, Dict]:
        """Get status of all tools"""
        status = {}
        
        # Check AI status
        import os
        ai_available = bool(os.getenv('OPENAI_API_KEY'))
        status['ai'] = {
            'available': ai_available,
            'status': '✅ Active' if ai_available else '⚠️ Not configured'
        }
        
        # Styleframe Manager Status
        styleframes_metadata = self.project_root / "01_styleframes_midjourney" / "styleframes_metadata.json"
        if styleframes_metadata.exists():
            try:
                with open(styleframes_metadata, 'r') as f:
                    metadata = json.load(f)
                    scenes_count = len(metadata)
                    total_frames = sum(len(scene_data.get('start', [])) + 
                                     len(scene_data.get('end', [])) + 
                                     len(scene_data.get('reference', [])) 
                                     for scene_data in metadata.values())
                    status['styleframes'] = {
                        'status': '✅ Active',
                        'scenes': scenes_count,
                        'frames': total_frames,
                        'health': 'healthy'
                    }
            except:
                status['styleframes'] = {'status': '⚠️ Error', 'health': 'warning'}
        else:
            status['styleframes'] = {'status': '❌ Not Setup', 'health': 'critical'}
        
        # Video Generation Status
        ledger_path = self.project_root / "02_prompts" / "ledger.jsonl"
        if ledger_path.exists():
            try:
                with open(ledger_path, 'r') as f:
                    entries = [json.loads(line) for line in f if line.strip()]
                    
                completed = 0
                active = 0
                total_cost = 0
                
                for entry in entries:
                    if entry.get('scene') == 'example':  # Skip example
                        continue
                    video_path = self.project_root / "04_flow_exports" / entry.get('filename', '')
                    if video_path.exists():
                        completed += 1
                    else:
                        active += 1
                    # Cost estimation based on official Veo pricing (per second)
                    duration = entry.get('duration', 8)  # Default 8 seconds
                    model = entry.get('model', 'veo-3.0-fast-generate-preview')  # Default to fast model
                    
                    # Check for audio setting in new format or fallback to notes
                    has_audio = entry.get('generate_audio', False)
                    if not has_audio and "with audio" in entry.get('notes', '').lower():
                        has_audio = True
                    
                    # Determine cost per second based on model and audio
                    if 'fast' in model.lower():
                        # Veo 3 Fast pricing
                        cost_per_second = 0.40 if has_audio else 0.25
                    else:
                        # Standard Veo 3 pricing  
                        cost_per_second = 0.75 if has_audio else 0.50
                    
                    estimated_cost = duration * cost_per_second
                    total_cost += estimated_cost
                
                status['video_gen'] = {
                    'status': f'🎬 {completed} Complete, {active} Active',
                    'completed': completed,
                    'active': active,
                    'cost': total_cost,
                    'health': 'healthy' if completed > 0 else 'warning'
                }
            except:
                status['video_gen'] = {'status': '⚠️ Error', 'health': 'warning'}
        else:
            status['video_gen'] = {'status': '❌ No Jobs', 'health': 'critical'}
        
        # Pipeline Monitor Status
        status['monitor'] = {
            'status': '📊 Ready',
            'refresh_rate': '5s',
            'health': 'healthy'
        }
        
        # Story Development Status
        story_dir = self.project_root / "07_story_development"
        if story_dir.exists():
            story_files = list(story_dir.glob("*.md"))
            status['story'] = {
                'status': f'📚 {len(story_files)} Documents',
                'files': len(story_files),
                'health': 'healthy' if len(story_files) > 0 else 'warning'
            }
        else:
            status['story'] = {'status': '❌ Missing', 'health': 'critical'}
        
        return status
    
    def create_tool_cards(self, status: Dict) -> Columns:
        """Create beautiful tool status cards"""
        cards = []
        
        # Styleframe Manager Card
        sf_status = status.get('styleframes', {})
        sf_card = Panel(
            f"""🔥 Status: {sf_status.get('status', '❓ Unknown')}
🎭 Scenes: [bold yellow]{sf_status.get('scenes', 0)}[/bold yellow] | 🖼️ Frames: [bold magenta]{sf_status.get('frames', 0)}[/bold magenta]
[dim italic]Interactive workflow • Auto optimization[/dim italic]
[bold cyan]🤖 AI Enhancement Available![/bold cyan]
[bold green on black] 🚀 Press 'S' to launch! 🚀 [/bold green on black]""",
            title="🎨 Styleframes 🎨",
            border_style="bright_cyan" if sf_status.get('health') == 'healthy' else "bright_yellow",
            width=38,
            padding=(0, 1)
        )
        cards.append(sf_card)
        
        # Video Generation Card
        vg_status = status.get('video_gen', {})
        vg_card = Panel(
            f"""⚡ Status: {vg_status.get('status', '❓ Unknown')}
✅ Completed: [bold green]{vg_status.get('completed', 0)}[/bold green] | 💰 Est: [bold red]${vg_status.get('cost', 0):.2f}[/bold red]
[dim italic]Veo 3 via Gemini API[/dim italic]
[bold cyan]🤖 AI Prompt Enhancement![/bold cyan]
[dim yellow]💡 Fast: $2/video, Standard: $4/video (+audio doubles cost)[/dim yellow]
[bold green on black] 🎥 Press 'V' to generate! 🎥 [/bold green on black]""",
            title="🎬 Video Gen 🎬",
            border_style="bright_magenta" if vg_status.get('health') == 'healthy' else "bright_yellow",
            width=38,
            padding=(0, 1)
        )
        cards.append(vg_card)
        
        # Pipeline Monitor Card
        pm_status = status.get('monitor', {})
        pm_card = Panel(
            f"""🎯 Status: {pm_status.get('status', '❓ Unknown')}
🔄 Refresh: [bold cyan]{pm_status.get('refresh_rate', '5s')}[/bold cyan] | 📈 Real-time Dashboard
[dim italic]Live monitoring & diagnostics[/dim italic]
[bold green on black] 📊 Press 'M' to monitor! 📊 [/bold green on black]""",
            title="📊 Monitor 📊",
            border_style="bright_blue",
            width=38,
            padding=(0, 1)
        )
        cards.append(pm_card)
        
        # Story Development Card
        story_status = status.get('story', {})
        story_card = Panel(
            f"""[bold yellow]📚🎭 Story Development 🎭📚[/bold yellow]
            
📖 Status: {story_status.get('status', '❓ Unknown')}
📄 Files: [bold cyan]{story_status.get('files', 0)}[/bold cyan]
🎬 Acts: [bold magenta]3 (Complete)[/bold magenta]

[dim italic]📝 Scene breakdowns
🎯 Production notes
⚡ 4-minute trailer plan[/dim italic]

[bold green on black] 📚 Press 'D' to view docs! 📚 [/bold green on black]""",
            title="📚 Story 📚",
            border_style="bright_yellow",
            width=38,
            padding=(0, 1)  # Reduce padding
        )
        cards.append(story_card)
        
        return Columns(cards, equal=True, expand=True)
    
    def create_quick_stats(self, status: Dict) -> Panel:
        """Create quick stats overview"""
        vg_status = status.get('video_gen', {})
        sf_status = status.get('styleframes', {})
        ai_status = status.get('ai', {})
        
        stats_table = Table(show_header=False, box=None, padding=(0, 2))
        stats_table.add_column("Metric", style="bold")
        stats_table.add_column("Value", style="cyan")
        stats_table.add_column("Metric", style="bold")
        stats_table.add_column("Value", style="cyan")
        
        stats_table.add_row(
            "🎬 Videos Generated", f"[bold green]{vg_status.get('completed', 0)}[/bold green]",
            "🎨 Styleframes", f"[bold magenta]{sf_status.get('frames', 0)}[/bold magenta]"
        )
        stats_table.add_row(
            "💰 Est. Cost", f"[bold red]${vg_status.get('cost', 0):.2f}[/bold red]",
            "📝 Scenes", f"[bold yellow]{sf_status.get('scenes', 0)}[/bold yellow]"
        )
        stats_table.add_row(
            "⚡ Active Jobs", f"[bold cyan]{vg_status.get('active', 0)}[/bold cyan]",
            "🤖 AI Status", f"[bold cyan]{ai_status.get('status', '❓ Unknown')}[/bold cyan]"
        )
        
        return Panel(
            stats_table,
            title="📈 Production Overview",
            border_style="bright_green",
            padding=(0, 1)  # Reduce padding
        )
    
    def create_controls_panel(self) -> Panel:
        """Create colorful controls and navigation panel"""
        controls_text = Text()
        controls_text.append("🎮✨ CONTROLS ✨🎮\n", style="bold cyan")  # Removed extra \n
        controls_text.append("🎨 S", style="bold green on black")
        controls_text.append(" - Styleframes  ", style="bright_cyan")
        controls_text.append("🎬 V", style="bold green on black") 
        controls_text.append(" - Video\n", style="bright_magenta")
        controls_text.append("📊 M", style="bold green on black")
        controls_text.append(" - Monitor     ", style="bright_blue")
        controls_text.append("📚 D", style="bold green on black")
        controls_text.append(" - Story\n", style="bright_yellow")
        controls_text.append("🏥 H", style="bold green on black")
        controls_text.append(" - Health      ", style="bright_green")
        controls_text.append("🔄 R", style="bold green on black")
        controls_text.append(" - Refresh\n", style="bright_white")
        controls_text.append("❌ Q", style="bold red on black")
        controls_text.append(" - Quit        ", style="bright_red")
        controls_text.append("✨ Ctrl+C to return! ✨", style="dim italic yellow")
        
        return Panel(
            controls_text,
            title="🎮 Navigation 🎮",
            border_style="bright_green",
            padding=(0, 1)  # Reduce padding
        )
    
    def create_main_layout(self) -> Layout:
        """Create the main dashboard layout with adaptive sizing"""
        status = self.get_tool_status()
        
        # Check terminal size for responsive design
        term_width, term_height = self.console.size
        
        # Calculate 90% height usage
        content_height = int(term_height * 0.9)
        padding_total = term_height - content_height
        top_padding = padding_total
        
        # Adaptive layout
        layout = Layout()
        
        # Header with logo
        header = Panel(
            Align.center(self.create_ascii_logo()),
            style="bold cyan",
            padding=(0, 0)  # No padding
        )
        
        # Tool cards
        tool_cards = self.create_tool_cards(status)
        
        # Stats and controls row - more compact
        stats = self.create_quick_stats(status)
        controls = self.create_controls_panel()
        
        # Create bottom section with tighter spacing
        bottom_layout = Layout()
        bottom_layout.split_row(
            Layout(stats, name="stats"),
            Layout(controls, name="controls")
        )
        
        # Assemble main content layout - using only ratios for proper scaling
        content_layout = Layout()
        
        # Use proportional sizing that adapts to any terminal height
        # Remove minimum_size constraints to allow proper shrinking/expanding
        content_layout.split_column(
            Layout(header, ratio=3, name="header"),      # Logo gets more space
            Layout(tool_cards, ratio=4, name="tools"),   # Tool cards get most space
            Layout(bottom_layout, ratio=2, name="bottom") # Controls/stats get less
        )
        
        # Wrap everything in a main border - no padding
        main_panel = Panel(
            content_layout,
            title="🌪️ STORMLIGHT CONTROL CENTER 🌪️",
            padding=(0, 0)
        )
        
        # Create responsive layout using 90% of terminal height
        padded_layout = Layout()
        padded_layout.split_column(
            Layout(size=top_padding),  # Top padding
            Layout(main_panel, size=content_height),  # Main content at 90% height
        )
        
        # Final layout with responsive sizing
        layout.add_split(padded_layout)
        
        return layout
    
    async def launch_tool(self, tool: str):
        """Launch a specific tool"""
        commands = {
            'S': ['python3', 'tools/styleframe_manager.py', 'interactive', 'new_scene', 'Scene description here'],
            'V': ['python3', 'tools/generate_veo3.py', '--help'],
            'M': ['python3', 'tools/pipeline_monitor.py', '--dashboard'],
            'D': ['ls', '07_story_development/'],
            'H': ['python3', 'tools/pipeline_monitor.py', '--health-check']
        }
        
        if tool in commands:
            console.clear()
            console.print(f"[bold green]Launching {tool}...[/bold green]")
            
            if tool == 'S':
                console.print("\n[bold yellow]🎨✨ Styleframe Manager - Interactive Mode ✨🎨[/bold yellow]")
                console.print("[dim]💡 Tip: Press Ctrl+C in the styleframe manager to return here![/dim]")
                
                # Offer auto-detection or manual input
                if Confirm.ask("🔍 Auto-detect next clip from story development?", default=True):
                    try:
                        subprocess.run(['python3', 'tools/styleframe_manager.py', 'interactive'])
                    except KeyboardInterrupt:
                        console.print("\n[green]✨ Returned to Control Center! ✨[/green]")
                else:
                    scene = Prompt.ask("🎭 Scene name (e.g., 'title_sequence')", default="new_scene")
                    description = Prompt.ask("📝 Scene description", default="Your scene description here")
                    try:
                        subprocess.run(['python3', 'tools/styleframe_manager.py', 'interactive', scene, description])
                    except KeyboardInterrupt:
                        console.print("\n[green]✨ Returned to Control Center! ✨[/green]")
            elif tool == 'V':
                console.print("\n[bold yellow]🎬✨ Video Generator - Interactive Mode ✨🎬[/bold yellow]")
                console.print("[dim]💡 Tip: Press Ctrl+C to return to Control Center![/dim]")
                try:
                    subprocess.run(['python3', 'tools/generate_veo3.py'])
                except KeyboardInterrupt:
                    console.print("\n[green]✨ Returned to Control Center! ✨[/green]")
            elif tool == 'D':
                console.print("\n[yellow]Story Development Files:[/yellow]")
                subprocess.run(commands[tool])
                console.print("\nUse your editor to view/edit story files in 07_story_development/")
            else:
                subprocess.run(commands[tool])
            
            console.print("\n[dim]Press Enter to return to Control Center...[/dim]")
            input()
    
    async def run_interactive(self):
        """Run the interactive control center"""
        while True:
            console.clear()
            
            # Get terminal size
            term_width, term_height = console.size
            
            # Let Rich handle the layout naturally - no fixed height
            # The layout will expand to fill available space properly
            layout = self.create_main_layout()
            console.print(layout)
            
            # Get user input
            try:
                key = console.input("\n[bold cyan]Choose an option: [/bold cyan]").upper()
                
                if key == 'Q':
                    console.print("\n[bold green]👋 Thanks for using Stormlight Control Center![/bold green]")
                    console.print("[dim]May the storms guide your creativity! 🌪️✨[/dim]")
                    break
                elif key == 'R':
                    console.print("\n[yellow]🔄 Refreshing status...[/yellow]")
                    await asyncio.sleep(1)
                    continue
                elif key in ['S', 'V', 'M', 'D', 'H']:
                    await self.launch_tool(key)
                else:
                    console.print(f"\n[red]Unknown option: {key}[/red]")
                    await asyncio.sleep(1)
                    
            except KeyboardInterrupt:
                console.print("\n[bold green]👋 Thanks for using Stormlight Control Center![/bold green]")
                break
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")
                await asyncio.sleep(2)


def main():
    """CLI interface for Stormlight Control Center"""
    parser = argparse.ArgumentParser(description="🌪️ Stormlight Control Center - Beautiful Meta Dashboard")
    parser.add_argument("--version", action="version", version="Stormlight Control v1.0")
    
    args = parser.parse_args()
    
    control = StormlightControl()
    
    try:
        asyncio.run(control.run_interactive())
    except KeyboardInterrupt:
        console.print("\n[bold green]👋 Goodbye![/bold green]")


if __name__ == "__main__":
    main()
