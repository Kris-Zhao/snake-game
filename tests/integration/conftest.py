import pytest


@pytest.fixture
def pygame_ready(monkeypatch):
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    import pygame
    pygame.init()
    yield pygame
    pygame.quit()
