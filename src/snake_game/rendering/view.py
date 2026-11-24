"""Deterministic woodland presentation; drawing never advances simulation."""

from random import Random
import pygame
from ..core import GameState, GameStatus

CELL_SIZE = 28
MARGIN = 20
BOARD_TOP = 96
FOOTER_HEIGHT = 68
BACKGROUND = (235, 229, 214)
BOARD_COLOR = (64, 79, 49)
GRID_COLOR = (79, 92, 61)
HEAD_COLOR = (181, 153, 99)
BODY_COLOR = (157, 130, 79)
FOOD_COLOR = (184, 71, 48)
TEXT_COLOR = (66, 68, 47)
MUTED_COLOR = (111, 116, 89)
_OUTLINE = (72, 61, 37)


def window_size(state: GameState) -> tuple[int, int]:
    return (max(460, state.width * CELL_SIZE + 2 * MARGIN),
            BOARD_TOP + max(140, state.height * CELL_SIZE) + FOOTER_HEIGHT)


def status_lines(state: GameState) -> tuple[str, ...]:
    if state.status is GameStatus.PAUSED:
        return ("Paused", "Space to resume")
    if state.status is GameStatus.GAME_OVER:
        return ("Game over", "R to restart")
    if state.status is GameStatus.WON:
        return ("You won!", "R to restart")
    return ()


