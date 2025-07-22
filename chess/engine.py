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

# Standard starting layout for an 8x8 chess board, using two-character codes:
# first char for color ('w' or 'b'), second for piece type.
CHESS_BOARD = [
    ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
    ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
    ['--', '--', '--', '--', '--', '--', '--', '--'],
    ['--', '--', '--', '--', '--', '--', '--', '--'],
    ['--', '--', '--', '--', '--', '--', '--', '--'],
    ['--', '--', '--', '--', '--', '--', '--', '--'],
    ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
]

def _get_piece_object(move, source_piece, target_piece, history=None, castle=None):
    """Instantiate the correct Piece subclass based on source_piece code."""
    piece_type = source_piece[1]
    extra_info = {}

    # Pass pawn movement history to Pawn for en passant logic
    if history and piece_type == 'p':
        extra_info['history'] = history

    # Pass castling rights to King for castle validation
    if castle and piece_type == 'K':
        extra_info['castling_rights'] = castle

    # Map the second character in the piece code to the appropriate class
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

    # Create the piece instance with its move, source, target and extra params
    return Piece(move, source_piece, target_piece, **extra_info)


def _get_castle_pos(color):
    """
    Determine rook starting squares and king target squares for castling
    based on color ('w' or 'b').
    Returns (left_rook, right_rook, queenside_target, kingside_target).
    """
    if color == 'w':
        left_rook, right_rook = (7, 0), (7, 7)
        queenside, kingside = (7, 2), (7, 6)
    else:
        left_rook, right_rook = (0, 0), (0, 7)
        queenside, kingside = (0, 2), (0, 6)

    return left_rook, right_rook, queenside, kingside


def _is_path_clear(board, source_piece, source_pos, target_pos):
    """
    Check all intermediate squares along a piece's straight-line trajectory.
    Knights are excluded, as they jump.
    """
    source_type = source_piece[1]
    if source_type == 'N':
        return True  # knights ignore intervening pieces

    sr, sc = source_pos
    tr, tc = target_pos
    dr = tr - sr
    dc = tc - sc

    # Normalize direction to unit step in each axis
    row_step = dr // max(1, abs(dr))
    col_step = dc // max(1, abs(dc))

    # Step one square at a time from source towards target (excluding endpoints)
    r, c = sr + row_step, sc + col_step
    while (r, c) != (tr, tc):
        if board[r][c] != EMPTY:
            return False
        r += row_step
        c += col_step

    return True


def gen_valid_moves(board, history, white_to_move, source_piece, source_pos, castling_rights):
    """
    Iterate over every square on the board, instantiate a hypothetical move,
    and yield whether it is valid for the given source_piece.
    """
    source_color = source_piece[0]  # 'w' or 'b'

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            target_piece = board[row][col]
            target_pos = (row, col)
            move = [source_pos, target_pos]

            # Instantiate a piece object for move-specific validation
            piece = _get_piece_object(move, source_piece, target_piece, history, castling_rights)
            is_white_piece = (source_color == 'w')

            # Enforce turn order
            if white_to_move and not is_white_piece:
                yield target_pos, False
                continue
            if not white_to_move and is_white_piece:
                yield target_pos, False
                continue

            # Prevent capturing own piece
            if source_color == target_piece[0]:
                yield target_pos, False
                continue

            # Piece-specific movement rules
            is_valid_piece, _ = piece.validate()
            if not is_valid_piece:
                yield target_pos, False
                continue

            # Check for blocking pieces along the path
            if not _is_path_clear(board, source_piece, source_pos, target_pos):
                yield target_pos, False
                continue

            yield target_pos, True


class Move:
    def __init__(self, board, history, white_to_move):
        """
        Track move context including the board state, move history,
        whose turn it is, and castling rights.
        """
        self.board = board
        self.history = history
        self.white_to_move = white_to_move
        # All castling rights start as available
        self.castling_rights = {
            'w_kingside': True, 'w_queenside': True,
            'b_kingside': True, 'b_queenside': True
        }

    def validate(self, source_pos, target_pos):
        """
        Validate a single move from source_pos to target_pos.
        Returns (is_valid, move_type) where move_type describes special moves.
        """
        source_piece = piece_name(self.board, source_pos)
        target_piece = piece_name(self.board, target_pos)
        src_color = source_piece[0]
        is_white_piece = (src_color == 'w')

        # Turn order check
        if self.white_to_move and not is_white_piece:
            return False, None
        if not self.white_to_move and is_white_piece:
            return False, None

        # Cannot capture own color
        if src_color == target_piece[0]:
            return False, None

        # Build piece instance for detailed validation
        move = [source_pos, target_pos]
        piece = _get_piece_object(move, source_piece, target_piece,
                                  self.history, self.castling_rights)
        is_valid_piece, move_type = piece.validate()
        if not is_valid_piece:
            return False, None

        # Ensure path is not obstructed
        if not _is_path_clear(self.board, source_piece, source_pos, target_pos):
            return False, None

        # Commit turn flip and update castling availability
        self.white_to_move = not self.white_to_move
        self.update_castle(source_pos, source_piece[1], src_color)

        return True, move_type

    def update_castle(self, source_pos, source_type, source_color):
        """
        Disable castling rights when a king or rook moves from its
        original square.
        """
        if source_type == 'K':
            # King moved: both sides of castling are now invalid
            self.castling_rights[f'{source_color}_kingside'] = False
            self.castling_rights[f'{source_color}_queenside'] = False
        elif source_type == 'R':
            # Identify which rook moved to disable the corresponding side
            left_rook, right_rook, _, _ = _get_castle_pos(source_color)
            if source_pos == right_rook:
                self.castling_rights[f'{source_color}_kingside'] = False
            elif source_pos == left_rook:
                self.castling_rights[f'{source_color}_queenside'] = False

    def log_turn(self):
        """Output current turn to console for debugging."""
        print("turn: white" if self.white_to_move else "turn: black")


class Engine:
    def __init__(self):
        # Use the standard opening position
        self.board = CHESS_BOARD
        # History entries are tuples: ((src, dst), (src_name, dst_name), board_snapshot)
        initial_move = (None, None), (None, None), CHESS_BOARD
        self.history = [initial_move]

    def perform_move(self, source_pos, target_pos, special_move):
        """
        Execute a move on the board, handling en passant and castling.
        Appends the new position to history.
        """
        sr, sc = source_pos
        tr, tc = target_pos

        source_name = piece_name(self.board, source_pos)
        target_name = piece_name(self.board, target_pos)

        # Move the piece on the board
        self.board[tr][tc] = self.board[sr][sc]
        self.board[sr][sc] = EMPTY

        if special_move == "en passant":
            # Remove the pawn that was jumped over
            direction = 1 if source_name[0] == 'w' else -1
            self.board[tr + direction][tc] = EMPTY

        if special_move == "castle":
            # Reposition the rook accordingly
            color = source_name[0]
            left_rook, right_rook, queenside, kingside = _get_castle_pos(color)
            if target_pos == queenside:
                rr, rc = left_rook
                # Move rook next to new king position
                self.board[rr][rc + 3] = self.board[rr][rc]
                # Clear the old rook and king squares
                self.board[rr][rc] = EMPTY
                self.board[sr][sc] = EMPTY
            elif target_pos == kingside:
                rr, rc = right_rook
                self.board[rr][rc - 2] = self.board[rr][rc]
                self.board[rr][rc] = EMPTY
                self.board[sr][sc] = EMPTY

        # Record move in history with current board reference
        new_entry = ((source_pos, target_pos), (source_name, target_name), self.board)
        self.history.append(new_entry)