import pygame
import sys
import random
import time
from collections import defaultdict

# --- Constants ---
# Players
LEFT_PLAYER = "Left (Blue)"
RIGHT_PLAYER = "Right (Red)"

# Colors (RGB) - Using solid standard colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GREEN = (0, 128, 0) # For highlighting legal moves
LIGHT_GREEN = (144, 238, 144) # For button hover
HIGHLIGHT_COLOR = GREEN # Use Green for highlighting legal moves
HIGHLIGHT_THICKNESS_INCREASE = 4 # How much thicker the highlight line is

# Screen and Grid
SQUARE_SIZE = 60
GRID_LINE_WIDTH = 1
EDGE_THICKNESS = 5
EDGE_CLICK_TOLERANCE = 8 # Pixels around the edge line for click detection
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600 # Height for the grid area
INFO_PANEL_HEIGHT = 50
TOTAL_SCREEN_HEIGHT = SCREEN_HEIGHT + INFO_PANEL_HEIGHT

# Edge Orientations
HORIZONTAL = 'H'
VERTICAL = 'V'

# Button Constants
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40
BUTTON_Y = INFO_PANEL_HEIGHT // 2 - BUTTON_HEIGHT // 2 # Center vertically in info panel
PLAY_AGAIN_BUTTON_X = SCREEN_WIDTH - BUTTON_WIDTH - 20 # Right align


# --- Game Logic Class ---

