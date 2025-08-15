#!/usr/bin/env bash
#
# Shell Configuration Fix Script for Stormlight Short Film Project
# ================================================================
#
# This script fixes common shell configuration issues, particularly with Google Cloud SDK paths.
# It creates a robust configuration that survives version updates.
#
# Usage: ./tools/fix_shell_config.sh [--dry-run]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DRY_RUN=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}" >&2
            echo "Usage: $0 [--dry-run]"
            exit 1
            ;;
    esac
done

log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Backup existing configuration
backup_config() {
    local config_file="$1"
    if [[ -f "$config_file" ]]; then
        local backup_file="${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
        if [[ "$DRY_RUN" == "false" ]]; then
            cp "$config_file" "$backup_file"
            log "Backed up $config_file to $backup_file"
        else
            log "[DRY-RUN] Would backup $config_file to $backup_file"
        fi
    fi
}

# Find Google Cloud SDK installation
find_gcloud_sdk() {
    local gcloud_path
    gcloud_path=$(which gcloud 2>/dev/null || echo "")
    
    if [[ -n "$gcloud_path" && -L "$gcloud_path" ]]; then
        # Follow the symlink to find the actual installation
        local real_path
        real_path=$(readlink "$gcloud_path")
        local sdk_dir
        sdk_dir=$(dirname "$(dirname "$real_path")")
        echo "$sdk_dir"
    else
        # Try common Homebrew installation paths
        for version_dir in /opt/homebrew/Caskroom/gcloud-cli/*/google-cloud-sdk; do
            if [[ -d "$version_dir" ]]; then
                echo "$version_dir"
                return
            fi
        done
        
        # Try other common paths
        for sdk_path in \
            "/opt/homebrew/Caskroom/google-cloud-sdk/latest/google-cloud-sdk" \
            "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk" \
            "$HOME/google-cloud-sdk"; do
            if [[ -d "$sdk_path" ]]; then
                echo "$sdk_path"
                return
            fi
        done
        
        echo ""
    fi
}

# Generate robust Google Cloud SDK configuration
generate_gcloud_config() {
    cat << 'EOF'

# ================================
# Google Cloud SDK Configuration
# ================================
# Auto-detects Google Cloud SDK installation and loads shell integration
# This configuration is version-agnostic and works with Homebrew installations

# Function to safely source Google Cloud SDK files
_source_gcloud_file() {
    local file="$1"
    if [[ -f "$file" ]]; then
        # shellcheck source=/dev/null
        source "$file"
        return 0
    fi
    return 1
}

# Find and configure Google Cloud SDK
_setup_gcloud_sdk() {
    local gcloud_sdk_dir=""
    
    # Method 1: Follow gcloud symlink if it exists
    if command -v gcloud >/dev/null 2>&1; then
        local gcloud_path
        gcloud_path=$(command -v gcloud)
        if [[ -L "$gcloud_path" ]]; then
            local real_path
            real_path=$(readlink "$gcloud_path")
            gcloud_sdk_dir=$(dirname "$(dirname "$real_path")")
        fi
    fi
    
    # Method 2: Search common Homebrew locations
    if [[ -z "$gcloud_sdk_dir" || ! -d "$gcloud_sdk_dir" ]]; then
        for candidate in /opt/homebrew/Caskroom/gcloud-cli/*/google-cloud-sdk; do
            if [[ -d "$candidate" ]]; then
                gcloud_sdk_dir="$candidate"
                break
            fi
        done
    fi
    
    # Method 3: Try other common locations
    if [[ -z "$gcloud_sdk_dir" || ! -d "$gcloud_sdk_dir" ]]; then
        for candidate in \
            "/opt/homebrew/Caskroom/google-cloud-sdk/latest/google-cloud-sdk" \
            "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk" \
            "$HOME/google-cloud-sdk"; do
            if [[ -d "$candidate" ]]; then
                gcloud_sdk_dir="$candidate"
                break
            fi
        done
    fi
    
    # Load Google Cloud SDK integration if found
    if [[ -n "$gcloud_sdk_dir" && -d "$gcloud_sdk_dir" ]]; then
        # Load path configuration
        _source_gcloud_file "$gcloud_sdk_dir/path.zsh.inc" || \
        _source_gcloud_file "$gcloud_sdk_dir/path.bash.inc"
        
        # Load command completion
        _source_gcloud_file "$gcloud_sdk_dir/completion.zsh.inc" || \
        _source_gcloud_file "$gcloud_sdk_dir/completion.bash.inc"
        
        export GCLOUD_SDK_DIR="$gcloud_sdk_dir"
    else
        echo "Warning: Google Cloud SDK not found in common locations" >&2
        echo "Please ensure gcloud is installed via: brew install --cask gcloud-cli" >&2
    fi
}

