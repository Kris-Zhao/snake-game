"""Independent acceptance checks for the approved woodland presentation."""
from copy import deepcopy
from dataclasses import replace
from random import Random
import random

import pytest

from snake_game.core import Direction, GameStatus, new_game
from snake_game.rendering import view


def render(pygame, state, renderer=None):
    surface = pygame.Surface(view.window_size(state))
    (renderer or view.GameView()).draw(surface, state)
    return surface


def center(cell):
    return (view.MARGIN + cell[0] * view.CELL_SIZE + 14,
            view.BOARD_TOP + cell[1] * view.CELL_SIZE + 14)


def assert_visible_text(pygame, surface, text, font, color):
    """Find the complete text raster on the actual output, independent of position."""
    glyph = font.render(text, True, color)
    expected = pygame.Surface(glyph.get_size())
    expected.fill(view.BACKGROUND)
    expected.blit(glyph, (0, 0))
    width, height = expected.get_size()
    reference = pygame.image.tobytes(expected, "RGB")
    background_row = bytes(view.BACKGROUND) * width
    row = next(y for y in range(height)
               if reference[y * width * 3:(y + 1) * width * 3] != background_row)
    needle = reference[row * width * 3:(row + 1) * width * 3]
    actual = pygame.image.tobytes(surface, "RGB")
    stride = surface.get_width() * 3
    offset = actual.find(needle)
    while offset >= 0:
        x, y = (offset % stride) // 3, offset // stride - row
        rect = pygame.Rect(x, y, width, height)
        if offset % 3 == 0 and surface.get_rect().contains(rect):
            if pygame.image.tobytes(surface.subsurface(rect), "RGB") == reference:
                return
        offset = actual.find(needle, offset + 1)
    pytest.fail(f"Complete visible raster missing: {text!r}")


@pytest.mark.parametrize("size", [(20, 20), (4, 3), (2, 7), (7, 2)])
@pytest.mark.parametrize("status", list(GameStatus))
def test_complete_score_controls_and_feedback_visible_on_rectangles(pygame_ready, size, status):
    pygame = pygame_ready
    state = replace(new_game(Random(42)), width=size[0], height=size[1],
                    snake=((1, 1), (0, 1)), food=None, score=3970, status=status)
    renderer = view.GameView()
    surface = render(pygame, state, renderer)
    for text, font, color in [
        ("SNAKE", renderer.heading_font, view.TEXT_COLOR),
        ("Score: 3970", renderer.text_font, view.TEXT_COLOR),
        ("Arrows  Move    Space  Pause / resume", renderer.text_font, view.MUTED_COLOR),
        ("R  Restart    Esc  Exit", renderer.text_font, view.MUTED_COLOR),
    ]:
        assert_visible_text(pygame, surface, text, font, color)
    labels = {GameStatus.PAUSED: ("Paused", "Space to resume"),
              GameStatus.GAME_OVER: ("Game over", "R to restart"),
              GameStatus.WON: ("You won!", "R to restart")}
    if status in labels:
        for text, font in zip(labels[status], (renderer.overlay_font, renderer.text_font)):
            assert_visible_text(pygame, surface, text, font, view.TEXT_COLOR)
    if size == (20, 20):
        assert surface.get_size() == (600, 724)


@pytest.mark.parametrize("direction", list(Direction))
def test_eyes_face_actual_direction_with_two_separate_pupils(pygame_ready, direction):
    pygame = pygame_ready
    state = replace(new_game(Random(42)), snake=((8, 8),), food=None,
                    direction=direction, pending_direction=Direction.LEFT)
    surface = render(pygame, state)
    cx, cy = center((8, 8))
    pupils = [(x - cx, y - cy) for x in range(cx - 14, cx + 14)
              for y in range(cy - 14, cy + 14)
              if tuple(surface.get_at((x, y)))[:3] == (37, 39, 25)]
    assert len(pupils) >= 8
    dx, dy = direction.delta
    assert sum(x * dx + y * dy for x, y in pupils) / len(pupils) > 3
    transverse = [x * -dy + y * dx for x, y in pupils]
    assert min(transverse) < -4 and max(transverse) > 4


