from dataclasses import replace
from random import Random

import pytest

from snake_game.core import GameStatus, new_game
from snake_game.rendering.view import (
    GameView, window_size, CELL_SIZE, MARGIN, BOARD_TOP,
    HEAD_COLOR, BODY_COLOR, FOOD_COLOR,
)


@pytest.mark.parametrize("status,message", [
    (GameStatus.RUNNING, None), (GameStatus.PAUSED, "Paused"),
    (GameStatus.GAME_OVER, "Game over"), (GameStatus.WON, "You won!"),
])
def test_view_draws_actual_score_status_and_controls_without_changing_state(pygame_ready, status, message):
    pygame = pygame_ready
    state = replace(new_game(Random(3)), status=status, score=120,
                    food=None if status is GameStatus.WON else (0, 0))
    original = state
    surface = pygame.display.set_mode(window_size(state))
    view = GameView()
    rendered_text = []

    class RecordingFont:
        def __init__(self, wrapped):
            self.wrapped = wrapped

        def render(self, text, *args):
            rendered_text.append(text)
            return self.wrapped.render(text, *args)

    for name in ("heading_font", "text_font", "overlay_font"):
        setattr(view, name, RecordingFont(getattr(view, name)))
    view.draw(surface, state)
    assert surface.get_size() == (600, 724)
    assert "Score: 120" in rendered_text
    assert any("Arrows" in text for text in rendered_text)
    assert any("Esc" in text for text in rendered_text)
    if message:
        assert message in rendered_text
        assert ("Space to resume" if status is GameStatus.PAUSED else "R to restart") in rendered_text
    else:
        assert not set(rendered_text) & {"Paused", "Game over", "You won!"}
    assert state == original


def test_snake_and_food_are_visually_distinguishable(pygame_ready):
    pygame = pygame_ready
    state = replace(new_game(Random(3)), food=(0, 0))
    surface = pygame.Surface(window_size(state))
    GameView().draw(surface, state)

    def cell_colors(cell):
        x, y = cell
        return {tuple(surface.get_at((MARGIN + x * CELL_SIZE + dx,
                                      BOARD_TOP + y * CELL_SIZE + dy)))[:3]
                for dx in range(4, 24) for dy in range(4, 24)}

    head = cell_colors(state.snake[0])
    body = cell_colors(state.snake[1])
    apple = cell_colors(state.food)
    assert HEAD_COLOR in head
    assert BODY_COLOR in body
    assert FOOD_COLOR in apple
    assert len(head) > 4 and len(body) >= 4 and len(apple) > 4
    assert not apple & {HEAD_COLOR, BODY_COLOR}
    assert any(r > 1.5 * g for r, g, b in apple)
    assert not any(r > 1.5 * g for r, g, b in body)
