import pygame

from circleshape import CircleShape
from constants import SHOT_LIFETIME, SHOT_RADIUS


class Shot(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, SHOT_RADIUS)
        self.age = 0.0

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, "white", self.position, self.radius)

    def update(self, dt: float) -> None:
        self.age += dt
        if self.age >= SHOT_LIFETIME:
            self.kill()
            return

        self.position += self.velocity * dt
        self.wrap_position()
