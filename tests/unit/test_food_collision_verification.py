"""Independent acceptance checks for Feature 02, using valid compact boards."""

from dataclasses import asdict
from itertools import permutations
from random import getstate

import pytest

from snake_game.core import Direction, GameState, GameStatus, request_direction, tick


DELTAS = {
    Direction.UP: (0, -1),
    Direction.DOWN: (0, 1),
    Direction.LEFT: (-1, 0),
    Direction.RIGHT: (1, 0),
}


class RecordingSelector:
    def __init__(self):
        self.calls = []

    def choice(self, cells):
        self.calls.append(tuple(cells))
        assert cells, "Never select from a full board"
        return cells[0]


@pytest.mark.parametrize("length", [3, 4, 5])
def test_every_contiguous_small_board_state_obeys_tick_contract(length):
    """Enumerate geometry independently; check outcomes and invariants together."""
    board = {(x, y) for x in range(3) for y in range(2)}
    outcomes = set()
    global_before = getstate()
    for snake in permutations(sorted(board), length):
        if any(abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1
               for a, b in zip(snake, snake[1:])):
            continue
        heading = (snake[0][0] - snake[1][0], snake[0][1] - snake[1][1])
        direction = next(d for d, delta in DELTAS.items() if delta == heading)
        for turn, (dx, dy) in DELTAS.items():
            if (dx, dy) == (-heading[0], -heading[1]):
                continue
            for food in sorted(board - set(snake)):
                initial = GameState(3, 2, snake, direction, None, food, 70,
                                    GameStatus.RUNNING)
                snapshot = asdict(initial)
                queued = request_direction(initial, turn)
                selector = RecordingSelector()
                result = tick(queued, selector)
                context = (snake, turn, food)
                target = (snake[0][0] + dx, snake[0][1] + dy)
                eating = target == food
                # Tail is a legal target because food cannot occupy the snake.
                collision = target not in board or target in set(snake[:-1])
                assert result.direction is turn, context
                assert result.pending_direction is None, context
                assert (result.width, result.height) == (3, 2), context
                assert asdict(initial) == snapshot, context
                if collision:
                    outcomes.add("collision")
                    assert result.status is GameStatus.GAME_OVER, context
                    assert result.snake == snake, context
                    assert (result.score, result.food) == (70, food), context
                    assert selector.calls == [], context
                    assert tick(result, selector) is result, context
                    continue
                outcomes.add("growth" if eating else "ordinary")
                assert result.snake[0] == target, context
                assert result.snake[1:] == (snake if eating else snake[:-1]), context
                assert len(result.snake) == len(set(result.snake)), context
                assert set(result.snake) <= board, context
                assert result.score == 70 + (10 if eating else 0), context
                free = board - set(result.snake)
                if not free:
                    outcomes.add("victory")
                    assert result.status is GameStatus.WON, context
                    assert result.food is None, context
                    assert selector.calls == [], context
                    assert tick(result, selector) is result, context
                else:
                    assert result.status is GameStatus.RUNNING, context
                    if eating:
                        assert len(selector.calls) == 1, context
                        candidates = selector.calls[0]
                        assert len(candidates) == len(set(candidates)) == len(free), context
                        assert set(candidates) == free, context
                        assert result.food in free, context
                    else:
                        assert selector.calls == [], context
                        assert result.food == food, context
    assert {"collision", "growth"} <= outcomes
    # On this bipartite board a five-cell snake cannot enter its own tail;
    # its sole remaining free cell is food, so every legal move grows.
    assert ("ordinary" in outcomes) == (length < 5)
    assert ("victory" in outcomes) == (length == 5)
    assert getstate() == global_before


def test_consecutive_meals_and_turns_fill_board_then_remain_inert():
    class NextFood:
        def __init__(self):
            self.targets = iter([(2, 1), (1, 1)])
            self.calls = 0

        def choice(self, cells):
            self.calls += 1
            assert self.calls <= 2, "Victory and terminal ticks need no new food"
            target = next(self.targets)
            assert target in cells
            return target

    selector = NextFood()
    initial = GameState(3, 2, ((1, 0), (0, 0), (0, 1)), Direction.RIGHT,
                        None, (2, 0), 0, GameStatus.RUNNING)
    first = tick(initial, selector)
    second = tick(request_direction(first, Direction.DOWN), selector)
    won = tick(request_direction(second, Direction.LEFT), selector)
    assert [len(state.snake) for state in (initial, first, second, won)] == [3, 4, 5, 6]
    assert [state.score for state in (initial, first, second, won)] == [0, 10, 20, 30]
    assert won.snake == ((1, 1), (2, 1), (2, 0), (1, 0), (0, 0), (0, 1))
    assert won.status is GameStatus.WON
    assert won.food is None
    assert selector.calls == 2
    for _ in range(10):
        assert tick(won, selector) is won
