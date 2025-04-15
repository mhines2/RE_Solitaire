import pygame
import sys
from typing import List, Optional, Tuple
from solitaire_solver import Card, Rank, Suit, Pile, PileType, SolitaireState
from memory_interface import MemoryReader, GameAutomator

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
CARD_WIDTH = 71
CARD_HEIGHT = 96
CARD_SPACING = 20
TABLEAU_SPACING = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

class SolitaireOverlay:
    def __init__(self, memory_reader: MemoryReader, automator: GameAutomator):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Solitaire Solver Overlay")
        
        self.memory_reader = memory_reader
        self.automator = automator
        self.font = pygame.font.Font(None, 24)
        
        # Load card images
        self.card_images = {}
        self._load_card_images()
        
        # Game state
        self.current_state: Optional[SolitaireState] = None
        self.suggested_moves: List[Tuple[Pile, Pile, List[Card]]] = []
        self.current_move_index = 0
        
        # UI state
        self.show_suggestions = True
        self.auto_play = False
        self.last_update_time = 0
        self.update_interval = 1000  # ms

    def _load_card_images(self):
        """Load card images from assets directory."""
        # This is a placeholder - you would need to implement actual image loading
        # For now, we'll draw simple rectangles for cards
        pass

    def run(self):
        """Main game loop."""
        clock = pygame.time.Clock()
        running = True

        while running:
            current_time = pygame.time.get_ticks()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_key_press(event.key)
            
            # Update game state
            if current_time - self.last_update_time > self.update_interval:
                self._update_game_state()
                self.last_update_time = current_time
            
            # Draw everything
            self._draw()
            pygame.display.flip()
            
            clock.tick(60)

        pygame.quit()
        sys.exit()

    def _handle_key_press(self, key):
        """Handle keyboard input."""
        if key == pygame.K_SPACE:
            self.show_suggestions = not self.show_suggestions
        elif key == pygame.K_a:
            self.auto_play = not self.auto_play
        elif key == pygame.K_RIGHT and self.suggested_moves:
            self._execute_next_move()
        elif key == pygame.K_r:
            self._update_game_state()

    def _update_game_state(self):
        """Update the current game state from memory."""
        self.current_state = self.memory_reader.read_game_state()
        if self.current_state and self.auto_play:
            self._execute_next_move()

    def _execute_next_move(self):
        """Execute the next suggested move."""
        if not self.suggested_moves or self.current_move_index >= len(self.suggested_moves):
            return

        source, target, cards = self.suggested_moves[self.current_move_index]
        if self.automator.execute_move(source, target, cards):
            self.current_move_index += 1

    def _draw(self):
        """Draw the current game state and overlay."""
        self.screen.fill((0, 0, 0, 128))  # Semi-transparent black background
        
        if self.current_state:
            self._draw_game_state()
        
        if self.show_suggestions and self.suggested_moves:
            self._draw_suggestions()
        
        self._draw_ui_elements()

    def _draw_game_state(self):
        """Draw the current game state."""
        # Draw stock and waste
        self._draw_pile(self.current_state.stock, (50, 50))
        self._draw_pile(self.current_state.waste, (150, 50))
        
        # Draw foundations
        for i, foundation in enumerate(self.current_state.foundations):
            x = 400 + i * (CARD_WIDTH + CARD_SPACING)
            self._draw_pile(foundation, (x, 50))
        
        # Draw tableau
        for i, tableau in enumerate(self.current_state.tableau):
            x = 50 + i * (CARD_WIDTH + TABLEAU_SPACING)
            self._draw_pile(tableau, (x, 200))

    def _draw_pile(self, pile: Pile, position: Tuple[int, int]):
        """Draw a pile of cards at the given position."""
        x, y = position
        for i, card in enumerate(pile.cards):
            if card.face_up:
                self._draw_card(card, (x, y + i * 20))
            else:
                self._draw_card_back((x, y + i * 20))

    def _draw_card(self, card: Card, position: Tuple[int, int]):
        """Draw a card at the given position."""
        x, y = position
        color = RED if card.is_red else BLACK
        pygame.draw.rect(self.screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
        pygame.draw.rect(self.screen, color, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
        
        # Draw card text
        text = self.font.render(f"{card.rank.name[0]}{card.suit.name[0]}", True, color)
        self.screen.blit(text, (x + 5, y + 5))

    def _draw_card_back(self, position: Tuple[int, int]):
        """Draw a card back at the given position."""
        x, y = position
        pygame.draw.rect(self.screen, BLUE, (x, y, CARD_WIDTH, CARD_HEIGHT))
        pygame.draw.rect(self.screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)

    def _draw_suggestions(self):
        """Draw the current move suggestions."""
        if not self.suggested_moves:
            return

        current_move = self.suggested_moves[self.current_move_index]
        source, target, cards = current_move
        
        # Draw move indicators
        self._draw_move_indicator(source, target, cards)

    def _draw_move_indicator(self, source: Pile, target: Pile, cards: List[Card]):
        """Draw an indicator for the suggested move."""
        # Implementation would draw arrows or highlights for the suggested move
        pass

    def _draw_ui_elements(self):
        """Draw UI elements like buttons and status text."""
        # Draw status text
        status_text = f"Auto-play: {'ON' if self.auto_play else 'OFF'} | "
        status_text += f"Suggestions: {'ON' if self.show_suggestions else 'OFF'}"
        text = self.font.render(status_text, True, WHITE)
        self.screen.blit(text, (10, WINDOW_HEIGHT - 30))
        
        # Draw controls help
        controls = "Space: Toggle suggestions | A: Toggle auto-play | Right: Next move | R: Refresh"
        text = self.font.render(controls, True, WHITE)
        self.screen.blit(text, (10, WINDOW_HEIGHT - 60)) 