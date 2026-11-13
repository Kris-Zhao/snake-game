from random import Random

from snake_game.core import Direction, GameStatus, new_game


def test_default_state():
    state = new_game(Random(7))
    assert (state.width, state.height) == (20, 20)
    assert len(state.snake) == len(set(state.snake)) == 3
    assert all(0 <= x < 20 and 0 <= y < 20 for x, y in state.snake)
    assert state.snake[0] == (10, 10)
    assert all(
        abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
        for a, b in zip(state.snake, state.snake[1:])
    )
    assert state.snake[1] == (state.snake[0][0] - 1, state.snake[0][1])
    assert state.direction is Direction.RIGHT
    assert state.pending_direction is None
    assert state.status is GameStatus.RUNNING
    assert state.score == 0
    assert state.food not in state.snake
    assert state.food is not None
    assert 0 <= state.food[0] < 20 and 0 <= state.food[1] < 20


def test_seeded_initialization_is_reproducible():
    assert new_game(Random(43)) == new_game(Random(43))


def test_food_choice_receives_all_and_only_free_cells():
    class RecordingRandom(Random):
        def choice(self, cells):
            self.cells = cells
            return cells[-1]

    rng = RecordingRandom(0)
    state = new_game(rng)
    assert rng.cells == [
        (x, y) for y in range(20) for x in range(20)
        if (x, y) not in state.snake
    ]
    assert len(rng.cells) == 397
    assert state.food == (19, 19)
