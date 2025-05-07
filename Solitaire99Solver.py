# COMPUTER SECURITY G9 Solitaire 99 Solver

# Import necessary libraries
import pymem
import struct
import copy
import heapq
import time
import tkinter as tk
from tkinter import ttk, messagebox
import copy

# Constants for card suits and ranks
SUITS = ["Clubs", "Diamonds", "Hearts", "Spades"]
RANKS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

# Converts card ID to human-readable string
def interpret_card_id(card_id):
    if card_id < 0 or card_id > 51:
        return f"UnknownCard({card_id})"
    suit = SUITS[card_id & 3]
    rank = RANKS[card_id >> 2]
    return f"{rank} of {suit}"

# Extracts rank from card ID
def card_rank(card_id):
    return card_id >> 2

# Extracts suit from card ID
def card_suit(card_id):
    return card_id & 3

# Class representing the game state of Solitaire
class GameState:
    def __init__(self, stock, waste, foundations, tableaus, stock_cycles=0):
        self.stock = stock
        self.waste = waste
        self.foundations = foundations
        self.tableaus = tableaus
        self.stock_cycles = stock_cycles

    # Checks if all cards have been moved to foundations
    def is_won(self):
        return all(rank == 12 for rank in self.foundations)

    # Creates deep copy of current game state
    def clone(self):
        return GameState(
            stock=self.stock.copy(),
            waste=self.waste.copy(),
            foundations=self.foundations.copy(),
            tableaus=[pile.copy() for pile in self.tableaus],
            stock_cycles=self.stock_cycles
        )

    # Returns all valid moves for current game state
    def available_moves(self):
        moves = []

        # Moves from waste to foundation or tableau
        if self.waste:
            top_card = self.waste[-1]
            if self.can_move_to_foundation(top_card):
                moves.append(("waste_to_foundation",))
            for i, tableau in enumerate(self.tableaus):
                if self.can_move_to_tableau(top_card, tableau):
                    moves.append(("waste_to_tableau", i))

        # Moves from tableau to foundation
        for i, tableau in enumerate(self.tableaus):
            if tableau and tableau[-1][1]:
                top_card = tableau[-1][0]
                if self.can_move_to_foundation(top_card):
                    moves.append(("tableau_to_foundation", i))

        # Moves of sequences between tableaus
        for i, tableau_from in enumerate(self.tableaus):
            face_up_start = next((idx for idx, (card, face_up) in enumerate(tableau_from) if face_up), len(tableau_from))
            for seq_start in range(face_up_start, len(tableau_from)):
                moving_sequence = tableau_from[seq_start:]
                for j, tableau_to in enumerate(self.tableaus):
                    if i != j and self.can_move_sequence(moving_sequence, tableau_to):
                        moves.append(("tableau_to_tableau_seq", i, seq_start, j))

        # Flip stock or recycle it
        if self.stock:
            moves.append(("stock_to_waste",))
        elif self.waste:
            moves.append(("recycle_stock",))

        return moves

    # Checks if card can go to its corresponding foundation
    def can_move_to_foundation(self, card_id):
        suit = card_suit(card_id)
        rank = card_rank(card_id)
        return rank == (self.foundations[suit] + 1)

    # Checks if card can be placed onto tableau pile
    def can_move_to_tableau(self, card_id, tableau):
        rank = card_rank(card_id)
        suit = card_suit(card_id)
        if not tableau:
            return rank == 12 # only Kings can be placed on empty tableau
        top_card, face_up = tableau[-1]
        if not face_up:
            return False
        top_rank = card_rank(top_card)
        top_suit = card_suit(top_card)
        colors = (suit in [0, 3], top_suit in [0, 3]) # Black vs Red
        return (colors[0] != colors[1]) and (rank == top_rank - 1)

    # Checks if sequence of cards can be moved to another tableau
    def can_move_sequence(self, moving_sequence, tableau):
        if not moving_sequence:
            return False
        moving_card = moving_sequence[0][0]
        return self.can_move_to_tableau(moving_card, tableau)

    # Applies move and returns new game state
    def apply_move(self, move):
        new_state = self.clone()
        action = move[0]

        if action == "waste_to_foundation":
            card = new_state.waste.pop()
            new_state.foundations[card_suit(card)] += 1

        elif action == "waste_to_tableau":
            tableau_idx = move[1]
            card = new_state.waste.pop()
            new_state.tableaus[tableau_idx].append((card, True))

        elif action == "tableau_to_foundation":
            tableau_idx = move[1]
            card, _ = new_state.tableaus[tableau_idx].pop()
            new_state.foundations[card_suit(card)] += 1
            if new_state.tableaus[tableau_idx]:
                top_card, face_up = new_state.tableaus[tableau_idx][-1]
                if not face_up:
                    new_state.tableaus[tableau_idx][-1] = (top_card, True)

        elif action == "tableau_to_tableau_seq":
            from_idx, start_idx, to_idx = move[1], move[2], move[3]
            sequence = new_state.tableaus[from_idx][start_idx:]
            del new_state.tableaus[from_idx][start_idx:]
            new_state.tableaus[to_idx].extend(sequence)
            if new_state.tableaus[from_idx]:
                top_card, face_up = new_state.tableaus[from_idx][-1]
                if not face_up:
                    new_state.tableaus[from_idx][-1] = (top_card, True)

        elif action == "stock_to_waste":
            card = new_state.stock.pop()
            new_state.waste.append(card)

        elif action == "recycle_stock":
            new_state.stock = new_state.waste[::-1]
            new_state.waste.clear()
            new_state.stock_cycles += 1

        return new_state

    # Heuristic function estimating "goodness" of state
    def heuristic_score(self):
        score = 0
        score += sum((rank + 1) * 10000 for rank in self.foundations) # prioritize filled foundations
        score += sum(200 for tableau in self.tableaus for card, face_up in tableau if face_up)
        score -= sum(1000 for tableau in self.tableaus for card, face_up in tableau if not face_up)
        score -= self.stock_cycles * 30000
        score -= len(self.waste) * 800
        score -= len(self.stock) * 200

        return score

