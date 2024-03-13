import pygame as pg
import numpy as np
import Engine

WIDTH = 864
HEIGHT = 864
BOARD_SIZE = 8 
PIECE_SIZE = HEIGHT // BOARD_SIZE
MAX_FPS = 60
IMAGES = {} 

def loadPieces():
    '''Load chess pieces. This will only be done ONCE.'''

    pieces = np.array(['bR', 'bN', 'bB', 'bK', 'bQ', 'bB', 'bN', 'bR', 
        'bp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'wB', 'wN', 'wR', 'wp'])

    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load("images/" + piece + ".png"), (PIECE_SIZE, PIECE_SIZE))  # IMAGES['wp']

def boardGraphics(screen, gameState):
    '''
    Responsible for generating and updating GUI graphics
    for each game state.
    '''

    def _drawTiles(screen):
        '''Generate tiles on the board.'''

        colors = np.array([pg.Color("#F7FCFC"), pg.Color("#C7D4D4")]) # Light gray, gray # Light red, red
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if ((row + col) % 2 == 0):
                    color = colors[0]
                else: 
                    color = colors[1]
                pg.draw.rect(screen, color, pg.Rect(col*PIECE_SIZE, row*PIECE_SIZE, PIECE_SIZE, PIECE_SIZE))
                     
    def _drawPieces(screen, board):
        '''Place pieces within tiles.'''
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = board[row, col]
                if (piece != "--"): # Not empty square
                    screen.blit(IMAGES[piece], pg.Rect(col*PIECE_SIZE, row*PIECE_SIZE, PIECE_SIZE, PIECE_SIZE))
        pass

    _drawTiles(screen)
    _drawPieces(screen, gameState.board)

def main():
    pg.init()
    
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    icon = pg.image.load("./images/bK.png")

    pg.display.set_caption("CHESS-NN")
    pg.display.set_icon(icon) # Set Icon
    clock = pg.time.Clock()

    gameState = Engine.GameState()
    loadPieces()

    running = True
    selectedPiece = () # No piece is selected
    playerClicks = [] # Keeps track of player clicks

    while (running):
        for event in pg.event.get():
            if (event.type == pg.QUIT):
                running = False
            elif (event.type == pg.MOUSEBUTTONDOWN):
                location = pg.mouse.get_pos() # (x, y) location of mouse
                col, row = (location[0] // PIECE_SIZE), (location[1] // PIECE_SIZE)

                if (selectedPiece == (row, col)): # The user selected the same piece twice
                    selectedPiece = (row, col)
                    playerClicks = [] # Reset
                elif (col > BOARD_SIZE - 1 or row > BOARD_SIZE - 1):
                    selectedPiece = (row, col)
                    playerClicks = [] # Reset
                else: 
                    selectedPiece = (row, col)
                    playerClicks.append(selectedPiece) 

                    # If 1st click and an empty square is selected, reset
                    if (len(playerClicks) == 1) and (gameState.board[row, col] == '--'): 
                        playerClicks = [] 
                        selectedPiece = ()
                        
                if (len(playerClicks) == 2): # 2nd click
                    move = Engine.Move(gameState.board, playerClicks[0], playerClicks[1])
                    # Check if the move is valid before playing it
                    if (gameState.isValid(move)):
                        gameState.makeMove(move)

                    selectedPiece, playerClicks = (), [] # Reset

        boardGraphics(screen, gameState) 
        clock.tick(MAX_FPS)  # Control the frame rate
        pg.display.flip()  # Update the display

    pg.quit()

if __name__ == '__main__':
    main()