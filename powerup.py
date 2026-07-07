import pygame

from circleshape import CircleShape
from constants import LINE_WIDTH, POWERUP_LIFETIME_SECONDS, POWERUP_RADIUS


class PowerUp(CircleShape):
    def __init__(self, x: float, y: float, kind: str) -> None:
        super().__init__(x, y, POWERUP_RADIUS)
        self.kind = kind
        self.lifetime = POWERUP_LIFETIME_SECONDS

    def update(self, dt: float) -> None:
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, screen: pygame.Surface) -> None:
        if self.kind == "shield":
            pygame.draw.circle(
                screen, "white", self.position, self.radius, LINE_WIDTH
            )
        elif self.kind == "speed":
            points = [
                self.position + pygame.Vector2(0, -self.radius),
                self.position + pygame.Vector2(-self.radius * 0.7, self.radius * 0.5),
                self.position + pygame.Vector2(self.radius * 0.7, self.radius * 0.5),
            ]
            pygame.draw.polygon(screen, "white", points, LINE_WIDTH)
