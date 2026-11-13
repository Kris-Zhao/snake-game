import pytest

from snake_game.core import Direction, GameState, GameStatus, tick


class NoRandom:
    def choice(self, cells):
        raise AssertionError("Collision or terminal tick must not select food")


@pytest.mark.parametrize(
    "direction,snake",
    [
        (Direction.LEFT, ((0, 2), (1, 2), (2, 2))),
        (Direction.RIGHT, ((4, 2), (3, 2), (2, 2))),
        (Direction.UP, ((2, 0), (2, 1), (2, 2))),
        (Direction.DOWN, ((2, 4), (2, 3), (2, 2))),
    ],
)
def test_solid_walls_end_game_and_preserve_last_valid_state(direction, snake):
    state = GameState(5, 5, snake, direction, None, (0, 0), 40, GameStatus.RUNNING)
    result = tick(state, NoRandom())
    assert result.status is GameStatus.GAME_OVER
    assert result.snake == snake
    assert result.food == state.food
    assert result.score == 40
    assert tick(result, NoRandom()) == result


def test_queued_turn_into_body_ends_game_and_clears_pending():
    state = GameState(
        5, 5, ((2, 2), (2, 3), (1, 3), (1, 2), (1, 1)),
        Direction.UP, Direction.LEFT, (4, 4), 10, GameStatus.RUNNING,
    )
    result = tick(state, NoRandom())
    assert result.status is GameStatus.GAME_OVER
    assert result.snake == state.snake
    assert result.food == state.food
    assert result.score == 10
    assert result.direction is Direction.LEFT
    assert result.pending_direction is None


def test_entering_vacating_tail_is_legal():
    state = GameState(
        4, 4, ((2, 1), (2, 2), (1, 2), (1, 1)),
        Direction.UP, Direction.LEFT, (3, 3), 10, GameStatus.RUNNING,
    )
    result = tick(state, NoRandom())
    assert result.snake == ((1, 1), (2, 1), (2, 2), (1, 2))
    assert result.status is GameStatus.RUNNING
    assert result.score == state.score
    assert result.food == state.food


@pytest.mark.parametrize("status", [GameStatus.PAUSED, GameStatus.GAME_OVER, GameStatus.WON])
def test_inactive_ticks_are_inert(status):
    state = GameState(
        5, 5, ((2, 1), (1, 1), (0, 1)), Direction.RIGHT, None,
        (3, 1), 20, status,
    )
    assert tick(state, NoRandom()) is state
