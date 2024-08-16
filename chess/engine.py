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

def _get_piece_object(move, source_piece, target_piece, history=None, castle=None):
    """Maps to each piece the associated piece type code."""

    piece_type = source_piece[1]
    extra_info = {}

    if history and piece_type == 'p':
        extra_info['history'] = history

    if castle and piece_type == 'K':
        extra_info['castling_rights'] = castle

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

    return Piece(move, source_piece, target_piece, **extra_info)


def _get_castle_pos(color):
    if color == 'w':
        left_rook, right_rook = (7, 0), (7, 7)
        queenside, kingside = (7, 2), (7, 6)
    else:
        left_rook, right_rook = (0, 0), (0, 7)
        queenside, kingside = (0, 2), (0, 6)

    return left_rook, right_rook, queenside, kingside



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


def gen_valid_moves(board, history, white_to_move, source_piece, source_pos, castling_rights):
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
            piece = _get_piece_object(move, source_piece, target_piece, history, castling_rights)

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
    def __init__(self, board, history, white_to_move):
        """
        Initializes a Move object.

        Parameters:
        source_pos (tuple): The starting position of the move (row, col).
        end_pos (tuple): The ending position of the move (row, col).
        board (list): The current state of the chess board.
        """

        self.board = board
        self.history = history
        self.white_to_move = white_to_move

        # For castling rights
        self.castling_rights = {'w_kingside': True, 'w_queenside': True,
                                'b_kingside': True, 'b_queenside': True}

    def validate(self, source_pos, target_pos):
        """
        Checks if the move is valid based on the current board state.

        Returns:
        bool: True if the move is valid, False otherwise.
        """

        source_piece = piece_name(self.board, source_pos)
        target_piece = piece_name(self.board, target_pos)

        source_color = source_piece[0]
        target_color = target_piece[0]

        is_white_piece = True if source_color == 'w' else False

        # Turn validation
        if self.white_to_move and not is_white_piece:
            return False, None
        
        if not self.white_to_move and is_white_piece:
            return False, None

        # Cannot attack friendly squares
        if source_color == target_color:
            return False, None

        # For piece-specific validation
        move = [source_pos, target_pos]
        piece = _get_piece_object(move, source_piece, target_piece,
                                  self.history, self.castling_rights)

        is_valid_piece, move_type = piece.validate()

        if not is_valid_piece:
            return False, None

        is_path_clear = _is_path_clear(self.board, source_piece,
                                       source_pos, target_pos)

        if not is_path_clear:
            return False, None

        self.white_to_move = not self.white_to_move

        source_type = source_piece[1]
        self.update_castle(source_pos, source_type, source_color)

        return True, move_type


    def update_castle(self, source_pos, source_type, source_color):
        if source_type == 'K':
            self.castling_rights[f'{source_color}_kingside'] = False
            self.castling_rights[f'{source_color}_queenside'] = False

        if source_type == 'R':
            left_rook_pos, right_rook_pos, _, _ = _get_castle_pos(source_color)

            if source_pos == right_rook_pos:
                self.castling_rights[f'{source_color}_kingside'] = False
            elif source_pos == left_rook_pos:
                self.castling_rights[f'{source_color}_queenside'] = False


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


    def perform_move(self, source_pos, target_pos, special_move):
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

        source_name = piece_name(self.board, source_pos)
        target_name = piece_name(self.board, target_pos)

        self.board[target_row][target_col] = self.board[source_row][source_col]
        self.board[source_row][source_col] = EMPTY

        if special_move == "en passant":
            source_color = source_name[0]
            if source_color == 'w':
                en_passant_row = target_row + 1
            else:
                en_passant_row = target_row - 1

            en_passant_col = target_col
            self.board[en_passant_row][en_passant_col] = EMPTY

        if special_move == "castle":
            source_color = source_name[0]
            left_rook, right_rook, queenside, kingside = _get_castle_pos(source_color)

            if target_pos == queenside:
                rook_row, rook_col = left_rook
                king_row, king_col = source_pos

                self.board[rook_row][rook_col+3] = self.board[rook_row][rook_col]
                self.board[king_row][king_col-3] = self.board[king_row][king_col]
                self.board[rook_row][rook_col] = EMPTY
                self.board[king_row][king_col] = EMPTY
            elif target_pos == kingside:
                rook_row, rook_col = right_rook
                king_row, king_col = source_pos

                self.board[rook_row][rook_col-2] = self.board[rook_row][rook_col]
                self.board[king_row][king_col+3] = self.board[king_row][king_col]
                self.board[rook_row][rook_col] = EMPTY
                self.board[king_row][king_col] = EMPTY

        new_entry = ((source_pos, target_pos), (source_name, target_name), self.board)
        self.history.append(new_entry)


