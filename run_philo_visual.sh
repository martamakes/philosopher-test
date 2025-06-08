#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="../philo"
VISUALIZER_SCRIPT="/Users/marta/Documents/PROJECTS/philosopher_visualizer_simple.py"

echo -e "${BLUE}===== PHILOSOPHERS VISUALIZATION =====${NC}"

# Make sure the visualizer script is executable
chmod +x "${VISUALIZER_SCRIPT}"

# Check if philo executable exists, if not compile it
if [ ! -f "$PROJECT_DIR/philo" ]; then
    echo -e "${YELLOW}Philo executable not found. Compiling...${NC}"
    cd "$PROJECT_DIR" || { echo -e "${RED}Error: Could not change to project directory${NC}"; exit 1; }
    make
    if [ ! -f "$PROJECT_DIR/philo" ]; then
        echo -e "${RED}Error: Compilation failed${NC}"
        exit 1
    fi
    echo -e "${GREEN}Compilation successful!${NC}"
fi

# Run the visualizer
python3 "${VISUALIZER_SCRIPT}" "${PROJECT_DIR}/philo" "$@"
