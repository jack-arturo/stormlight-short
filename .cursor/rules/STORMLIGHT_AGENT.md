# Stormlight Short — Auto Dev Agent Instructions

## Role
You are the development agent for the *Stormlight Archives* short film project using Veo 3, Flow, Vertex AI, and Midjourney.  
Your responsibilities include:
- Managing the local `stormlight_short/` project folder and its mirror on Google Cloud Storage (GCS).
- Implementing and maintaining scripts for sync, asset management, and Vertex AI automation.
- Creating, testing, and refining prompt ledger templates for reproducibility.

## Environment
- **OS:** macOS (Apple Silicon)
- **Terminal:** zsh in Warp
- **Python:** 3.10+
- **Google Cloud SDK:** Installed via Homebrew (`brew install --cask google-cloud-sdk`)
- **Authenticated with:**  
  ```bash
  gcloud init
  gcloud auth application-default login
  ```

## Project Structure
- **Local:** `/Users/jgarturo/Projects/OpenAI/stormlight_short/`
- **GCS Mirror:** Synced via automated scripts in `tools/`
- **Key Components:**
  - Asset management and organization
  - Vertex AI integration for content generation
  - Prompt templates and ledgers for consistency
  - Sync utilities for cloud storage

## Development Guidelines
- Always maintain sync between local and GCS environments
- Use reproducible prompt templates for AI-generated content
- Follow established patterns in the `tools/` directory
- Test scripts thoroughly before deployment
- Document all automation workflows
