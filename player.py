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
    PLAYER_MAX_BOMBS,
    PLAYER_STARTING_BOMBS,
    PLAYER_STOP_EPSILON,
    PLAYER_TURN_SPEED,
    SHIELD_DRAW_RADIUS,
    SPEED_BOOST_DURATION_SECONDS,
    SPEED_BOOST_MULTIPLIER,
)
from shot import Shot


class Player(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, PLAYER_RADIUS)
        self.cool_down_timer = 0
        self.invulnerable_timer = 0.0
        self.rotation = 0
        self.shield_active = False
        self.speed_timer = 0.0
        self.bombs_remaining = PLAYER_STARTING_BOMBS
        self.combat_locked = False

    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen: pygame.Surface) -> None:
        if not (self.is_invulnerable() and int(self.invulnerable_timer * 10) % 2 == 0):
            pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

        if self.shield_active:
            pygame.draw.circle(
                screen, "white", self.position, SHIELD_DRAW_RADIUS, LINE_WIDTH
            )

    def rotate(self, dt: float):
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt: float) -> None:
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        if self.speed_timer > 0:
            self.speed_timer = max(0.0, self.speed_timer - dt)

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

    def current_acceleration(self) -> float:
        if self.speed_timer > 0:
            return PLAYER_ACCELERATION * SPEED_BOOST_MULTIPLIER
        return PLAYER_ACCELERATION

    def current_max_speed(self) -> float:
        if self.speed_timer > 0:
            return PLAYER_MAX_SPEED * SPEED_BOOST_MULTIPLIER
        return PLAYER_MAX_SPEED

    def thrust(self, dt: float) -> None:
        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        self.velocity += direction * self.current_acceleration() * dt

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
        max_speed = self.current_max_speed()
        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)

    def stop_if_slow(self) -> None:
        if self.velocity.length() < PLAYER_STOP_EPSILON:
            self.velocity = pygame.Vector2(0, 0)

    def shoot(self) -> None:
        if self.combat_locked or self.cool_down_timer > 0:
            return

        self.cool_down_timer = PLAYER_SHOOT_COOLDOWN_SECONDS

        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOT_SPEED

    def try_use_bomb(self) -> bool:
        if self.bombs_remaining <= 0:
            return False

        self.bombs_remaining -= 1
        return True

    def apply_shield(self) -> None:
        self.shield_active = True

    def apply_speed(self) -> None:
        self.speed_timer = SPEED_BOOST_DURATION_SECONDS

    def apply_bomb(self) -> None:
        self.bombs_remaining = min(PLAYER_MAX_BOMBS, self.bombs_remaining + 1)

    def clear_temporary_effects(self) -> None:
        self.shield_active = False
        self.speed_timer = 0.0

    def is_vulnerable(self) -> bool:
        return self.invulnerable_timer <= 0

    def is_invulnerable(self) -> bool:
        return self.invulnerable_timer > 0

    def respawn(self, x: float, y: float) -> None:
        self.position = pygame.Vector2(x, y)
        self.rotation = 0
        self.velocity = pygame.Vector2(0, 0)
        self.invulnerable_timer = PLAYER_RESPAWN_INVULNERABLE_SECONDS
        self.clear_temporary_effects()

    def reposition_for_level_up(
        self, x: float, y: float, invulnerable_seconds: float
    ) -> None:
        self.position = pygame.Vector2(x, y)
        self.rotation = 0
        self.velocity = pygame.Vector2(0, 0)
        self.invulnerable_timer = invulnerable_seconds

    def reset_to_start(self, x: float, y: float) -> None:
        self.position = pygame.Vector2(x, y)
        self.rotation = 0
        self.velocity = pygame.Vector2(0, 0)
        self.cool_down_timer = 0
        self.invulnerable_timer = 0.0
        self.bombs_remaining = PLAYER_STARTING_BOMBS
        self.clear_temporary_effects()