class FragmentedSquaresGame:
    """Manages the game state and logic for Fragmented Squares."""
    def __init__(self, squares_coords):
        """
        Initializes the game state.
        Args:
            squares_coords (set): A set of (row, col) tuples representing the squares.
        """
        if not squares_coords:
            raise ValueError("Game must be initialized with at least one square.")

        self.all_squares_coords = set(squares_coords) # Keep track of the original shape
        self.reset() # Initialize/reset game variables

    def reset(self):
        """Resets the game to its initial state with the original shape."""
        self.active_squares_coords = self.all_squares_coords.copy() # Squares not yet destroyed
        self.edges = {}  # Maps edge tuple ((r, c), orientation) -> {'color': COLOR, 'exists': bool}
        self.current_player = LEFT_PLAYER # Left (Blue) starts
        self.winner = None
        self.last_move_destructions = 0 # How many squares were destroyed by the last move
        self.move_history = [] # To store data for reporting
        self._initialize_edges()
        print("-" * 20)
        print("Game Reset / Initialized")
        print(f"Starting with {len(self.active_squares_coords)} active squares.")
        print("-" * 20)


    def _initialize_edges(self):
        """Creates all edges for the given squares and assigns random colors."""
        potential_edges = set()
        # Iterate through all squares defined in the initial shape
        for r, c in self.all_squares_coords:
            # Define the 4 potential edges associated with this square (r,c)
            # Edge below (r, c)
            potential_edges.add(((r, c), HORIZONTAL))
            # Edge right of (r, c)
            potential_edges.add(((r, c), VERTICAL))
            # Edge above (r, c) - represented by edge below (r-1, c)
            potential_edges.add(((r - 1, c), HORIZONTAL))
            # Edge left of (r, c) - represented by edge right of (r, c-1)
            potential_edges.add(((r, c - 1), VERTICAL))

        # Now, process the collected potential edges
        for edge_tuple in potential_edges:
            # Only consider edges that haven't been added yet
            if edge_tuple not in self.edges:
                squares_bordered = self.get_squares_sharing_edge(edge_tuple)
                # Crucially, only add edges that are part of the shape
                # (i.e., border at least one square defined in all_squares_coords)
                if squares_bordered & self.all_squares_coords:
                    # Simple random assignment for demo - could be predefined
                    color = random.choice([RED, BLUE])
                    self.edges[edge_tuple] = {'color': color, 'exists': True}

        print(f"Initialized {len(self.edges)} edges.")


    def get_squares_sharing_edge(self, edge_tuple):
        """Returns the set of square coords ((r, c)) sharing a given edge."""
        (r, c), orientation = edge_tuple
        squares = set()
        if orientation == HORIZONTAL: # Edge below (r, c)
            squares.add((r, c))
            squares.add((r + 1, c))
        elif orientation == VERTICAL: # Edge right of (r, c)
            squares.add((r, c))
            squares.add((r, c + 1))
        # Return only squares that are part of the originally defined board shape
        # This prevents considering squares outside the intended play area.
        return squares & self.all_squares_coords

    def get_edges_of_square(self, square_coord):
        """Returns the 4 edge tuples potentially bounding a square."""
        r, c = square_coord
        return {
            ((r - 1, c), HORIZONTAL),  # Top edge (below square r-1, c)
            ((r, c), HORIZONTAL),      # Bottom edge (below square r, c)
            ((r, c - 1), VERTICAL),    # Left edge (right of square r, c-1)
            ((r, c), VERTICAL)         # Right edge (right of square r, c)
        }

    def is_valid_move(self, edge_tuple):
        """
        Checks if removing the edge is a valid move for the current player,
        according to the updated ruleset (Rule 4).
        """
        # 0. Game already over?
        if self.winner:
            return False

        # 1. Edge must exist in the game's definition and not be already removed
        if edge_tuple not in self.edges or not self.edges[edge_tuple]['exists']:
            return False

        # 2. Edge must be of the correct color for the current player
        edge_color = self.edges[edge_tuple]['color']
        player_can_remove = (self.current_player == LEFT_PLAYER and edge_color == BLUE) or \
                            (self.current_player == RIGHT_PLAYER and edge_color == RED)
        if not player_can_remove:
            return False

        # 3. Edge must border at least one *active* square (Rule 4.3)
        squares_bordered = self.get_squares_sharing_edge(edge_tuple)
        borders_active_square = any(sq in self.active_squares_coords for sq in squares_bordered)
        if not borders_active_square:
            return False

        # If all conditions pass, it's a valid move
        return True

    def get_legal_moves(self):
        """Returns a list of all valid edge_tuples for the current player."""
        legal = []
        # Iterate through all edges defined for the board
        for edge_tuple in self.edges:
            # Use the updated is_valid_move check
            if self.is_valid_move(edge_tuple):
                legal.append(edge_tuple)
        return legal

    def make_move(self, edge_tuple):
        """
        Attempts to remove an edge, updates game state according to rules,
        logs the move, checks for win condition, and switches player.
        Returns (success_boolean, message_string).
        """
        if not self.is_valid_move(edge_tuple):
            # Provide more specific feedback if possible
            reason = "Unknown reason"
            if edge_tuple not in self.edges or not self.edges[edge_tuple]['exists']:
                reason = "Edge does not exist or already removed"
            else:
                 edge_color = self.edges[edge_tuple]['color']
                 player_req_color = BLUE if self.current_player == LEFT_PLAYER else RED
                 if edge_color != player_req_color:
                     reason = f"Incorrect color (Player: {self.current_player}, Edge: {'Blue' if edge_color == BLUE else 'Red'})"
                 else:
                     squares_bordered = self.get_squares_sharing_edge(edge_tuple)
                     if not any(sq in self.active_squares_coords for sq in squares_bordered):
                         reason = "Edge does not border any active squares"

            print(f"Invalid move attempt: {edge_tuple} for {self.current_player}. Reason: {reason}")
            return False, f"Invalid Move: {reason}"

        # --- Perform the move ---
        self.edges[edge_tuple]['exists'] = False # Mark edge as removed
        edge_color = self.edges[edge_tuple]['color']

        # Identify squares adjacent to the removed edge
        squares_potentially_affected = self.get_squares_sharing_edge(edge_tuple)
        destroyed_this_turn = set()

        # Destroy any of those squares that were active
        for sq_coord in squares_potentially_affected:
            if sq_coord in self.active_squares_coords:
                self.active_squares_coords.remove(sq_coord)
                destroyed_this_turn.add(sq_coord)

        self.last_move_destructions = len(destroyed_this_turn)

        # --- Log Move Data ---
        # Capture state *before* this move for accurate logging
        active_squares_before_move = self.active_squares_coords | destroyed_this_turn

        move_data = {
            'turn': len(self.move_history) + 1,
            'player': self.current_player,
            'edge_removed': edge_tuple,
            'edge_color': 'Blue' if edge_color == BLUE else 'Red',
            'squares_destroyed': destroyed_this_turn.copy(), # Log a copy
            'active_squares_before': active_squares_before_move.copy(), # Log a copy
            'active_squares_after': self.active_squares_coords.copy(), # Log a copy
            'game_over_after': False,
            'winner': None
        }

        # --- Check for Game Over (Isolated Play Rule 5) ---
        if not self.active_squares_coords:
            self.winner = self.current_player # The player who made this move wins
            move_data['game_over_after'] = True
            move_data['winner'] = self.winner
            print(f"Game Over! Winner: {self.winner}")

        self.move_history.append(move_data) # Append log entry

        # --- Switch Player (only if game is not over) ---
        if not self.winner:
            self.current_player = RIGHT_PLAYER if self.current_player == LEFT_PLAYER else LEFT_PLAYER

        return True, f"Destroyed {self.last_move_destructions} square(s)."

    def get_state_summary(self):
        """Returns a dictionary summarizing the current game state."""
        return {
            'active_squares': len(self.active_squares_coords),
            'current_player': self.current_player,
            'winner': self.winner,
            'total_moves': len(self.move_history)
        }

