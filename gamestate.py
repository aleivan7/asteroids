import pygame

from asteroid import Asteroid
from constants import (
    HUD_GAME_OVER_INSTRUCTION_OFFSET,
    HUD_GAME_OVER_MESSAGE,
    HUD_GAME_OVER_QUIT_MESSAGE,
    HUD_GAME_OVER_RETRY_MESSAGE,
    HUD_LIFE_ICON_RADIUS,
    HUD_LIFE_ICON_SPACING,
    HUD_BOMB_ICON_RADIUS,
    HUD_BOMB_ICON_SPACING,
    HUD_PANEL_BORDER_COLOR,
    HUD_PANEL_BORDER_WIDTH,
    HUD_PANEL_FILL_COLOR,
    HUD_PANEL_PADDING,
    HUD_POWERUP_ICON_RADIUS,
    HUD_SCORE_PANEL_HEIGHT,
    HUD_SCORE_PANEL_TOP,
    HUD_SCORE_PANEL_WIDTH,
    HUD_STATUS_PANEL_MARGIN,
    HUD_STATUS_PANEL_WIDTH,
    HUD_STATUS_LABEL_WIDTH,
    HUD_STATUS_ROW_SPACING,
    HUD_TEXT_COLOR,
    LEVEL_SCORE_THRESHOLDS,
    LEVEL_SPAWN_PAUSE_SECONDS,
    LEVEL_TRANSITION_SECONDS,
    LINE_WIDTH,
    MAX_LEVEL,
    PLAYER_STARTING_BOMBS,
    PLAYER_STARTING_LIVES,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


def level_for_score(score: int) -> int:
    level = 1
    for index, threshold in enumerate(LEVEL_SCORE_THRESHOLDS):
        if score >= threshold:
            level = index + 1
    return min(level, MAX_LEVEL)


class GameState:
    def __init__(self) -> None:
        self.score = 0
        self.lives = PLAYER_STARTING_LIVES
        self.game_over = False
        self.level = 1
        self.level_transition_timer = 0.0
        self.spawn_pause_timer = 0.0
        self.transition_to_level = 1

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
        self.level = 1
        self.level_transition_timer = 0.0
        self.spawn_pause_timer = 0.0
        self.transition_to_level = 1

    def check_for_level_up(self) -> int | None:
        if self.game_over or self.is_transitioning():
            return None

        score_level = level_for_score(self.score)
        if score_level > self.level:
            return min(score_level, MAX_LEVEL)
        return None

    def start_level_transition(self, new_level: int) -> None:
        if self.game_over or new_level <= self.level or self.level >= MAX_LEVEL:
            return
        if self.is_transitioning():
            return

        self.level = new_level
        self.transition_to_level = new_level
        self.level_transition_timer = LEVEL_TRANSITION_SECONDS
        self.spawn_pause_timer = LEVEL_SPAWN_PAUSE_SECONDS

    def update_timers(self, dt: float) -> None:
        if self.level_transition_timer > 0:
            self.level_transition_timer = max(0.0, self.level_transition_timer - dt)
        if self.spawn_pause_timer > 0:
            self.spawn_pause_timer = max(0.0, self.spawn_pause_timer - dt)

    def is_transitioning(self) -> bool:
        return self.level_transition_timer > 0

    def is_spawning_paused(self) -> bool:
        return self.spawn_pause_timer > 0

    def draw(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        player,
        deployed_bomb_count: int,
    ) -> None:
        self.draw_score_panel(screen, font)
        self.draw_status_panel(screen, font, player, deployed_bomb_count)

        if self.is_transitioning():
            self.draw_level_transition(screen, font)

        if self.game_over:
            self.draw_game_over(screen, font)

    def draw_panel(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
    ) -> None:
        pygame.draw.rect(screen, HUD_PANEL_FILL_COLOR, rect)
        pygame.draw.rect(
            screen,
            HUD_PANEL_BORDER_COLOR,
            rect,
            HUD_PANEL_BORDER_WIDTH,
        )

    def draw_score_panel(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        panel_rect = pygame.Rect(0, 0, HUD_SCORE_PANEL_WIDTH, HUD_SCORE_PANEL_HEIGHT)
        panel_rect.centerx = SCREEN_WIDTH // 2
        panel_rect.top = HUD_SCORE_PANEL_TOP
        self.draw_panel(screen, panel_rect)

        score_text = f"Score: {self.score} | Level: {self.level}"
        score_surface = font.render(score_text, True, HUD_TEXT_COLOR)
        score_rect = score_surface.get_rect(center=panel_rect.center)
        screen.blit(score_surface, score_rect)

    def draw_status_panel(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        player,
        deployed_bomb_count: int,
    ) -> None:
        rows = self.status_rows(player, deployed_bomb_count)
        row_heights = []
        for row in rows:
            label_surface = font.render(f"{row['label']}:", True, HUD_TEXT_COLOR)
            row_heights.append(max(HUD_STATUS_ROW_SPACING, label_surface.get_height() + 4))

        panel_height = HUD_PANEL_PADDING * 2 + sum(row_heights)
        panel_rect = pygame.Rect(
            SCREEN_WIDTH - HUD_STATUS_PANEL_WIDTH - HUD_STATUS_PANEL_MARGIN,
            SCREEN_HEIGHT - panel_height - HUD_STATUS_PANEL_MARGIN,
            HUD_STATUS_PANEL_WIDTH,
            panel_height,
        )
        self.draw_panel(screen, panel_rect)

        content_x = panel_rect.left + HUD_PANEL_PADDING
        content_y = panel_rect.top + HUD_PANEL_PADDING

        for row, row_height in zip(rows, row_heights):
            self.draw_status_row(screen, font, row, content_x, content_y)
            content_y += row_height

    def status_rows(self, player, deployed_bomb_count: int) -> list[dict]:
        rows = [
            {"label": "Lives", "kind": "lives"},
            {
                "label": "Bombs",
                "kind": "bombs",
                "deployed": deployed_bomb_count,
                "remaining": player.bombs_remaining,
            },
        ]

        if player.shield_active:
            rows.append(
                {
                    "label": "Shield",
                    "kind": "shield",
                }
            )

        if player.speed_timer > 0:
            rows.append(
                {
                    "label": "Speed",
                    "kind": "speed",
                    "timer": player.speed_timer,
                }
            )

        return rows

    def draw_status_row(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        row: dict,
        x: int,
        y: int,
    ) -> None:
        label_surface = font.render(f"{row['label']}:", True, HUD_TEXT_COLOR)
        screen.blit(label_surface, (x, y))

        content_x = x + HUD_STATUS_LABEL_WIDTH
        content_y = y + label_surface.get_height() // 2

        if row["kind"] == "lives":
            self.draw_life_icons(screen, content_x, content_y, self.lives)
        elif row["kind"] == "bombs":
            self.draw_bomb_icons(
                screen,
                content_x,
                content_y,
                row["remaining"],
                row["deployed"],
            )
        elif row["kind"] == "shield":
            pygame.draw.circle(
                screen,
                HUD_TEXT_COLOR,
                (content_x, content_y),
                HUD_POWERUP_ICON_RADIUS,
                LINE_WIDTH,
            )
        elif row["kind"] == "speed":
            timer_surface = font.render(f"{row['timer']:.1f}s", True, HUD_TEXT_COLOR)
            timer_rect = timer_surface.get_rect(left=content_x, centery=content_y)
            screen.blit(timer_surface, timer_rect)

    def draw_life_icons(self, screen: pygame.Surface, x: int, y: int, lives: int) -> None:
        for i in range(lives):
            center = pygame.Vector2(x + i * HUD_LIFE_ICON_SPACING, y)
            forward = pygame.Vector2(0, -1)
            right = pygame.Vector2(1, 0)
            radius = HUD_LIFE_ICON_RADIUS
            points = [
                center + forward * radius,
                center - forward * radius * 0.35 + right * radius * 0.85,
                center - forward * radius * 0.35 - right * radius * 0.85,
            ]
            pygame.draw.polygon(screen, HUD_TEXT_COLOR, points, LINE_WIDTH)

    def draw_bomb_icons(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        bombs_remaining: int,
        deployed_bomb_count: int,
    ) -> None:
        total_slots = PLAYER_STARTING_BOMBS

        for i in range(total_slots):
            center = pygame.Vector2(x + i * HUD_BOMB_ICON_SPACING, y)

            if i < bombs_remaining:
                pygame.draw.circle(screen, HUD_TEXT_COLOR, center, HUD_BOMB_ICON_RADIUS)
            elif i < bombs_remaining + deployed_bomb_count:
                pygame.draw.circle(
                    screen,
                    HUD_TEXT_COLOR,
                    center,
                    HUD_BOMB_ICON_RADIUS,
                    LINE_WIDTH,
                )

    def draw_level_transition(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        message = f"LEVEL {self.transition_to_level}"
        message_surface = font.render(message, True, HUD_TEXT_COLOR)
        message_rect = message_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        screen.blit(message_surface, message_rect)

    def draw_game_over(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        game_over_surface = font.render(HUD_GAME_OVER_MESSAGE, True, HUD_TEXT_COLOR)
        game_over_rect = game_over_surface.get_rect(center=(center_x, center_y))
        screen.blit(game_over_surface, game_over_rect)

        retry_surface = font.render(HUD_GAME_OVER_RETRY_MESSAGE, True, HUD_TEXT_COLOR)
        retry_rect = retry_surface.get_rect(
            center=(center_x, center_y + HUD_GAME_OVER_INSTRUCTION_OFFSET)
        )
        screen.blit(retry_surface, retry_rect)

        quit_surface = font.render(HUD_GAME_OVER_QUIT_MESSAGE, True, HUD_TEXT_COLOR)
        quit_rect = quit_surface.get_rect(
            center=(center_x, center_y + HUD_GAME_OVER_INSTRUCTION_OFFSET * 2)
        )
        screen.blit(quit_surface, quit_rect)
