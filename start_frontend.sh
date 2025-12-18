#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

BAR_WIDTH=30

progress_bar() {
    local current=$1
    local total=$2
    local pct=0
    if [ "$total" -gt 0 ]; then
        pct=$((current * 100 / total))
    fi
    local filled=$((pct * BAR_WIDTH / 100))
    local empty=$((BAR_WIDTH - filled))
    [ "$filled" -lt 0 ] && filled=0
    [ "$empty" -lt 0 ] && empty=0
    local bar_filled
    local bar_empty
    bar_filled=$(printf "%${filled}s" "" | tr ' ' '#')
    bar_empty=$(printf "%${empty}s" "" | tr ' ' '.')
    printf "\r${GREEN}[2/2] Installing packages from requirements.txt...${NC} [${GREEN}%s${NC}%s] %3d%%" "$bar_filled" "$bar_empty" "$pct"
}

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Clear screen and show welcome message
clear
echo ""
echo -e "${BLUE}  Welcome to use AI Annual Summary Tool!${NC}"
echo -e "${BLUE}  Just wait a second to build the dependencies...${NC}"
echo ""

# Change to script directory
cd "$SCRIPT_DIR"

# Silent check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠ Python3 not found. Please install Python3 first.${NC}"
    exit 1
fi

# Silent check for deepseek.py
if [ ! -f "$SCRIPT_DIR/deepseek.py" ]; then
    echo -e "${YELLOW}⚠ deepseek.py not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Check if dependencies need to be installed
NEED_INSTALL=false

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    NEED_INSTALL=true
    python3 -m venv venv > /dev/null 2>&1
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are already installed
if [ ! -f "venv/.deps_installed" ]; then
    NEED_INSTALL=true
fi

# Install dependencies with progress indication
if [ "$NEED_INSTALL" = true ]; then
    echo -e "${BOLD}${CYAN}  Installing dependencies...${NC}"
    echo ""

    # Install Flask and Flask-CORS first
    echo -ne "${GREEN}[1/2] Installing Flask...${NC}"
    pip install -q flask flask-cors --upgrade 2>&1 | grep -v "WARNING: Ignoring invalid distribution" || true
    echo -e " ${GREEN}✓${NC}"

    # Install requirements.txt with a filling progress bar
    if [ -f "requirements.txt" ]; then
        TOTAL=$(grep -E "^[A-Za-z0-9]" requirements.txt | wc -l | tr -d ' ')
        [ -z "$TOTAL" ] && TOTAL=0
        CURRENT=0

        # Start progress bar line
        progress_bar "$CURRENT" "$TOTAL"

        pip install -r requirements.txt 2>&1 | \
            grep -v "WARNING: Ignoring invalid distribution" | \
            grep -v "Requirement already satisfied" | \
            while IFS= read -r line; do
                if [[ "$line" == Collecting* ]]; then
                    CURRENT=$((CURRENT + 1))
                    if [ "$CURRENT" -gt "$TOTAL" ]; then
                        TOTAL=$CURRENT
                    fi
                    progress_bar "$CURRENT" "$TOTAL"
                fi
            done

        # Finish progress bar
        CURRENT=$TOTAL
        progress_bar "$CURRENT" "$TOTAL"
        echo -e " ${GREEN}✓${NC}"
    fi

    # Mark as installed
    touch venv/.deps_installed
    echo ""
fi

# Show completion message
echo -e "${NC} ${CYAN} Dependencies done!${NC} ${CYAN}Now trying to start the server...${NC}"
echo ""

# Run the Flask app
python3 deepseek.py