def test_bends_connect_consecutive_cells_without_bridging_touching_nonconsecutive_cells(pygame_ready, monkeypatch):
    pygame = pygame_ready
    base = replace(new_game(Random(42)), snake=(), food=None)
    ground = render(pygame, base)
    # Head and fourth segment touch vertically, but must stay disconnected.
    snake = ((5, 5), (4, 5), (4, 6), (5, 6), (6, 6), (7, 6))
    surface = render(pygame, replace(base, snake=snake))
    for a, b in zip(snake, snake[1:]):
        ax, ay = center(a)
        bx, by = center(b)
        seam = ((ax + bx) // 2, (ay + by) // 2)
        assert surface.get_at(seam) != ground.get_at(seam)
    x, y = center((5, 5))
    seam = (x, y + 14)
    # A translucent shadow may touch this seam; it is not a body connection.
    # Isolate foreground geometry by suppressing only the shadow draw color.
    for name in ("line", "circle"):
        original_draw = getattr(pygame.draw, name)
        def foreground_only(target, color, *args, _draw=original_draw, **kwargs):
            if color != (19, 25, 14, 65):
                return _draw(target, color, *args, **kwargs)
        monkeypatch.setattr(pygame.draw, name, foreground_only)
    foreground = render(pygame, replace(base, snake=snake))
    assert foreground.get_at(seam) == ground.get_at(seam)
    for a, b in zip(snake, snake[1:]):
        ax, ay = center(a)
        bx, by = center(b)
        seam = ((ax + bx) // 2, (ay + by) // 2)
        assert foreground.get_at(seam) != ground.get_at(seam)


@pytest.mark.parametrize("direction", list(Direction))
def test_tail_tapers_in_each_direction_and_entities_stay_inside_board(pygame_ready, direction):
    pygame = pygame_ready
    dx, dy = direction.delta
    tail = (0 if dx >= 0 else 19, 0 if dy >= 0 else 19)
    snake = tuple((tail[0] + dx * n, tail[1] + dy * n) for n in (2, 1, 0))
    base = replace(new_game(Random(42)), snake=(), food=None)
    ground = render(pygame, base)
    state = replace(base, snake=snake, direction=direction, food=(19, 19))
    surface = render(pygame, state)
    board = pygame.Rect(view.MARGIN, view.BOARD_TOP, 560, 560)
    # Erasing the board leaves equal HUD, footer and margins: no shadow/sprite leaks.
    a, b = surface.copy(), ground.copy()
    a.fill((0, 0, 0), board)
    b.fill((0, 0, 0), board)
    assert pygame.image.tobytes(a, "RGB") == pygame.image.tobytes(b, "RGB")
    cx, cy = center(tail)
    nx, ny = -dy, dx
    colors = {(72, 61, 37), view.BODY_COLOR, (192, 165, 108)}
    def thickness(along):
        return sum(tuple(surface.get_at((cx + dx * along + nx * side,
                                         cy + dy * along + ny * side)))[:3] in colors
                   for side in range(-12, 13))
    assert thickness(-8) < thickness(9)
    assert thickness(-8) > 0


def test_food_none_removes_only_the_apple_cell(pygame_ready):
    pygame = pygame_ready
    base = replace(new_game(Random(42)), food=None)
    without = render(pygame, base)
    for food in [(0, 0), (19, 19), (5, 8)]:
        with_apple = render(pygame, replace(base, food=food))
        cell = pygame.Rect(view.MARGIN + food[0] * 28, view.BOARD_TOP + food[1] * 28, 28, 28)
        assert pygame.image.tobytes(with_apple.subsurface(cell), "RGB") != pygame.image.tobytes(without.subsurface(cell), "RGB")
        colors = {tuple(with_apple.get_at((x, y)))[:3] for x in range(cell.left, cell.right)
                  for y in range(cell.top, cell.bottom)}
        assert view.FOOD_COLOR in colors
        with_apple.blit(without, cell, cell)
        assert pygame.image.tobytes(with_apple, "RGB") == pygame.image.tobytes(without, "RGB")


def test_cache_resize_repeatability_preserves_state_and_global_rng(pygame_ready):
    pygame = pygame_ready
    state = replace(new_game(Random(42)), pending_direction=Direction.UP, score=70)
    original = deepcopy(state)
    before_rng = random.getstate()
    renderer = view.GameView()
    first = render(pygame, state, renderer)
    render(pygame, replace(state, width=5, height=3, snake=((1, 1),), food=None), renderer)
    again = render(pygame, state, renderer)
    fresh = render(pygame, state)
    assert pygame.image.tobytes(first, "RGB") == pygame.image.tobytes(again, "RGB") == pygame.image.tobytes(fresh, "RGB")
    assert state == original
    assert random.getstate() == before_rng

