import pygame as pg
from config import *

IMAGES = {}

def draw_rect(row, col):
    # Compute a pygame Rect for a board tile at (row, col) in pixel coordinates.
    rect = pg.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    return rect


def load_pieces():
    """
    Load chess piece sprites into the global IMAGES dict.
    This runs once at startup to preload and scale all piece images.
    """
    pieces = ['bR', 'bN', 'bB', 'bK', 'bQ', 'bB', 'bN', 'bR', 'bp',
              'wR', 'wN', 'wB', 'wK', 'wQ', 'wB', 'wN', 'wR', 'wp']

    for piece in pieces:
        # Load from the images directory, then smooth scale to PIECE_SIZE
        image = pg.image.load("../images/" + piece + ".png")
        IMAGES[piece] = pg.transform.smoothscale(image, size=(PIECE_SIZE, PIECE_SIZE))


def load_grid(screen):
    """
    Draw the chessboard grid onto the given screen surface.
    Uses a two-color checker pattern based on row+col parity.
    """
    white, purple = '#f1f1f1', '#8475b9'
    colors = [pg.Color(white), pg.Color(purple)]

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # Alternate colors in a checker pattern
            color = colors[(row + col) % 2]
            rect = draw_rect(row, col)
            pg.draw.rect(screen, color, rect)


def update_pieces(screen, board):
    """
    Blit all piece images onto the board according to the current game state.
    Each piece is centered in its tile with a small vertical offset for visual balance.
    """
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece == EMPTY:
                continue

            piece_image = IMAGES[piece]
            piece_rect = piece_image.get_rect()

            # Offset to visually center the piece within the tile
            offset = 5
            piece_rect.center = (
                col * TILE_SIZE + TILE_SIZE // 2,
                row * TILE_SIZE + TILE_SIZE // 2 + offset
            )
            screen.blit(piece_image, piece_rect.topleft)


def highlight_valid_moves(screen, valid_moves):
    """
    Overlay semi-transparent circles on tiles representing valid move destinations.
    Each circle is drawn on its own surface with alpha blending.
    """
    for row, col in valid_moves:
        # Create a transparent tile-sized surface
        surface = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)

        # Position circle at center with a radius proportional to tile size
        center = (TILE_SIZE // 2, TILE_SIZE // 2)
        radius = TILE_SIZE // 6

        # RGBA for the marker (semi-transparent dark)
        black = (51, 55, 76, 120)
        pg.draw.circle(surface, black, center, radius)

        # Blit the marker onto the main screen at the correct tile location
        screen.blit(surface, (col * TILE_SIZE, row * TILE_SIZE))


def _highlight_tile(screen, tile):
    """
    Highlight a specific tile (e.g., selected piece) with a semi-transparent overlay.
    Expects tile as a (row, col) tuple; ignores if it contains None.
    """
    if None in tile:
        return

    row, col = tile
    surface = pg.Surface((TILE_SIZE, TILE_SIZE))
    surface.set_alpha(150)

    # Fill with a red tint to indicate selection
    rouge = pg.Color('#7d3d54')
    surface.fill(rouge)

    screen.blit(surface, (col * TILE_SIZE, row * TILE_SIZE))


def graphics(screen, board, highlighted):
    """
    Render the full chessboard scene: draw grid, highlight selected tiles, then pieces.
    """
    load_grid(screen)

    # Apply highlights for any tiles in the highlighted list
    for tile in highlighted:
        _highlight_tile(screen, tile)

    # Draw all pieces above the board and highlights
    update_pieces(screen, board)