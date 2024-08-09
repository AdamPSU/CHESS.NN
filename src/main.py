import pygame as pg
import numpy as np

from chess.engine import Engine, Move

from src.config import *

def _load_pieces():
    """
    Load chess pieces. This will only be done once, at the start of the
    game's execution.
    """

    pieces = ['bR', 'bN', 'bB', 'bK', 'bQ', 'bB', 'bN', 'bR', 'bp',
              'wR', 'wN', 'wB', 'wK', 'wQ', 'wB', 'wN', 'wR', 'wp']

    for piece in pieces:
        image = pg.image.load("../images/" + piece + ".png")
        IMAGES[piece] = pg.transform.smoothscale(image, size=(PIECE_SIZE, PIECE_SIZE))


def _load_grid(screen):
    """
    Responsible for generating and updating GUI graphics
    for each chessboard game state.
    """

    # surface = pg.Surface((screen.get_size()))

    white, purple = '#f1f1f1', '#8475b9'
    colors = [pg.Color(white), pg.Color(purple)]

    # Checker pattern on the board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 0:
                color = colors[0]
            else:
                color = colors[1]

            rect = pg.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pg.draw.rect(screen, color, rect)


def _update_pieces(screen, board):
    """
    Responsible for generating and updating GUI graphics
    for each chessboard game state.
    """

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]

            if piece == EMPTY:
                continue

            piece_image = IMAGES[piece]
            piece_rect = piece_image.get_rect()

            offset = 5
            piece_rect.center = (col * TILE_SIZE + TILE_SIZE // 2,
                                 row * TILE_SIZE + TILE_SIZE // 2 + offset)
            screen.blit(piece_image, piece_rect.topleft)


def _highlight_tile(screen, tile):
    if None in tile:
        return

    row, col = tile

    surface = pg.Surface((TILE_SIZE, TILE_SIZE))
    surface.set_alpha(150)

    rouge = pg.Color('#7d3d54')
    surface.fill(rouge)

    screen.blit(surface, (col*TILE_SIZE, row*TILE_SIZE))


def _graphics(screen, board, highlighted):
    _load_grid(screen)

    for tile in highlighted:
        _highlight_tile(screen, tile)

    _update_pieces(screen, board)
    
    
class Chess:
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.icon = pg.image.load("../images/bK.png")

        pg.display.set_caption("CHESS-NN")
        pg.display.set_icon(self.icon)
        self.clock = pg.time.Clock()

        self.engine = Engine()
        self.move = Move(board=self.engine.board, white_to_move=True)

        self.highlighted = set()
        self.selected = None
        self.drop_position = None

        _load_pieces()
        _load_grid(self.screen)

        self.running = True


    def highlight_handler(self, tile):
        # Highlighted piece has been highlighted twice, un-highlight
        if tile in self.highlighted:
            self.highlighted.discard(tile)
        else:
            self.highlighted.add(tile)


    def move_handler(self, row, col):
        """
        Handles player clicks on the chessboard.

        Parameters:
        row (int): The row index of the clicked square.
        col (int): The column index of the clicked square.

        This method handles the logic for selecting and moving pieces on the board.
        It checks for invalid clicks (e.g., clicking the same piece twice or clicking
        out of bounds), validates the move, and updates the game state accordingly.
        """


        self.move.update(row, col)
        is_valid_move = self.move.validate()

        if not is_valid_move: return

        start_pos = self.move.move_logger[0]
        end_pos = self.move.move_logger[1]

        # self.move.log_move()

        self.engine.perform_move(start_pos, end_pos)
        self.move.reset()


    def click_handler(self, event, row, col):
        left_click = event.button == 1
        right_click = event.button == 3

        if left_click:
            # Un-highlight all highlighted pieces
            self.highlighted.clear()

            self.move_handler(row, col)
        elif right_click:  # Right mouse click
            tile = (row, col)
            self.highlight_handler(tile)


    def get_square_under_mouse(self):
        x_mouse, y_mouse = pg.mouse.get_pos()

        row = y_mouse // TILE_SIZE
        col = x_mouse // TILE_SIZE

        try:
            if row >= 0 and col >= 0:
                location = (row, col)

                return self.engine.piece(location), row, col

        except IndexError:
            pass

        return None, None, None


    def draw_drag(self, selected):
        if not selected:
            return

        piece, row, col = selected

        if piece == EMPTY:
            return

        if col is not None:
            rect = col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE
            pg.draw.rect(self.screen, '#cda7e7', rect, 5)

        image = IMAGES[piece]

        pos = pg.mouse.get_pos()
        offset = (1, 1)

        self.screen.blit(image, image.get_rect(center = pg.Vector2(pos) + offset))
        self.screen.blit(image, image.get_rect(center = pg.Vector2(pos)))

        new_row = pos[1] // TILE_SIZE
        new_col = pos[0] // TILE_SIZE

        return new_row, new_col


    def run(self):
        """Run the chess game."""

        while self.running:
            piece, row, col = self.get_square_under_mouse()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

                if event.type == pg.MOUSEBUTTONDOWN:
                    if piece is not None:
                        self.selected = piece, row, col

                    right_click = event.button == 3

                    if right_click:
                        tile = (row, col)
                        self.highlight_handler(tile)
                if event.type == pg.MOUSEBUTTONUP:
                    if self.drop_position:
                        piece, old_row, old_col = self.selected
                        self.engine.board[old_row][old_col] = EMPTY

                        new_row, new_col = self.drop_position

                        self.engine.board[new_row][new_col] = piece

                    self.selected = None
                    self.drop_position = None

            _graphics(self.screen, self.engine.board, self.highlighted)
            self.drop_position = self.draw_drag(self.selected)

            self.clock.tick(MAX_FPS) # Control the frame rate
            pg.display.flip()  # Update the display

        pg.quit()


if __name__ == '__main__':
    main = Chess()
    main.run()