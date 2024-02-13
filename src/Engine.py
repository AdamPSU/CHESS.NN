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
    
    def makeMove(self, move): 
        '''
        Logic for determining which move to make based on 
        selected piece.
        '''

        board = self.getBoard()
        piece = board[move.startRow, move.startCol]

        if (piece == 'wp'): # Pawn
            self._pawn(move)
        elif (piece == 'wR'): # Rook
            self._rook(move)
        elif (piece == 'wN'): # Knight
            self._knight(move)
        elif (piece == 'wB'):
            self._bishop(move)
        elif (piece == 'wK'):
            self._king(move)
        elif (piece == 'wQ'):
            self._queen(move)

    def _update(self, move):
        '''
        Performs the move, logs it in the terminal, and 
        switches the player's turn after moving.
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
        
        if (move.startCol != move.endCol) or (move.startRow > move.endRow + 2):
            return None  # If the columns are changed or moved more than 2 spaces, no move is made
        self._update(move)  # Otherwise, update the state

    
    def _rook(self, move):
        '''Defines the rules for a chess rook.'''

        # Can only move along the rows or columns; no diagonals
        if (move.startCol != move.endCol) and (move.startRow != move.endRow):
            return None
        self._update(move)
    
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

        if (not match):
            return None # If no matches, keep the board
        self._update(move)
    
    def _bishop(self, move):
        '''Defines the rules for a chess bishop.'''

        dy = move.endCol - move.startCol
        dx = move.endRow - move.startRow

        if (dx == 0): return None  # Division by 0

        slope = (dy)/(dx)
        # Bishop can move anywhere with a slope of 1
        if (abs(slope) != 1.0):
            return None
        self._update(move)
    
    def _king(self, move):
        '''Defines the rules for a chess king.'''

        dx = (move.endRow - move.startRow)
        dy = (move.endCol - move.startCol)

        # Can move anywhere with a radius of 1
        if (abs(dx) > 1 or abs(dy) > 1):
            return None # Otherwise, keep the board
        self._update(move)

    def _queen(self, move):
        '''Defines the rules for a chess queen.'''

        # Rook logic
        if (move.startCol == move.endCol) or (move.startRow == move.endRow):
            self._update(move)

        # Bishop logic
        dy = move.endCol - move.startCol
        dx = move.endRow - move.startRow

        if (dx == 0): return None 

        slope = (dy/dx)
        if (abs(slope) != 1.0):
            return None
        self._update(move)






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

