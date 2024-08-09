from chess.pieces import (
    Pawn,
    Knight,
    Bishop,
    Rook,
    King,
    Queen,
)

from src.config import EMPTY, BOUNDS


CHESS_BOARD =[['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
              ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['--', '--', '--', '--', '--', '--', '--', '--'],
              ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
              ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]


class Move:
    def __init__(self, board, white_to_move):
        """
        Initializes a Move object.

        Parameters:
        start_pos (tuple): The starting position of the move (row, col).
        end_pos (tuple): The ending position of the move (row, col).
        board (list): The current state of the chess board.
        """

        self.board = board
        self.white_to_move = white_to_move

        self.move_logger = []
        self.piece_logger = []

        self.total_clicks = 0


    def log_move(self):
        print(f"move log: {self.move_logger}, total clicks: {self.total_clicks}")

    def log_turn(self):
        if self.white_to_move:
            print("turn: white")

        print("turn: black")


    def start_piece(self, piece):
        color = 'w' if self.white_to_move else 'b'

        piece_map = {
            'p': Pawn(color),
            'N': Knight(),
            'B': Bishop(),
            'R': Rook(),
            'K': King(color),
            'Q': Queen(),
        }

        piece_type = piece_map.get(piece)

        return piece_type


    def update(self, row, col):
        self.move_logger.append((row, col))

        selected_piece = self.board[row][col]
        self.piece_logger.append(selected_piece)

        self.total_clicks += 1


    def reset(self):
        """
        Resets the selected piece and player clicks. This method is called
        to clear the selection state, either when an invalid move is detected
        or a valid move is completed.
        """

        self.move_logger = []
        self.piece_logger = []

        self.total_clicks = 0


    def reset_last(self):
        """
        Resets the last selected piece and decrements total counts by 1.
        This method is called to clear the selection state when the second
        piece is invalid.
        """

        self.move_logger = self.move_logger[:-1]
        self.piece_logger = self.piece_logger[:-1]

        self.total_clicks -= 1


    def _is_path_clear(self, start_row, start_col, end_row, end_col):
        # pawn = self.piece_logger[0][1] == 'p'
        knight = self.piece_logger[0][1] == 'N'

        # Pawns and Knights don't need this validation
        if knight:
            return True

        change_in_row = end_row - start_row
        change_in_col = end_col - start_col

        # Normalize steps to be between 1, 0, and -1
        row_step = change_in_row // max(1, abs(change_in_row))
        col_step = change_in_col // max(1, abs(change_in_col))

        current_row = start_row + row_step
        current_col = start_col + col_step

        while (current_row, current_col) != (end_row, end_col):
            current_piece = self.board[current_row][current_col]

            if current_piece != EMPTY:
                return False

            current_row += row_step
            current_col += col_step

        return True


    def validate(self):
        """
        Checks if the move is valid based on the current board state.

        Returns:
        bool: True if the move is valid, False otherwise.
        """

        # TODO: pieces cannot attack friendly squares

        row, col = self.move_logger[-1]
        # Player clicked out of bounds
        if col > BOUNDS or row > BOUNDS:
            self.reset()

            return False

        piece = self.piece_logger[0]
        piece_color = piece[0]
        is_white_piece = True if piece_color == 'w' else False

        if self.total_clicks == 1:
            # First move cannot be an empty piece
            if piece == EMPTY:
                self.reset()

            # Turn validation
            if self.white_to_move and not is_white_piece:
                self.reset()
            elif not self.white_to_move and is_white_piece:
                self.reset()

            return False

        selected_piece = self.piece_logger[0]
        target_piece = self.piece_logger[1]

        # User clicked the same piece twice
        if selected_piece == target_piece:
            self.reset()

            return False

        target_piece_color = target_piece[0]

        if piece_color == target_piece_color:
            self.reset_last()

            return False

        piece_type = self.start_piece(selected_piece[1])

        start_row, start_col = self.move_logger[0]
        end_row, end_col = self.move_logger[1]

        is_valid_piece = piece_type.validate(self.piece_logger, start_row, start_col,
                                             end_row, end_col)

        if not is_valid_piece:
            self.reset_last()

            return False

        is_path_clear = self._is_path_clear(start_row, start_col, end_row, end_col)

        if not is_path_clear:
            self.reset_last()

            return False

        self.white_to_move = not self.white_to_move

        return True


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


    def perform_move(self, start_pos, end_pos):
        """
        Attempts to make a move and updates the game state accordingly.

        Parameters:
        start_pos (tuple): The starting position of the move (row, col).
        end_pos (tuple): The ending position of the move (row, col).

        Returns:
        bool: True if the move was successfully made, False otherwise.
        """

        start_row, start_col = start_pos
        end_row, end_col = end_pos

        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[start_row][start_col] = EMPTY


