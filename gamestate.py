import pygame

from asteroid import Asteroid
from constants import (
    BOMB_RADIUS,
    HUD_BOMBS_POSITION,
    HUD_GAME_OVER_INSTRUCTION_OFFSET,
    HUD_GAME_OVER_MESSAGE,
    HUD_GAME_OVER_QUIT_MESSAGE,
    HUD_GAME_OVER_RETRY_MESSAGE,
    HUD_LIVES_POSITION,
    HUD_SCORE_POSITION,
    HUD_SHIELD_POSITION,
    HUD_SPEED_POSITION,
    PLAYER_RADIUS,
    PLAYER_STARTING_LIVES,
    POWERUP_RADIUS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHIELD_ABSORB_INVULNERABLE_SECONDS,
)


class GameState:
    def __init__(self) -> None:
        self.score = 0
        self.lives = PLAYER_STARTING_LIVES
        self.game_over = False

    def add_asteroid_score(self, asteroid: Asteroid) -> None:
        self.score += asteroid.points()

    def lose_life(self) -> None:
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True

    def reset(self) -> None:
        self.score = 0
        self.lives = PLAYER_STARTING_LIVES
        self.game_over = False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font, player) -> None:
        score_surface = font.render(f"Score: {self.score}", True, "white")
        screen.blit(score_surface, HUD_SCORE_POSITION)

        lives_surface = font.render(f"Lives: {self.lives}", True, "white")
        screen.blit(lives_surface, HUD_LIVES_POSITION)

        if player.speed_timer > 0:
            speed_surface = font.render(
                f"Speed: {player.speed_timer:.1f}s", True, "white"
            )
            screen.blit(speed_surface, HUD_SPEED_POSITION)

        if player.shield_active:
            shield_surface = font.render("Shield: ON", True, "white")
            screen.blit(shield_surface, HUD_SHIELD_POSITION)

        bombs_surface = font.render(f"Bombs: {player.bombs_remaining}", True, "white")
        screen.blit(bombs_surface, HUD_BOMBS_POSITION)

        if self.game_over:
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2

            game_over_surface = font.render(HUD_GAME_OVER_MESSAGE, True, "white")
            game_over_rect = game_over_surface.get_rect(center=(center_x, center_y))
            screen.blit(game_over_surface, game_over_rect)

            retry_surface = font.render(HUD_GAME_OVER_RETRY_MESSAGE, True, "white")
            retry_rect = retry_surface.get_rect(
                center=(center_x, center_y + HUD_GAME_OVER_INSTRUCTION_OFFSET)
            )
            screen.blit(retry_surface, retry_rect)

            quit_surface = font.render(HUD_GAME_OVER_QUIT_MESSAGE, True, "white")
            quit_rect = quit_surface.get_rect(
                center=(center_x, center_y + HUD_GAME_OVER_INSTRUCTION_OFFSET * 2)
            )
            screen.blit(quit_surface, quit_rect)
