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

    def pixel(cell):
        x, y = cell
        return tuple(surface.get_at((MARGIN + x * CELL_SIZE + CELL_SIZE // 2,
                                     BOARD_TOP + y * CELL_SIZE + CELL_SIZE // 2)))[:3]

    assert pixel(state.snake[0]) == HEAD_COLOR
    assert pixel(state.snake[1]) == BODY_COLOR
    assert pixel(state.food) == FOOD_COLOR
    assert len({HEAD_COLOR, BODY_COLOR, FOOD_COLOR}) == 3
