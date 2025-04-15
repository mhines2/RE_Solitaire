# Solitaire Solver and Automation Tool

This project provides a comprehensive solution for analyzing and solving Windows Solitaire games through memory reading and automation. It combines memory forensics with game-solving algorithms to provide both analysis and automated gameplay capabilities.

## Features

- Real-time memory reading of Solitaire game state
- Advanced solving algorithm with move suggestions
- GUI overlay for visualizing game state and moves
- CLI mode for automated gameplay
- Support for both manual and automatic move execution

## Contributors

- Michael Hines
- August Berchelmann
- Owen Grimaldi

## Prerequisites

- Python 3.8 or higher
- Cheat Engine with Lua scripting support
- Windows Solitaire game
- Pygame for GUI overlay
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository:

```bash
git clone https://github.com/mhines2/solitaire-solver.git
cd solitaire-solver
```

2. Install required Python packages:

```bash
pip install -r requirements.txt
```

3. Ensure Cheat Engine is installed and configured with Lua scripting support

## Usage

### GUI Mode (Default)

```bash
python main.py
```

### CLI Mode

```bash
python main.py --no-gui
```

### Auto-play Mode

```bash
python main.py --auto-play
```

### Additional Options

- `--update-interval`: Set the update interval in milliseconds (default: 1000)
- `--no-gui`: Run in command-line interface mode
- `--auto-play`: Enable automatic move execution

## Controls (GUI Mode)

- Space: Toggle move suggestions
- A: Toggle auto-play mode
- Right Arrow: Execute next suggested move
- R: Refresh game state
- ESC: Exit

## Project Structure

- `main.py`: Main entry point and CLI interface
- `solitaire_solver.py`: Core game logic and solving algorithm
- `memory_interface.py`: Memory reading and game automation
- `gui_overlay.py`: Pygame-based GUI overlay
- `solitaire_memory_reader.lua`: Cheat Engine Lua script for memory reading

## Memory Reading

The project uses a custom Lua script (`solitaire_memory_reader.lua`) to read the game's memory state. The script:

- Locates the base memory address
- Reads card data structures
- Decodes card identities and states
- Provides real-time game state information

## Solving Algorithm

The solver implements a depth-first search with backtracking to find optimal solutions. It considers:

- Valid card movements
- Foundation building rules
- Tableau building rules
- Stock and waste pile management

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Cheat Engine for memory reading capabilities
- Pygame for GUI implementation
- The Solitaire community for game rules and strategies
