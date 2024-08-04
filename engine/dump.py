from engine.pieces import (
    Pawn,
    Knight,
    Bishop,
    Rook,
    King,
    Queen,
)
from src.config import EMPTY, BOARD_SIZE


CHESS_BOARD =[['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
              ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
              ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

PIECE_MAP = {
    'p': Pawn(),
    'N': Knight(),
    'B': Bishop(),
    'R': Rook(),
    'K': King(),
    'Q': Queen(),
}


class Move:
    def __init__(self, start_pos, end_pos, board, white_to_move):
        """
        Initializes a Move object.

        Parameters:
        start_pos (tuple): The starting position of the move (row, col).
        end_pos (tuple): The ending position of the move (row, col).
        board (list): The current state of the chess board.
        """

        self.start_row, self.start_col = start_pos
        self.end_row, self.end_col = end_pos

        self.board = board

        self.selected_piece = board[self.start_row][self.start_col]
        self.target_piece = board[self.end_row][self.end_col]

        self.white_to_move = white_to_move


    def log_move(self):
        pass
        # print(f"start: {(self.start_row, self.start_col)}, end: {(self.end_row, self.end_col)}")


    def _is_same_piece(self):
        """Check if the starting position is the same as the ending position."""

        if self.selected_piece == self.target_piece:
            return True

        return False


    def _is_path_clear(self, piece):
        """
        Check if there is any piece on the way of a move's trajectory.

        Parameters:
        board (list): 2D list representing the chess board.
        start_pos (tuple): Starting position as (row, col).
        end_pos (tuple): Ending position as (row, col).

        Returns:
        bool: True if the path is clear, False otherwise.
        """

        target_color = self.target_piece[0]
        friendly_color = self.selected_piece[0]

        # Cannot attack friendly piece
        if target_color == friendly_color:
            return False

        knight = self.selected_piece[1] == 'N'

        # Knights don't need further validation
        if knight:
            return True

        change_in_row = self.end_row - self.start_row
        change_in_col = self.end_col - self.start_col

        # Normalize steps to be between 1, 0, and -1
        row_step = change_in_row // max(1, abs(change_in_row))
        col_step = change_in_col // max(1, abs(change_in_col))

        current_row = self.start_row + row_step
        current_col = self.start_col + col_step

        while (current_row, current_col) != (self.end_row, self.end_col):
            current_piece = self.board[current_row][current_col]

            if current_piece != EMPTY:
                return False

            current_row += row_step
            current_col += col_step

        return True


    def is_valid_move(self):
        """
        Checks if the move is valid based on the current board state.

        Returns:
        bool: True if the move is valid, False otherwise.
        """

        if self._is_same_piece():
            return False

        piece_symbol = self.selected_piece[1]
        piece = PIECE_MAP.get(piece_symbol)

        is_valid_piece = piece.validate(self.start_row, self.start_col, self.end_row,
                                        self.end_col, white_to_move=self.white_to_move)

        if not is_valid_piece:
            return False

        if not self._is_path_clear(piece):
            return False

        return True


    def execute(self):
        """
        Executes the move by updating the board state.
        """

        if self.is_valid_move():
            self.board[self.end_row][self.end_col] = self.selected_piece
            self.board[self.start_row][self.start_col] = EMPTY

            return True

        return False


class Game:
    def __init__(self):
        self.board = CHESS_BOARD
        self.white_to_move = True


    def perform_move(self, start_pos, end_pos):
        """
        Attempts to make a move and updates the game state accordingly.

        Parameters:
        start_pos (tuple): The starting position of the move (row, col).
        end_pos (tuple): The ending position of the move (row, col).

        Returns:
        bool: True if the move was successfully made, False otherwise.
        """

        move = Move(start_pos, end_pos, self.board, self.white_to_move)

        if move.execute():
            self.white_to_move = not self.white_to_move

            move.log_move()
            return True

        move.log_move()
        return False


# if __name__ == '__main__':
#     game = Game()
#     start_pos = (7, 2)  # White piece position
#     end_pos_empty = (5, 0)  # Empty position
#
#
#     print(game.perform_move(start_pos, end_pos_empty))


