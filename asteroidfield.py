import random

import pygame

from asteroid import Asteroid
from constants import *

Edge = pygame.Vector2


class AsteroidField(pygame.sprite.Sprite):
    containers: pygame.sprite.Group

    edges: list[Edge] = [
        pygame.Vector2(1, 0),
        pygame.Vector2(-1, 0),
        pygame.Vector2(0, 1),
        pygame.Vector2(0, -1),
    ]

    def __init__(self) -> None:
        pygame.sprite.Sprite.__init__(self, self.containers)
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
        self.spawn_timer += dt
        if self.spawn_timer > ASTEROID_SPAWN_RATE_SECONDS:
            self.spawn_timer = 0

            # spawn a new asteroid at a random edge
            edge = random.choice(self.edges)
            speed = random.randint(40, 100)
            velocity = edge * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            kind = random.randint(1, ASTEROID_KINDS)
            radius = ASTEROID_MIN_RADIUS * kind
            position = self.spawn_position(edge, random.uniform(0, 1), radius)
            self.spawn(radius, position, velocity)