def _center(cell):
    return (MARGIN + cell[0] * CELL_SIZE + CELL_SIZE // 2,
            BOARD_TOP + cell[1] * CELL_SIZE + CELL_SIZE // 2)


def _adjacent(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1


class GameView:
    def __init__(self):
        self.heading_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 23)
        self.overlay_font = pygame.font.Font(None, 44)
        self.small_font = pygame.font.Font(None, 18)
        self._terrain_size = None
        self._terrain = None

    def _text(self, surface, text, font, position, color=TEXT_COLOR):
        surface.blit(font.render(text, True, color), position)

    def _ground(self, size):
        """Cache one board-sized terrain; never consume simulation randomness."""
        if self._terrain_size == size:
            return self._terrain
        width, height = size
        ground = pygame.Surface(size)
        for y in range(height):
            light = 1 - y / max(1, height)
            color = (int(54 + light * 20), int(70 + light * 19), int(43 + light * 14))
            pygame.draw.line(ground, color, (0, y), (width - 1, y))
        rng = Random(1947 + width * 31 + height)
        for _ in range(width * height // 32):
            px, py = rng.randrange(width), rng.randrange(height)
            base = ground.get_at((px, py))
            delta = rng.randrange(-5, 6)
            color = tuple(max(0, min(255, channel + delta)) for channel in base[:3])
            pygame.draw.line(ground, color, (px, py), (min(width - 1, px + 1), py))
        for _ in range(width * height // 900):
            px, py = rng.randrange(width), rng.randrange(height)
            pygame.draw.lines(ground, (86 + rng.randrange(12), 101 + rng.randrange(12), 66),
                              False, [(px - 2, py - 5), (px, py), (px + 1, py - 8)], 1)
        for _ in range(width * height // 12000):
            leaf = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.ellipse(leaf, (135, 124, 76, 48), (8, 3, 8, 17))
            pygame.draw.line(leaf, (80, 84, 49, 55), (12, 5), (12, 21))
            leaf = pygame.transform.rotate(leaf, rng.randrange(360))
            ground.blit(leaf, (rng.randrange(width) - 12, rng.randrange(height) - 12))
        grid = pygame.Surface(size, pygame.SRCALPHA)
        for px in range(CELL_SIZE, width, CELL_SIZE):
            pygame.draw.line(grid, (206, 211, 161, 12), (px, 0), (px, height))
        for py in range(CELL_SIZE, height, CELL_SIZE):
            pygame.draw.line(grid, (206, 211, 161, 12), (0, py), (width, py))
        ground.blit(grid, (0, 0))
        pygame.draw.rect(ground, (93, 107, 70), ground.get_rect(), 1)
        self._terrain_size, self._terrain = size, ground
        return ground

    def _snake(self, surface, state):
        cells = state.snake
        if not cells:
            return
        centers = [_center(cell) for cell in cells]
        links = [(centers[i], centers[i + 1]) for i in range(len(cells) - 1)
                 if _adjacent(cells[i], cells[i + 1])]
        shadow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for a, b in links:
            pygame.draw.line(shadow, (19, 25, 14, 65), (a[0] + 1, a[1] + 3),
                             (b[0] + 1, b[1] + 3), 23)
        for p in centers:
            pygame.draw.circle(shadow, (19, 25, 14, 65), (p[0] + 1, p[1] + 3), 11)
        surface.blit(shadow, (0, 0))
        for color, radius in ((_OUTLINE, 11), (BODY_COLOR, 9)):
            for a, b in links:
                pygame.draw.line(surface, color, a, b, radius * 2)
            for p in centers:
                pygame.draw.circle(surface, color, p, radius)
        for index in range(1, len(cells)):
            p, other = centers[index], centers[index - 1]
            if not _adjacent(cells[index], cells[index - 1]):
                continue
            dx, dy = (other[0] - p[0]) // CELL_SIZE, (other[1] - p[1]) // CELL_SIZE
            nx, ny = -dy, dx
            for offset in (-7, 0, 7):
                points = [(p[0] + dx * offset + nx * side + dx * abs(side) // 3,
                           p[1] + dy * offset + ny * side + dy * abs(side) // 3)
                          for side in (-7, -3, 0, 3, 7)]
                pygame.draw.lines(surface, (100, 82, 48), False, points, 2)
            pygame.draw.line(surface, (193, 165, 108),
                             (p[0] - nx * 5 - dx * 9, p[1] - ny * 5 - dy * 9),
                             (p[0] - nx * 5 + dx * 9, p[1] - ny * 5 + dy * 9), 1)
        if len(cells) > 1 and _adjacent(cells[-1], cells[-2]):
            p, toward = centers[-1], centers[-2]
            dx, dy = (toward[0] - p[0]) // CELL_SIZE, (toward[1] - p[1]) // CELL_SIZE
            nx, ny = -dy, dx
            rect = pygame.Rect(p[0] - 14, p[1] - 14, 28, 28)
            surface.blit(self._terrain, rect, (rect.x - MARGIN, rect.y - BOARD_TOP, 28, 28))
            tip = (p[0] - dx * 11, p[1] - dy * 11)
            for color, half in ((_OUTLINE, 11), (BODY_COLOR, 8)):
                pygame.draw.polygon(surface, color,
                                    [(p[0] + dx * 14 + nx * half, p[1] + dy * 14 + ny * half),
                                     tip,
                                     (p[0] + dx * 14 - nx * half, p[1] + dy * 14 - ny * half)])
            pygame.draw.line(surface, (192, 165, 108), tip,
                             (p[0] + dx * 12, p[1] + dy * 12), 1)
        head = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(head, _OUTLINE, (1, 3, 26, 22))
        pygame.draw.ellipse(head, HEAD_COLOR, (2, 4, 24, 20))
        pygame.draw.arc(head, (209, 183, 127), (5, 5, 17, 15), .3, 2.8, 1)
        for y in (7, 21):
            pygame.draw.circle(head, (205, 181, 117), (18, y), 4)
            pygame.draw.circle(head, (37, 39, 25), (19, y), 2)
            head.set_at((19, y - 1), (249, 241, 212))
        pygame.draw.line(head, (113, 91, 53), (23, 12), (23, 15), 1)
        angle = {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): 270}[state.direction.delta]
        head = pygame.transform.rotate(head, angle)
        surface.blit(head, head.get_rect(center=centers[0]))

    def _apple(self, surface, cell):
        apple = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(apple, (19, 27, 15, 70), (5, 22, 20, 5))
        pygame.draw.ellipse(apple, (113, 48, 31), (3, 7, 22, 19))
        pygame.draw.ellipse(apple, FOOD_COLOR, (3, 6, 13, 18))
        pygame.draw.ellipse(apple, (203, 91, 58), (11, 6, 13, 18))
        pygame.draw.ellipse(apple, (222, 129, 83), (5, 8, 7, 11))
        pygame.draw.ellipse(apple, (246, 181, 123), (6, 9, 3, 5))
        pygame.draw.line(apple, (81, 59, 32), (14, 8), (16, 1), 2)
        pygame.draw.ellipse(apple, (155, 170, 92), (16, 2, 9, 4))
        surface.blit(apple, apple.get_rect(center=_center(cell)))

    def _overlay(self, surface, board, state):
        lines = status_lines(state)
        if not lines:
            return
        veil = pygame.Surface(board.size, pygame.SRCALPHA)
        veil.fill((21, 31, 17, 100))
        surface.blit(veil, board)
        panel = pygame.Rect(0, 0, min(surface.get_width() - 32, 340), 120)
        panel.center = (board.center if board.height >= 140 else
                        (surface.get_width() // 2, BOARD_TOP + 70))
        panel.clamp_ip(surface.get_rect().inflate(-16, -16))
        shadow = pygame.Surface((panel.width + 12, panel.height + 14), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (18, 26, 14, 70), shadow.get_rect(), border_radius=15)
        surface.blit(shadow, (panel.x - 6, panel.y + 3))
        pygame.draw.rect(surface, BACKGROUND, panel, border_radius=12)
        pygame.draw.rect(surface, (185, 174, 146), panel, 1, border_radius=12)
        accent = (155, 109, 72) if state.status is GameStatus.GAME_OVER else (112, 133, 78)
        pygame.draw.line(surface, accent, (panel.centerx - 21, panel.top + 12),
                         (panel.centerx + 21, panel.top + 12), 3)
        for index, text in enumerate(lines):
            font = self.overlay_font if index == 0 else self.text_font
            rendered = font.render(text, True, TEXT_COLOR)
            rect = rendered.get_rect(center=(panel.centerx, panel.top + 36 + index * 43))
            surface.blit(rendered, rect)

    def draw(self, surface: pygame.Surface, state: GameState) -> None:
        surface.fill(BACKGROUND)
        self._text(surface, "SNAKE", self.heading_font, (MARGIN, 22))
        self._text(surface, f"Score: {state.score}", self.text_font, (MARGIN, 60))
        subtitle = self.small_font.render("IN THE UNDERGROWTH", True, MUTED_COLOR)
        surface.blit(subtitle, (surface.get_width() - subtitle.get_width() - MARGIN, 29))
        pygame.draw.line(surface, (191, 183, 159), (surface.get_width() - 116, 59),
                         (surface.get_width() - MARGIN, 59))
        self._text(surface, "WOODLAND", self.small_font,
                   (surface.get_width() - 96, 68), MUTED_COLOR)
        board = pygame.Rect(MARGIN, BOARD_TOP, state.width * CELL_SIZE, state.height * CELL_SIZE)
        surface.blit(self._ground(board.size), board)
        previous_clip = surface.get_clip()
        surface.set_clip(board.clip(previous_clip))
        try:
            self._snake(surface, state)
            if state.food is not None:
                self._apple(surface, state.food)
        finally:
            surface.set_clip(previous_clip)
        footer_top = BOARD_TOP + max(140, board.height)
        self._text(surface, "Arrows  Move    Space  Pause / resume", self.text_font,
                   (MARGIN, footer_top + 14), MUTED_COLOR)
        self._text(surface, "R  Restart    Esc  Exit", self.text_font,
                   (MARGIN, footer_top + 38), MUTED_COLOR)
        self._overlay(surface, board, state)
