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

    def collides_with_circle(self, shape: CircleShape) -> bool:
        triangle = self.triangle()
        if self.point_is_inside_triangle(shape.position, triangle):
            return True

        return (
            self.circle_touches_segment(
                shape.position, shape.radius, triangle[0], triangle[1]
            )
            or self.circle_touches_segment(
                shape.position, shape.radius, triangle[1], triangle[2]
            )
            or self.circle_touches_segment(
                shape.position, shape.radius, triangle[2], triangle[0]
            )
        )

    def point_is_inside_triangle(
        self, point: pygame.Vector2, triangle: list[pygame.Vector2]
    ) -> bool:
        a, b, c = triangle
        d1 = self.triangle_sign(point, a, b)
        d2 = self.triangle_sign(point, b, c)
        d3 = self.triangle_sign(point, c, a)

        has_negative = d1 < 0 or d2 < 0 or d3 < 0
        has_positive = d1 > 0 or d2 > 0 or d3 > 0
        return not (has_negative and has_positive)

    def triangle_sign(
        self, point: pygame.Vector2, start: pygame.Vector2, end: pygame.Vector2
    ) -> float:
        return (point.x - end.x) * (start.y - end.y) - (
            start.x - end.x
        ) * (point.y - end.y)

    def circle_touches_segment(
        self,
        circle_center: pygame.Vector2,
        circle_radius: float,
        segment_start: pygame.Vector2,
        segment_end: pygame.Vector2,
    ) -> bool:
        segment = segment_end - segment_start
        segment_length_squared = segment.length_squared()
        if segment_length_squared == 0:
            distance_squared = circle_center.distance_squared_to(segment_start)
            return distance_squared <= circle_radius**2

        # Clamp the projection so the closest point stays on this triangle edge.
        t = (circle_center - segment_start).dot(segment) / segment_length_squared
        t = max(0, min(1, t))
        closest_point = segment_start + segment * t
        return circle_center.distance_squared_to(closest_point) <= circle_radius**2

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