# Initialize Google Cloud SDK
_setup_gcloud_sdk

# Clean up helper functions
unset -f _source_gcloud_file _setup_gcloud_sdk
EOF
}

# Fix .zprofile
fix_zprofile() {
    local zprofile="$HOME/.zprofile"
    log "Fixing $zprofile..."
    
    backup_config "$zprofile"
    
    # Remove old Google Cloud SDK lines
    if [[ -f "$zprofile" ]]; then
        if [[ "$DRY_RUN" == "false" ]]; then
            # Create temporary file with old Google Cloud lines removed
            grep -v 'google-cloud-sdk\|gcloud-cli' "$zprofile" > "${zprofile}.tmp" || true
            mv "${zprofile}.tmp" "$zprofile"
        else
            log "[DRY-RUN] Would remove old Google Cloud SDK configuration lines"
        fi
    fi
    
    # Add new configuration
    if [[ "$DRY_RUN" == "false" ]]; then
        generate_gcloud_config >> "$zprofile"
        log "Added robust Google Cloud SDK configuration to $zprofile"
    else
        log "[DRY-RUN] Would add new Google Cloud SDK configuration"
    fi
}

# Fix .zshrc (if it exists and has gcloud config)
fix_zshrc() {
    local zshrc="$HOME/.zshrc"
    if [[ -f "$zshrc" ]] && grep -q "google-cloud-sdk\|gcloud-cli" "$zshrc"; then
        log "Found Google Cloud SDK references in $zshrc, fixing..."
        
        backup_config "$zshrc"
        
        if [[ "$DRY_RUN" == "false" ]]; then
            # Remove old lines and add a note
            grep -v 'google-cloud-sdk\|gcloud-cli' "$zshrc" > "${zshrc}.tmp" || true
            echo "" >> "${zshrc}.tmp"
            echo "# Google Cloud SDK configuration moved to ~/.zprofile" >> "${zshrc}.tmp"
            mv "${zshrc}.tmp" "$zshrc"
            log "Cleaned up $zshrc and added reference note"
        else
            log "[DRY-RUN] Would clean up $zshrc"
        fi
    fi
}

# Verify installation
verify_setup() {
    log "Verifying Google Cloud SDK setup..."
    
    local gcloud_sdk_dir
    gcloud_sdk_dir=$(find_gcloud_sdk)
    
    if [[ -n "$gcloud_sdk_dir" ]]; then
        success "Google Cloud SDK found at: $gcloud_sdk_dir"
        
        # Check if required files exist
        local files_to_check=(
            "$gcloud_sdk_dir/path.zsh.inc"
            "$gcloud_sdk_dir/completion.zsh.inc"
            "$gcloud_sdk_dir/path.bash.inc"
            "$gcloud_sdk_dir/completion.bash.inc"
        )
        
        local found_files=0
        for file in "${files_to_check[@]}"; do
            if [[ -f "$file" ]]; then
                ((found_files++))
                log "✓ Found: $(basename "$file")"
            fi
        done
        
        if [[ $found_files -gt 0 ]]; then
            success "Google Cloud SDK shell integration files are available"
        else
            warn "No shell integration files found - SDK may need reinstallation"
        fi
    else
        error "Google Cloud SDK not found!"
        error "Please install with: brew install --cask gcloud-cli"
        return 1
    fi
    
    # Test gcloud command
    if command -v gcloud >/dev/null 2>&1; then
        local gcloud_version
        gcloud_version=$(gcloud version --format="value(Google Cloud SDK)" 2>/dev/null || echo "unknown")
        success "gcloud command available (version: $gcloud_version)"
    else
        warn "gcloud command not available - may need to restart shell"
    fi
}

# Main execution
main() {
    log "Starting shell configuration fix..."
    log "Working directory: $PROJECT_ROOT"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        warn "DRY RUN MODE - No changes will be made"
    fi
    
    # Fix configurations
    fix_zprofile
    fix_zshrc
    
    # Verify setup
    verify_setup
    
    if [[ "$DRY_RUN" == "false" ]]; then
        success "Shell configuration fixed!"
        warn "Please restart your shell or run: source ~/.zprofile"
        log "You can test the fix with: gcloud --version"
    else
        log "[DRY-RUN] Configuration check completed"
    fi
}

# Run main function
main "$@"