# Philosophers Project Testing Guide

This documentation explains how to use the testing tools for your Philosophers project.

## Overview

The testing suite includes:

1. `philosopher_tester_simple.py` - A Python script that automates testing of your Philosophers implementation
2. `run_philo_tests.sh` - A shell script that compiles your project and runs the tests
3. `philosophers_eval_checklist.md` - A comprehensive checklist for evaluation preparation

## Requirements

- Python 3.x
- Bash shell
- Valgrind (optional, for memory testing)

## Running the Tests

### Option 1: Using the Shell Script

The easiest way to run all tests is to use the provided shell script:

```bash
# Make the script executable
chmod +x /Users/marta/Documents/PROJECTS/run_philo_tests.sh

# Run the script
/Users/marta/Documents/PROJECTS/run_philo_tests.sh
```

This script will:
1. Clean and recompile your project
2. Run all the automated tests
3. Optionally run a memory check with valgrind

### Option 2: Running the Python Tester Directly

You can also run the Python tester directly:

```bash
python3 /Users/marta/Documents/PROJECTS/philosopher_tester_simple.py [path_to_philo_executable]
```

If you don't provide a path, it defaults to `/Users/marta/Documents/PROJECTS/philo/philo`.

## Understanding the Tests

The tester performs the following checks:

1. **Basic Format Test** - Ensures your program outputs messages in the correct format
2. **Death Detection Test** - Verifies that philosopher death is detected and reported within 10ms
3. **One Philosopher Test** - Tests the edge case with only one philosopher
4. **Stop After Meals Test** - Checks that the simulation stops correctly when all philosophers eat enough times
5. **Error Handling Test** - Tests how your program handles various invalid inputs
6. **Deadlock Test** - Verifies that no deadlocks occur and all philosophers get to eat
7. **Stress Test** - Checks that your program can handle many philosophers without crashing

## Preparing for Evaluation

Use the provided checklist (`philosophers_eval_checklist.md`) to ensure your project meets all requirements before submission:

1. Go through each item in the checklist
2. Run the automated tests to catch any obvious issues
3. Perform manual testing for scenarios not covered by the automated tests
4. Practice explaining your implementation (common evaluation questions are listed in the checklist)

## Manual Testing Commands

Here are some commands you can use for manual testing:

```bash
# Basic test - should run indefinitely
./philo 5 800 200 200

# Death test - should result in death
./philo 4 310 200 100

# Meals test - should stop after all eat 7 times
./philo 5 800 200 200 7

# One philosopher - should take fork and die
./philo 1 800 200 200

# Stress test - many philosophers
./philo 100 800 200 200

# Invalid inputs
./philo                     # Too few arguments
./philo 5 -800 200 200      # Negative number
./philo 5 800 200 200 0     # Zero times to eat
./philo 5 abc 200 200       # Non-numeric input
```

## Memory Testing

To check for memory leaks:

```bash
valgrind --leak-check=full --show-leak-kinds=all ./philo 5 800 200 200
```

## Good luck with your evaluation!

Remember that understanding your code and being able to explain your implementation decisions is as important as having a working program.
