#!/usr/bin/env python3
import subprocess
import time
import re
import os
import sys
import threading
from datetime import datetime
from collections import defaultdict

class PhilosopherVisualizer:
    def __init__(self, philo_path="/Users/marta/Documents/PROJECTS/philo/philo"):
        self.philo_path = philo_path
        self.process = None
        self.output_lines = []
        self.stop_thread = False
        self.output_thread = None
        self.eating_events = []
        self.fork_events = []
        self.philosopher_states = {}
        self.max_time = 0

    def run_simulation(self, args, timeout=20):
        """Run the philosopher simulation and collect data"""
        self.output_lines = []
        self.eating_events = []
        self.fork_events = []
        self.philosopher_states = {}
        self.stop_thread = False
        
        num_philosophers = int(args[0]) if len(args) > 0 else 5
        
        # Initialize philosopher states
        for i in range(1, num_philosophers + 1):
            self.philosopher_states[i] = {"state": "thinking", "forks": 0, "meals": 0, "last_change": 0}
        
        try:
            # Print simulation parameters
            print(f"\n{'=' * 60}")
            print(f" PHILOSOPHER SIMULATION ".center(60, '='))
            print(f"{'=' * 60}")
            print(f"Parameters: {' '.join(args)}")
            print(f"Running for {timeout} seconds...")
            print(f"{'=' * 60}\n")
            
            # Start the process
            self.process = subprocess.Popen(
                [self.philo_path] + args, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Start threads to capture output and display visualization
            self.output_thread = threading.Thread(target=self._capture_output)
            self.output_thread.start()
            
            display_thread = threading.Thread(target=self._display_live_visualization, args=(num_philosophers,))
            display_thread.start()
            
            # Wait for the process to complete or timeout
            start_time = time.time()
            while self.process.poll() is None and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            # Kill process if it's still running and we reached timeout
            if self.process.poll() is None:
                print("\nTerminating simulation...")
                self.process.terminate()
                time.sleep(0.2)
                if self.process.poll() is None:
                    self.process.kill()
            
            # Stop the output thread
            self.stop_thread = True
            self.output_thread.join()
            display_thread.join()
            
            # Process collected events
            self._process_events()
            
            # Generate statistics and visualization
            print("\n\n")
            self.print_statistics()
            self.create_ascii_visualization()
            
        except Exception as e:
            print(f"Error running simulation: {e}")
    
    def _capture_output(self):
        """Thread function to capture output from process"""
        while not self.stop_thread:
            if self.process.stdout:
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    self.output_lines.append(line)
                    self._parse_event(line)
                else:
                    break
        
        # Get any remaining output
        if self.process and self.process.stdout:
            remaining = self.process.stdout.readlines()
            for line in remaining:
                line = line.strip()
                self.output_lines.append(line)
                self._parse_event(line)
    
    def _parse_event(self, line):
        """Parse a line of output into event data"""
        pattern = r"^(\d+) (\d+) (.+)$"
        match = re.match(pattern, line)
        if not match:
            return
        
        timestamp = int(match.group(1))
        self.max_time = max(self.max_time, timestamp)
        philo_id = int(match.group(2))
        action = match.group(3)
        
        # Update philosopher state
        if action == "is eating":
            self.eating_events.append((timestamp, philo_id))
            self.philosopher_states[philo_id]["state"] = "eating"
            self.philosopher_states[philo_id]["meals"] += 1
            self.philosopher_states[philo_id]["last_change"] = timestamp
        elif action == "is sleeping":
            self.philosopher_states[philo_id]["state"] = "sleeping"
            self.philosopher_states[philo_id]["forks"] = 0
            self.philosopher_states[philo_id]["last_change"] = timestamp
        elif action == "is thinking":
            self.philosopher_states[philo_id]["state"] = "thinking"
            self.philosopher_states[philo_id]["last_change"] = timestamp
        elif action == "has taken a fork":
            self.fork_events.append((timestamp, philo_id))
            self.philosopher_states[philo_id]["forks"] += 1
            self.philosopher_states[philo_id]["last_change"] = timestamp
        elif action == "died":
            self.philosopher_states[philo_id]["state"] = "died"
            self.philosopher_states[philo_id]["last_change"] = timestamp
    
    def _display_live_visualization(self, num_philosophers):
        """Display a live text-based visualization of philosopher states"""
        state_icons = {
            "thinking": "🤔",
            "eating": "🍽️ ",
            "sleeping": "💤",
            "died": "💀"
        }
        
        fork_status = ["_"] * num_philosophers
        
        try:
            while not self.stop_thread:
                # Clear screen (use appropriate command for your OS)
                os.system('cls' if os.name == 'nt' else 'clear')
                
                # Show philosopher states
                print("\n" + "=" * 50)
                print(" PHILOSOPHERS SIMULATION ".center(50, '='))
                print("=" * 50)
                
                # Display table header
                print("\n{:<5} {:<10} {:<10} {:<8} {:<15}".format(
                    "ID", "State", "Forks", "Meals", "Last Change (ms)"
                ))
                print("-" * 50)
                
                # Display each philosopher's state
                for philo_id in sorted(self.philosopher_states.keys()):
                    state = self.philosopher_states[philo_id]["state"]
                    forks = self.philosopher_states[philo_id]["forks"]
                    meals = self.philosopher_states[philo_id]["meals"]
                    last_change = self.philosopher_states[philo_id]["last_change"]
                    
                    # Update fork display
                    if state == "eating":
                        # Both forks are in use by this philosopher
                        if philo_id == 1:
                            fork_status[0] = "1"
                            fork_status[num_philosophers-1] = "1"
                        else:
                            fork_status[philo_id-2] = str(philo_id)
                            fork_status[philo_id-1] = str(philo_id)
                    
                    print("{:<5} {:<2} {:<7} {:<10} {:<8} {:<15}".format(
                        philo_id, state_icons[state], state, forks, meals, last_change
                    ))
                
                # Display table for forks
                print("\n" + "-" * 50)
                print("Forks status (who's holding each fork):")
                print(" ".join([f"{i+1}:{s}" for i, s in enumerate(fork_status)]))
                print("-" * 50)
                
                # Print activity log (last 5 events)
                print("\nRecent events:")
                for line in self.output_lines[-5:]:
                    print(f"  {line}")
                
                time.sleep(0.5)  # Update every half second
                
        except Exception as e:
            print(f"Visualization error: {e}")
    
    def _process_events(self):
        """Process collected events to prepare for statistics and visualization"""
        self.eating_events.sort(key=lambda x: x[0])  # Sort by timestamp
        
        # Calculate intervals between meals for each philosopher
        self.meal_intervals = defaultdict(list)
        last_meal_time = {}
        
        for time, philo_id in self.eating_events:
            if philo_id in last_meal_time:
                interval = time - last_meal_time[philo_id]
                self.meal_intervals[philo_id].append(interval)
            last_meal_time[philo_id] = time
    
    def print_statistics(self):
        """Print detailed statistics about the simulation"""
        print("\n" + "=" * 70)
        print(" PHILOSOPHER STATISTICS ".center(70, '='))
        print("=" * 70)
        
        # Count eating events per philosopher
        eating_counts = defaultdict(int)
        for _, philo_id in self.eating_events:
            eating_counts[philo_id] += 1
        
        total_meals = sum(eating_counts.values())
        num_philosophers = len(self.philosopher_states)
        
        print(f"\nTotal simulation time: {self.max_time} ms")
        print(f"Total meals eaten: {total_meals}")
        print(f"Average meals per philosopher: {total_meals/num_philosophers:.2f}\n")
        
        # Print table header
        print("{:<5} {:<10} {:<15} {:<20} {:<20}".format(
            "ID", "Meals", "% of Total", "Avg Interval (ms)", "Last State"
        ))
        print("-" * 70)
        
        # Print each philosopher's stats
        for philo_id in sorted(self.philosopher_states.keys()):
            meals = eating_counts.get(philo_id, 0)
            percent = (meals / total_meals * 100) if total_meals > 0 else 0
            
            # Calculate average interval
            intervals = self.meal_intervals.get(philo_id, [])
            avg_interval = sum(intervals) / len(intervals) if intervals else "N/A"
            avg_interval_str = f"{avg_interval:.2f}" if isinstance(avg_interval, float) else avg_interval
            
            last_state = self.philosopher_states[philo_id]["state"]
            
            print("{:<5} {:<10} {:<15.2f} {:<20} {:<20}".format(
                philo_id, meals, percent, avg_interval_str, last_state
            ))
        
        # Detect potential issues
        all_ate = all(eating_counts.get(philo_id, 0) > 0 for philo_id in range(1, num_philosophers + 1))
        fair_distribution = True
        if all_ate and total_meals >= num_philosophers:
            avg_meals = total_meals / num_philosophers
            for philo_id in range(1, num_philosophers + 1):
                meals = eating_counts.get(philo_id, 0)
                if meals < avg_meals * 0.5:
                    fair_distribution = False
        
        print("\nDiagnosis:")
        if not all_ate:
            print("⚠️  ISSUE: Not all philosophers ate - potential deadlock detected")
            ate_count = len(eating_counts)
            print(f"   Only {ate_count} of {num_philosophers} philosophers ate")
        elif not fair_distribution:
            print("⚠️  ISSUE: Meal distribution is significantly uneven - potential starvation detected")
            print("   Some philosophers are getting far fewer meals than others")
        else:
            print("✅ No deadlocks or starvation detected")
            print("   All philosophers are eating with a fair meal distribution")
    
    def create_ascii_visualization(self):
        """Create an ASCII visualization of the simulation results"""
        print("\n\n" + "=" * 70)
        print(" PHILOSOPHER VISUALIZATION ".center(70, '='))
        print("=" * 70)
        
        # Count meals per philosopher
        eating_counts = defaultdict(int)
        for _, philo_id in self.eating_events:
            eating_counts[philo_id] += 1
        
        max_meals = max(eating_counts.values()) if eating_counts else 0
        scale_factor = 40 / max_meals if max_meals > 0 else 0
        
        print("\nMeals per philosopher (bar chart):")
        print("-" * 70)
        
        for philo_id in sorted(self.philosopher_states.keys()):
            meals = eating_counts.get(philo_id, 0)
            bar_length = int(meals * scale_factor)
            bar = "█" * bar_length
            print(f"Philosopher {philo_id}: {bar} {meals}")
        
        print("\nEating timeline (simplified, last 20 events):")
        print("-" * 70)
        
        # Create a simplified timeline of the last 20 eating events
        num_philosophers = len(self.philosopher_states)
        recent_events = self.eating_events[-20:] if len(self.eating_events) > 20 else self.eating_events
        
        # Group events by timestamp (rounded to nearest second)
        timeline = defaultdict(list)
        for time, philo_id in recent_events:
            # Round to nearest second for simplification
            rounded_time = (time // 1000) * 1000
            timeline[rounded_time].append(philo_id)
        
        # Sort by time
        sorted_times = sorted(timeline.keys())
        
        for t in sorted_times:
            philos = timeline[t]
            philo_str = ", ".join([str(p) for p in philos])
            print(f"Time {t} ms: Philosopher(s) {philo_str} eating")
        
        print("\nEating pattern:")
        print("-" * 70)
        
        # Create a simple visualization of eating patterns
        # Each row represents a philosopher, each column a time segment
        
        if not self.eating_events:
            print("No eating events recorded")
            return
        
        # Calculate time segments
        start_time = self.eating_events[0][0]
        end_time = self.max_time
        duration = end_time - start_time
        
        # Use a reasonable number of columns (time segments)
        num_cols = min(70, duration // 100 + 1)
        segment_size = duration / num_cols if num_cols > 0 else 1
        
        # Create a matrix of eating events
        pattern = [[' ' for _ in range(num_cols)] for _ in range(num_philosophers)]
        
        for time, philo_id in self.eating_events:
            col = min(int((time - start_time) / segment_size), num_cols - 1)
            row = philo_id - 1
            pattern[row][col] = 'E'
        
        # Print pattern
        print(f"Each 'E' represents an eating event, each column is ~{int(segment_size)} ms")
        print("Time --->")
        print(" " + "-" * num_cols)
        
        for i, row in enumerate(pattern):
            print(f"{i+1}|" + "".join(row))

if __name__ == "__main__":
    # Check if arguments are provided
    if len(sys.argv) < 2:
        print("Usage: python3 philosopher_visualizer_simple.py [philo_binary_path] [philosopher_args...]")
        print("Example: python3 philosopher_visualizer_simple.py ./philo 5 800 200 200")
        sys.exit(1)
    
    philo_path = sys.argv[1]
    args = sys.argv[2:]
    
    # Default arguments if none provided
    if not args:
        args = ["5", "800", "200", "200"]
    
    visualizer = PhilosopherVisualizer(philo_path)
    visualizer.run_simulation(args)
