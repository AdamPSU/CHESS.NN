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
        start_row, start_col = move.startRow, move.startCol

        if (board[start_row, start_col] == 'wp'): # Pawn
            self._pawn(move)
        elif (board[start_row, start_col] == 'wR'): # Rook
            self._rook(move)
        elif (board[start_row, start_col] == 'wN'): # Knight
            self._knight(move)

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
        
        if (move.startCol != move.endCol):
            return board # If the columns are changed, keep the board
        elif (move.startRow > move.endRow + 2):
            return board # If moved more than 2 spaces, keep the board
        self._update(move) # Otherwise, update the state
    
    def _rook(self, move):
        '''Defines the rules for a chess rook.'''

        board = self.getBoard()

        # Can only move along the rows or columns; no diagonals
        if (move.startCol != move.endCol) and (move.startRow != move.endRow):
            return board 

        self._update(move)
    
    def _knight(self, move):
        '''Defines the rules for a chess knight.'''

        board = self.getBoard()
        # All the possible moves relative to the knight
        knightPositions = np.array([(2, -1), (2, 1), (-2, -1), (-2, 1),
                           (1, -2), (1, 2), (-1, -2), (-1, 2)])
        
        # Unpack the tuples and repeatedly check for a match
        for dr, dc in knightPositions: 
            try:
                if (move.startRow+dr, move.startCol+dc) == (move.endRow, move.endCol):
                    self._update(move)
                    break
            except IndexError: 
                continue 
        return board
        

class Move():s
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