# Ranks moves by strategic priority
def prioritize_moves(moves, state):
    priorities = {
        "waste_to_foundation": 1000000,
        "tableau_to_foundation": 900000,
        "tableau_to_tableau_seq": 500000,
        "waste_to_tableau": 400000,
        "stock_to_waste": 1000,
        "recycle_stock": -100000,
    }
    move_priority = [(priorities.get(move[0], 0), move) for move in moves]
    move_priority.sort(reverse=True)
    return [move for score, move in move_priority]

# A* search to find sequence of optimal moves that leads to winning game
# Uses priority queue with heuristic-based scoring to explore most promising states first
def a_star_search(initial_state, max_iterations=100000):
    heap = []
    counter = 0
    visited = set()
    initial_cost = 0
    heapq.heappush(heap, (initial_cost - initial_state.heuristic_score(), counter, initial_cost, initial_state, []))

    iterations = 0
    while heap and iterations < max_iterations:
        _, _, cost_so_far, state, path = heapq.heappop(heap)
        state_key = (
            tuple(state.stock),
            tuple(state.waste),
            tuple(state.foundations),
            tuple(tuple((card, face_up) for card, face_up in tableau) for tableau in state.tableaus),
            state.stock_cycles
        )
        if state_key in visited:
            continue
        visited.add(state_key)

        if state.is_won():
            return path

        moves = prioritize_moves(state.available_moves(), state)
        for move in moves:
            next_state = state.apply_move(move)
            next_state_key = (
                tuple(next_state.stock),
                tuple(next_state.waste),
                tuple(next_state.foundations),
                tuple(tuple((card, face_up) for card, face_up in tableau) for tableau in next_state.tableaus),
                next_state.stock_cycles
            )
            if next_state_key in visited:
                continue
            counter += 1
            next_cost = cost_so_far + 1
            priority = next_cost - next_state.heuristic_score()
            heapq.heappush(heap, (priority, counter, next_cost, next_state, path + [move]))

        iterations += 1
    return None

