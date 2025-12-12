#!/bin/bash

# DeepSeek Annual Summary Frontend Launcher
# This script starts the Flask server for the annual summary tool

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}DeepSeek Annual Summary Tool${NC}"
echo -e "${GREEN}===============================================${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found. Please install Python3 first.${NC}"
    exit 1
fi

echo -e "${YELLOW}✓ Python3 found: $(python3 --version)${NC}"

# Check if we're in the right directory
if [ ! -f "$SCRIPT_DIR/deepseek.py" ]; then
    echo -e "${RED}❌ deepseek.py not found in $SCRIPT_DIR${NC}"
    echo -e "${YELLOW}Make sure this script is in the GPT-Rewind directory.${NC}"
    exit 1
fi

echo -e "${YELLOW}✓ Project files found${NC}"

# Change to script directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists, if not create one
if [ ! -d "venv" ]; then
    echo ""
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade required packages
echo ""
echo -e "${YELLOW}Installing required packages...${NC}"
pip install -q flask flask-cors --upgrade

# Check if additional dependencies are needed
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}Installing project dependencies from requirements.txt...${NC}"
    pip install -q -r requirements.txt || echo -e "${YELLOW}Warning: Some dependencies may have failed to install${NC}"
fi

# Start the server
echo ""
echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}Starting DeepSeek Annual Summary Server${NC}"
echo -e "${GREEN}===============================================${NC}"
echo ""
echo -e "${GREEN}✓ Server starting at http://localhost:5000${NC}"
echo -e "${GREEN}✓ Open your browser and navigate to the URL above${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Run the Flask app
python3 deepseek.py