# --- Pygame Visualization ---

def world_to_screen(r, c):
    """Converts grid row, col to screen x, y (top-left of square)."""
    x = c * SQUARE_SIZE
    y = r * SQUARE_SIZE + INFO_PANEL_HEIGHT # Offset for info panel
    return x, y

def screen_to_world(x, y):
     """Converts screen x, y to grid row, col."""
     if y < INFO_PANEL_HEIGHT:
         return None, None # Clicked in info panel
     c = x // SQUARE_SIZE
     r = (y - INFO_PANEL_HEIGHT) // SQUARE_SIZE
     return r, c

def get_edge_rect_and_tuple(screen_x, screen_y, game):
    """
    Finds the edge tuple corresponding to screen coords, if close enough.
    This checks proximity to the visual center line of potential edges.
    Returns (edge_tuple, rect) or (None, None).
    """
    # Check Horizontal Edges first
    # Find the y-coordinate of the nearest horizontal grid line.
    grid_line_y_index = round((screen_y - INFO_PANEL_HEIGHT) / SQUARE_SIZE)
    grid_line_y = grid_line_y_index * SQUARE_SIZE + INFO_PANEL_HEIGHT

    # Check if click is vertically close to this line
    if abs(screen_y - grid_line_y) <= EDGE_CLICK_TOLERANCE:
        # The edge tuple corresponds to the square *above* this line.
        r_h = grid_line_y_index - 1
        c_h = screen_x // SQUARE_SIZE
        # Check if click is within the horizontal span of this potential edge
        square_x_start, _ = world_to_screen(r_h, c_h)
        if square_x_start <= screen_x < square_x_start + SQUARE_SIZE:
            edge_h_tuple = ((r_h, c_h), HORIZONTAL)
            # Check if this edge actually exists in the game model
            if edge_h_tuple in game.edges and game.edges[edge_h_tuple]['exists']:
                rect = pygame.Rect(c_h * SQUARE_SIZE, grid_line_y - EDGE_THICKNESS // 2, SQUARE_SIZE, EDGE_THICKNESS)
                return edge_h_tuple, rect

    # Check Vertical Edges
    # Find the x-coordinate of the nearest vertical grid line.
    grid_line_x_index = round(screen_x / SQUARE_SIZE)
    grid_line_x = grid_line_x_index * SQUARE_SIZE

    # Check if click is horizontally close to this line
    if abs(screen_x - grid_line_x) <= EDGE_CLICK_TOLERANCE:
        # The edge tuple corresponds to the square *left* of this line.
        r_v = (screen_y - INFO_PANEL_HEIGHT) // SQUARE_SIZE
        c_v = grid_line_x_index - 1
        # Check if click is within the vertical span of this potential edge
        _, square_y_start = world_to_screen(r_v, c_v)
        if square_y_start <= screen_y < square_y_start + SQUARE_SIZE:
            edge_v_tuple = ((r_v, c_v), VERTICAL)
            # Check if this edge actually exists in the game model
            if edge_v_tuple in game.edges and game.edges[edge_v_tuple]['exists']:
                rect = pygame.Rect(grid_line_x - EDGE_THICKNESS // 2, r_v * SQUARE_SIZE + INFO_PANEL_HEIGHT, EDGE_THICKNESS, SQUARE_SIZE)
                return edge_v_tuple, rect

    return None, None # No existing edge found nearby


def draw_board(screen, game, font, play_again_button_rect, mouse_pos):
    """Draws the entire game board, info panel, and buttons."""
    screen.fill(WHITE)

    # --- Draw Info Panel ---
    info_rect = pygame.Rect(0, 0, SCREEN_WIDTH, INFO_PANEL_HEIGHT)
    pygame.draw.rect(screen, GRAY, info_rect)

    # Display Player Turn or Winner - Positioned Left
    player_text = f"Turn: {game.current_player}"
    player_color = BLUE if game.current_player == LEFT_PLAYER else RED
    if game.winner:
        player_text = f"Winner: {game.winner}!"
        player_color = GREEN # Winner shown in green

    text_surf = font.render(player_text, True, player_color)
    # Align text to the left with some padding
    text_rect = text_surf.get_rect(midleft=(20, INFO_PANEL_HEIGHT // 2)) # Use midleft for alignment
    screen.blit(text_surf, text_rect)

    # Display Active Squares Count - Positioned Center-Right (before button)
    squares_text = f"Active Squares: {len(game.active_squares_coords)}"
    sq_surf = font.render(squares_text, True, BLACK)
    # Align text towards the right, before the button area
    sq_rect = sq_surf.get_rect(midright=(PLAY_AGAIN_BUTTON_X - 30, INFO_PANEL_HEIGHT // 2)) # Use midright
    screen.blit(sq_surf, sq_rect)

    # --- Draw Play Again Button (if game over) ---
    if game.winner:
        button_color = DARK_GRAY
        text_color = WHITE
        # Check for hover
        if play_again_button_rect.collidepoint(mouse_pos):
            button_color = LIGHT_GREEN # Hover color

        pygame.draw.rect(screen, button_color, play_again_button_rect, border_radius=5)
        button_text_surf = font.render("Play Again", True, text_color)
        button_text_rect = button_text_surf.get_rect(center=play_again_button_rect.center)
        screen.blit(button_text_surf, button_text_rect)


    # --- Draw Grid and Edges ---
    # Determine grid bounds needed for drawing based on the original shape
    if not game.all_squares_coords: # Handle empty case
        pygame.display.flip()
        return

    min_r = min((r for r, c in game.all_squares_coords), default=0)
    max_r = max((r for r, c in game.all_squares_coords), default=0)
    min_c = min((c for r, c in game.all_squares_coords), default=0)
    max_c = max((c for r, c in game.all_squares_coords), default=0)

    # Draw active squares backgrounds (optional, helps visibility)
    for r_sq, c_sq in game.active_squares_coords:
        x, y = world_to_screen(r_sq, c_sq)
        sq_rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)
        # Light checkerboard pattern for active squares
        bg_color = (230, 230, 250) if (r_sq + c_sq) % 2 == 0 else (240, 240, 255)
        pygame.draw.rect(screen, bg_color , sq_rect)

    # Draw Edges
    legal_moves = set(game.get_legal_moves()) # Get all legal moves once for efficiency

    # Iterate through all *possible* edge locations relevant to the shape
    # Extend range slightly to catch edges bordering the min/max squares
    for r in range(min_r - 1, max_r + 2):
        for c in range(min_c - 1, max_c + 2):
             # Horizontal edge below (r, c)
            edge_h = ((r, c), HORIZONTAL)
            if edge_h in game.edges and game.edges[edge_h]['exists']:
                # Calculate screen coordinates for the line segment
                x1, y1 = world_to_screen(r + 1, c) # Line is at the top of square (r+1, c)
                x2 = x1 + SQUARE_SIZE
                y2 = y1
                color = game.edges[edge_h]['color']

                # Highlight if it's a legal move for the current player
                # Draw the thicker highlight color *first*
                if edge_h in legal_moves:
                     pygame.draw.line(screen, HIGHLIGHT_COLOR, (x1, y1), (x2, y2), EDGE_THICKNESS + HIGHLIGHT_THICKNESS_INCREASE)

                # Draw the actual edge line on top with its original color and thickness
                pygame.draw.line(screen, color, (x1, y1), (x2, y2), EDGE_THICKNESS)

            # Vertical edge right of (r, c)
            edge_v = ((r, c), VERTICAL)
            if edge_v in game.edges and game.edges[edge_v]['exists']:
                # Calculate screen coordinates for the line segment
                x1, y1 = world_to_screen(r, c + 1) # Line is at the left of square (r, c+1)
                x2 = x1
                y2 = y1 + SQUARE_SIZE
                color = game.edges[edge_v]['color']

                # Highlight if it's a legal move
                # Draw the thicker highlight color *first*
                if edge_v in legal_moves:
                     pygame.draw.line(screen, HIGHLIGHT_COLOR, (x1, y1), (x2, y2), EDGE_THICKNESS + HIGHLIGHT_THICKNESS_INCREASE)

                # Draw the actual edge line on top with its original color and thickness
                pygame.draw.line(screen, color, (x1, y1), (x2, y2), EDGE_THICKNESS)


    # Optional: Draw faint grid lines for all original square boundaries for context
    # Useful for seeing the shape even after squares are destroyed
    for r_sq, c_sq in game.all_squares_coords:
         x, y = world_to_screen(r_sq, c_sq)
         rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)
         pygame.draw.rect(screen, GRAY, rect, 1) # Draw outline only

    pygame.display.flip()


# --- Main Game Loop ---
def main():
    # Define potential shapes
    l_shape_squares = {(0, 0), (0, 1), (1, 0)}
    simple_square = {(0,0)}
    two_by_two = {(0,0), (0,1), (1,0), (1,1)}
    long_strip = {(0,0), (0,1), (0,2), (0,3)}
    

    # --- Select the shape to use for the game ---
    # current_shape = simple_square
    # current_shape = l_shape_squares
    current_shape = two_by_two
    # current_shape = long_strip
    # ---------------------------------------------

    try:
        # Initialize the game instance
        game = FragmentedSquaresGame(current_shape)
    except ValueError as e:
        print(f"Error initializing game: {e}")
        sys.exit(1)


    pygame.init()
    # Adjust screen height to include the info panel
    screen = pygame.display.set_mode((SCREEN_WIDTH, TOTAL_SCREEN_HEIGHT))
    pygame.display.set_caption("Fragmented Squares")
    font = pygame.font.Font(None, 30) # Default font, size 36
    clock = pygame.time.Clock()

    # Define the Play Again button rectangle
    play_again_button_rect = pygame.Rect(PLAY_AGAIN_BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos() # Get mouse position once per frame

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    # Check Play Again button first (only if game is over)
                    if game.winner and play_again_button_rect.collidepoint(event.pos):
                        print("Play Again button clicked!")
                        game.reset() # Reset the game state
                    # If game not over, check for edge clicks
                    elif not game.winner:
                        clicked_edge, _ = get_edge_rect_and_tuple(event.pos[0], event.pos[1], game)
                        if clicked_edge:
                            print(f"Attempting move on edge: {clicked_edge} by {game.current_player}")
                            success, message = game.make_move(clicked_edge)
                            if success:
                                print(message)
                            else:
                                print(f"Move failed: {message}")
                        else:
                            print("Clicked, but not near a valid, existing edge.")

        # --- Drawing ---
        draw_board(screen, game, font, play_again_button_rect, mouse_pos)

        # --- Frame Limiting ---
        clock.tick(30) # Limit FPS to 30

    pygame.quit()

    # --- Final Data Output ---
    print("\n" + "="*30)
    print("--- Game Session Ended ---")
    # Check if the last game actually finished
    if game.move_history:
        print(f"Last game winner: {game.winner if game.winner else 'Game Incomplete'}")
        print(f"Total Moves in last game: {len(game.move_history)}")
        print("\n--- Move History (Last Game) ---")
        # Basic print, consider formatting or saving elsewhere
        for i, move in enumerate(game.move_history):
            print(f"Move {i+1}:")
            print(f"  Player: {move['player']}")
            print(f"  Edge Removed: {move['edge_removed']} (Color: {move['edge_color']})")
            # Convert sets to sorted lists for consistent print order
            destroyed_list = sorted(list(move['squares_destroyed']))
            active_before_list = sorted(list(move['active_squares_before']))
            active_after_list = sorted(list(move['active_squares_after']))
            print(f"  Squares Destroyed: {destroyed_list}")
            print(f"  Active Squares Before: {len(active_before_list)} {active_before_list}")
            print(f"  Active Squares After: {len(active_after_list)} {active_after_list}")
            if move['game_over_after']:
                 print(f"  GAME OVER! Winner declared: {move['winner']}")
    else:
        print("No moves were made in the last game session.")
    print("="*30)


if __name__ == "__main__":
    main()
