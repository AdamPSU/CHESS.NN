import pygame as pg
from config import *

IMAGES = {}

def draw_rect(row, col):
    """
    Creates a rectangle object at a specified grid position.

    Args:
        row (int): The row index of the rectangle.
        col (int): The column index of the rectangle.

    Returns:
        pg.Rect: A rectangle object representing the tile at the specified position.
    """
    # Calculate the rectangle's position and size based on the grid and tile size
    rect = pg.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    return rect
def load_pieces():
    """
    Load chess pieces. This will only be done once, at the start of the
    game's execution.
    """

    pieces = ['bR', 'bN', 'bB', 'bK', 'bQ', 'bB', 'bN', 'bR', 'bp',
              'wR', 'wN', 'wB', 'wK', 'wQ', 'wB', 'wN', 'wR', 'wp']

    for piece in pieces:
        image = pg.image.load("../images/" + piece + ".png")
        IMAGES[piece] = pg.transform.smoothscale(image, size=(PIECE_SIZE, PIECE_SIZE))


def load_grid(screen):
    """
    Responsible for generating and updating GUI graphics
    for each chessboard game state.
    """

    # surface = pg.Surface((screen.get_size()))

    white, purple = '#f1f1f1', '#8475b9'
    colors = [pg.Color(white), pg.Color(purple)]

    # Checker pattern on the board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 0:
                color = colors[0]
            else:
                color = colors[1]

            rect = draw_rect(row, col)
            pg.draw.rect(screen, color, rect)


def update_pieces(screen, board):
    """
    Responsible for generating and updating GUI graphics
    for each chessboard game state.
    """

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]

            if piece == EMPTY:
                continue

            piece_image = IMAGES[piece]
            piece_rect = piece_image.get_rect()

            offset = 5
            piece_rect.center = (col * TILE_SIZE + TILE_SIZE // 2,
                                 row * TILE_SIZE + TILE_SIZE // 2 + offset)

            screen.blit(piece_image, piece_rect.topleft)


def highlight_valid_moves(screen, valid_moves):
    """
    This function is responsible for the visualization
    of the move space for the clicked piece. If a
    move is valid, it will be "highlighted," or marked
    with a black circle.
    """

    for pos in valid_moves:
        row, col = pos

        surface = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)

        # Circles must be centered within the tile
        center = (TILE_SIZE // 2, TILE_SIZE // 2)
        radius = TILE_SIZE // 6

        alpha = 120
        black = (51, 55, 76, alpha)

        pg.draw.circle(surface, black, center, radius)

        screen.blit(surface, (col * TILE_SIZE, row * TILE_SIZE))



def _highlight_tile(screen, tile):
    if None in tile:
        return

    row, col = tile

    surface = pg.Surface((TILE_SIZE, TILE_SIZE))
    surface.set_alpha(150)

    rouge = pg.Color('#7d3d54')
    surface.fill(rouge)

    screen.blit(surface, (col*TILE_SIZE, row*TILE_SIZE))


def graphics(screen, board, highlighted):
    """
    Updates the game graphics by loading the grid, highlighting selected tiles, and updating game pieces.

    Args:
        screen: The game screen object.
        board: The current state of the game board.
        highlighted: A collection of highlighted tile positions.
    """
    # Load the grid onto the screen
    load_grid(screen)

    # Highlight each selected tile on the screen
    for tile in highlighted:
        _highlight_tile(screen, tile)

    # Update the game pieces on the screen based on the current board state
    update_pieces(screen, board)
```