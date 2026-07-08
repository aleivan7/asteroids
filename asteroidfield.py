import random

import pygame

from asteroid import Asteroid
from constants import (
    ASTEROID_KINDS,
    ASTEROID_MIN_RADIUS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    asteroid_max_count_for_level,
    asteroid_spawn_rate_for_level,
    asteroid_speed_range_for_level,
)

Edge = pygame.Vector2


class AsteroidField(pygame.sprite.Sprite):
    containers: pygame.sprite.Group

    edges: list[Edge] = [
        pygame.Vector2(1, 0),
        pygame.Vector2(-1, 0),
        pygame.Vector2(0, 1),
        pygame.Vector2(0, -1),
    ]

    def __init__(self, asteroids: pygame.sprite.Group, game_state) -> None:
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.asteroids = asteroids
        self.game_state = game_state
        self.spawn_timer = 0.0

    def spawn_position(
        self, direction: Edge, ratio: float, radius: float
    ) -> pygame.Vector2:
        if direction.x > 0:
            return pygame.Vector2(-radius, ratio * SCREEN_HEIGHT)
        if direction.x < 0:
            return pygame.Vector2(SCREEN_WIDTH + radius, ratio * SCREEN_HEIGHT)
        if direction.y > 0:
            return pygame.Vector2(ratio * SCREEN_WIDTH, -radius)
        return pygame.Vector2(ratio * SCREEN_WIDTH, SCREEN_HEIGHT + radius)

    def spawn(
        self, radius: float, position: pygame.Vector2, velocity: pygame.Vector2
    ) -> None:
        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity

    def update(self, dt: float) -> None:
        if self.game_state.is_spawning_paused():
            return

        level = self.game_state.level
        if len(self.asteroids) >= asteroid_max_count_for_level(level):
            return

        self.spawn_timer += dt
        spawn_rate = asteroid_spawn_rate_for_level(level)
        if self.spawn_timer <= spawn_rate:
            return

        self.spawn_timer = 0

        edge = random.choice(self.edges)
        speed_min, speed_max = asteroid_speed_range_for_level(level)
        speed = random.randint(speed_min, speed_max)
        velocity = edge * speed
        velocity = velocity.rotate(random.randint(-30, 30))
        kind = random.randint(1, ASTEROID_KINDS)
        radius = ASTEROID_MIN_RADIUS * kind
        position = self.spawn_position(edge, random.uniform(0, 1), radius)
        self.spawn(radius, position, velocity)
