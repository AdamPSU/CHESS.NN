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


```python
class King(Piece):
    def validate(self):
        # Determine the king's default position and castling positions based on color
        if self.source_color == 'w':
            king_default_pos = (7, 4)  # Default position for white king
            castle = ((7, 2), (7, 6))  # Castling positions for white king

        else:
            king_default_pos = (0, 4)  # Default position for black king
            castle = ((0, 2), (0, 6))  # Castling positions for black king

        # Check if the move is a castling move
        if self.source_pos == king_default_pos and self.target_pos in castle:
            # Determine the side of castling
            queenside = castle[0]
            side = 'queenside' if self.target_pos == queenside else 'kingside'

            # Check if castling rights are available
            if not self.castling_rights[f'{self.source_color}_{side}']:
                # If castling rights are not available, the move is invalid
                return False, None

            # If castling rights are available, the move is valid and considered 'castle'
            return True, "castle"

        # Check if the move is not more than one space in any direction
        if self.row_length > 1 or self.col_length > 1:
            # If more than one space, the move is invalid
            return False, None

        # If one space or castling, the move is valid and considered 'normal'
        return True, "normal"
```
```python
class Bishop(Piece):
    def validate(self):
        # Check if the bishop's move is diagonal
        if self.row_length == self.col_length:
            # If diagonal, the move is valid and considered 'normal'
            return True, "normal"

        # If not diagonal, the move is invalid
        return False, None
```

##
```python
class Rook(Piece):
    def validate(self):
        # Check if the rook's move is horizontal or vertical
        on_same_row = self.source_row == self.target_row  # Check if move is on the same row
        on_same_col = self.source_col == self.target_col  # Check if move is on the same column

        # If horizontal or vertical, the move is valid and considered 'normal'
        if on_same_row or on_same_col:
            return True, "normal"

        # If not horizontal or vertical, the move is invalid
        return False, None
```

##
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


```python
class Knight(Piece):
    def validate(self):
        # Check if the knight's move is L-shaped (2 spaces in one direction, 1 space in another)
        if self.row_length == 2 and self.col_length == 1:
            # If L-shaped, the move is valid and considered 'normal'
            return True, "normal"

        if self.row_length == 1 and self.col_length == 2:
            # If L-shaped, the move is valid and considered 'normal'
            return True, "normal"

        # If not L-shaped, the move is invalid
        return False, None
```

##
class Pawn(Piece):
    def __init__(self, move, source_piece, target_piece, history):
        super().__init__(move, source_piece, target_piece, history)

        if self.history is not None:
            self.prev_source_pos = self.history[-1][0][0]
            self.prev_target_pos = self.history[-1][0][1]

            self.prev_source_piece = self.history[-1][1][0]
            self.prev_target_piece = self.history[-1][1][1]


```python
def validate(self):
    # Determine pawn start row, en passant row, and direction based on source color
    if self.source_color == 'w':
        pawn_start_row = 6  # Starting row for white pawns
        en_passant_row = 3  # Row where en passant can occur for white pawns
        direction = -1  # Direction of movement for white pawns
    else:
        pawn_start_row = 1  # Starting row for black pawns
        en_passant_row = 4  # Row where en passant can occur for black pawns
        direction = 1  # Direction of movement for black pawns

    # Check if move is diagonal
    is_attacking_diagonal = self.row_length == self.col_length == 1
    # Check if target piece is not empty
    is_attacking_piece = self.target_piece != EMPTY
    # Check if move is in correct direction
    is_correct_direction = self.change_in_row == direction

    # Validate en passant move
    if (is_attacking_diagonal and is_correct_direction and not is_attacking_piece) and (
            self.source_row == en_passant_row and self.row_length == 1):
        # Check if move history is available
        if self.history is not None:
            # Check if previous piece was a pawn
            is_pawn = self.prev_source_piece[1] == 'p'

            if is_pawn:
                # Get previous source and target positions
                prev_source_row, prev_source_col = self.prev_source_pos
                prev_target_row, prev_target_col = self.prev_target_pos

                # Calculate length of previous move
                prev_row_length = abs(prev_target_row - prev_source_row)

                # Check if enemy pawn moved two squares and is next to our pawn
                if (prev_row_length == 2 and prev_target_col == self.target_col and
                        abs(self.source_col - prev_target_col) == 1):
                    # En passant move is valid
                    return True, "en passant"

    # Validate normal attack move
    if is_attacking_diagonal and is_attacking_piece and is_correct_direction:
        # Attack move is valid
        return True, "normal"

    # Check if move is on the same column
    on_same_col = self.source_col == self.target_col
    # Determine total allowed steps based on starting row
    total_allowed_steps = 2 if self.source_row == pawn_start_row else 1

    # Check if pawn is moving in the correct direction
    if ((self.source_color == 'w' and self.change_in_row > 0) or
            (self.source_color == 'b' and self.change_in_row < 0)):
        # Pawn is not moving in the correct direction
        return False, None

    # Check if move is valid
    if not on_same_col or self.row_length > total_allowed_steps or self.target_piece != EMPTY:
        # Move is not valid
        return False, None

    # Normal move is valid
    return True, "normal"
```