# Reads current Solitaire game memory from "sol.exe" process
# Uses Cheat Engine offsets and assumptions about structure:
#   - Pile layout in memory starts at base pointer
#   - Each pile holds an array of cards, each 12 bytes
#   - Foundations, stock, waste, and tableau are mapped by their known indices (0–12)
# Returns decoded stock, waste, foundations, and tableau data
def read_game_memory():
    process_name = "sol.exe"
    try:
        pm = pymem.Pymem(process_name)
    except pymem.exception.ProcessNotFound:
        print(f"Process '{process_name}' not found.")
        exit()

    base_pointer_address = 0x100D01C
    try:
        base_pointer = pm.read_int(base_pointer_address)
    except Exception as e:
        print(f"Failed to read base pointer: {e}")
        exit()

    if base_pointer is None or base_pointer == 0:
        print("Invalid base pointer.")
        exit()

    stock = []
    waste = []
    foundations = [-1 for _ in range(4)]
    tableaus = [[] for _ in range(7)]

    column_count_offset = 0x64
    first_column_pointer_offset = 0x6C
    card_array_count_offset = 0x1C
    card_array_start_offset = 0x24
    bytes_per_card = 12
    card_header_offset = 0x0

    pile_count = pm.read_int(base_pointer + column_count_offset)
    if pile_count > 13:
        pile_count = 13

    for i in range(pile_count):
        pointer_offset = first_column_pointer_offset + i * 4
        try:
            pile_address = pm.read_int(base_pointer + pointer_offset)
        except Exception:
            continue

        if pile_address is None:
            continue

        try:
            card_total = pm.read_int(pile_address + card_array_count_offset)
        except Exception:
            continue

        if card_total == 0:
            continue

        pile_cards = []
        for j in range(card_total):
            card_location = pile_address + card_array_start_offset + j * bytes_per_card
            try:
                card_header_bytes = pm.read_bytes(card_location + card_header_offset, 2)
                card_header = struct.unpack("<H", card_header_bytes)[0]
            except Exception:
                continue

            is_face_up = (card_header & 0x8000) != 0
            card_id = card_header & 0x7FFF

            if i == 0:
                stock.append(card_id)
            elif i == 1:
                waste.append(card_id)
            elif 2 <= i <= 5:
                suit = i - 2
                foundations[suit] = card_rank(card_id)
            elif 6 <= i <= 12:
                tableau_idx = i - 6
                pile_cards.append((card_id, is_face_up))

        if 6 <= i <= 12:
            tableaus[tableau_idx] = pile_cards

    print(stock, waste, foundations, tableaus)
    return stock, waste, foundations, tableaus

# Converts move tuple into human-readable text description
# Used for displaying action taken on GUI or console
def describe_move(move, state):
    action = move[0]
    if action == "waste_to_foundation":
        return "Move card from Waste to Foundation."
    elif action == "waste_to_tableau":
        return f"Move card from Waste to Tableau {move[1] + 1}."
    elif action == "tableau_to_foundation":
        return f"Move top card from Tableau {move[1] + 1} to Foundation."
    elif action == "tableau_to_tableau_seq":
        from_idx, start_idx, to_idx = move[1], move[2], move[3]
        num_cards = len(state.tableaus[from_idx]) - start_idx
        return f"Move top {num_cards} cards from Tableau {from_idx + 1} to Tableau {to_idx + 1}."
    elif action == "stock_to_waste":
        return "Flip top card from Stock to Waste."
    elif action == "recycle_stock":
        return "Recycle Waste back into Stock pile."
    else:
        return f"Unknown move: {move}"

# Debugging utility that prints current board state to console
# Shows Stock, Waste, Foundations, and each Tableau pile
def print_board(state):
    print("\n=== Current Board State ===")
    print("\nStock:")
    if state.stock:
        for card in reversed(state.stock):
            print(f"  - {interpret_card_id(card)}")
    else:
        print("  (empty)")

    print("\nWaste:")
    if state.waste:
        for card in reversed(state.waste):
            print(f"  - {interpret_card_id(card)}")
    else:
        print("  (empty)")

    print("\nFoundations:")
    for suit_idx, rank in enumerate(state.foundations):
        if rank >= 0:
            print(f"  {SUITS[suit_idx]}: {RANKS[rank]}")
        else:
            print(f"  {SUITS[suit_idx]}: (empty)")

    print("\nTableaus:")
    for idx, tableau in enumerate(state.tableaus):
        print(f"  Tableau {idx+1}:")
        if tableau:
            for card_id, is_face_up in tableau:
                face = "Face-Up" if is_face_up else "Face-Down"
                print(f"    - {interpret_card_id(card_id)} ({face})")
        else:
            print("    (empty)")
    print("============================\n")

