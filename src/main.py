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
        IMAGES[piece] = pg.transform.scale(pg.image.load("../images/" + piece + ".png"),
                                           size=(PIECE_SIZE, PIECE_SIZE))


def _graphics(screen, game):
    """
    Responsible for generating and updating GUI graphics
    for each game state.
    """

    board = game.board
    colors = np.array([pg.Color("#F7FCFC"), pg.Color("#C7D4D4")]) # Light gray, gray

    # Checker pattern on the board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 0:
                color = colors[0]
            else:
                color = colors[1]
            pg.draw.rect(screen, color, pg.Rect(col*PIECE_SIZE, row*PIECE_SIZE, PIECE_SIZE, PIECE_SIZE))

    # Place pieces on the board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row, col]
            if piece != EMPTY:
                screen.blit(IMAGES[piece], pg.Rect(col*PIECE_SIZE, row*PIECE_SIZE, PIECE_SIZE, PIECE_SIZE))


class Chess:
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.icon = pg.image.load("../images/bK.png")

        pg.display.set_caption("CHESS-NN")
        pg.display.set_icon(self.icon)
        self.clock = pg.time.Clock()

        self.game = Game()
        _load_pieces()

        self.clicked_piece = ()  # No piece is selected
        self.click_logger = []  # Keeps track of player clicks

        self.running = True


    def reset_move(self):
        """
        Resets the selected piece and player clicks. This method is called
        to clear the selection state, either when an invalid move is detected
        or a valid move is completed.
        """

        self.clicked_piece = ()
        self.click_logger = []


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

        # Player clicked the same piece twice
        if self.clicked_piece == (row, col):
            self.reset_move()

            return

        bounds = BOARD_SIZE - 1

        # Player clicked out of bounds
        if col > bounds or row > bounds:
            self.reset_move()

            return

        self.clicked_piece = (row, col)
        self.click_logger.append(self.clicked_piece)

        total_clicks = len(self.click_logger)
        chess_piece = self.game.board[row, col]

        # If 1st click and empty square is selected, restart
        if total_clicks == 1 and chess_piece == EMPTY:
            self.reset_move()

        if total_clicks == 2:
            move = Move(self.game.board, self.click_logger[0], self.click_logger[1])
            is_valid = self.game.isValid(move)

            # Check if the move is valid before playing it
            if is_valid:
                self.game.makeMove(move)

            self.reset_move()


    def run(self):
        """Run the chess game."""

        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    pos = pg.mouse.get_pos()  # Location of mouse on the chess board

                    col = pos[0] // PIECE_SIZE
                    row = pos[1] // PIECE_SIZE

                    self.move_handler(row, col)

            _graphics(self.screen, self.game)
            self.clock.tick(MAX_FPS)  # Control the frame rate
            pg.display.flip()  # Update the display

        pg.quit()


if __name__ == '__main__':
    chess = Chess()
    chess.run()