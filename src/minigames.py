import pygame
import random
import sys
from settings import (
    WIDTH,
    HEIGHT,
    FPS,
    TILE_SIZE,
    BG_COLOR,
    PLAYER_COLOR,
    SPIKE_COLOR,
    GOAL_COLOR,
    SPEEDRUN_TIME,
    SPEEDRUN_LEVEL,
)
from objects import build_level

def start_minigame(screen, clock, minigame_id):
    minigames = {
        "speedrun": run_speedrun,
    }

    game_fn = minigames.get(minigame_id)
    if game_fn is None:
        return False

    return game_fn(screen, clock)

def run_speedrun(screen, clock):
    world_width = len(SPEEDRUN_LEVEL[0]) * TILE_SIZE
    world_rect = pygame.Rect(0, 0, world_width, HEIGHT)

    platforms, spikes, shooters, bullets, player, goal, npcs = build_level(SPEEDRUN_LEVEL)

    start_x = player.rect.x
    time_left = SPEEDRUN_TIME

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update course platforms, shooters, bullets, and player
        for platform in platforms:
            platform.update(platforms, world_rect, player.rect)
    
        for shooter in shooters:
            shooter.shoot(bullets)
    
        for bullet in bullets:
            bullet.update(platforms, world_rect)
        bullets = [b for b in bullets if b.active]
    
        # Update player movement and collisions
        player.update(platforms, world_rect)

        # Win check: reached the goal in time
        if goal and player.rect.colliderect(goal.rect):
            return True

        hit_hazard = (
            player.rect.bottom >= world_rect.bottom
            or any(player.rect.colliderect(s.rect) for s in spikes)
            or any(player.rect.colliderect(b.rect) for b in bullets)
        )
        if hit_hazard:
            platforms, spikes, shooters, bullets, player, goal, npcs = build_level(SPEEDRUN_LEVEL)

        time_left -= 1
        if time_left <= 0:
            return False

        camera_x = player.rect.centerx - (WIDTH // 2)
        camera_x = max(0, min(camera_x, world_width - WIDTH))

        screen.fill(BG_COLOR)
        for platform in platforms:
            platform.draw(screen, camera_x)
        for spike in spikes:
            spike.draw(screen, camera_x)
        for bullet in bullets:
            bullet.draw(screen, camera_x)
        if goal:
            goal.draw(screen, camera_x)
        player.draw(screen, camera_x)

        time_ratio = time_left / SPEEDRUN_TIME
        pygame.draw.rect(screen, (50, 50, 50), (150, 16, 500, 14))
        pygame.draw.rect(screen, SPIKE_COLOR, (150, 16, int(500 * time_ratio), 14))

        if goal and goal.rect.x > start_x:
            dist_ratio = (player.rect.x - start_x) / (goal.rect.x - start_x)
            dist_ratio = max(0.0, min(1.0, dist_ratio))
            pygame.draw.rect(screen, (50, 50, 50), (150, 34, 500, 6))
            pygame.draw.rect(screen, GOAL_COLOR, (150, 34, int(500 * dist_ratio), 6))

        pygame.display.flip()