import pygame as pg
import numpy as np

from engine.chess import Game, Move

from src.config import *

def _load_pieces():
    """
    Load chess pieces. This will only be done once, at the start of the
    program's execution.
    """

    # 'b' prefixes for black pieces, 'w' for white pieces
    pieces = ['bR', 'bN', 'bB', 'bK', 'bQ', 'bB', 'bN', 'bR', 'bp',
              'wR', 'wN', 'wB', 'wK', 'wQ', 'wB', 'wN', 'wR', 'wp']

    for piece in pieces:
        image = pg.image.load("../images/" + piece + ".png")
        IMAGES[piece] = pg.transform.smoothscale(image, size=(PIECE_SIZE, PIECE_SIZE))


def _graphics(screen, game):
    """
    Responsible for generating and updating GUI graphics
    for each chessboard game state.
    """

    board = game.board

    white, purple = '#f1f1f1', '#8475b9'
    colors = np.array([pg.Color(white), pg.Color(purple)])

    # Checker pattern on the board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 0:
                color = colors[0]
            else:
                color = colors[1]
            pg.draw.rect(screen, color, pg.Rect(col*TILE_SIZE, row*TILE_SIZE,
                                                TILE_SIZE, TILE_SIZE))

    # Place pieces on the board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece != EMPTY:
                piece_image = IMAGES[piece]
                piece_rect = piece_image.get_rect()

                offset = 5
                piece_rect.center = (col * TILE_SIZE + TILE_SIZE // 2,
                                     row * TILE_SIZE + TILE_SIZE // 2 + offset)
                screen.blit(piece_image, piece_rect.topleft)


class Chess:
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.icon = pg.image.load("../images/bK.png")

        pg.display.set_caption("CHESS-NN")
        pg.display.set_icon(self.icon)
        self.clock = pg.time.Clock()

        self.game = Game()
        self.move = Move(board=self.game.board, white_to_move=True)
        _load_pieces()

        self.running = True


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

        if not is_valid_move:
            return

        start_pos = self.move.move_logger[0]
        end_pos = self.move.move_logger[1]

        self.game.perform_move(start_pos, end_pos)
        self.move.reset()


    def run(self):
        """Run the chess game."""

        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    pos = pg.mouse.get_pos() # Location of mouse on the chess board

                    col = pos[0] // TILE_SIZE
                    row = pos[1] // TILE_SIZE

                    self.move_handler(row, col)

            _graphics(self.screen, self.game)
            self.clock.tick(MAX_FPS) # Control the frame rate
            pg.display.flip()  # Update the display

        pg.quit()


if __name__ == '__main__':
    main = Chess()
    main.run()