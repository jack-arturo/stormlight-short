#!/bin/bash
# 🚀 Stormlight Short - Production Pipeline Launcher
# One-click launch for the complete AI video generation pipeline

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Banner
echo -e "${CYAN}"
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║   _____ _                       _ _       _     _         ║
║  / ____| |                     | (_)     | |   | |        ║
║ | (___ | |_ ___  _ __ _ __ ___ | |_  __ _| |__ | |_       ║
║  \___ \| __/ _ \| '__| '_ ` _ \| | |/ _` | '_ \| __|      ║
║  ____) | || (_) | |  | | | | | | | | (_| | | | | |_       ║
║ |_____/ \__\___/|_|  |_| |_| |_|_|_|\__, |_| |_|\__|      ║
║                                       __/ |                ║
║           Short Film AI Pipeline    |___/     v1.0        ║
╚════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✅ Python3 installed$(python3 --version)${NC}"
    else
        echo -e "${RED}❌ Python3 not found${NC}"
        exit 1
    fi
    
    # Check gcloud
    if command -v gcloud &> /dev/null; then
        echo -e "${GREEN}✅ Google Cloud SDK installed${NC}"
    else
        echo -e "${RED}❌ Google Cloud SDK not found${NC}"
        echo "Install with: brew install --cask google-cloud-sdk"
        exit 1
    fi
    
    # Check authentication
    if gcloud auth list --format="value(account)" | grep -q "@"; then
        echo -e "${GREEN}✅ GCP authenticated${NC}"
    else
        echo -e "${YELLOW}⚠️  Not authenticated. Running: gcloud auth application-default login${NC}"
        gcloud auth application-default login
    fi
}

# Function to install dependencies
install_dependencies() {
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    pip3 install -q -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Function to validate configuration
validate_config() {
    echo -e "${YELLOW}⚙️  Validating configuration...${NC}"
    python3 tools/master_pipeline.py --validate
}

# Function to show menu
show_menu() {
    echo -e "\n${CYAN}🎬 Stormlight Short - Main Menu${NC}\n"
    echo "1) 📊 Monitor Dashboard - Real-time pipeline monitoring"
    echo "2) 🎯 Run Test Scene - Test with a single scene"
    echo "3) 🚀 Run Full Pipeline - Process all scenes"
    echo "4) 📝 Create Batch Job - Submit multiple Vertex AI jobs"
    echo "5) 🔄 Sync to GCS - Sync local files to cloud storage"
    echo "6) 🏥 Health Check - Check system status"
    echo "7) 📖 View Documentation - Open project docs"
    echo "8) ⚙️  Configure Project - Edit pipeline settings"
    echo "9) 🛠️  Fix Shell Config - Repair Google Cloud SDK paths"
    echo "0) 🚪 Exit"
    echo ""
}

# Function to run monitor
run_monitor() {
    echo -e "${GREEN}🖥️  Launching Pipeline Monitor...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to return to menu${NC}\n"
    python3 tools/pipeline_monitor.py --dashboard
}

# Function to run test scene
run_test_scene() {
    echo -e "${CYAN}Available scenes:${NC}"
    echo "  - opening_kaladin"
    echo "  - bridge_run"
    echo "  - spren_encounter"
    echo "  - stormwall"
    echo ""
    read -p "Enter scene name to test: " scene_name
    
    echo -e "${GREEN}🧪 Running test for scene: $scene_name${NC}"
    python3 tools/master_pipeline.py --test-scene "$scene_name"
}

# Function to run full pipeline
run_full_pipeline() {
    echo -e "${RED}⚠️  WARNING: This will submit real Vertex AI jobs and incur costs!${NC}"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        echo -e "${GREEN}🚀 Starting full pipeline execution...${NC}"
        python3 tools/master_pipeline.py --full-pipeline
    else
        echo -e "${YELLOW}Pipeline execution cancelled${NC}"
    fi
}

# Function to create batch job
create_batch_job() {
    echo -e "${CYAN}📝 Creating batch job configuration...${NC}"
    
    if [ -f "02_prompts/batch_example.json" ]; then
        echo -e "${GREEN}Using example batch configuration${NC}"
        python3 tools/vertex_manager.py --batch-config 02_prompts/batch_example.json
    else
        echo -e "${YELLOW}No batch configuration found. Create one in 02_prompts/batch_example.json${NC}"
    fi
}

# Function to sync to GCS
sync_to_gcs() {
    echo -e "${CYAN}🔄 Syncing to Google Cloud Storage...${NC}"
    echo "1) Dry run (preview changes)"
    echo "2) Real sync"
    echo "3) Sync with delete (remove cloud files not in local)"
    read -p "Select option: " sync_option
    
    case $sync_option in
        1)
            python3 tools/sync_to_gcs.py.py \
                --local . \
                --bucket stormlight-short \
                --dry-run
            ;;
        2)
            python3 tools/sync_to_gcs.py.py \
                --local . \
                --bucket stormlight-short
            ;;
        3)
            echo -e "${RED}⚠️  This will delete cloud files not present locally!${NC}"
            read -p "Are you sure? (yes/no): " confirm_delete
            if [ "$confirm_delete" = "yes" ]; then
                python3 tools/sync_to_gcs.py.py \
                    --local . \
                    --bucket stormlight-short \
                    --delete
            fi
            ;;
    esac
}

# Function to run health check
run_health_check() {
    echo -e "${CYAN}🏥 Running Pipeline Health Check...${NC}\n"
    python3 tools/pipeline_monitor.py --health-check
}

# Function to view documentation
view_docs() {
    echo -e "${CYAN}📖 Project Documentation${NC}\n"
    echo "1) View README"
    echo "2) View CLAUDE.md"
    echo "3) View SETUP.md"
    echo "4) View Tools Documentation"
    read -p "Select document: " doc_choice
    
    case $doc_choice in
        1) less README.md ;;
        2) less CLAUDE.md ;;
        3) less SETUP.md ;;
        4) less tools/README.md ;;
    esac
}

# Function to configure project
configure_project() {
    echo -e "${CYAN}⚙️  Opening pipeline configuration...${NC}"
    ${EDITOR:-nano} config/pipeline_config.yaml
}

# Function to fix shell config
fix_shell_config() {
    echo -e "${CYAN}🛠️  Fixing Google Cloud SDK shell configuration...${NC}"
    bash tools/fix_shell_config.sh
    echo -e "${GREEN}✅ Shell configuration fixed. Restart terminal for changes to take effect.${NC}"
}

# Main script
main() {
    # Check prerequisites
    check_prerequisites
    
    # Install dependencies if needed
    if ! python3 -c "import google.cloud.aiplatform" 2>/dev/null; then
        install_dependencies
    fi
    
    # Main loop
    while true; do
        show_menu
        read -p "Select option (0-9): " choice
        
        case $choice in
            1) run_monitor ;;
            2) run_test_scene ;;
            3) run_full_pipeline ;;
            4) create_batch_job ;;
            5) sync_to_gcs ;;
            6) run_health_check ;;
            7) view_docs ;;
            8) configure_project ;;
            9) fix_shell_config ;;
            0) 
                echo -e "${GREEN}👋 Goodbye! May the Stormlight be with you.${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option. Please try again.${NC}"
                ;;
        esac
        
        echo -e "\n${YELLOW}Press Enter to continue...${NC}"
        read
    done
}

# Run main function
main