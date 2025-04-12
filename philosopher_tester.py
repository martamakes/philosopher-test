#!/usr/bin/env python3
import subprocess
import time
import re
import signal
import os
import sys
from datetime import datetime
from termcolor import colored
import threading

class PhilosopherTester:
    def __init__(self, philo_path="/Users/marta/Documents/PROJECTS/philo/philo"):
        self.philo_path = philo_path
        self.process = None
        self.output_lines = []
        self.stop_thread = False
        self.output_thread = None
        self.tests_passed = 0
        self.tests_failed = 0
        self.total_tests = 0

    def run_command(self, args, timeout=10):
        """Run a command with arguments and capture output"""
        self.output_lines = []
        self.stop_thread = False
        
        try:
            # Start the process
            self.process = subprocess.Popen(
                [self.philo_path] + args, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Start a thread to capture output
            self.output_thread = threading.Thread(target=self._capture_output)
            self.output_thread.start()
            
            # Wait for the process to complete or timeout
            start_time = time.time()
            
            # Only return process if we have a timeout
            if timeout:
                while self.process.poll() is None and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
                
                # Kill process if it's still running and we reached timeout
                if self.process.poll() is None:
                    self.process.terminate()
                    time.sleep(0.2)
                    if self.process.poll() is None:
                        self.process.kill()
            else:
                # For tests where we don't want timeout (like waiting for death)
                self.process.wait()
            
            # Stop the output thread
            self.stop_thread = True
            self.output_thread.join(1)
            
            return self.process.returncode, self.output_lines
            
        except Exception as e:
            print(f"Error running command: {e}")
            return -1, []

    def _capture_output(self):
        """Thread function to capture output from process"""
        while not self.stop_thread:
            if self.process.stdout:
                line = self.process.stdout.readline()
                if line:
                    self.output_lines.append(line.strip())
                else:
                    break
        
        # Get any remaining output
        if self.process and self.process.stdout:
            remaining = self.process.stdout.readlines()
            self.output_lines.extend([line.strip() for line in remaining])

    def print_test_header(self, title):
        """Print formatted test header"""
        print("\n" + "=" * 80)
        print(f" TEST: {title} ".center(80, '='))
        print("=" * 80)

    def print_test_result(self, test_name, passed, details=""):
        """Print test result with colored output"""
        self.total_tests += 1
        
        if passed:
            result = colored("PASSED", "green", attrs=["bold"])
            self.tests_passed += 1
        else:
            result = colored("FAILED", "red", attrs=["bold"])
            self.tests_failed += 1
        
        print(f"{test_name}: {result}")
        if details:
            print(f"  {details}")

    def check_format(self, line):
        """Check if a line matches the expected format"""
        pattern = r"^\d+ \d+ (has taken a fork|is eating|is sleeping|is thinking|died)$"
        return bool(re.match(pattern, line))

    def run_basic_format_test(self):
        """Test that the program outputs messages in the correct format"""
        self.print_test_header("Basic Format Test")
        
        # Run with parameters that should work for a while
        returncode, output = self.run_command(["5", "800", "200", "200"], timeout=3)
        
        # Check if all output lines have the correct format
        valid_format = True
        invalid_lines = []
        
        for i, line in enumerate(output):
            if not self.check_format(line) and "All philosophers have eaten enough" not in line:
                valid_format = False
                invalid_lines.append(f"Line {i+1}: {line}")
                if len(invalid_lines) >= 5:  # Limit number of reported invalid lines
                    break
        
        self.print_test_result("Output format", valid_format, 
                              "All output lines follow the required format" if valid_format 
                              else f"Invalid format found in lines:\n    " + "\n    ".join(invalid_lines))
        
        return valid_format

    def run_death_detection_test(self):
        """Test that philosopher death is detected and reported correctly"""
        self.print_test_header("Death Detection Test")
        
        # Parameters that should cause death
        returncode, output = self.run_command(["4", "310", "200", "100"], timeout=None)
        
        # Check if death was reported
        death_reported = any("died" in line for line in output)
        
        self.print_test_result("Death detection", death_reported,
                              "Death was correctly reported" if death_reported
                              else "No death reported when one was expected")
        
        # Check death timestamp is within 10ms of expected
        if death_reported:
            death_line = next(line for line in output if "died" in line)
            death_time = int(death_line.split()[0])
            time_to_die = 310
            
            within_tolerance = abs(death_time - time_to_die) <= 10
            
            self.print_test_result("Death timing accuracy", within_tolerance,
                                  f"Death reported at {death_time}ms (expected ~{time_to_die}ms)" if within_tolerance
                                  else f"Death reported at {death_time}ms, which is outside the 10ms tolerance from {time_to_die}ms")
        
        return death_reported

    def run_one_philosopher_test(self):
        """Test the case with only one philosopher"""
        self.print_test_header("One Philosopher Test")
        
        # Run with only one philosopher
        returncode, output = self.run_command(["1", "800", "200", "200"], timeout=None)
        
        # One philosopher should take one fork and then die
        took_fork = any("has taken a fork" in line for line in output)
        died = any("died" in line for line in output)
        
        # Check death occurs near time_to_die
        if died:
            death_line = next(line for line in output if "died" in line)
            death_time = int(death_line.split()[0])
            time_to_die = 800
            within_tolerance = abs(death_time - time_to_die) <= 30  # slightly more tolerance for 1 philo
        else:
            within_tolerance = False
        
        self.print_test_result("One philosopher takes fork", took_fork,
                              "Philosopher correctly took a fork" if took_fork
                              else "Philosopher didn't take a fork")
        
        self.print_test_result("One philosopher dies", died,
                              "Philosopher correctly died after taking fork" if died
                              else "Philosopher didn't die as expected")
        
        self.print_test_result("Death timing for one philosopher", within_tolerance,
                              f"Death reported at {death_time}ms (expected ~{time_to_die}ms)" if within_tolerance and died
                              else "Death time outside acceptable range" if died else "No death detected")
        
        return took_fork and died and within_tolerance

    def run_stop_after_meals_test(self):
        """Test that simulation stops after all philosophers eat required meals"""
        self.print_test_header("Stop After Meals Test")
        
        # Run with parameters that shouldn't cause death and specified meal count
        returncode, output = self.run_command(["5", "800", "200", "200", "7"], timeout=None)
        
        # Check if simulation reported all philosophers ate enough
        all_ate = any("All philosophers have eaten enough" in line for line in output)
        
        # Check no philosopher died
        no_death = not any("died" in line for line in output)
        
        self.print_test_result("All philosophers ate required meals", all_ate,
                              "Simulation correctly reported all philosophers ate enough" if all_ate
                              else "Simulation did not report all philosophers ate enough")
        
        self.print_test_result("No philosopher died during meal test", no_death,
                              "No philosopher died as expected" if no_death
                              else "A philosopher died when all should have eaten enough")
        
        return all_ate and no_death

    def run_error_handling_test(self):
        """Test program's error handling for invalid inputs"""
        self.print_test_header("Error Handling Test")
        
        test_cases = [
            # No arguments
            ([], "Too few arguments"),
            # Negative number
            (["5", "-800", "200", "200"], "Invalid argument (negative)"),
            # Non-numeric argument
            (["5", "abc", "200", "200"], "Non-numeric argument"),
            # Zero value
            (["5", "0", "200", "200"], "Zero value"),
            # Too many arguments
            (["5", "800", "200", "200", "7", "extra"], "Too many arguments")
        ]
        
        results = []
        
        for args, desc in test_cases:
            returncode, output = self.run_command(args, timeout=1)
            
            # Should print error message and exit with non-zero code
            has_error = any("Error" in line for line in output)
            error_exit = returncode != 0
            
            passed = has_error and error_exit
            results.append(passed)
            
            self.print_test_result(f"Error handling: {desc}", passed,
                                  f"Program correctly detected error and exited with code {returncode}" if passed
                                  else f"Program failed to handle error correctly (exit code: {returncode}, error message: {'yes' if has_error else 'no'})")
        
        return all(results)

    def run_deadlock_test(self):
        """Test for deadlocks in the program"""
        self.print_test_header("Deadlock Test")
        
        # Run with parameters where deadlock might occur
        returncode, output = self.run_command(["5", "800", "200", "200"], timeout=5)
        
        # Check if each philosopher eats at least once
        philosopher_eating = {}
        for line in output:
            if "is eating" in line:
                philosopher_id = int(line.split()[1])
                philosopher_eating[philosopher_id] = True
        
        all_eating = len(philosopher_eating) == 5
        
        self.print_test_result("No deadlocks", all_eating,
                              "All philosophers managed to eat at least once" if all_eating
                              else f"Only {len(philosopher_eating)} of 5 philosophers managed to eat - possible deadlock")
        
        return all_eating

    def run_stress_test(self):
        """Run a stress test with many philosophers"""
        self.print_test_header("Stress Test (Many Philosophers)")
        
        # Run with more philosophers
        returncode, output = self.run_command(["100", "800", "200", "200"], timeout=5)
        
        # Just check the program doesn't crash
        no_crash = returncode != -1 and not any("Segmentation fault" in line for line in output)
        
        self.print_test_result("Handle many philosophers", no_crash,
                              "Program handled 100 philosophers without crashing" if no_crash
                              else "Program crashed with many philosophers")
        
        return no_crash

    def run_all_tests(self):
        """Run all tests and print summary"""
        print(colored("\n===== PHILOSOPHER TESTER =====", "cyan", attrs=["bold"]))
        print(f"Testing binary: {self.philo_path}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 40)
        
        tests = [
            self.run_basic_format_test,
            self.run_death_detection_test,
            self.run_one_philosopher_test,
            self.run_stop_after_meals_test,
            self.run_error_handling_test,
            self.run_deadlock_test,
            self.run_stress_test
        ]
        
        for test in tests:
            test()
        
        # Print summary
        print("\n" + "=" * 80)
        print(colored(f" SUMMARY: {self.tests_passed}/{self.total_tests} tests passed ", "cyan", attrs=["bold"]).center(80, '='))
        print("=" * 80)
        
        if self.tests_passed == self.total_tests:
            print(colored("\nAll tests passed! Your implementation looks good.", "green", attrs=["bold"]))
        else:
            print(colored(f"\n{self.tests_failed} tests failed. Review the issues above.", "yellow", attrs=["bold"]))
        
        print("\nRemember to manually check these aspects:")
        print("  - Memory leaks (use valgrind or other tools)")
        print("  - No global variables")
        print("  - Proper handling of mutexes")
        print("  - Code organization and readability")

if __name__ == "__main__":
    # Check if custom path is provided
    philo_path = sys.argv[1] if len(sys.argv) > 1 else "/Users/marta/Documents/PROJECTS/philo/philo"
    
    # Run tests
    tester = PhilosopherTester(philo_path)
    tester.run_all_tests()
