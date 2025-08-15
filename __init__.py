"""
Stormlight Short Film Production Pipeline

A comprehensive pipeline for generating cinematic sequences for the Stormlight Archives short film
using AI-generated style frames, vertex AI processing, and automated workflow management.

This package provides:
- Midjourney style frame management
- Vertex AI video generation jobs
- Automated sync and backup systems
- Flow diagram exports
- Audio integration tools
- Final Cut Pro integration
"""

__version__ = "0.1.0"
__author__ = "Stormlight Short Production Team"
__description__ = "AI-powered short film production pipeline for Stormlight Archives"

# Core modules
from . import tools
from . import config

# Version info
version_info = tuple(map(int, __version__.split(".")))

# Main pipeline components
__all__ = [
    "tools",
    "config",
    "__version__",
    "version_info"
]