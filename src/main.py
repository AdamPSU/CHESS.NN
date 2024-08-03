import pygame as pg
import numpy as np
from Engine.engine import Game, Move

from src.config import *

def load_pieces():
    """Load chess pieces. This will only be done ONCE."""

    # 'b' prefix denotes black pieces, 'w' represents white
    pieces = np.array(['bR', 'bN', 'bB', 'bK', 'bQ', 'bB', 'bN', 'bR', 'bp',
                       'wR', 'wN', 'wB', 'wK', 'wQ', 'wB', 'wN', 'wR', 'wp'])

    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load("../images/" + piece + ".png"),
                                           size=(PIECE_SIZE, PIECE_SIZE))


def graphics(screen, game):
    """
    Responsible for generating and updating GUI graphics
    for each game state.
    """

    board = game.board
    colors = np.array([pg.Color("#F7FCFC"), pg.Color("#C7D4D4")]) # Light gray, gray

    # Checker pattern on the board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 0:
                color = colors[0]
            else:
                color = colors[1]
            pg.draw.rect(screen, color, pg.Rect(col*PIECE_SIZE, row*PIECE_SIZE, PIECE_SIZE, PIECE_SIZE))

    # Place pieces on the board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row, col]
            if piece != EMPTY:
                screen.blit(IMAGES[piece], pg.Rect(col*PIECE_SIZE, row*PIECE_SIZE, PIECE_SIZE, PIECE_SIZE))


def main():
    pg.init()
    
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    icon = pg.image.load("../images/bK.png")

    pg.display.set_caption("CHESS-NN")
    pg.display.set_icon(icon)
    clock = pg.time.Clock()

    game = Game()
    load_pieces()

    selectedPiece = () # No piece is selected
    playerClicks = [] # Keeps track of player clicks
    
    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                location = pg.mouse.get_pos() # (x, y) location of mouse
                col, row = (location[0] // PIECE_SIZE), (location[1] // PIECE_SIZE)

                if selectedPiece == (row, col): # The user selected the same piece twice
                    selectedPiece = (row, col)
                    playerClicks = [] # Reset
                elif col > BOARD_SIZE - 1 or row > BOARD_SIZE - 1:
                    selectedPiece = (row, col)
                    playerClicks = [] # Reset
                else: 
                    selectedPiece = (row, col)
                    playerClicks.append(selectedPiece) 

                    # If 1st click and an empty square is selected, reset
                    if (len(playerClicks) == 1) and (game.board[row, col] == EMPTY):
                        playerClicks = [] 
                        selectedPiece = ()
                        
                if len(playerClicks) == 2: # 2nd click
                    move = Move(game.board, playerClicks[0], playerClicks[1])
                    # Check if the move is valid before playing it
                    if game.isValid(move):
                        game.makeMove(move)

                    selectedPiece, playerClicks = (), [] # Reset

        graphics(screen, game)
        clock.tick(MAX_FPS)  # Control the frame rate
        pg.display.flip()  # Update the display

    pg.quit()

if __name__ == '__main__':
    main()