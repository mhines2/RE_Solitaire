import argparse
import sys
from memory_interface import MemoryReader, GameAutomator
from solitaire_solver import SolitaireSolver, SolitaireState
from gui_overlay import SolitaireOverlay

def main():
    parser = argparse.ArgumentParser(description="Solitaire Solver and Automation Tool")
    parser.add_argument("--no-gui", action="store_true", help="Run in CLI mode without GUI overlay")
    parser.add_argument("--auto-play", action="store_true", help="Enable auto-play mode")
    parser.add_argument("--update-interval", type=int, default=1000,
                      help="Update interval in milliseconds (default: 1000)")
    args = parser.parse_args()

    # Initialize components
    memory_reader = MemoryReader()
    automator = GameAutomator(memory_reader)

    if args.no_gui:
        run_cli_mode(memory_reader, automator, args)
    else:
        run_gui_mode(memory_reader, automator, args)

def run_cli_mode(memory_reader: MemoryReader, automator: GameAutomator, args):
    """Run the solver in command-line interface mode."""
    print("Running in CLI mode. Press Ctrl+C to exit.")
    
    try:
        while True:
            # Read current game state
            state = memory_reader.read_game_state()
            if not state:
                print("Failed to read game state. Make sure the game is running.")
                continue

            # Create solver and find solution
            solver = SolitaireSolver(state)
            solution = solver.solve()

            if solution:
                print("\nFound solution!")
                for i, (source, target, cards) in enumerate(solution, 1):
                    print(f"Move {i}: Move {len(cards)} card(s) from {source.pile_type.name} to {target.pile_type.name}")
                
                if args.auto_play:
                    print("\nExecuting moves...")
                    for source, target, cards in solution:
                        if not automator.execute_move(source, target, cards):
                            print("Failed to execute move. Stopping auto-play.")
                            break
            else:
                print("No solution found for current game state.")

    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

def run_gui_mode(memory_reader: MemoryReader, automator: GameAutomator, args):
    """Run the solver with GUI overlay."""
    overlay = SolitaireOverlay(memory_reader, automator)
    overlay.auto_play = args.auto_play
    overlay.update_interval = args.update_interval
    overlay.run()

if __name__ == "__main__":
    main() 