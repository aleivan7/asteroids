import pygame

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import HUD_FONT_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from gamestate import GameState
from logger import log_event, log_state
from player import Player
from shot import Shot


def main():
    pygame.init()
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

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = updatable
    Shot.containers = (shots, updatable, drawable)

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    asteroid_field = AsteroidField()

    game_state = GameState()
    font = pygame.font.Font(None, HUD_FONT_SIZE)

    def reset_game() -> None:
        game_state.reset()
        player.reset_to_start(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        for asteroid in list(asteroids):
            asteroid.kill()
        for shot in list(shots):
            shot.kill()

        asteroid_field.spawn_timer = 0.0

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

        if not game_state.game_over:
            updatable.update(dt)

            player_hit_this_frame = False

            for asteroid in asteroids:
                if (
                    not player_hit_this_frame
                    and player.is_vulnerable()
                    and asteroid.collides_with(player)
                ):
                    log_event("player_hit")
                    game_state.lose_life()
                    if not game_state.game_over:
                        player.respawn(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                    player_hit_this_frame = True

                for shot in shots:
                    if asteroid.collides_with(shot):
                        game_state.add_asteroid_score(asteroid)
                        log_event("asteroid_shot")
                        shot.kill()
                        asteroid.split()
                        break

        screen.fill("black")

        for sprite in drawable:
            sprite.draw(screen)

        game_state.draw(screen, font)

        pygame.display.flip()

        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
