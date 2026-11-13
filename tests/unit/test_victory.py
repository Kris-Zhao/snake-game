from snake_game.core import Direction, GameState, GameStatus, tick


def test_final_food_wins_without_random_selection():
    class NoRandom:
        def choice(self, cells):
            raise AssertionError("Full board must not request food")

    state = GameState(
        2, 2, ((1, 0), (0, 0), (0, 1)), Direction.RIGHT, Direction.DOWN,
        (1, 1), 10, GameStatus.RUNNING,
    )
    result = tick(state, NoRandom())
    assert result.snake == ((1, 1),) + state.snake
    assert result.status is GameStatus.WON
    assert result.score == 20
    assert result.food is None
    assert result.direction is Direction.DOWN
    assert result.pending_direction is None
    assert tick(result, NoRandom()) is result


def test_only_free_cell_is_selected_after_growth():
    class OneChoice:
        calls = 0

        def choice(self, cells):
            self.calls += 1
            assert cells == [(2, 1)]
            return cells[0]

    state = GameState(
        3, 2, ((1, 0), (0, 0), (0, 1), (1, 1)), Direction.UP, Direction.RIGHT,
        (2, 0), 30, GameStatus.RUNNING,
    )
    rng = OneChoice()
    result = tick(state, rng)
    assert result.food == (2, 1)
    assert len(result.snake) == 5
    assert result.score == 40
    assert result.status is GameStatus.RUNNING
    assert rng.calls == 1
