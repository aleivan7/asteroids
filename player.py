import pygame

from circleshape import CircleShape
from constants import (
    LINE_WIDTH,
    PLAYER_ACCELERATION,
    PLAYER_BRAKE_STRENGTH,
    PLAYER_DRAG,
    PLAYER_MAX_SPEED,
    PLAYER_RADIUS,
    PLAYER_RESPAWN_INVULNERABLE_SECONDS,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_SHOT_SPEED,
    PLAYER_STOP_EPSILON,
    PLAYER_TURN_SPEED,
)
from shot import Shot


class Player(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, PLAYER_RADIUS)
        self.cool_down_timer = 0
        self.invulnerable_timer = 0.0
        self.rotation = 0

    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen: pygame.Surface) -> None:
        if self.is_invulnerable() and int(self.invulnerable_timer * 10) % 2 == 0:
            return

        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

    def rotate(self, dt: float):
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt: float) -> None:
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        keys = pygame.key.get_pressed()

        self.cool_down_timer -= dt

        if keys[pygame.K_a]:
            self.rotate(dt * -1)
        if keys[pygame.K_d]:
            self.rotate(dt)
        is_thrusting = keys[pygame.K_w]
        is_braking = keys[pygame.K_s]

        if is_thrusting:
            self.thrust(dt)
        if is_braking:
            self.brake(dt)
        if keys[pygame.K_SPACE]:
            self.shoot()

        self.apply_drag(dt)
        self.limit_speed()
        if not is_thrusting and not is_braking:
            self.stop_if_slow()
        self.position += self.velocity * dt
        self.wrap_position()

    def thrust(self, dt: float) -> None:
        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        self.velocity += direction * PLAYER_ACCELERATION * dt

    def brake(self, dt: float) -> None:
        self.slow_down(PLAYER_BRAKE_STRENGTH, dt)

    def apply_drag(self, dt: float) -> None:
        self.slow_down(PLAYER_DRAG, dt)

    def slow_down(self, amount_per_second: float, dt: float) -> None:
        speed = self.velocity.length()
        if speed == 0:
            return

        new_speed = max(0, speed - amount_per_second * dt)
        if new_speed == 0:
            self.velocity = pygame.Vector2(0, 0)
            return

        self.velocity.scale_to_length(new_speed)

    def limit_speed(self) -> None:
        if self.velocity.length() > PLAYER_MAX_SPEED:
            self.velocity.scale_to_length(PLAYER_MAX_SPEED)

    def stop_if_slow(self) -> None:
        if self.velocity.length() < PLAYER_STOP_EPSILON:
            self.velocity = pygame.Vector2(0, 0)

    def shoot(self) -> None:
        if self.cool_down_timer > 0:
            return

        self.cool_down_timer = PLAYER_SHOOT_COOLDOWN_SECONDS

        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOT_SPEED

    def is_vulnerable(self) -> bool:
        return self.invulnerable_timer <= 0

    def is_invulnerable(self) -> bool:
        return self.invulnerable_timer > 0

    def respawn(self, x: float, y: float) -> None:
        self.position = pygame.Vector2(x, y)
        self.rotation = 0
        self.velocity = pygame.Vector2(0, 0)
        self.invulnerable_timer = PLAYER_RESPAWN_INVULNERABLE_SECONDS

    def reset_to_start(self, x: float, y: float) -> None:
        self.position = pygame.Vector2(x, y)
        self.rotation = 0
        self.velocity = pygame.Vector2(0, 0)
        self.cool_down_timer = 0
        self.invulnerable_timer = 0.0
