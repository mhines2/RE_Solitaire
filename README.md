# Solitaire 99 Solver

A sophisticated Solitaire game solver and solution checker that uses memory reading and A\* search algorithm to find optimal solutions for Solitaire games.

## Overview

This project consists of two main components:

1. **Solitaire99Solver.py**: The main solver that reads the game state from memory and finds optimal solutions using A\* search algorithm.
2. **SolutionChecker.py**: A tool to verify and validate solutions for Solitaire games.

The project includes a Lua script (`solitaire_memory_reader.lua`) that was originally developed for use with Cheat Engine, a memory scanning and modification tool. This script was adapted to read the Solitaire game state from memory.

## Features

- Real-time game state reading from memory
- A\* search algorithm for finding optimal solutions
- Interactive GUI for visualizing solutions
- Solution verification and validation
- Support for standard Solitaire rules
- Memory-efficient state management
- Move prioritization for faster solutions

## Requirements

- Python 3.x
- Required Python packages:
  - pymem
  - tkinter
  - struct
  - heapq
  - copy

## Installation

1. Clone this repository:

```bash
git clone [repository-url]
cd RE_Solitaire
```

2. Install required Python packages:

```bash
pip install pymem
```

## Usage

### Running the Solver

To run the Solitaire solver:

```bash
python Solitaire99Solver.py
```

The solver will:

1. Read the current game state from memory
2. Use A\* search to find an optimal solution
3. Display the solution through an interactive GUI

### Checking Solutions

To verify a solution:

```bash
python SolutionChecker.py
```

The checker will validate the moves and ensure they follow Solitaire rules.

## Project Structure

- `Solitaire99Solver.py`: Main solver implementation
- `SolutionChecker.py`: Solution verification tool
- `solitaire_memory_reader.lua`: Memory reading functionality
- `G9 Demo Video.mp4`: Demonstration video
- `Computer Security Project Report – G9.pdf`: Project documentation

## How It Works

1. **Memory Reading**: The program reads the current game state from memory using the Lua script.
2. **State Representation**: The game state is represented using a custom `GameState` class that tracks:
   - Stock pile
   - Waste pile
   - Foundation piles
   - Tableau piles
3. **A\* Search**: The solver uses A\* search with a custom heuristic to find optimal solutions.
4. **Move Validation**: All moves are validated against standard Solitaire rules.
5. **GUI Display**: Solutions are displayed through an interactive GUI that shows:
   - Current game state
   - Available moves
   - Solution path

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is part of a Computer Security course project (G9). Please refer to the project report for more details about licensing and usage rights.

## Acknowledgments

- Computer Security Course G9 Team
- All contributors and testers
