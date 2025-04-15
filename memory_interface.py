import subprocess
import json
from typing import List, Optional, Dict
from dataclasses import dataclass
from solitaire_solver import Card, Rank, Suit, Pile, PileType, SolitaireState

@dataclass
class MemoryCard:
    id: int
    face_up: bool

class MemoryReader:
    def __init__(self, lua_script_path: str = "solitaire_memory_reader.lua"):
        self.lua_script_path = lua_script_path

    def read_game_state(self) -> Optional[SolitaireState]:
        try:
            # Run the Lua script and capture its output
            result = subprocess.run(
                ["cheatengine-cli", "-e", self.lua_script_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Error running Lua script: {result.stderr}")
                return None

            # Parse the output and convert to SolitaireState
            return self._parse_output(result.stdout)
        except Exception as e:
            print(f"Error reading memory: {e}")
            return None

    def _parse_output(self, output: str) -> SolitaireState:
        state = SolitaireState()
        current_pile = None
        
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith('['):
                # New pile section
                pile_name = line[1:-1]  # Remove brackets
                current_pile = self._get_pile_from_name(state, pile_name)
            elif line.startswith('  ') and current_pile is not None:
                # Card line
                card = self._parse_card_line(line.strip())
                if card:
                    current_pile.cards.append(card)

        return state

    def _get_pile_from_name(self, state: SolitaireState, name: str) -> Pile:
        if name == "Stock":
            return state.stock
        elif name == "Waste":
            return state.waste
        elif name.startswith("Foundation"):
            idx = int(name.split()[-1]) - 1
            return state.foundations[idx]
        elif name.startswith("Tableau"):
            idx = int(name.split()[-1]) - 1
            return state.tableau[idx]
        raise ValueError(f"Unknown pile name: {name}")

    def _parse_card_line(self, line: str) -> Optional[Card]:
        try:
            # Example line: "Face Up - Ace of Hearts (0x1234)"
            face_up = "Face Up" in line
            card_str = line.split(" - ")[1].split(" (")[0]
            rank_str, suit_str = card_str.split(" of ")
            
            rank = Rank[rank_str.upper()]
            suit = Suit[suit_str.upper()]
            
            return Card(rank=rank, suit=suit, face_up=face_up)
        except Exception as e:
            print(f"Error parsing card line '{line}': {e}")
            return None

class GameAutomator:
    def __init__(self, memory_reader: MemoryReader):
        self.memory_reader = memory_reader

    def execute_move(self, source: Pile, target: Pile, cards: List[Card]) -> bool:
        """
        Execute a move in the actual game by simulating mouse clicks.
        This is a placeholder - actual implementation would depend on the game's UI layout.
        """
        try:
            # Convert pile locations to screen coordinates
            source_pos = self._get_pile_screen_position(source)
            target_pos = self._get_pile_screen_position(target)
            
            # Simulate drag and drop
            # Implementation would use pyautogui or similar
            return True
        except Exception as e:
            print(f"Error executing move: {e}")
            return False

    def _get_pile_screen_position(self, pile: Pile) -> tuple:
        """
        Convert a pile to screen coordinates.
        This is a placeholder - actual implementation would need to be calibrated
        for the specific game window layout.
        """
        # Implementation would map pile types and indices to screen coordinates
        return (0, 0)  # Placeholder 