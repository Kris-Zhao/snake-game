from dataclasses import replace
from random import Random
import random

import pytest

from snake_game.core import Direction, GameStatus, new_game
from snake_game.rendering import view


def pixels(pygame, surface):
    return pygame.image.tobytes(surface, "RGB")


def test_woodland_terrain_is_textured_and_drawing_is_repeatable(pygame_ready):
    pygame = pygame_ready
    state = replace(new_game(Random(2)), snake=(), food=None)
    before_random = random.getstate()
    renderer = view.GameView()
    surface = pygame.Surface(view.window_size(state))
    renderer.draw(surface, state)
    first = pixels(pygame, surface)
    colors = {tuple(surface.get_at((view.MARGIN + x, view.BOARD_TOP + y)))
              for x in range(5, 150, 3) for y in range(5, 150, 3)}
    assert len(colors) > 20
    assert surface.get_at((0, 0)).r > 180  # warm, light interface
    renderer.draw(surface, state)
    assert pixels(pygame, surface) == first
    assert random.getstate() == before_random


def test_adjacent_body_cells_are_connected_but_disjoint_cells_are_not(pygame_ready):
    pygame = pygame_ready
    renderer = view.GameView()
    base = replace(new_game(Random(2)), snake=(), food=None)
    ground = pygame.Surface(view.window_size(base))
    renderer.draw(ground, base)
    connected = ground.copy()
    renderer.draw(connected, replace(base, snake=((8, 8), (7, 8), (6, 8))))
    seam = (view.MARGIN + 8 * view.CELL_SIZE, view.BOARD_TOP + 8 * view.CELL_SIZE + 14)
    assert connected.get_at(seam) != ground.get_at(seam)
    disjoint = ground.copy()
    renderer.draw(disjoint, replace(base, snake=((8, 8), (4, 8))))
    middle = (view.MARGIN + 6 * view.CELL_SIZE + 14, seam[1])
    assert disjoint.get_at(middle) == ground.get_at(middle)


def test_head_appearance_follows_current_direction_not_pending(pygame_ready):
    pygame = pygame_ready
    renderer = view.GameView()
    base = replace(new_game(Random(2)), snake=((8, 8),), food=None)
    results = []
    for direction in Direction:
        surface = pygame.Surface(view.window_size(base))
        renderer.draw(surface, replace(base, direction=direction))
        results.append(pixels(pygame, surface))
    assert len(set(results)) == 4
    a = pygame.Surface(view.window_size(base))
    b = a.copy()
    renderer.draw(a, base)
    renderer.draw(b, replace(base, pending_direction=Direction.UP))
    assert pixels(pygame, a) == pixels(pygame, b)


@pytest.mark.parametrize("status", list(GameStatus))
def test_small_rectangular_state_has_room_for_interface(pygame_ready, status):
    state = replace(new_game(Random(2)), width=4, height=3,
                    snake=((2, 1), (1, 1), (0, 1)), food=(3, 2), status=status)
    surface = pygame_ready.Surface(view.window_size(state))
    view.GameView().draw(surface, state)
