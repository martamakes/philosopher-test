#!/usr/bin/env python3
import subprocess
import time
import re
import os
import sys
import threading
import matplotlib.pyplot as plt
import numpy as np
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
            self.create_visualization()
            
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
    
    def create_visualization(self):
        """Create a graphical visualization of the simulation results"""
        try:
            num_philosophers = len(self.philosopher_states)
            
            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1]})
            
            # Color map for different philosophers
            colors = plt.cm.tab10(np.linspace(0, 1, num_philosophers))
            
            # SUBPLOT 1: Timeline of eating events
            for i, (time, philo_id) in enumerate(self.eating_events):
                ax1.scatter(time, philo_id, color=colors[philo_id-1], s=100, alpha=0.7)
                
                # Draw a line representing eating duration
                eating_duration = self.philosopher_states[philo_id]["data"]["time_to_eat"] if hasattr(self, "philosopher_states") and philo_id in self.philosopher_states and "data" in self.philosopher_states[philo_id] else 200
                ax1.plot([time, time + eating_duration], [philo_id, philo_id], color=colors[philo_id-1], alpha=0.5)
            
            ax1.set_title('Philosopher Eating Timeline', fontsize=16)
            ax1.set_xlabel('Time (ms)', fontsize=12)
            ax1.set_ylabel('Philosopher ID', fontsize=12)
            ax1.set_yticks(range(1, num_philosophers + 1))
            ax1.grid(True, alpha=0.3)
            
            # SUBPLOT 2: Meal count distribution
            meal_counts = [self.philosopher_states[philo_id]["meals"] for philo_id in range(1, num_philosophers + 1)]
            bars = ax2.bar(range(1, num_philosophers + 1), meal_counts, color=colors)
            
            ax2.set_title('Meals per Philosopher', fontsize=16)
            ax2.set_xlabel('Philosopher ID', fontsize=12)
            ax2.set_ylabel('Number of Meals', fontsize=12)
            ax2.set_xticks(range(1, num_philosophers + 1))
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax2.annotate(f'{height}',
                             xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3),  # 3 points vertical offset
                             textcoords="offset points",
                             ha='center', va='bottom')
            
            plt.tight_layout()
            
            # Save the figure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"philo_visualization_{timestamp}.png"
            plt.savefig(output_path)
            print(f"\nVisualization saved to: {output_path}")
            
            # Show the plot
            plt.show()
            
        except Exception as e:
            print(f"Error creating visualization: {e}")
            print("This is likely because matplotlib is not installed.")
            print("Install it with: pip install matplotlib")

if __name__ == "__main__":
    # Check if arguments are provided
    if len(sys.argv) < 2:
        print("Usage: python3 philosopher_visualizer.py [philo_binary_path] [philosopher_args...]")
        print("Example: python3 philosopher_visualizer.py ./philo 5 800 200 200")
        sys.exit(1)
    
    philo_path = sys.argv[1]
    args = sys.argv[2:]
    
    # Default arguments if none provided
    if not args:
        args = ["5", "800", "200", "200"]
    
    visualizer = PhilosopherVisualizer(philo_path)
    visualizer.run_simulation(args)
