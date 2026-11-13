"""Primitive drawing of core state with no simulation or random side effects."""

import pygame

from ..core import GameState, GameStatus

CELL_SIZE = 28
MARGIN = 20
BOARD_TOP = 96
FOOTER_HEIGHT = 68
BACKGROUND = (15, 23, 36)
BOARD_COLOR = (23, 35, 49)
GRID_COLOR = (34, 48, 63)
HEAD_COLOR = (139, 246, 146)
BODY_COLOR = (52, 190, 125)
FOOD_COLOR = (255, 118, 103)
TEXT_COLOR = (235, 242, 250)
MUTED_COLOR = (162, 180, 199)


def window_size(state: GameState) -> tuple[int, int]:
    return (
        state.width * CELL_SIZE + 2 * MARGIN,
        BOARD_TOP + state.height * CELL_SIZE + FOOTER_HEIGHT,
    )


def status_lines(state: GameState) -> tuple[str, ...]:
    if state.status is GameStatus.PAUSED:
        return ("Paused", "Space to resume")
    if state.status is GameStatus.GAME_OVER:
        return ("Game over", "R to restart")
    if state.status is GameStatus.WON:
        return ("You won!", "R to restart")
    return ()


class GameView:
    def __init__(self):
        self.heading_font = pygame.font.Font(None, 40)
        self.text_font = pygame.font.Font(None, 25)
        self.overlay_font = pygame.font.Font(None, 48)

    def _text(self, surface, text, font, position, color=TEXT_COLOR):
        surface.blit(font.render(text, True, color), position)

    def draw(self, surface: pygame.Surface, state: GameState) -> None:
        surface.fill(BACKGROUND)
        self._text(surface, "SNAKE", self.heading_font, (MARGIN, 18))
        self._text(surface, f"Score: {state.score}", self.text_font, (MARGIN, 60))
        board = pygame.Rect(MARGIN, BOARD_TOP, state.width * CELL_SIZE, state.height * CELL_SIZE)
        pygame.draw.rect(surface, BOARD_COLOR, board)
        for x in range(state.width + 1):
            px = MARGIN + x * CELL_SIZE
            pygame.draw.line(surface, GRID_COLOR, (px, board.top), (px, board.bottom))
        for y in range(state.height + 1):
            py = BOARD_TOP + y * CELL_SIZE
            pygame.draw.line(surface, GRID_COLOR, (board.left, py), (board.right, py))

        def cell_rect(cell):
            x, y = cell
            return pygame.Rect(MARGIN + x * CELL_SIZE + 3, BOARD_TOP + y * CELL_SIZE + 3,
                               CELL_SIZE - 6, CELL_SIZE - 6)

        for index, cell in enumerate(state.snake):
            pygame.draw.rect(surface, HEAD_COLOR if index == 0 else BODY_COLOR,
                             cell_rect(cell), border_radius=5)
        if state.food is not None:
            pygame.draw.circle(surface, FOOD_COLOR, cell_rect(state.food).center, CELL_SIZE // 3)

        self._text(surface, "Arrows  Move    Space  Pause / resume", self.text_font,
                   (MARGIN, board.bottom + 14), MUTED_COLOR)
        self._text(surface, "R  Restart    Esc  Exit", self.text_font,
                   (MARGIN, board.bottom + 38), MUTED_COLOR)
        lines = status_lines(state)
        if lines:
            panel = pygame.Rect(0, 0, min(board.width - 16, 340), 120)
            panel.center = board.center
            pygame.draw.rect(surface, BACKGROUND, panel, border_radius=12)
            pygame.draw.rect(surface, MUTED_COLOR, panel, width=1, border_radius=12)
            for index, text in enumerate(lines):
                font = self.overlay_font if index == 0 else self.text_font
                rendered = font.render(text, True, TEXT_COLOR)
                rect = rendered.get_rect(center=(panel.centerx, panel.top + 36 + index * 43))
                surface.blit(rendered, rect)
