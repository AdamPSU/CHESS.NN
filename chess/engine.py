from chess.pieces import (
    Pawn,
    Knight,
    Bishop,
    Rook,
    King,
    Queen,
)

from src.config import EMPTY, BOARD_SIZE


CHESS_BOARD =[['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
              ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
              ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

def _piece_type(piece):
    piece_map = {
        'p': Pawn(),
        'N': Knight(),
        'B': Bishop(),
        'R': Rook(),
        'K': King(),
        'Q': Queen(),
    }

    piece_symbol = piece_map.get(piece[1])

    if piece_symbol is None:
        raise ValueError(
            f"Piece type is not supported. Please make sure the provided piece "
            f"is correct. Invalid piece: '{piece}'."
        )

    return piece_symbol


def _is_path_clear(board, start_piece, start_piece_idx, target_piece_idx):
    start_piece_type = start_piece[1]
    knight = start_piece_type == 'N'

    # Knights don't need this validation
    if knight:
        return True

    start_row, start_col = start_piece_idx
    end_row, end_col = target_piece_idx

    change_in_row = end_row - start_row
    change_in_col = end_col - start_col

    # Normalize steps to be between 1, 0, and -1
    row_step = change_in_row // max(1, abs(change_in_row))
    col_step = change_in_col // max(1, abs(change_in_col))

    current_row = start_row + row_step
    current_col = start_col + col_step

    while (current_row, current_col) != (end_row, end_col):
        current_piece = board[current_row][current_col]

        if current_piece != EMPTY:
            return False

        current_row += row_step
        current_col += col_step

    return True


def gen_valid_moves(board, white_to_move, start_piece, start_piece_idx):
    start_piece_color = start_piece[0] # Necessary for pawn moves
    piece = _piece_type(start_piece)

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            target_piece = board[row][col]
            target_piece_idx = (row, col)
            target_piece_color = target_piece[0]

            is_white_piece = True if start_piece_color == 'w' else False

            # Turn validation
            if white_to_move and not is_white_piece:
                yield target_piece_idx, False
                continue

            if not white_to_move and is_white_piece:
                yield target_piece_idx, False
                continue

            # Cannot attack friendly squares
            if start_piece_color == target_piece_color:
                yield target_piece_idx, False
                continue

            move = (start_piece, target_piece)
            is_valid_piece = piece.validate(move, start_piece_color, start_piece_idx, target_piece_idx)

            if not is_valid_piece:
                yield target_piece_idx, False
                continue

            if not _is_path_clear(board, start_piece, start_piece_idx, target_piece_idx):
                yield target_piece_idx, False
                continue

            yield target_piece_idx, True


class Move:
    def __init__(self, board, white_to_move, start, end):
        """
        Initializes a Move object.

        Parameters:
        start_pos (tuple): The starting position of the move (row, col).
        end_pos (tuple): The ending position of the move (row, col).
        board (list): The current state of the chess board.
        """

        self.start_piece_idx = start
        self.target_piece_idx = end
        self.board = board
        self.white_to_move = white_to_move

        self.start_row, self.start_col = start

        self.start_piece = self.piece(start)
        self.start_piece_color = self.start_piece[0]
        self.start_piece_type = self.start_piece[1]

        self.target_row, self.target__col = end

        self.target_piece = self.piece(end)
        self.target_piece_color = self.target_piece[0]
        self.target_piece_type = self.target_piece[1]


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

        # For piece-specific validation
        piece = _piece_type(self.start_piece)

        move = (self.start_piece, self.target_piece)
        is_valid_piece = piece.validate(move, self.start_piece_color,
                                        self.start_piece_idx, self.target_piece_idx)

        if not is_valid_piece:
            return False

        is_path_clear = _is_path_clear(self.board, self.start_piece,
                                       self.start_piece_idx, self.target_piece_idx)

        if not is_path_clear:
            return False

        self.white_to_move = not self.white_to_move

        return True


    def piece(self, loc):
        if None in loc:
            return None

        row = loc[0]
        col = loc[1]

        piece = self.board[row][col]

        return piece


    # def _is_path_clear(self):
    #     knight = self.start_piece_idx_piece_type == 'N'
    # 
    #     # Knights don't need this validation
    #     if knight:
    #         return True
    # 
    #     change_in_row = self.target_piece_idx_row - self.start_piece_idx_row
    #     change_in_col = self.target_piece_idx_col - self.start_piece_idx_col
    # 
    #     # Normalize steps to be between 1, 0, and -1
    #     row_step = change_in_row // max(1, abs(change_in_row))
    #     col_step = change_in_col // max(1, abs(change_in_col))
    # 
    #     current_row = self.start_piece_idx_row + row_step
    #     current_col = self.start_piece_idx_col + col_step
    # 
    #     while (current_row, current_col) != (self.target_piece_idx_row, self.target_piece_idx_col):
    #         current_piece = self.board[current_row][current_col]
    # 
    #         if current_piece != EMPTY:
    #             return False
    # 
    #         current_row += row_step
    #         current_col += col_step
    # 
    #     return True


    def log_turn(self):
        if self.white_to_move:
            print("turn: white")

        print("turn: black")


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


