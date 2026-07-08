import random

import pygame

from constants import (
    PLAYER_MAX_BOMBS,
    POWERUP_KIND_WEIGHTS,
    POWERUP_MAX_ON_SCREEN,
    POWERUP_SPAWN_INTERVAL_SECONDS,
    POWERUP_SPAWN_MARGIN,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from powerup import PowerUp


class PowerUpField(pygame.sprite.Sprite):
    containers: pygame.sprite.Group

    def __init__(self, powerups: pygame.sprite.Group, player) -> None:
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.powerups = powerups
        self.player = player
        self.spawn_timer = 0.0

    def choose_powerup_kind(self) -> str:
        kinds = ["shield", "speed"]
        weights = [
            POWERUP_KIND_WEIGHTS["shield"],
            POWERUP_KIND_WEIGHTS["speed"],
        ]

        if self.player.bombs_remaining < PLAYER_MAX_BOMBS:
            kinds.append("bomb")
            weights.append(POWERUP_KIND_WEIGHTS["bomb"])

        return random.choices(kinds, weights=weights, k=1)[0]

    def update(self, dt: float) -> None:
        self.spawn_timer += dt
        if self.spawn_timer < POWERUP_SPAWN_INTERVAL_SECONDS:
            return

        self.spawn_timer = 0

        if len(self.powerups) >= POWERUP_MAX_ON_SCREEN:
            return

        kind = self.choose_powerup_kind()
        x = random.uniform(POWERUP_SPAWN_MARGIN, SCREEN_WIDTH - POWERUP_SPAWN_MARGIN)
        y = random.uniform(POWERUP_SPAWN_MARGIN, SCREEN_HEIGHT - POWERUP_SPAWN_MARGIN)
        PowerUp(x, y, kind)
