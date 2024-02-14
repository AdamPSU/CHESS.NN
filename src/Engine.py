import numpy as np 

class GameState:
    def __init__(self):
        self.board = np.array(
            [['bR', 'bN', 'bB', 'bK', 'bQ', 'bB', 'bN', 'bR'],
             ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
             ['--', '--', '--', '--', '--', '--', '--', '--'],
             ['--', '--', '--', '--', '--', '--', '--', '--'],
             ['--', '--', '--', '--', '--', '--', '--', '--'],
             ['--', '--', '--', '--', '--', '--', '--', '--'],
             ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
             ['wR', 'wN', 'wB', 'wK', 'wQ', 'wB', 'wN', 'wR']]
        )

        self.whiteToMove = True
        self.moveLog = [] # For debugging
    
    def getBoard(self):
        return self.board

    def getPiece(self, move):
        board = self.getBoard()
        return board[move.startRow, move.startCol]
    
    def isValid(self, move): 
        '''Logic for determining whether a move is valid/invalid.'''
        
        def _turn(move):
            '''
            Determines who will play and disables other player 
            from making a move.
            '''

            piece = self.getPiece(move)

            if (self.whiteToMove) and (piece.startswith('w')):
                return True # White's turn
            elif (not self.whiteToMove) and (piece.startswith('b')):
                return True # Black's turn
            return False
    
        if not (_turn(move)):
            return False
        
        pieceType = self.getPiece(move)[1] # Get the symbol of the piece
        pieceHandlers = {
        'p': self._pawn,
        'R': self._rook,
        'N': self._knight, 
        'B': self._bishop,
        'K': self._king,
        'Q': self._queen
        }

        handler = pieceHandlers.get(pieceType)

        if (handler):
            return handler(move) 
        return False 

    def makeMove(self, move):
        '''
        Performs the move, logs it in the terminal, and switches 
        the player's turn after moving.
        '''
        board = self.getBoard() 

        # Move the piece to the new square
        board[move.startRow, move.startCol] = "--"
        board[move.endRow, move.endCol] = move.pieceMoved

        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove # Switch player turns

    def _pawn(self, move): 
        '''
        Defines the rules for a chess pawn. Can only 
        move forward up to two pieces (currently)

        Missing: after the first march, make it so that it only goes 
        forward once. 
        '''
        board = self.getBoard()
        stepSize = move.endRow - move.startRow

        if abs(move.startCol - move.endCol) > 0 or abs(stepSize) > 2:
            # Check if the pawn moved more than 2 spaces or if it moved sideways
            return False
        
        # Determine where the pawn should be facing
        if (self.whiteToMove):
            direction = 1
        else:
            direction = -1

        # Check for each step if there's a piece in its way
        for i in range(1, abs(stepSize)+1):
            movedRow = move.startRow - (i * direction) 
            if not (board[movedRow, move.startCol] == '--'):
                return False # If there is, no need to check further
        return True # Otherwise, valid move

    def _rook(self, move):
        '''Defines the rules for a chess rook.'''

        # Can only move along the rows or columns; no diagonals
        if (move.startCol != move.endCol) and (move.startRow != move.endRow):
            return False
        return True 
    
    def _knight(self, move):
        '''Defines the rules for a chess knight.'''

        board = self.getBoard()
        size = len(board)
        # All  possible moves relative to the knight
        knightPositions = np.array([(2, -1), (2, 1), (-2, -1), (-2, 1),
            (1, -2), (1, 2), (-1, -2), (-1, 2)])
        
        match = False 
        for dr, dc in knightPositions: # Loop through moves
            movedRow = move.startRow + dr
            movedCol = move.startCol + dc
            # Determine whether player's move matches with any valid moves
            if (0 <= movedRow < size) and (0 <= movedCol < size) and (movedRow, movedCol) == (move.endRow, move.endCol):
                match = True 

        return match 
    
    def _bishop(self, move):
        '''Defines the rules for a chess bishop.'''

        dy = move.endCol - move.startCol
        dx = move.endRow - move.startRow

        if (dx == 0): return False  # Division by 0

        slope = (dy)/(dx)
        # Bishop can move anywhere with a slope of 1
        if (abs(slope) != 1.0):
            return False
        return True
    
    def _king(self, move):
        '''Defines the rules for a chess king.'''

        dx = (move.endRow - move.startRow)
        dy = (move.endCol - move.startCol)

        # Can move anywhere with a radius of 1
        if (abs(dx) > 1 or abs(dy) > 1):
            return False # Otherwise, keep the board
        return True     

    def _queen(self, move):
        '''Defines the rules for a chess queen.'''

        # Rook logic
        if (move.startCol == move.endCol) or (move.startRow == move.endRow):
            return True

        # Bishop logic
        dy = move.endCol - move.startCol
        dx = move.endRow - move.startRow

        if (dx == 0): return False 

        slope = (dy/dx)
        if (abs(slope) != 1.0):
            return False
        return True 

class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {values: key for key, values in ranksToRows.items()} # Reverses ranksToRows

    filesToCols = {"a": 0, "b": 1, "c":2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {values: key for key, values in filesToCols.items()} # Reverses filesToCols

    def __init__(self, startSquare, endSquare, board):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]

        self.pieceMoved = board[self.startRow, self.startCol]
        self.pieceCaptured = board[self.endRow, self.endCol]
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]

