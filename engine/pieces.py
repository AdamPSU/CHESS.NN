from abc import ABC, abstractmethod


class Piece(ABC):
    @abstractmethod
    def validate(self, start_row, start_col, end_row, end_col, white_to_move=None):
        """
        Checks whether a chess piece is valid.

        Parameters:
        start_row (int): The starting row index.
        start_col (int): The starting column index.
        end_row (int): The ending row index.
        end_col (int): The ending column index.

        Returns:
        bool: True if the move is valid, False otherwise.
        """



class King(Piece):
    def validate(self, start_row, start_col, end_row, end_col, white_to_move=None):
        change_in_row = abs(end_row - start_row)
        change_in_col = abs(end_row - start_row)

        if change_in_row <= 1 & change_in_col <= 1:
            return True

        return False


class Bishop(Piece):
    def validate(self, start_row, start_col, end_row, end_col, white_to_move=None):

        change_in_row = abs(end_row - start_row)
        change_in_col = abs(end_col - start_col)

        if change_in_row == change_in_col:
            return True

        return False


class Rook(Piece):
    def validate(self, start_row, start_col, end_row, end_col, white_to_move=None):
        on_same_row = start_row == end_row
        on_same_col = start_col == end_col

        if on_same_row or on_same_col:
            return True

        return False


class Queen(Piece):
    def validate(self, start_row, start_col, end_row, end_col, white_to_move=None):
        # Check if the move is valid as a bishop move
        change_in_row = abs(end_row - start_row)
        change_in_col = abs(end_col - start_col)

        if change_in_row == change_in_col:
            return True

        # Check if the move is valid as a rook move
        on_same_row = start_row == end_row
        on_same_col = start_col == end_col

        if on_same_row or on_same_col:
            return True

        return False


class Knight(Piece):
    def validate(self, start_row, start_col, end_row, end_col, white_to_move=None):
        row_length = abs(end_row - start_row)
        col_length = abs(end_col - start_col)

        if row_length == 2 and col_length == 1:
            return True

        if row_length == 1 and col_length == 2:
            return True

        print(1)
        return False


class Pawn(Piece):
    def validate(self, start_row, start_col, end_row, end_col, white_to_move=None):
        pawn_starting_row = 6 if white_to_move else 1

        on_same_col = start_col == end_col
        row_length = abs(end_row - start_row)

        total_allowed_steps = 2 if start_row == pawn_starting_row else 1

        if on_same_col and row_length <= total_allowed_steps:
            return True

        return False











