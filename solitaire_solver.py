from dataclasses import dataclass
from typing import List, Optional, Set, Tuple
from enum import Enum
import numpy as np

class Suit(Enum):
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3

class Rank(Enum):
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13

@dataclass
class Card:
    rank: Rank
    suit: Suit
    face_up: bool = False

    def __str__(self):
        return f"{self.rank.name} of {self.suit.name}"

    @property
    def is_red(self) -> bool:
        return self.suit in [Suit.HEARTS, Suit.DIAMONDS]

class PileType(Enum):
    STOCK = 0
    WASTE = 1
    FOUNDATION = 2
    TABLEAU = 3

@dataclass
class Pile:
    cards: List[Card]
    pile_type: PileType
    index: int  # For tableau/foundation identification

class SolitaireState:
    def __init__(self):
        self.stock: Pile = Pile([], PileType.STOCK, 0)
        self.waste: Pile = Pile([], PileType.WASTE, 0)
        self.foundations: List[Pile] = [Pile([], PileType.FOUNDATION, i) for i in range(4)]
        self.tableau: List[Pile] = [Pile([], PileType.TABLEAU, i) for i in range(7)]

    def is_valid_move(self, source: Pile, target: Pile, cards: List[Card]) -> bool:
        if not cards:
            return False

        if target.pile_type == PileType.FOUNDATION:
            return self._is_valid_foundation_move(source, target, cards[0])
        elif target.pile_type == PileType.TABLEAU:
            return self._is_valid_tableau_move(source, target, cards[0])
        return False

    def _is_valid_foundation_move(self, source: Pile, target: Pile, card: Card) -> bool:
        if len(target.cards) == 0:
            return card.rank == Rank.ACE
        if len(source.cards) > 1:
            return False
        top_card = target.cards[-1]
        return (card.suit == top_card.suit and 
                card.rank.value == top_card.rank.value + 1)

    def _is_valid_tableau_move(self, source: Pile, target: Pile, card: Card) -> bool:
        if len(target.cards) == 0:
            return card.rank == Rank.KING
        top_card = target.cards[-1]
        return (card.is_red != top_card.is_red and 
                card.rank.value == top_card.rank.value - 1)

class SolitaireSolver:
    def __init__(self, initial_state: SolitaireState):
        self.initial_state = initial_state
        self.visited_states: Set[str] = set()

    def solve(self) -> Optional[List[Tuple[Pile, Pile, List[Card]]]]:
        """
        Implements a depth-first search with backtracking to find a solution.
        Returns a list of moves (source_pile, target_pile, cards_to_move) if a solution is found.
        """
        return self._solve_recursive(self.initial_state, [])

    def _solve_recursive(self, state: SolitaireState, moves: List[Tuple[Pile, Pile, List[Card]]]) -> Optional[List[Tuple[Pile, Pile, List[Card]]]]:
        if self._is_winning_state(state):
            return moves

        state_hash = self._hash_state(state)
        if state_hash in self.visited_states:
            return None

        self.visited_states.add(state_hash)

        # Try all possible moves
        for source in self._get_all_piles(state):
            for target in self._get_all_piles(state):
                if source == target:
                    continue

                for i in range(len(source.cards)):
                    cards = source.cards[i:]
                    if state.is_valid_move(source, target, cards):
                        # Make move
                        new_state = self._apply_move(state, source, target, cards)
                        new_moves = moves + [(source, target, cards)]
                        
                        # Recursive call
                        result = self._solve_recursive(new_state, new_moves)
                        if result:
                            return result

        return None

    def _is_winning_state(self, state: SolitaireState) -> bool:
        return all(len(foundation.cards) == 13 for foundation in state.foundations)

    def _hash_state(self, state: SolitaireState) -> str:
        # Create a unique string representation of the state
        state_str = []
        for pile in self._get_all_piles(state):
            state_str.append(f"{pile.pile_type.name}:{','.join(str(card) for card in pile.cards)}")
        return "|".join(sorted(state_str))

    def _get_all_piles(self, state: SolitaireState) -> List[Pile]:
        return ([state.stock, state.waste] + 
                state.foundations + 
                state.tableau)

    def _apply_move(self, state: SolitaireState, source: Pile, target: Pile, cards: List[Card]) -> SolitaireState:
        new_state = SolitaireState()
        # Deep copy the state and apply the move
        # Implementation details omitted for brevity
        return new_state 