from chess.pieces import (
    Pawn,
    Knight,
    Bishop,
    Rook,
    King,
    Queen
)

from src.config import EMPTY, BOARD_SIZE
from chess.utils import piece_name

CHESS_BOARD =[['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
              ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
              ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]



def _piece_type(move, source_piece, target_piece, history=None):
    """Maps to each piece the associated piece type code."""

    piece_type = source_piece[1]

    piece_map = {
        'p': Pawn,
        'N': Knight,
        'B': Bishop,
        'R': Rook,
        'K': King,
        'Q': Queen,
    }

    Piece = piece_map.get(piece_type)

    if Piece is None:
        raise ValueError(
            f"Piece type is not supported. Please make sure the provided piece "
            f"is correct. Invalid piece: '{source_piece}'."
        )

    require_history = {'p', 'K', 'R'}

    if history and piece_type in require_history:
        return Piece(move, source_piece, target_piece, history)

    return Piece(move, source_piece, target_piece)


def _is_path_clear(board, source_piece, source_pos, target_pos):
    """
    Checks if a piece is standing along the selected piece's
    trajectory before reaching the target index. For knights,
    this function is unnecessary, as they can can jump over pieces
    freely.
    """

    source_type = source_piece[1]
    knight = source_type == 'N'

    # Knights don't need this validation
    if knight:
        return True

    source_row, source_col = source_pos
    target_row, target_col = target_pos

    change_in_row = target_row - source_row
    change_in_col = target_col - source_col

    # Normalize steps to be between 1, 0, and -1
    row_step = change_in_row // max(1, abs(change_in_row))
    col_step = change_in_col // max(1, abs(change_in_col))

    current_row = source_row + row_step
    current_col = source_col + col_step

    while (current_row, current_col) != (target_row, target_col):
        current_piece = board[current_row][current_col]

        if current_piece != EMPTY:
            return False

        current_row += row_step
        current_col += col_step

    return True


def gen_valid_moves(board, history, white_to_move, source_piece, source_pos):
    """
    Generates the available move space for the selected piece.
    This works by simulating all possible target locations and
    exhaustively validating the move until a valid move is reached.

    Yields:
        target_pos: the position of the target piece
        bool: True if the move is valid, False otherwise.
    """

    source_color = source_piece[0] # Necessary for pawn moves

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            target_piece = board[row][col]
            target_pos = (row, col)
            target_color = target_piece[0]

            move = [source_pos, target_pos]
            piece = _piece_type(move, source_piece, target_piece, history)

            is_white_piece = True if source_color == 'w' else False

            # Turn validation
            if white_to_move and not is_white_piece:
                yield target_pos, False
                continue

            if not white_to_move and is_white_piece:
                yield target_pos, False
                continue

            # Cannot attack friendly squares
            if source_color == target_color:
                yield target_pos, False
                continue

            is_valid_piece, _ = piece.validate()

            if not is_valid_piece:
                yield target_pos, False
                continue

            if not _is_path_clear(board, source_piece, source_pos, target_pos):
                yield target_pos, False
                continue

            yield target_pos, True


class Move:
    def __init__(self, board, history, white_to_move, source_pos, target_pos):
        """
        Initializes a Move object.

        Parameters:
        source_pos (tuple): The starting position of the move (row, col).
        end_pos (tuple): The ending position of the move (row, col).
        board (list): The current state of the chess board.
        """

        self.source_pos = source_pos
        self.target_pos = target_pos
        self.board = board
        self.history = history
        self.white_to_move = white_to_move

        self.source_row, self.source_col = source_pos

        self.source_piece = piece_name(board, source_pos)
        self.source_color = self.source_piece[0]
        self.source_type = self.source_piece[1]

        self.target_row, self.target_col = target_pos

        self.target_piece = piece_name(board, target_pos)
        self.target_color = self.target_piece[0]
        self.target_type = self.target_piece[1]


    def validate(self):
        """
        Checks if the move is valid based on the current board state.

        Returns:
        bool: True if the move is valid, False otherwise.
        """

        is_white_piece = True if self.source_color == 'w' else False

        # Turn validation
        if self.white_to_move and not is_white_piece:
            return False, None
        
        if not self.white_to_move and is_white_piece:
            return False, None

        # Cannot attack friendly squares
        if self.source_color == self.target_color:
            return False, None

        # For piece-specific validation
        move = [self.source_pos, self.target_pos]
        piece = _piece_type(move, self.source_piece, self.target_piece, self.history)

        is_valid_piece, move_type = piece.validate()

        if not is_valid_piece:
            return False, None

        is_path_clear = _is_path_clear(self.board, self.source_piece,
                                       self.source_pos, self.target_pos)

        if not is_path_clear:
            return False, None

        self.white_to_move = not self.white_to_move

        return True, move_type


    def log_turn(self):
        """Prints the turn for troubleshooting purposes."""

        if self.white_to_move:
            print("turn: white")
        else:
            print("turn: black")


class Engine:
    def __init__(self):
        self.board = CHESS_BOARD

        move, piece_names = (None, None), (None, None)
        self.history = [(move, piece_names, CHESS_BOARD)] # Keeps track of board state


    def perform_move(self, source_pos, target_pos, en_passant=False):
        """
        Attempts to make a move and updates the game state accordingly.

        Parameters:
        source_pos (tuple): The starting position of the move (row, col).
        source_pos (tuple): The ending position of the move (row, col).

        Returns:
        bool: True if the move was successfully made, False otherwise.
        """

        source_row, source_col = source_pos
        target_row, target_col = target_pos

        source_piece_name = piece_name(self.board, source_pos)
        target_piece_name = piece_name(self.board, target_pos)

        self.board[target_row][target_col] = self.board[source_row][source_col]
        self.board[source_row][source_col] = EMPTY

        if en_passant:
            source_piece_color = source_piece_name[0]
            if source_piece_color == 'w':
                en_passant_row = target_row + 1
            else:
                en_passant_row = target_row - 1

            en_passant_col = target_col
            self.board[en_passant_row][en_passant_col] = EMPTY

        new_entry = ((source_pos, target_pos), (source_piece_name, target_piece_name), self.board)
        self.history.append(new_entry)


