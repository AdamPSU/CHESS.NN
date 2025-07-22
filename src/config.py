WIDTH = 864
HEIGHT = 864

# Number of squares along each side of the board
BOARD_SIZE = 8

# Pixel size of each board tile (assuming square board and integer division)
TILE_SIZE = HEIGHT // BOARD_SIZE

# Render size for a piece, leaving a small margin within its tile
PIECE_SIZE = TILE_SIZE * 0.9

# Upper bound for row/column indices (0-based indexing)
BOUNDS = BOARD_SIZE - 1

# Target frames per second for the game loop
MAX_FPS = 60

# Representation for an empty square on the board
EMPTY = '--'