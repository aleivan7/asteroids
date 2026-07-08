import pygame

from asteroid import Asteroid, destroy_asteroids_in_radius
from asteroidfield import AsteroidField
from bomb import Bomb
from constants import (
    BOMB_RADIUS,
    HUD_FONT_SIZE,
    LEVEL_SAFE_RADIUS,
    LEVEL_UP_INVULNERABLE_SECONDS,
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
    bombs = pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = updatable
    Shot.containers = (shots, updatable, drawable)
    PowerUp.containers = (powerups, updatable, drawable)
    PowerUpField.containers = updatable
    Bomb.containers = (bombs, updatable, drawable)

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    game_state = GameState()
    asteroid_field = AsteroidField(asteroids, game_state)
    powerup_field = PowerUpField(powerups)

    font = pygame.font.Font(None, HUD_FONT_SIZE)
    screen_center = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def clear_shots() -> None:
        for shot in list(shots):
            shot.kill()

    def clear_center_asteroids() -> None:
        for asteroid in list(asteroids):
            if asteroid.position.distance_to(screen_center) <= LEVEL_SAFE_RADIUS:
                asteroid.kill()

    def begin_level_transition(new_level: int) -> None:
        if game_state.game_over:
            return

        game_state.start_level_transition(new_level)
        if not game_state.is_transitioning():
            return

        player.reposition_for_level_up(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            LEVEL_UP_INVULNERABLE_SECONDS,
        )
        clear_center_asteroids()
        clear_shots()
        asteroid_field.spawn_timer = 0.0
        log_event("level_up")

    def maybe_begin_level_transition() -> None:
        new_level = game_state.check_for_level_up()
        if new_level is not None:
            begin_level_transition(new_level)

    def reset_game() -> None:
        game_state.reset()
        player.reset_to_start(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        for asteroid in list(asteroids):
            asteroid.kill()
        for shot in list(shots):
            shot.kill()
        for powerup in list(powerups):
            powerup.kill()
        for bomb in list(bombs):
            bomb.kill()

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
                and not game_state.is_transitioning()
                and event.type == pygame.KEYDOWN
            ):
                if event.key == pygame.K_b:
                    if player.try_use_bomb():
                        Bomb(player.position.x, player.position.y)
                        log_event("bomb_dropped")

                if event.key == pygame.K_n:
                    detonated_any = False
                    for bomb in list(bombs):
                        if bomb.detonated:
                            continue

                        destroy_asteroids_in_radius(
                            asteroids,
                            bomb.position,
                            BOMB_RADIUS,
                            game_state.add_asteroid_score,
                        )
                        bomb.detonate()
                        detonated_any = True

                    if detonated_any:
                        log_event("bomb_detonated")
                        maybe_begin_level_transition()

        if not game_state.game_over:
            game_state.update_timers(dt)
            player.combat_locked = game_state.is_transitioning()
            updatable.update(dt)

            if not game_state.is_transitioning():
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

            if not game_state.is_transitioning():
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
                            player.invulnerable_timer = (
                                SHIELD_ABSORB_INVULNERABLE_SECONDS
                            )
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

                maybe_begin_level_transition()

        screen.fill("black")

        for sprite in drawable:
            sprite.draw(screen)

        deployed_bomb_count = sum(1 for bomb in bombs if not bomb.detonated)
        game_state.draw(screen, font, player, deployed_bomb_count)

        pygame.display.flip()

        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
