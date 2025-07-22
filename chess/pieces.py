from abc import ABC, abstractmethod

from src.config import EMPTY

# TODO: Pawn promotions
# TODO: King checks
# TODO: Castling

class Piece(ABC):
    def __init__(self, move, source_piece, target_piece, history=None, castling_rights=None):
        self.source_pos, self.target_pos = move
        self.source_piece = source_piece
        self.target_piece = target_piece
        self.history = history
        self.castling_rights = castling_rights

        self.source_row = self.source_pos[0]
        self.source_col = self.source_pos[1]
        self.target_row = self.target_pos[0]
        self.target_col = self.target_pos[1]

        # Color is encoded as first character of piece string, e.g., 'wP' -> 'w'
        self.source_color = source_piece[0]
        self.target_color = target_piece[0]

        # Relative movement deltas
        self.change_in_row = self.target_row - self.source_row
        self.change_in_col = self.target_col - self.source_col
        self.row_length = abs(self.change_in_row)
        self.col_length = abs(self.change_in_col)

    @abstractmethod
    def validate(self):
        """
        Checks whether a chess piece has made a valid move.

        Returns:
        bool: True if the move is valid, False otherwise.
        str: "en passant" if the valid move is an en passant capture, else "normal".
        """


class King(Piece):
    def validate(self):
        # Determine initial kingside/queenside positions by color
        if self.source_color == 'w':
            king_default_pos = (7, 4)
            castle_positions = ((7, 2), (7, 6))
        else:
            king_default_pos = (0, 4)
            castle_positions = ((0, 2), (0, 6))

        # Castling attempt: king must be in start square and target one of the rooks' positions
        if self.source_pos == king_default_pos and self.target_pos in castle_positions:
            queenside_target, kingside_target = castle_positions
            side = 'queenside' if self.target_pos == queenside_target else 'kingside'
            # Check castling rights mapping, e.g., 'w_kingside': True/False
            if not self.castling_rights.get(f'{self.source_color}_{side}', False):
                return False, None
            return True, "castle"

        # Normal king move: at most one square in any direction
        if self.row_length > 1 or self.col_length > 1:
            return False, None

        return True, "normal"


class Bishop(Piece):
    def validate(self):
        # Bishop moves strictly along diagonals
        if self.row_length == self.col_length:
            return True, "normal"
        return False, None


class Rook(Piece):
    def validate(self):
        # Rook moves orthogonally: along same row or same column
        if self.source_row == self.target_row or self.source_col == self.target_col:
            return True, "normal"
        return False, None


class Queen(Piece):
    def validate(self):
        # Queen combines rook and bishop movement
        if self.row_length == self.col_length:
            return True, "normal"
        if self.source_row == self.target_row or self.source_col == self.target_col:
            return True, "normal"
        return False, None


class Knight(Piece):
    def validate(self):
        # L-shaped moves: two in one direction and one in the perpendicular
        if (self.row_length == 2 and self.col_length == 1) or \
           (self.row_length == 1 and self.col_length == 2):
            return True, "normal"
        return False, None


class Pawn(Piece):
    def __init__(self, move, source_piece, target_piece, history):
        super().__init__(move, source_piece, target_piece, history)
        # Unpack the last move from history, if available, to evaluate en passant
        if self.history:
            last_move, last_pieces = self.history[-1]
            self.prev_source_pos, self.prev_target_pos = last_move
            self.prev_source_piece, self.prev_target_piece = last_pieces

    def validate(self):
        # Set direction and starting rows by color
        if self.source_color == 'w':
            pawn_start_row = 6
            en_passant_row = 3
            direction = -1  # white moves up the board
        else:
            pawn_start_row = 1
            en_passant_row = 4
            direction = 1   # black moves down the board

        is_diag_move = self.row_length == self.col_length == 1
        is_forward_step = self.change_in_row == direction

        # En passant condition: diagonal empty capture on correct turn
        if is_diag_move and is_forward_step and self.target_piece == EMPTY:
            # Pawn must be on the correct rank to perform en passant
            if self.source_row == en_passant_row and self.history:
                # Ensure last moved piece was a pawn that did a two-square advance next to us
                if self.prev_source_piece[1] == 'p':
                    prev_src_r, prev_src_c = self.prev_source_pos
                    prev_tgt_r, prev_tgt_c = self.prev_target_pos
                    if abs(prev_tgt_r - prev_src_r) == 2 and \
                       prev_tgt_c == self.target_col and \
                       abs(self.source_col - prev_tgt_c) == 1:
                        return True, "en passant"

        # Standard capture: diagonal occupied by opponent
        if is_diag_move and self.target_piece != EMPTY and is_forward_step:
            return True, "normal"

        on_same_col = self.source_col == self.target_col
        max_steps = 2 if self.source_row == pawn_start_row else 1

        # Prevent backward moves
        if (self.source_color == 'w' and self.change_in_row > 0) or \
           (self.source_color == 'b' and self.change_in_row < 0):
            return False, None

        # Forward moves must be unobstructed and within allowed step count
        if not on_same_col or self.row_length > max_steps or self.target_piece != EMPTY:
            return False, None

        return True, "normal"
