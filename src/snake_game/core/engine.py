"""Game commands driven by explicit ticks and supplied randomness."""

from dataclasses import replace
from random import Random

from .model import Cell, Direction, GameState, GameStatus


def _choose_food(
    width: int, height: int, snake: tuple[Cell, ...], rng: Random,
) -> Cell | None:
    occupied = set(snake)
    free_cells = [
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in occupied
    ]
    return rng.choice(free_cells) if free_cells else None


def new_game(rng: Random) -> GameState:
    """Create the default board, selecting food uniformly from free cells."""
    width = height = 20
    head_x, head_y = width // 2, height // 2
    snake = tuple((head_x - offset, head_y) for offset in range(3))
    return GameState(
        width=width,
        height=height,
        snake=snake,
        direction=Direction.RIGHT,
        pending_direction=None,
        food=_choose_food(width, height, snake, rng),
        score=0,
        status=GameStatus.RUNNING,
    )


def request_direction(state: GameState, direction: Direction) -> GameState:
    """Queue the first perpendicular turn without advancing the simulation."""
    if (
        state.status is not GameStatus.RUNNING
        or state.pending_direction is not None
        or direction is state.direction
    ):
        return state
    dx, dy = state.direction.delta
    if direction.delta == (-dx, -dy):
        return state
    return replace(state, pending_direction=direction)


def toggle_pause(state: GameState) -> GameState:
    """Toggle running/paused without moving or disturbing an accepted turn."""
    if state.status is GameStatus.RUNNING:
        return replace(state, status=GameStatus.PAUSED)
    if state.status is GameStatus.PAUSED:
        return replace(state, status=GameStatus.RUNNING)
    return state


def restart(state: GameState, rng: Random) -> GameState:
    """Start a default game from any state, continuing the supplied RNG stream."""
    return new_game(rng)


def tick(state: GameState, rng: Random) -> GameState:
    """Advance one running tick, resolving growth, collisions, and victory."""
    if state.status is not GameStatus.RUNNING:
        return state
    direction = state.pending_direction or state.direction
    dx, dy = direction.delta
    head_x, head_y = state.snake[0]
    head = (head_x + dx, head_y + dy)
    growing = head == state.food
    occupied = state.snake if growing else state.snake[:-1]
    if (
        not (0 <= head[0] < state.width and 0 <= head[1] < state.height)
        or head in occupied
    ):
        return replace(
            state,
            status=GameStatus.GAME_OVER,
            direction=direction,
            pending_direction=None,
        )
    snake = (head,) + (state.snake if growing else state.snake[:-1])
    food = _choose_food(state.width, state.height, snake, rng) if growing else state.food
    won = len(snake) == state.width * state.height
    return replace(
        state,
        snake=snake,
        direction=direction,
        pending_direction=None,
        food=None if won else food,
        score=state.score + (10 if growing else 0),
        status=GameStatus.WON if won else GameStatus.RUNNING,
    )
