import pygame

from asteroid import Asteroid, destroy_asteroids_in_radius
from asteroidfield import AsteroidField
from constants import (
    BOMB_RADIUS,
    HUD_FONT_SIZE,
    PLAYER_RADIUS,
    POWERUP_RADIUS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHIELD_ABSORB_INVULNERABLE_SECONDS,
)
from gamestate import GameState
from logger import log_event, log_state
from player import Player
from powerup import PowerUp
from powerupfield import PowerUpField
from shot import Shot


def main():
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    clock = pygame.time.Clock()
    dt = 0.0

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = updatable
    Shot.containers = (shots, updatable, drawable)
    PowerUp.containers = (powerups, updatable, drawable)
    PowerUpField.containers = updatable

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    asteroid_field = AsteroidField()
    powerup_field = PowerUpField(powerups)

    game_state = GameState()
    font = pygame.font.Font(None, HUD_FONT_SIZE)

    def reset_game() -> None:
        game_state.reset()
        player.reset_to_start(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        for asteroid in list(asteroids):
            asteroid.kill()
        for shot in list(shots):
            shot.kill()
        for powerup in list(powerups):
            powerup.kill()

        asteroid_field.spawn_timer = 0.0
        powerup_field.spawn_timer = 0.0

    while True:
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if game_state.game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return
                if event.key == pygame.K_r:
                    reset_game()

            if (
                not game_state.game_over
                and event.type == pygame.KEYDOWN
                and event.key == pygame.K_b
            ):
                center = player.try_drop_bomb()
                if center is not None:
                    destroy_asteroids_in_radius(
                        asteroids,
                        center,
                        BOMB_RADIUS,
                        game_state.add_asteroid_score,
                    )
                    log_event("bomb_dropped")

        if not game_state.game_over:
            updatable.update(dt)

            for powerup in list(powerups):
                if player.position.distance_to(powerup.position) < (
                    PLAYER_RADIUS + POWERUP_RADIUS
                ):
                    if powerup.kind == "shield":
                        player.apply_shield()
                    elif powerup.kind == "speed":
                        player.apply_speed()
                    powerup.kill()
                    log_event("powerup_collected")

            player_hit_this_frame = False

            for asteroid in asteroids:
                if (
                    not player_hit_this_frame
                    and asteroid.collides_with_triangle(player.triangle())
                ):
                    if not player.is_vulnerable():
                        player_hit_this_frame = True
                    elif player.shield_active:
                        player.shield_active = False
                        player.invulnerable_timer = SHIELD_ABSORB_INVULNERABLE_SECONDS
                        log_event("shield_absorbed")
                        player_hit_this_frame = True
                    else:
                        log_event("player_hit")
                        game_state.lose_life()
                        if not game_state.game_over:
                            player.respawn(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                        player_hit_this_frame = True

                for shot in shots:
                    if asteroid.collides_with_circle(shot.position, shot.radius):
                        game_state.add_asteroid_score(asteroid)
                        log_event("asteroid_shot")
                        shot.kill()
                        asteroid.split()
                        break

        screen.fill("black")

        for sprite in drawable:
            sprite.draw(screen)

        game_state.draw(screen, font, player)

        pygame.display.flip()

        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
