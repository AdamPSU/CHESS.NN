import pygame as pg

from chess.engine import Engine, Move, gen_valid_moves

from src.graphics import draw_rect, load_pieces, load_grid, graphics; load_pieces()

from src.config import *
from src.graphics import IMAGES


def _highlight_valid_moves(screen, valid_moves):
    for move in valid_moves:
        row, col = move

        surface = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)

        center = (TILE_SIZE // 2, TILE_SIZE // 2)
        radius = TILE_SIZE // 6

        alpha = 120
        black = (51, 55, 76, alpha)

        # Draw a semi-transparent circle
        pg.draw.circle(surface, black, center, radius)

        # Blit the surface onto the screen at the correct position
        screen.blit(surface, (col * TILE_SIZE, row * TILE_SIZE))


class Chess:
    """Chess interface facilitated by Pygame."""

    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))

        pg.display.set_caption("CHESS-NN")
        self.clock = pg.time.Clock()

        self.engine = Engine()
        self.white_to_move = True

        self.highlighted = set()
        self.valid_moves = set()

        self.start_piece = None

        self.start_loc = None
        self.target_loc = None

        load_grid(self.screen)

        self.icon = IMAGES['bK']
        pg.display.set_icon(self.icon)

        self.running = True


    def run(self):
        """Run the chess game."""

        while self.running:
            current_piece, row, col = self.get_tile_under_mouse()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

                if event.type == pg.MOUSEBUTTONDOWN:
                    self.highlight_handler(event, row, col)

                    left_click = event.button == 1
                    if left_click and current_piece is not None:
                        self.start_piece = current_piece
                        self.start_loc = (row, col)

                        if current_piece != EMPTY:
                            self.generate_moves()

                if event.type == pg.MOUSEBUTTONUP:
                    self.valid_moves.clear()

                    if self.target_loc:
                        self.move_handler(self.start_loc, self.target_loc)

                    self.start_loc = None
                    self.target_loc = None

            graphics(self.screen, self.engine.board, self.highlighted)
            _highlight_valid_moves(self.screen, self.valid_moves)

            self.target_loc = self.drag(self.start_piece, self.start_loc)

            self.clock.tick(MAX_FPS)
            pg.display.flip()

        pg.quit()


    def get_tile_under_mouse(self):
        """Obtains the tile belonging to the mouse position."""

        x_mouse, y_mouse = pg.mouse.get_pos()

        row = y_mouse // TILE_SIZE
        col = x_mouse // TILE_SIZE

        try:
            if row >= 0 and col >= 0:
                loc = (row, col)

                return self.engine.piece(loc), row, col

        except IndexError:
            pass

        return None, None, None


    def highlight_handler(self, event, row, col):
        """
        Logic to handle the highlighting of chess tiles.

        - If a tile is left-clicked, all highlighted tiles will be cleared.
        - If a tile is right-clicked, it will be highlighted.
        - If a tile is right-clicked twice, it will be cleared.
        """

        left_click = event.button == 1
        right_click = event.button == 3

        if left_click:
            self.highlighted.clear()

        elif right_click:
            tile = (row, col)

            if tile in self.highlighted:
                self.highlighted.discard(tile)
            else:
                self.highlighted.add(tile)


    def generate_moves(self):
        if len(self.valid_moves) > 0:
            self.valid_moves.clear()

        for loc, valid_move in gen_valid_moves(self.engine.board, self.white_to_move,
                                               self.start_piece, self.start_loc):
            if valid_move:
                self.valid_moves.add(loc)


    def drag(self, piece, loc):
        """
        Responsible for dragging the selected piece to the target
        location. If the piece location is out of bounds or the selected
        piece is an empty tile, this method will be ignored.
        """

        if not loc:
            return

        if piece == EMPTY:
            return

        row, col = loc

        rect = draw_rect(row, col)
        pg.draw.rect(self.screen, '#cda7e7', rect, 5)

        image = IMAGES[piece]

        pos = pg.mouse.get_pos()
        offset = (1, 1)

        self.screen.blit(image, image.get_rect(center = pg.Vector2(pos) + offset))
        self.screen.blit(image, image.get_rect(center = pg.Vector2(pos)))

        end_row = pos[1] // TILE_SIZE
        end_col = pos[0] // TILE_SIZE

        return end_row, end_col


    def move_handler(self, start, end):
        """
        Handles the logic for selecting and moving pieces on the board.
        It checks for invalid clicks (e.g., attacking a friendly piece), validates the move,
        and updates the game state accordingly.
        """

        move = Move(self.engine.board, self.white_to_move, start, end)
        is_valid_move = move.validate()

        if not is_valid_move:
            return

        self.white_to_move = not self.white_to_move
        self.engine.perform_move(start, end)


if __name__ == '__main__':
    main = Chess()
    main.run()