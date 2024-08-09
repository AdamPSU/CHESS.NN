from chess.pieces import (
    Pawn,
    Knight,
    Bishop,
    Rook,
    King,
    Queen,
)

from src.config import EMPTY, BOUNDS


CHESS_BOARD =[['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
              ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
              ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]


class Move:
    def __init__(self, board, white_to_move, start, end):
        """
        Initializes a Move object.

        Parameters:
        start_pos (tuple): The starting position of the move (row, col).
        end_pos (tuple): The ending position of the move (row, col).
        board (list): The current state of the chess board.
        """

        self.start = start
        self.end = end
        self.board = board
        self.white_to_move = white_to_move

        self.start_row, self.start_col = start
        self.end_row, self.end_col = end

        start_piece_idx = (self.start_row, self.start_col)
        self.start_piece = self.piece(start_piece_idx)
        self.start_piece_color = self.start_piece[0]
        self.start_piece_type = self.start_piece[1]

        target_piece_idx = (self.end_row, self.end_col)
        self.target_piece = self.piece(target_piece_idx)
        self.target_piece_color = self.target_piece[0]
        self.target_piece_type = self.target_piece[1]


    def log_turn(self):
        if self.white_to_move:
            print("turn: white")

        print("turn: black")


    def piece_type(self):
        color = 'w' if self.white_to_move else 'b'

        piece_map = {
            'p': Pawn(),
            'N': Knight(),
            'B': Bishop(),
            'R': Rook(),
            'K': King(),
            'Q': Queen(),
        }

        piece_type = piece_map.get(self.start_piece_type)

        return piece_type


    def piece(self, index):
        if None in index:
            return None

        row = index[0]
        col = index[1]

        piece = self.board[row][col]

        return piece


    def _is_path_clear(self):
        knight = self.start_piece_type == 'N'

        # Pawns and Knights don't need this validation
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


    def validate(self):
        """
        Checks if the move is valid based on the current board state.

        Returns:
        bool: True if the move is valid, False otherwise.
        """


        is_white_piece = True if self.start_piece_color == 'w' else False

        # Turn validation
        if self.white_to_move and not is_white_piece:
            return False

        if not self.white_to_move and is_white_piece:
            return False

        # Cannot attack friendly squares
        if self.start_piece_color == self.target_piece_color:
            return False

        # Piece-specific validation
        piece_handler = self.piece_type()
        move = (self.start_piece, self.target_piece)

        is_valid_piece = piece_handler.validate(move, self.start_piece_color, self.start, self.end)

        if not is_valid_piece:
            return False

        is_path_clear = self._is_path_clear()

        if not is_path_clear:

            return False

        self.white_to_move = not self.white_to_move

        return True


class Engine:
    def __init__(self):
        self.board = CHESS_BOARD


    def piece(self, location):
        if None in location:
            return None

        row = location[0]
        col = location[1]

        piece = self.board[row][col]

        return piece


    def perform_move(self, start, end):
        """
        Attempts to make a move and updates the game state accordingly.

        Parameters:
        start_pos (tuple): The starting position of the move (row, col).
        end_pos (tuple): The ending position of the move (row, col).

        Returns:
        bool: True if the move was successfully made, False otherwise.
        """

        start_row, start_col = start
        end_row, end_col = end

        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[start_row][start_col] = EMPTY


