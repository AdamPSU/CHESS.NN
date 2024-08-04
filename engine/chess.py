import numpy as np
from src.config import EMPTY

CHESS_BOARD = np.array(
            [['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
             ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
             ['--', '--', '--', '--', '--', '--', '--', '--'],
             ['--', '--', '--', '--', '--', '--', '--', '--'],
             ['--', '--', '--', '--', '--', '--', '--', '--'],
             ['--', '--', '--', '--', '--', '--', '--', '--'],
             ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
             ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        )

class Game:
    def __init__(self):
        self.board = CHESS_BOARD

        self.white_to_move = True
        self.move_log = [] # For debugging


    def get_board(self):
        return self.board


    def get_piece(self, move):
        board = self.get_board()
        return board[move.start_row, move.start_col]


    def get_attacked_piece(self, move):
        board = self.get_board()
        return board[move.end_row, move.end_col]


    def is_valid_move(self, move): 
        """Logic for determining whether a move is valid/invalid."""
        
        piece = self.get_piece(move)

        # Determins who will play
        if self.white_to_move and (piece.startswith('b')):
            return False # Not black's turn to play
        elif (not self.white_to_move) and (piece.startswith('w')):
            return False # Not white's turn to play
        
        piece_type = piece[1] # Get the symbol of the piece
        piece_mapping = {
        'p': self.pawn,
        'R': self.rook,
        'N': self.knight, 
        'B': self.bishop,
        'K': self.king,
        'Q': self.queen
        }

        handler = piece_mapping.get(piece_type)

        if handler:
            return handler(move) 
        return False 

    def make_move(self, move):
        """
        Performs the move, logs it in the terminal, and switches 
        the player's turn after moving.
        """

        board = self.get_board() 

        # Move the piece to the new square
        board[move.start_row, move.start_col] = "--"
        board[move.end_row, move.end_col] = move.piece_moved

        self.move_log.append(move)
        self.white_to_move = not self.white_to_move # Switch player turns

    def pawn(self, move): 
        '''
        Defines the rules for a chess pawn. 

        Missing: En Passant
        '''

        board = self.get_board()
        change_in_col = abs(move.end_col - move.start_col)
        change_in_row = abs(move.end_row - move.start_row)
        direction = 1 if (self.white_to_move) else -1 # White moves upwards, black moves downwards

        def has_moved_before(move):
            '''
            If a pawn is not in its starting position, 
            the pawn is only allowed to move 1 square at a time.
            '''
            # White starts at row 6, black starts at row 1 (list indices)
            default_row = 6 if (self.white_to_move) else 1
            
            if (move.start_row != default_row):
                return True 
            return False  
            
        def cannot_attack(move):
            '''
            Assuming the pawn is looking at a diagonal, it cannot
            attack if the attacked piece is a friendly/empty square.
            '''

            target = 'b' if (self.white_to_move) else 'w' # White targets black, black targets white
            change_in_row = move.end_row - move.start_row
            attacked_piece = self.get_attacked_piece(move) # Retrieve the attacked square

            if (change_in_row * change_in_col != -1*direction) or (not attacked_piece.startswith(target)):
                return True 
            return False # It can attack
        
        def has_conflict(move):
            '''
            Incrementally checks for each step taken whether
            there is a conflicting piece. There will be at most 
            two steps.
            '''

            # Check for each step if there's a piece in its way
            for i in range(1, change_in_row+1):
                moved_row = move.start_row - (i * direction) 
                if not (board[moved_row, move.start_col] == '--'):
                    return True # There are conflicts; don't move there
            return False
        
        if (change_in_row > 2) or (change_in_col > 1):
            # Pawns can't move more than 2 rows up or more than 1 column sideways
            return False 
        elif (has_moved_before(move)) and (change_in_row > 1):
            return False 
        elif (cannot_attack(move) and (change_in_col > 0)):
            return False 
        elif (has_conflict(move) and (change_in_col == 0)):
            return False
        return True # Otherwise, valid move

    def rook(self, move):
        '''Defines the rules for a chess rook.'''

        board = self.get_board()
        change_in_row = abs(move.end_row - move.start_row)
        change_in_col = abs(move.end_col - move.start_col)
        
        def has_conflict(move):
            '''
            Determines whether there is a piece preventing the bishop's move 
            along a diagonal.
            '''

            friendly = 'w' if (self.white_to_move) else 'b' # Determine the color of the current player's pieces
            attacked_piece = self.get_attacked_piece(move)

            if (attacked_piece.startswith(friendly)):
                return True  # Can't capture a friendly piece
            
            move_distance = change_in_row + change_in_col # Calculate total squares to check
            rowStep = 1 if move.end_row > move.start_row else -1
            colStep = 1 if move.end_col > move.start_col else -1

            rowMovement = 1 if change_in_row > 0 else 0 # 0 means row will not be checked
            colMovement = 1 if change_in_col > 0 else 0 # 0 means column will not be checked

            for i in range(1, move_distance):
                new_pos = (move.start_row + (i * rowStep * rowMovement), 
                    move.start_col + (i * colStep * colMovement)) 

                if board[new_pos] != '--': # Check if the square is occupied
                    return True  # Conflicting piece on rook's path
            return False 
            
        if (change_in_col > 0) and (change_in_row > 0):
            # Can only move along the rows or columns; no diagonals
            return False
        
        if (has_conflict(move)):
            return False
        return True 
    
    def knight(self, move):
        '''Defines the rules for a chess knight.'''
        
        def has_conflict(move):
            '''
            If the attacked piece is not an enemy piece, 
            there is a piece preventing the knight's move.
            '''

            target = 'b' if (self.white_to_move) else 'w'
            attacked_piece = self.get_attacked_piece(move)

            if (attacked_piece.startswith(target)) or (attacked_piece == '--'):
                # Knight is not staring at a friendly piece, valid attack
                return False
            return True # Otherwise, illegal move
        
        if (has_conflict(move)):
            return False
        
        # All  possible moves relative to the knight
        knight_squares = np.array([(2, -1), (2, 1), (-2, -1), (-2, 1),
            (1, -2), (1, 2), (-1, -2), (-1, 2)])
        
        # For each move, determine whether there is a match
        match = any((move.start_row + dr, move.start_col + dc) == (move.end_row, move.end_col)
            for dr, dc in knight_squares)

        return match 
    
    def bishop(self, move):
        '''Defines the rules for a chess bishop.'''

        board = self.get_board()
        change_in_row = abs(move.end_row - move.start_row)  
        change_in_col = abs(move.end_col - move.start_col)

        def has_conflict(move):
            '''
            Determines whether there is a piece preventing the bishop's move 
            along a diagonal.
            '''

            friendly = 'w' if (self.white_to_move) else 'b'
            attacked_piece = self.get_attacked_piece(move)

            if (attacked_piece.startswith(friendly)):
                return True  # Can't attack a friendly piece
            
            amount_moved = change_in_row
            row_direction = 1 if (move.end_row > move.start_row) else -1
            col_direction = 1 if (move.end_col > move.start_col) else -1

            for i in range(1, amount_moved):
                new_pos = (move.start_row + (i * row_direction), 
                    move.start_col + (i * col_direction))  # Diagonal movement

                if (board[new_pos] != '--'):
                    return True  # Conflicting piece on the diagonal

            return False

        if (change_in_col == 0): 
            # This is to prevent division by 0 errors
            return False 
        
        slope = change_in_row / change_in_col
        if (slope != 1.0): 
            return False # Can only move on diagonals
        
        if (has_conflict(move)):
            return False 
        return True
    
    def king(self, move):
        '''Defines the rules for a chess king.'''

        change_in_row = abs(move.end_row - move.start_row)
        change_in_col = abs(move.end_col - move.start_col)

        def has_conflict(move):
            '''
            If the attacked piece is not an enemy piece, 
            there is a piece preventing the king's move.
            '''

            target = 'b' if (self.white_to_move) else 'w'
            attacked_piece = self.get_attacked_piece(move)

            if (attacked_piece.startswith(target)) or (attacked_piece == '--'):
                return False
            return True 
        
        if (has_conflict(move)):
            return False

        # Can move anywhere with a radius of 1
        if (change_in_row > 1 or change_in_col > 1):
            return False # Otherwise, keep the board
        return True     

    def queen(self, move):
        '''
        Defines the rules for a chess queen, taking advantage
        of the fact that a queen is simply a rook and a bishop combined.
        '''

        change_in_row = abs(move.end_row - move.start_row)
        change_in_col = abs(move.end_col - move.start_col)

        if (change_in_row > 0 and change_in_col > 0):
            # Is likely a bishop move
            return self.bishop(move)
        else: 
            # Is likely a rook move
            return self.rook(move)
        
        
class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {values: key for key, values in ranks_to_rows.items()} # Reverses ranks_to_rows

    files_to_cols = {"a": 0, "b": 1, "c":2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {values: key for key, values in files_to_cols.items()} # Reverses files_to_cols

    def __init__(self, board, start, end=None):
        self.start_row, self.start_col = start

        self.piece = board[self.start_row, self.start_col]

        if end:
            self.end_row, self.end_col = end

            self.piece_captured = board[self.end_row, self.end_col]

    
    def get_chess_notation(self):
        return (self.get_rank_file(self.start_row, self.start_col) + 
                self.get_rank_file(self.end_row, self.end_col))


    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]

