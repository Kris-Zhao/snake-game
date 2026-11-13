from dataclasses import replace
from random import Random, getstate

from snake_game.core import Direction, GameState, GameStatus, tick


def eating_state():
    return GameState(
        width=5, height=3, snake=((2, 1), (1, 1), (0, 1)),
        direction=Direction.RIGHT, pending_direction=None,
        food=(3, 1), score=20, status=GameStatus.RUNNING,
    )


def test_eating_grows_one_cell_adds_ten_and_selects_all_free_cells_once():
    class Recorder:
        calls = 0

        def choice(self, cells):
            self.calls += 1
            self.cells = cells
            return cells[-1]

    rng = Recorder()
    state = eating_state()
    original_random = getstate()
    result = tick(state, rng)
    assert result.snake == ((3, 1),) + state.snake
    assert result.score == 30
    assert result.status is GameStatus.RUNNING
    assert result.food == (4, 2)
    assert rng.calls == 1
    assert rng.cells == [
        (x, y) for y in range(3) for x in range(5)
        if (x, y) not in result.snake
    ]
    assert state == eating_state()
    assert getstate() == original_random


def test_growth_is_reproducible_with_seeded_randomness():
    assert tick(eating_state(), Random(32)) == tick(eating_state(), Random(32))


def test_ordinary_tick_preserves_food_and_does_not_use_randomness():
    class NoRandom:
        def choice(self, cells):
            raise AssertionError("No food selection during ordinary movement")

    state = replace(eating_state(), food=(4, 2))
    result = tick(state, NoRandom())
    assert result.snake == ((3, 1), (2, 1), (1, 1))
    assert result.food == state.food
    assert result.score == state.score
