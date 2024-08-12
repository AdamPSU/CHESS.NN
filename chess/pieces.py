from abc import ABC, abstractmethod
from src.config import EMPTY

# TODO: En passant with pawns
# TODO: Pawn promotions
# TODO: King checks

class Piece(ABC):
    def __init__(self, move, source_piece, target_piece):
        self.source_pos, self.target_pos = move
        self.source_piece = source_piece
        self.target_piece = target_piece

        self.source_row = self.source_pos[0]
        self.source_col = self.source_pos[1]
        self.target_row = self.target_pos[0]
        self.target_col = self.target_pos[1]

        self.source_color = source_piece[0]
        self.target_color = target_piece[1]

        self.change_in_row = self.target_row - self.source_row
        self.change_in_col = self.target_col - self.source_col
        self.row_length = abs(self.target_row - self.source_row)
        self.col_length = abs(self.target_col - self.source_col)


    @abstractmethod
    def validate(self):
        """
        Checks whether a chess piece has made a valid move.

        Returns:
        bool: True if the move is valid, False otherwise.
        """


class King(Piece):
    def validate(self):
        if self.row_length <= 1 & self.col_length <= 1:
            return True

        return False


class Bishop(Piece):
    def validate(self):
        if self.row_length == self.col_length:
            return True

        return False


class Rook(Piece):
    def validate(self):
        on_same_row = self.source_row == self.target_row
        on_same_col = self.source_col == self.target_col

        if on_same_row or on_same_col:
            return True

        return False


class Queen(Piece):
    def validate(self):
        # Check if the move is valid as a bishop move
        if self.row_length == self.col_length:
            return True

        # Check if the move is valid as a rook move
        on_same_row = self.source_row == self.target_row
        on_same_col = self.source_col == self.target_col

        if on_same_row or on_same_col:
            return True

        return False


class Knight(Piece):
    def validate(self):
        if self.row_length == 2 and self.col_length == 1:
            return True

        if self.row_length == 1 and self.col_length == 2:
            return True

        return False


class Pawn(Piece):
    def validate(self):
        if self.source_color == 'w':
            pawn_start_row = 6
            direction = -1
        else:
            pawn_start_row = 1
            direction = 1

        is_attacking_diagonal = self.row_length == self.col_length == 1
        is_correct_direction = self.change_in_row == direction
        is_attacking_piece = self.target_piece != EMPTY

        # Validate attack
        if is_attacking_diagonal and is_attacking_piece and is_correct_direction:
            return True

        on_same_col = self.source_col == self.target_col
        total_allowed_steps = 2 if self.source_row == pawn_start_row else 1

        # Pawn must face right direction
        if ((self.source_color == 'w' and self.change_in_row > 0) or
            (self.source_color == 'b' and self.change_in_row < 0)):
            return False

        if not on_same_col or self.row_length > total_allowed_steps:
            return False

        return True
