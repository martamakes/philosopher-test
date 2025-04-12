#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/Users/marta/Documents/PROJECTS/philo"
TESTER_SCRIPT="/Users/marta/Documents/PROJECTS/philosopher_tester_simple.py"

echo -e "${BLUE}===== PHILOSOPHERS PROJECT TESTER =====${NC}"
echo -e "${BLUE}=== Compilation and Testing Script ===${NC}"
echo

# Make sure we're in the right directory
cd "$PROJECT_DIR" || { echo -e "${RED}Error: Could not change to project directory${NC}"; exit 1; }

# Clean and recompile the project
echo -e "${YELLOW}Cleaning project...${NC}"
make fclean
echo -e "${YELLOW}Compiling project...${NC}"
make

# Check if compilation was successful
if [ ! -f "$PROJECT_DIR/philo" ]; then
    echo -e "${RED}Error: Compilation failed or executable not found${NC}"
    exit 1
fi
echo -e "${GREEN}Compilation successful!${NC}"
echo

# Run the tests
echo -e "${YELLOW}Running tests...${NC}"
python3 "$TESTER_SCRIPT" "$PROJECT_DIR/philo"

# Optional: Run memory tests
echo
echo -e "${YELLOW}Do you want to run a memory check? (y/n)${NC}"
read -r run_memcheck

if [[ "$run_memcheck" == "y" || "$run_memcheck" == "Y" ]]; then
    # Detect operating system
    if [[ "$(uname)" == "Darwin" ]]; then
        # macOS - use leaks command
        if command -v leaks &> /dev/null; then
            echo -e "${YELLOW}Running memory check with leaks (macOS)...${NC}"
            # Use a small number of philosophers and meals to ensure it terminates
            echo -e "${YELLOW}This will run a small test case. Press Ctrl+C after a few seconds to see leak report.${NC}"
            echo -e "${YELLOW}Starting test in 3 seconds...${NC}"
            sleep 3
            leaks --atExit -- "$PROJECT_DIR/philo" 3 800 200 200 5
        else
            echo -e "${RED}The 'leaks' command is not available on your macOS system.${NC}"
            echo -e "${YELLOW}You can manually check for leaks using:${NC}"
            echo -e "${GREEN}leaks --atExit -- $PROJECT_DIR/philo 3 800 200 200 5${NC}"
        fi
    else
        # Linux - use valgrind
        if command -v valgrind &> /dev/null; then
            echo -e "${YELLOW}Running memory check with valgrind (Linux)...${NC}"
            valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes "$PROJECT_DIR/philo" 3 800 200 200 5
        else
            echo -e "${RED}Valgrind is not installed. Skipping memory check.${NC}"
            echo -e "${YELLOW}You can install valgrind with:${NC}"
            echo -e "${GREEN}sudo apt-get install valgrind${NC} (Debian/Ubuntu)"
            echo -e "${GREEN}sudo yum install valgrind${NC} (CentOS/RHEL/Fedora)"
        fi
    fi
fi

echo
echo -e "${BLUE}===== Test run complete =====${NC}"
