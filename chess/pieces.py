from abc import ABC, abstractmethod
from src.config import EMPTY


class Piece(ABC):
    @abstractmethod
    def validate(self, move, color, start, end):
        """
        Checks whether a chess piece has made a valid move.

        Parameters:
        move (list): List of tuples indicating the start and ending pieces.
        start_row (int): The starting row index.
        start_col (int): The starting column index.
        end_row (int): The ending row index.
        end_col (int): The ending column index.

        Returns:
        bool: True if the move is valid, False otherwise.
        """


class King(Piece):
    def validate(self, move, color, start, end):
        start_row, start_col = start
        end_row, end_col = end

        row_length = abs(end_row - start_row)
        col_length = abs(end_col - start_col)

        if row_length <= 1 & col_length <= 1:
            return True

        return False


class Bishop(Piece):
    def validate(self, move, color, start, end):
        start_row, start_col = start
        end_row, end_col = end

        row_length = abs(end_row - start_row)
        col_length = abs(end_col - start_col)

        if row_length == col_length:
            return True

        return False


class Rook(Piece):
    def validate(self, move, color, start, end):
        start_row, start_col = start
        end_row, end_col = end

        on_same_row = start_row == end_row
        on_same_col = start_col == end_col

        if on_same_row or on_same_col:
            return True

        return False


class Queen(Piece):
    def validate(self, move, color, start, end):
        start_row, start_col = start
        end_row, end_col = end

        # Check if the move is valid as a bishop move
        row_length = abs(end_row - start_row)
        col_length = abs(end_col - start_col)

        if row_length == col_length:
            return True

        # Check if the move is valid as a rook move
        on_same_row = start_row == end_row
        on_same_col = start_col == end_col

        if on_same_row or on_same_col:
            return True

        return False


class Knight(Piece):
    def validate(self, move, color, start, end):
        start_row, start_col = start
        end_row, end_col = end

        row_length = abs(end_row - start_row)
        col_length = abs(end_col - start_col)

        if row_length == 2 and col_length == 1:
            return True

        if row_length == 1 and col_length == 2:
            return True

        return False


class Pawn(Piece):

    def _is_valid_attack(self, move, color, start_row, start_col, end_row, end_col):
        row_length = abs(end_row - start_row)
        col_length = abs(end_col - start_col)
        change_in_row = end_row - start_row

        direction = -1 if color == 'w' else 1

        is_attacking_diagonal = row_length == col_length == 1
        is_correct_direction = change_in_row == direction
        is_attacking_piece = move[1] != EMPTY

        if is_attacking_diagonal and is_correct_direction and is_attacking_piece:
            return True

        return False


    def validate(self, move, color, start, end):
        start_row, start_col = start
        end_row, end_col = end

        valid_attack = self._is_valid_attack(move, color, start_row, start_col, end_row, end_col)

        if valid_attack:
            return True

        pawn_starting_row = 6 if color == 'w' else 1

        on_same_col = start_col == end_col
        steps_taken = end_row - start_row
        total_allowed_steps = 2 if start_row == pawn_starting_row else 1

        if (color == 'w' and steps_taken > 0) or (color == 'b' and steps_taken < 0):
            return False

        if on_same_col and abs(steps_taken) <= total_allowed_steps:
            return True

        return False











