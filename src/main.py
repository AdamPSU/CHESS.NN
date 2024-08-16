import pygame as pg

from chess.engine import Engine, Move, gen_valid_moves
from chess.utils import piece_name
from src.graphics import draw_rect, load_pieces, load_grid, graphics; load_pieces()

from src.config import *
from src.graphics import IMAGES


def _highlight_valid_moves(screen, valid_moves):
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


class Chess:
    """Chess interface facilitated by Pygame."""

    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))

        pg.display.set_caption("CHESS-NN")
        self.clock = pg.time.Clock()

        self.white_to_move = True
        self.engine = Engine()
        self.move = Move(self.engine.board, self.engine.history, self.white_to_move)

        self.marked_moves = set()
        self.valid_moves = set()

        self.source_piece = None
        self.source_pos = None
        self.target_pos = None

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
                    self.marked_moves_handler(event, row, col)

                    left_click = event.button == 1
                    if left_click and current_piece is not None:
                        self.source_piece = current_piece
                        self.source_pos = (row, col)

                        if current_piece != EMPTY:
                            self.generate_moves()

                if event.type == pg.MOUSEBUTTONUP:
                    self.valid_moves.clear()

                    if self.target_pos:
                        self.move_handler(self.source_pos, self.target_pos)

                    self.source_pos = None
                    self.target_pos = None

            graphics(self.screen, self.engine.board, self.marked_moves)
            _highlight_valid_moves(self.screen, self.valid_moves)

            self.target_pos = self.drag(self.source_piece, self.source_pos)

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
                pos = (row, col)
                current_piece = piece_name(self.engine.board, pos)

                return current_piece, row, col

        except IndexError:
            pass

        return None, None, None


    def marked_moves_handler(self, event, row, col):
        """
        Logic to handle the marking/highlighting of chess tiles.

        - If a tile is left-clicked, all marked tiles will be cleared.
        - If a tile is right-clicked, it will be marked.
        - If a tile is right-clicked twice, it will be cleared.
        """

        left_click = event.button == 1
        right_click = event.button == 3

        if left_click:
            self.marked_moves.clear()

        elif right_click:
            pos = (row, col)

            if pos in self.marked_moves:
                self.marked_moves.discard(pos)
            else:
                self.marked_moves.add(pos)


    def generate_moves(self):
        """
        Find valid moves in the move space and add them
        to the valid_moves set.
        """

        if len(self.valid_moves) > 0:
            self.valid_moves.clear()

        for loc, valid_move in gen_valid_moves(self.engine.board, self.engine.history,
                                               self.white_to_move, self.source_piece, self.source_pos,
                                               self.move.castling_rights):
            if valid_move:
                self.valid_moves.add(loc)


    def drag(self, piece, loc):
        """
        This function is responsible for dragging the selected piece to the target
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


    def move_handler(self, source, target):
        """
        Handles the logic for selecting and moving pieces on the board.
        It checks for invalid clicks (e.g., attacking a friendly piece), validates the move,
        and updates the game state accordingly.
        """

        is_valid_move, move_type = self.move.validate(source, target)

        if not is_valid_move:
            return

        self.white_to_move = not self.white_to_move

        self.engine.perform_move(source, target, special_move=move_type)


if __name__ == '__main__':
    main = Chess()
    main.run()