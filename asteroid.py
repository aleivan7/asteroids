import random

import pygame

from circleshape import CircleShape
from constants import (
    ASTEROID_MAX_RADIUS,
    ASTEROID_MIN_RADIUS,
    ASTEROID_LUMPINESS,
    ASTEROID_NUM_VERTICES,
    LINE_WIDTH,
    SCORE_LARGE_ASTEROID,
    SCORE_MEDIUM_ASTEROID,
    SCORE_SMALL_ASTEROID,
)
from logger import log_event


class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)
        self.outline_points = self.make_outline_points()

    def draw(self, screen: pygame.Surface) -> None:
        points = [self.position + point for point in self.outline_points]
        pygame.draw.polygon(screen, "white", points, LINE_WIDTH)

    def make_outline_points(self) -> list[pygame.Vector2]:
        points = []
        angle_step = 360 / ASTEROID_NUM_VERTICES

        for i in range(ASTEROID_NUM_VERTICES):
            angle = angle_step * i
            radius = self.radius * random.uniform(
                1 - ASTEROID_LUMPINESS, 1 + ASTEROID_LUMPINESS
            )
            points.append(pygame.Vector2(0, -radius).rotate(angle))

        return points

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.wrap_position()

    def points(self) -> int:
        if self.radius >= ASTEROID_MAX_RADIUS:
            return SCORE_LARGE_ASTEROID
        if self.radius >= ASTEROID_MIN_RADIUS * 2:
            return SCORE_MEDIUM_ASTEROID
        return SCORE_SMALL_ASTEROID

    def split(self) -> None:
        self.kill()

        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        log_event("asteroid_split")

        angle = random.uniform(20, 50)
        velocity_1 = self.velocity.rotate(angle)
        velocity_2 = self.velocity.rotate(-angle)

        new_angle = self.radius - ASTEROID_MIN_RADIUS

        asteroid_1 = Asteroid(self.position.x, self.position.y, new_angle)
        asteroid_2 = Asteroid(self.position.x, self.position.y, new_angle)

        asteroid_1.velocity = velocity_1 * 1.2
        asteroid_2.velocity = velocity_2 * 1.2