# GUI frontend for Solitaire solver using Tkinter (it's a bit ugly)
# Allows user to click "Solve" and visually step through moves
# Shows current board state and highlights most recent move 
class SolitaireSolverGUI:
    def __init__(self, root): # sets up GUI layout with buttons, canvas, and initial state variables
        self.root = root
        root.title("Solitaire 99 Solver")

        self.solve_button = ttk.Button(root, text="Solve Game", command=self.solve_game)
        self.solve_button.pack(pady=10)

        self.button_frame = ttk.Frame(root)
        self.button_frame.pack(pady=5)

        self.prev_button = ttk.Button(self.button_frame, text="Previous Move", command=self.prev_move, state=tk.DISABLED)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.next_button = ttk.Button(self.button_frame, text="Next Move", command=self.next_move, state=tk.DISABLED)
        self.next_button.grid(row=0, column=1, padx=5)

        self.canvas = tk.Canvas(root, width=1200, height=700, bg="green")
        self.canvas.pack(padx=10, pady=10)

        self.solving_message = None

        self.solution_states = []
        self.solution_moves = []
        self.current_index = 0

    # Triggered when "Solve Game" is pressed
    # Reads memory, initializes state, and begins solving process
    # Displays "solving..." while background process runs
    def solve_game(self):
        try:
            stock, waste, foundations, tableaus = read_game_memory()
            initial_state = GameState(stock, waste, foundations, tableaus)

            self.canvas.delete("all")
            self.root.update()

            self.solving_message = self.canvas.create_text(
                600, 350, text="Solving in progress...", font=("Helvetica", 24), fill="yellow"
            )
            self.root.update_idletasks()

            start_time = time.time()

            self.root.after(100, lambda: self.perform_solving(initial_state, start_time))

        except Exception as e:
            self.canvas.delete(self.solving_message)
            self.solving_message = None
            messagebox.showerror("Error", str(e))

    # Runs A* search, builds solution state path, and stores sequence
    # Enables GUI navigation if solution is found, or shows "No solution" dialog
    def perform_solving(self, initial_state, start_time):
        moves = a_star_search(initial_state)

        if self.solving_message:
            self.canvas.delete(self.solving_message)
            self.solving_message = None
        self.root.update_idletasks()

        if moves:
            elapsed = time.time() - start_time
            print(f"Solved in {elapsed:.2f} seconds.")

            self.solution_states = [initial_state.clone()]
            current_state = initial_state.clone()
            for move in moves:
                current_state = current_state.apply_move(move)
                self.solution_states.append(current_state.clone())

            self.solution_moves = moves
            self.current_index = 0

            self.update_display()

            self.next_button.config(state=tk.NORMAL)
            self.prev_button.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("No Solution", "No solution found.")
            self.solution_states = []
            self.solution_moves = []
            self.current_index = 0
            self.next_button.config(state=tk.DISABLED)
            self.prev_button.config(state=tk.DISABLED)

    # Redraws entire board based on current solution state
    # Highlights recent moves (source and destination)
    # Renders stock, waste, foundations, and all tableaus with spacing
    def update_display(self):
        self.canvas.delete("all")
        state = self.solution_states[self.current_index]

        move_to_highlight = None
        if self.current_index > 0:
            move_to_highlight = self.solution_moves[self.current_index - 1]

        self.canvas.create_text(100, 20, text="Stock", font=("Helvetica", 14), fill="white")
        self.canvas.create_text(300, 20, text="Waste", font=("Helvetica", 14), fill="white")
        self.canvas.create_text(550, 20, text="Foundations", font=("Helvetica", 14), fill="white")

        # Draws stock
        highlight_stock = False
        if move_to_highlight and move_to_highlight[0] == "recycle_stock":
            highlight_stock = True

        if state.stock:
            self.draw_card(50, 50, "STOCK", highlight=highlight_stock)
        else:
            self.draw_empty_slot(50, 50)

        # Draws waste
        highlight_waste = False
        if move_to_highlight:
            action = move_to_highlight[0]
            if action == "stock_to_waste":
                highlight_waste = True

        if state.waste:
            top_card = state.waste[-1]
            self.draw_card(250, 50, self.card_text(top_card), highlight=highlight_waste)
        else:
            self.draw_empty_slot(250, 50)

        # Draws foundations
        for i, rank in enumerate(state.foundations):
            x = 450 + i * 70
            highlight_foundation = False

            if move_to_highlight:
                action = move_to_highlight[0]

                if action == "waste_to_foundation":
                    suit_idx = card_suit(self.solution_states[self.current_index-1].waste[-1])
                    if i == suit_idx:
                        highlight_foundation = True

                elif action == "tableau_to_foundation":
                    tableau_idx = move_to_highlight[1]
                    if self.solution_states[self.current_index-1].tableaus[tableau_idx]:
                        last_card_id = self.solution_states[self.current_index-1].tableaus[tableau_idx][-1][0]
                        suit_idx = card_suit(last_card_id)
                        if i == suit_idx:
                            highlight_foundation = True

            self.draw_empty_slot(x, 50)
            if rank >= 0:
                card_id = (rank << 2) | i  # rebuilds card_id from rank and suit
                card_name = self.card_text(card_id)
                self.draw_card(x, 50, card_name, highlight=highlight_foundation)

        # Draws 4 tableaus (order is not always accurate to real game display)
        for col, tableau in enumerate(state.tableaus):
            x = 80 + col * 150
            self.canvas.create_text(x, 150, text=f"Tableau {col+1}", font=("Helvetica", 12), fill="white")
            for row, (card_id, face_up) in enumerate(tableau):
                y = 170 + row * 20

                highlight = False
                if move_to_highlight:
                    action = move_to_highlight[0]

                    if action == "waste_to_tableau":
                        dest_idx = move_to_highlight[1]
                        if col == dest_idx and row == len(tableau) - 1:
                            highlight = True

                    elif action == "tableau_to_tableau_seq":
                        dest_idx = move_to_highlight[3]
                        prev_state = self.solution_states[self.current_index-1]
                        from_idx = move_to_highlight[1]
                        start_idx = move_to_highlight[2]
                        moved_cards_count = len(prev_state.tableaus[from_idx]) - start_idx
                        if col == dest_idx and row >= len(tableau) - moved_cards_count:
                            highlight = True

                if face_up:
                    self.draw_card(x-30, y, self.card_text(card_id), highlight=highlight)
                else:
                    self.draw_card(x-30, y, "🂠", face_up=False)

        # Prints move description text at bottom
        if self.current_index > 0:
            move_desc = describe_move(self.solution_moves[self.current_index-1], self.solution_states[self.current_index-1])
            total_moves = len(self.solution_moves)
            self.canvas.create_text(
                600, 660,
                text=f"Move {self.current_index}/{total_moves}: {move_desc}",
                font=("Helvetica", 14), fill="yellow"
            )
        else:
            self.canvas.create_text(
                600, 660,
                text="Initial State",
                font=("Helvetica", 14), fill="yellow"
            )

    # Draws card on canvas at specified (x, y)
    # Can show face-up (with rank/suit) or face-down (blue rectangle)
    # Red border indicates card affected by last move
    def draw_card(self, x, y, text, face_up=True, highlight=False):
        if face_up:
            if highlight:
                self.canvas.create_rectangle(x-2, y-2, x+62, y+82, outline="red", width=4)
            self.canvas.create_rectangle(x, y, x+60, y+80, fill="white")
            self.canvas.create_text(x+30, y+40, text=text, font=("Helvetica", 12))
        else:
            if highlight:
                self.canvas.create_rectangle(x-2, y-2, x+62, y+82, outline="red", width=4)
            self.canvas.create_rectangle(x, y, x+60, y+80, fill="blue")

    # Draws dashed rectangle to represent empty card slot
    def draw_empty_slot(self, x, y):
        self.canvas.create_rectangle(x, y, x+60, y+80, outline="white", dash=(4,2))


    # Returns short string for card (e.g., "A♠", "10♦")
    # Converts full card ID to rank/suit symbol
    def card_text(self, card_id):
        rank = RANKS[card_rank(card_id)]
        suit = card_suit(card_id)

        suit_symbols = ["♣", "♦", "♥", "♠"]

        # If rank is "10", "Jack", "Queen", "King", "Ace", shorten it
        if rank == "Ace":
            rank_str = "A"
        elif rank == "Jack":
            rank_str = "J"
        elif rank == "Queen":
            rank_str = "Q"
        elif rank == "King":
            rank_str = "K"
        else:
            rank_str = rank  # 2-10 stay as-is

        return f"{rank_str}{suit_symbols[suit]}"

    # GUI navigation handlers for stepping forward/backward in the move sequence
    # Updates current index and redraws the display
    def next_move(self):
        if self.current_index < len(self.solution_states) - 1:
            self.current_index += 1
            self.update_display()

        self.prev_button.config(state=tk.NORMAL)
        if self.current_index == len(self.solution_states) - 1:
            self.next_button.config(state=tk.DISABLED)

    def prev_move(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()

        self.next_button.config(state=tk.NORMAL)
        if self.current_index == 0:
            self.prev_button.config(state=tk.DISABLED)


# Launches GUI app when script is executed directly
if __name__ == "__main__":
    root = tk.Tk()
    app = SolitaireSolverGUI(root)
    root.mainloop()