import numpy as np 
import pygame as pg

class Game:
    def __init__(self):
        self.board = np.array(
            [['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
             ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
             ['--', '--', '--', '--', '--', '--', '--', '--'],
             ['--', '--', '--', '--', '--', '--', '--', '--'],
             ['--', '--', '--', '--', '--', '--', '--', '--'],
             ['--', '--', '--', '--', '--', '--', '--', '--'],
             ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
             ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        )

        self.whiteToMove = True
        self.moveLog = [] # For debugging


    def getBoard(self):
        return self.board


    def getPiece(self, move):
        board = self.getBoard()
        return board[move.startRow, move.startCol]


    def getAttackedPiece(self, move):
        board = self.getBoard()
        return board[move.endRow, move.endCol]


    def isValid(self, move): 
        """Logic for determining whether a move is valid/invalid."""
        
        piece = self.getPiece(move)

        # Determins who will play
        if (self.whiteToMove) and (piece.startswith('b')):
            return False # Not black's turn to play
        elif (not self.whiteToMove) and (piece.startswith('w')):
            return False # Not white's turn to play
        
        pieceType = self.getPiece(move)[1] # Get the symbol of the piece
        pieceHandlers = {
        'p': self.pawn,
        'R': self.rook,
        'N': self.knight, 
        'B': self.bishop,
        'K': self.king,
        'Q': self.queen
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

    def pawn(self, move): 
        '''
        Defines the rules for a chess pawn. 

        Missing: En Passant
        '''

        board = self.getBoard()
        changeInCol = abs(move.endCol - move.startCol)
        changeInRow = abs(move.endRow - move.startRow)
        direction = 1 if (self.whiteToMove) else -1 # White moves upwards, black moves downwards

        def hasMovedBefore(move):
            '''
            If a pawn is not in its starting position, 
            the pawn is only allowed to move 1 square at a time.
            '''
            # White starts at row 6, black starts at row 1 (list indices)
            defaultRow = 6 if (self.whiteToMove) else 1
            
            if (move.startRow != defaultRow):
                return True 
            return False  
            
        def cannotAttack(move):
            '''
            Assuming the pawn is looking at a diagonal, it cannot
            attack if the attacked piece is a friendly/empty square.
            '''

            target = 'b' if (self.whiteToMove) else 'w' # White targets black, black targets white
            changeInRow = move.endRow - move.startRow
            attackedPiece = self.getAttackedPiece(move) # Retrieve the attacked square

            if (changeInRow * changeInCol != -1*direction) or (not attackedPiece.startswith(target)):
                return True 
            return False # It can attack
        
        def hasConflicts(move):
            '''
            Incrementally checks for each step taken whether
            there is a conflicting piece. There will be at most 
            two steps.
            '''

            # Check for each step if there's a piece in its way
            for i in range(1, changeInRow+1):
                movedRow = move.startRow - (i * direction) 
                if not (board[movedRow, move.startCol] == '--'):
                    return True # There are conflicts; don't move there
            return False
        
        if (changeInRow > 2) or (changeInCol > 1):
            # Pawns can't move more than 2 rows up or more than 1 column sideways
            return False 
        elif (hasMovedBefore(move)) and (changeInRow > 1):
            return False 
        elif (cannotAttack(move) and (changeInCol > 0)):
            return False 
        elif (hasConflicts(move) and (changeInCol == 0)):
            return False
        return True # Otherwise, valid move

    def rook(self, move):
        '''Defines the rules for a chess rook.'''

        board = self.getBoard()
        changeInRow = abs(move.endRow - move.startRow)
        changeInCol = abs(move.endCol - move.startCol)
        
        def hasConflicts(move):
            '''
            Determines whether there is a piece preventing the bishop's move 
            along a diagonal.
            '''

            friendly = 'w' if (self.whiteToMove) else 'b' # Determine the color of the current player's pieces
            attackedPiece = self.getAttackedPiece(move)

            if (attackedPiece.startswith(friendly)):
                return True  # Can't capture a friendly piece
            
            moveDistance = changeInRow + changeInCol # Calculate total squares to check
            rowStep = 1 if move.endRow > move.startRow else -1
            colStep = 1 if move.endCol > move.startCol else -1

            rowMovement = 1 if changeInRow > 0 else 0 # 0 means row will not be checked
            colMovement = 1 if changeInCol > 0 else 0 # 0 means column will not be checked

            for i in range(1, moveDistance):
                newPosition = (move.startRow + (i * rowStep * rowMovement), 
                    move.startCol + (i * colStep * colMovement)) 

                if board[newPosition] != '--': # Check if the square is occupied
                    return True  # Conflicting piece on rook's path
            return False 
            
        if (changeInCol > 0) and (changeInRow > 0):
            # Can only move along the rows or columns; no diagonals
            return False
        
        if (hasConflicts(move)):
            return False
        return True 
    
    def knight(self, move):
        '''Defines the rules for a chess knight.'''
        
        def hasConflicts(move):
            '''
            If the attacked piece is not an enemy piece, 
            there is a piece preventing the knight's move.
            '''

            target = 'b' if (self.whiteToMove) else 'w'
            attackedPiece = self.getAttackedPiece(move)

            if (attackedPiece.startswith(target)) or (attackedPiece == '--'):
                # Knight is not staring at a friendly piece, valid attack
                return False
            return True # Otherwise, illegal move
        
        if (hasConflicts(move)):
            return False
        
        # All  possible moves relative to the knight
        potentialKnightPositions = np.array([(2, -1), (2, 1), (-2, -1), (-2, 1),
            (1, -2), (1, 2), (-1, -2), (-1, 2)])
        
        # For each move, determine whether there is a match
        match = any((move.startRow + dr, move.startCol + dc) == (move.endRow, move.endCol)
            for dr, dc in potentialKnightPositions)

        return match 
    
    def bishop(self, move):
        '''Defines the rules for a chess bishop.'''

        board = self.getBoard()
        changeInRow = abs(move.endRow - move.startRow)  
        changeInCol = abs(move.endCol - move.startCol)

        def hasConflicts(move):
            '''
            Determines whether there is a piece preventing the bishop's move 
            along a diagonal.
            '''

            friendly = 'w' if (self.whiteToMove) else 'b'
            attackedPiece = self.getAttackedPiece(move)

            if (attackedPiece.startswith(friendly)):
                return True  # Can't attack a friendly piece
            
            amountMoved = changeInRow
            rowDirection = 1 if (move.endRow > move.startRow) else -1
            colDirection = 1 if (move.endCol > move.startCol) else -1

            for i in range(1, amountMoved):
                newPosition = (move.startRow + (i * rowDirection), 
                    move.startCol + (i * colDirection))  # Diagonal movement

                if (board[newPosition] != '--'):
                    return True  # Conflicting piece on the diagonal

            return False

        if (changeInCol == 0): 
            # This is to prevent division by 0 errors
            return False 
        
        slope = changeInRow / changeInCol
        if (slope != 1.0): 
            return False # Can only move on diagonals
        
        if (hasConflicts(move)):
            return False 
        return True
    
    def king(self, move):
        '''Defines the rules for a chess king.'''

        changeInRow = abs(move.endRow - move.startRow)
        changeInCol = abs(move.endCol - move.startCol)

        def hasConflicts(move):
            '''
            If the attacked piece is not an enemy piece, 
            there is a piece preventing the king's move.
            '''

            target = 'b' if (self.whiteToMove) else 'w'
            attackedPiece = self.getAttackedPiece(move)

            if (attackedPiece.startswith(target)) or (attackedPiece == '--'):
                return False
            return True 
        
        if (hasConflicts(move)):
            return False

        # Can move anywhere with a radius of 1
        if (changeInRow > 1 or changeInCol > 1):
            return False # Otherwise, keep the board
        return True     

    def queen(self, move):
        '''
        Defines the rules for a chess queen, taking advantage
        of the fact that a queen is simply a rook and a bishop combined.
        '''

        changeInRow = abs(move.endRow - move.startRow)
        changeInCol = abs(move.endCol - move.startCol)

        if (changeInRow > 0 and changeInCol > 0):
            # Is likely a bishop move
            return self.bishop(move)
        else: 
            # Is likely a rook move
            return self.rook(move)


class MoveGenerator: 
    def __init__(self, screen, turn, board, piece):
        self.screen = screen
        self.whiteToMove = turn
        self.board = board
        self.row = piece[0]
        self.col = piece[1]

    def validPawnMoves(self):
        board = self.board
        direction = 1 if (self.whiteToMove) else -1 
        moves = []

        def hasNotMoved(moves):
            target = 'b' if (self.whiteToMove) else 'w'
            forwardMoves = [(0, 1), (0, 2)]
            diagonalMoves = [(-1, 1), (1, 1)]

            for dr, dc in forwardMoves:
                newMove = (self.row + dr * direction, self.col + dc * direction)
                moves.append(newMove)
            
            for dr, dc in diagonalMoves:
                newMove = (self.row + dr * direction, self.col + dc * direction)

                if (board[newMove].startswith(target)):
                    moves.append(newMove)

        hasNotMoved(moves)
        return moves

        




            
        # def cannotAttack(move):
        #     '''
        #     Assuming the pawn is looking at a diagonal, it cannot
        #     attack if the attacked piece is a friendly/empty square.
        #     '''

        #     target = 'b' if (self.whiteToMove) else 'w' # White targets black, black targets white
        #     changeInRow = move.endRow - move.startRow
        #     attackedPiece = self.getAttackedPiece(move) # Retrieve the attacked square

        #     if (changeInRow * changeInCol != -1*direction) or (not attackedPiece.startswith(target)):
        #         return True 
        #     return False # It can attack
        
        # def hasConflicts(move):
        #     '''
        #     Incrementally checks for each step taken whether
        #     there is a conflicting piece. There will be at most 
        #     two steps.
        #     '''

        #     # Check for each step if there's a piece in its way
        #     for i in range(1, changeInRow+1):
        #         movedRow = move.startRow - (i * direction) 
        #         if not (board[movedRow, move.startCol] == '--'):
        #             return True # There are conflicts; don't move there
        #     return False
        
        # if (changeInRow > 2) or (changeInCol > 1):
        #     # Pawns can't move more than 2 rows up or more than 1 column sideways
        #     return False 
        # elif (hasMovedBefore(move)) and (changeInRow > 1):
        #     return False 
        # elif (cannotAttack(move) and (changeInCol > 0)):
        #     return False 
        # elif (hasConflicts(move) and (changeInCol == 0)):
        #     return False
        # return True # Otherwise, valid move

        
        
class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {values: key for key, values in ranksToRows.items()} # Reverses ranksToRows

    filesToCols = {"a": 0, "b": 1, "c":2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {values: key for key, values in filesToCols.items()} # Reverses filesToCols

    def __init__(self, board, startSquare, endSquare=None):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]

        self.pieceMoved = board[self.startRow, self.startCol]

        if endSquare is not None:
            self.endRow = endSquare[0]
            self.endCol = endSquare[1]

            self.pieceCaptured = board[self.endRow, self.endCol]
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]

