from abc import ABC, abstractmethod

from src.config import EMPTY

# TODO: Pawn promotions
# TODO: King checks

class Piece(ABC):
    def __init__(self, move, source_piece, target_piece, history=None):
        self.source_pos, self.target_pos = move
        self.source_piece = source_piece
        self.target_piece = target_piece
        self.history = history

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
        str: "en passant" if the valid move is an en passant capture, else "normal".
        """


class King(Piece):
    def validate(self):
        if self.row_length <= 1 & self.col_length <= 1:
            return True, "normal"

        return False, None


class Bishop(Piece):
    def validate(self):
        if self.row_length == self.col_length:
            return True, "normal"

        return False, None


class Rook(Piece):
    def validate(self):
        on_same_row = self.source_row == self.target_row
        on_same_col = self.source_col == self.target_col

        if on_same_row or on_same_col:
            return True, "normal"

        return False, None


class Queen(Piece):
    def validate(self):
        # Check if the move is valid as a bishop move
        if self.row_length == self.col_length:
            return True, "normal"

        # Check if the move is valid as a rook move
        on_same_row = self.source_row == self.target_row
        on_same_col = self.source_col == self.target_col

        if on_same_row or on_same_col:
            return True, "normal"

        return False, None


class Knight(Piece):
    def validate(self):
        if self.row_length == 2 and self.col_length == 1:
            return True, "normal"

        if self.row_length == 1 and self.col_length == 2:
            return True, "normal"

        return False, None


class Pawn(Piece):
    def __init__(self, move, source_piece, target_piece, history):
        super().__init__(move, source_piece, target_piece, history)

        if self.history is not None:
            self.prev_source_pos = self.history[-1][0][0]
            self.prev_target_pos = self.history[-1][0][1]

            self.prev_source_piece = self.history[-1][1][0]
            self.prev_target_piece = self.history[-1][1][1]


    def validate(self):
        if self.source_color == 'w':
            pawn_start_row = 6
            en_passant_row = 3
            direction = -1
        else:
            pawn_start_row = 1
            en_passant_row = 4
            direction = 1

        is_attacking_diagonal = self.row_length == self.col_length == 1
        is_attacking_piece = self.target_piece != EMPTY
        is_correct_direction = self.change_in_row == direction

        # Validate en passant
        if (is_attacking_diagonal and is_correct_direction and not is_attacking_piece) and (
        self.source_row == en_passant_row and self.row_length == 1):
            if self.history is not None:
                is_pawn = self.prev_source_piece[1] == 'p'

                if is_pawn:
                    prev_source_row, prev_source_col = self.prev_source_pos
                    prev_target_row, prev_target_col = self.prev_target_pos

                    prev_row_length = abs(prev_target_row - prev_source_row)

                    # Check if the enemy pawn moved two squares and is next to our pawn
                    if (prev_row_length == 2 and prev_target_col == self.target_col and
                        abs(self.source_col - prev_target_col) == 1):
                        return True, "en passant"

        # Validate attack
        if is_attacking_diagonal and is_attacking_piece and is_correct_direction:
            return True, "normal"

        on_same_col = self.source_col == self.target_col
        total_allowed_steps = 2 if self.source_row == pawn_start_row else 1

        # Pawn must face right direction
        if ((self.source_color == 'w' and self.change_in_row > 0) or
            (self.source_color == 'b' and self.change_in_row < 0)):
            return False, None

        if not on_same_col or self.row_length > total_allowed_steps or self.target_piece != EMPTY:
            return False, None

        return True, "normal"







