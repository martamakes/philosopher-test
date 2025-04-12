# Philosophers Project Evaluation Checklist

## Project Setup
- [ ] Code is well-organized with clear separation of functions
- [ ] Makefile works correctly (compiles with `-Wall -Wextra -Werror` flags)
- [ ] No memory leaks (checked with valgrind)
- [ ] No global variables
- [ ] Code has proper error handling

## Basic Functionality
- [ ] Each philosopher is a thread
- [ ] Each fork is protected by a mutex
- [ ] Philosophers rotate between eating, sleeping, and thinking
- [ ] Philosophers need both forks to eat
- [ ] Forks are released after eating

## Output Format
- [ ] Messages follow the format: `timestamp_in_ms X action`
- [ ] Actions include: has taken a fork, is eating, is sleeping, is thinking, died
- [ ] Output is clear and not mixed up

## Death Handling
- [ ] Simulation stops when a philosopher dies
- [ ] Death is detected within 10ms of time_to_die
- [ ] Death message is printed correctly

## Edge Cases
- [ ] Works with 1 philosopher (takes fork, waits, dies)
- [ ] Works with many philosophers (100+)
- [ ] Handles the optional meals argument correctly
- [ ] Handles invalid inputs gracefully (negative numbers, non-numeric, etc.)

## Deadlock Prevention
- [ ] No philosophers starve (all get to eat)
- [ ] No deadlocks occur

## Test Scenarios
- [ ] `./philo 5 800 200 200` - All philosophers survive
- [ ] `./philo 4 310 200 100` - A philosopher dies
- [ ] `./philo 5 800 200 200 7` - Stops after each eats 7 times
- [ ] `./philo 1 800 200 200` - One philosopher dies after time_to_die
- [ ] Invalid inputs are rejected with appropriate error messages

## Common Evaluation Questions
- [ ] Can explain implementation details clearly
- [ ] Can explain how mutexes are used to protect shared resources
- [ ] Can explain deadlock prevention strategy
- [ ] Can explain how death is detected within 10ms
- [ ] Understands race conditions and how to prevent them

## Additional Considerations
- [ ] Code is readable and well-commented
- [ ] Variable/function names are clear and meaningful
- [ ] Error messages are helpful
- [ ] Exit is clean (no memory leaks, all threads joined)
