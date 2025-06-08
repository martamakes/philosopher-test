# Philosopher Project Testing Tools

This repository contains testing and visualization tools for the Philosopher project at 42 School.

## Installation

You can install these tools directly from your Philosopher project directory using:

```bash
make get-tools
```

This will:
1. Clone this repository into a `tests` folder in your philo project
2. Automatically fix paths in the scripts to work with your project structure
3. Make the shell scripts executable

## Usage

After installation, you can use the following commands from your philo project directory:

### Running Tests

```bash
make run-tests
```

This will:
1. Ensure your philo executable is compiled
2. Run a series of tests to validate your implementation
3. Display results showing which tests passed or failed

### Running the Visualizer

```bash
make run-visual [parameters]
```

For example:
```bash
make run-visual 5 800 200 200
```

This will:
1. Ensure your philo executable is compiled
2. Start the visualizer with the given parameters
3. Display a real-time visualization of your philosophers simulation

## Features

- Output format validation
- Death detection testing
- Single philosopher scenario testing
- Meal counting validation
- Error handling checks
- Deadlock and starvation detection
- Stress testing with many philosophers
- Real-time visualization of dining philosophers

## Updating

To update the tools to the latest version, simply run:

```bash
make get-tools
```

Again, and it will pull the latest changes from the repository.

## Notes

- The visualizer requires Python with matplotlib installed
- All tests are designed to be non-destructive and won't modify your project files
- Test results are printed to the console for easy diagnosis of issues
