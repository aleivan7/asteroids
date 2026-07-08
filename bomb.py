import pygame

from circleshape import CircleShape
from constants import (
    BOMB_BODY_RADIUS,
    BOMB_EFFECT_DURATION_SECONDS,
    BOMB_RADIUS,
    LINE_WIDTH,
)


class Bomb(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, BOMB_BODY_RADIUS)
        self.effect_timer = 0.0
        self.detonated = False

    def draw(self, screen: pygame.Surface) -> None:
        if self.detonated:
            pygame.draw.circle(
                screen,
                "white",
                self.position,
                BOMB_RADIUS,
                LINE_WIDTH,
            )
            return

        pygame.draw.circle(
            screen,
            "white",
            self.position,
            self.radius,
            LINE_WIDTH,
        )
        cross_size = self.radius * 0.6
        pygame.draw.line(
            screen,
            "white",
            self.position + pygame.Vector2(-cross_size, 0),
            self.position + pygame.Vector2(cross_size, 0),
            LINE_WIDTH,
        )
        pygame.draw.line(
            screen,
            "white",
            self.position + pygame.Vector2(0, -cross_size),
            self.position + pygame.Vector2(0, cross_size),
            LINE_WIDTH,
        )

    def update(self, dt: float) -> None:
        if not self.detonated:
            return

        self.effect_timer = max(0.0, self.effect_timer - dt)
        if self.effect_timer <= 0:
            self.kill()

    def detonate(self) -> None:
        if self.detonated:
            return

        self.detonated = True
        self.effect_timer = BOMB_EFFECT_DURATION_SECONDS
