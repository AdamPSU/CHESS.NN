import pygame as pg

from chess.engine import Engine, Move, gen_valid_moves
from chess.utils import piece_name
from src.graphics import draw_rect, load_pieces, load_grid, highlight_valid_moves, graphics; load_pieces()  # Preload all piece images into IMAGES
from src.config import *
from src.graphics import IMAGES


class Chess:
    """Chess interface facilitated by Pygame."""

    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("CHESS-NN")
        self.clock = pg.time.Clock()

        # Track side to move and underlying game engine
        self.white_to_move = True
        self.engine = Engine()
        self.move = Move(self.engine.board, self.engine.history, self.white_to_move)

        # Right-click markers vs. generated legal moves for drag-and-drop
        self.marked_moves = set()
        self.valid_moves = set()

        # State for dragging pieces
        self.source_piece = None
        self.source_pos = None
        self.target_pos = None

        load_grid(self.screen)  # Draw board background once

        # Set window icon to black king as placeholder
        self.icon = IMAGES['bK']
        pg.display.set_icon(self.icon)

        self.running = True

    def run(self):
        """Main game loop: handle events, render board, and process moves."""
        while self.running:
            current_piece, row, col = self.get_tile_under_mouse()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

                if event.type == pg.MOUSEBUTTONDOWN:
                    # Handle marking tiles with right-click or clearing with left-click
                    self.marked_moves_handler(event, row, col)

                    left_click = event.button == 1
                    if left_click and current_piece is not None:
                        # Begin drag: record the piece and its origin
                        self.source_piece = current_piece
                        self.source_pos = (row, col)
                        # If not dragging an empty square, compute its legal moves
                        if current_piece != EMPTY:
                            self.generate_moves()

                if event.type == pg.MOUSEBUTTONUP:
                    # Release drag: clear highlight of potential moves
                    self.valid_moves.clear()
                    if self.target_pos:
                        # Attempt a move from source to drop target
                        self.move_handler(self.source_pos, self.target_pos)
                    # Reset drag state
                    self.source_pos = None
                    self.target_pos = None

            # Render pieces and any right-click markers
            graphics(self.screen, self.engine.board, self.marked_moves)
            # Show valid moves for current drag, if any
            highlight_valid_moves(self.screen, self.valid_moves)

            # Continue dragging piece with mouse
            self.target_pos = self.drag(self.source_piece, self.source_pos)

            self.clock.tick(MAX_FPS)
            pg.display.flip()

        pg.quit()

    def get_tile_under_mouse(self):
        """Return the piece name and board coordinates under the mouse, if valid."""
        x_mouse, y_mouse = pg.mouse.get_pos()
        row = y_mouse // TILE_SIZE
        col = x_mouse // TILE_SIZE
        try:
            if row >= 0 and col >= 0:
                pos = (row, col)
                current_piece = piece_name(self.engine.board, pos)
                return current_piece, row, col
        except IndexError:
            # Mouse outside board bounds
            pass
        return None, None, None

    def marked_moves_handler(self, event, row, col):
        """
        Handle left/right clicks to toggle markers on tiles for player notes.
        Left-click clears all markers; right-click toggles a marker at (row, col).
        """
        left_click = event.button == 1
        right_click = event.button == 3

        if left_click:
            self.marked_moves.clear()
        elif right_click:
            pos = (row, col)
            if pos in self.marked_moves:
                self.marked_moves.discard(pos)
            else:
                self.marked_moves.add(pos)

    def generate_moves(self):
        """
        Populate self.valid_moves by querying engine.gen_valid_moves.
        Each tuple returned is (destination, is_move_allowed).
        """
        if self.valid_moves:
            self.valid_moves.clear()
        for loc, is_allowed in gen_valid_moves(
            self.engine.board,
            self.engine.history,
            self.white_to_move,
            self.source_piece,
            self.source_pos,
            self.move.castling_rights
        ):
            if is_allowed:
                self.valid_moves.add(loc)

    def drag(self, piece, loc):
        """
        Visualize dragging a piece image with the mouse.
        Returns the board coordinates under the cursor for potential drop.
        """
        if not loc or piece == EMPTY:
            return

        row, col = loc
        # Highlight the origin tile
        rect = draw_rect(row, col)
        pg.draw.rect(self.screen, '#cda7e7', rect, 5)

        image = IMAGES[piece]
        mouse_pos = pg.mouse.get_pos()
        # Slight offset for layered rendering effect
        offset = (1, 1)
        # Draw shadow copy then actual piece under cursor
        self.screen.blit(image, image.get_rect(center=pg.Vector2(mouse_pos) + offset))
        self.screen.blit(image, image.get_rect(center=pg.Vector2(mouse_pos)))

        # Convert mouse pixel position back into board indices
        end_row = mouse_pos[1] // TILE_SIZE
        end_col = mouse_pos[0] // TILE_SIZE
        return end_row, end_col

    def move_handler(self, source, target):
        """
        Validate and execute a move from source to target.
        Move.validate returns (bool, special_move_flag).
        """
        is_valid_move, special_move = self.move.validate(source, target)
        if not is_valid_move:
            return

        # Toggle turn and apply move to internal engine state
        self.white_to_move = not self.white_to_move
        self.engine.perform_move(source, target, special_move=special_move)


if __name__ == '__main__':
    main = Chess()
    main.run()