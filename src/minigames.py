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

pygame.init()

def start_minigame(screen, clock, minigame_id):
    minigames = {
        "speedrun": run_speedrun,
        "minesweeper": run_minesweeper,
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

def run_minesweeper(screen, clock):
    """Runs the Minesweeper clone and returns True on win, False on loss/exit."""
    MineLocations = [
        "0141000000",
        "0112110011",
        "1101410014",
        "4322110011",
        "2442110000",
        "1233410000",
        "1114221100",
        "4111114100",
    ]

    tileSize = 80
    rows = len(MineLocations)
    cols = len(MineLocations[0])
    width, height = cols * tileSize, rows * tileSize

    GRID_LINE_COLOR = (60, 60, 60)
    TILE_COLORS = {
        0: (0, 255, 0),   # Cleared
        5: (50, 50, 50),  # Untouched
        6: (255, 0, 0),   # Flag
    }

    # Resize window to fit the 800x640 board cleanly
    screen = pygame.display.set_mode((width, height))

    def load_tile(filename):
        img = pygame.image.load(filename).convert_alpha()
        if filename == "sprites/Cat.png":
            return pygame.transform.scale(img, (tileSize + 37, tileSize + 37))
        return pygame.transform.scale(img, (tileSize, tileSize))

    TILE_IMAGES = {
        0: load_tile("sprites/Minesweeper0.png"),
        1: load_tile("sprites/Minesweeper1.png"),
        2: load_tile("sprites/Minesweeper2.png"),
        3: load_tile("sprites/Minesweeper3.png"),
        4: load_tile("sprites/Cat.png"),
    }

    solution_grid = [[int(char) for char in row] for row in MineLocations]
    revealed = [[False for _ in range(cols)] for _ in range(rows)]
    flagged = [[False for _ in range(cols)] for _ in range(rows)]

    result = None  # None while playing, True on win, False on loss

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.display.set_mode((WIDTH, HEIGHT))
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and result is None:
                mouse_x, mouse_y = event.pos
                col = mouse_x // tileSize
                row = mouse_y // tileSize
                revealed[row][col] = True
                if event.button == 1 and not flagged[row][col]:
                    revealed[row][col] = True
                    # Check if a cat/mine (4) was uncovered
                    if solution_grid[row][col] == 4:
                        result = False
                elif event.button == 3:
                    flagged[row][col] = not flagged[row][col]
                    if not flagged[row][col]:
                        revealed[row][col] = False

                # Check if every safe (non-4) tile has been revealed
                if result is None:
                    all_safe_cleared = all(
                        revealed[r][c]
                        for r in range(rows)
                        for c in range(cols)
                        if solution_grid[r][c] != 4
                    )
                    if all_safe_cleared:
                        result = True

        # Pass 1: Draw base rectangles and grid lines
        for row in range(rows):
            for col in range(cols):
                rect = pygame.Rect(
                    col * tileSize,
                    row * tileSize,
                    tileSize,
                    tileSize,
                )

                if flagged[row][col]:
                    color = TILE_COLORS[6]
                elif not revealed[row][col]:
                    color = 5
                else:
                    tile_type = solution_grid[row][col]
                    color = TILE_COLORS.get(tile_type, TILE_COLORS[0])

                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1)

        # Pass 2: Draw centered images
        for row in range(rows):
            for col in range(cols):
                if revealed[row][col] and not flagged[row][col]:
                    tile_type = solution_grid[row][col]
                    if tile_type in TILE_IMAGES:
                        tile_rect = pygame.Rect(
                            col * tileSize,
                            row * tileSize,
                            tileSize,
                            tileSize,
                        )
                        img = TILE_IMAGES[tile_type]
                        img_rect = img.get_rect(center=tile_rect.center)
                        screen.blit(img, img_rect)

        pygame.display.flip()
        clock.tick(FPS)

        # Pause briefly on win/loss so the player sees the final click, then return
        if result is not None:
            pygame.time.delay(800)
            pygame.display.set_mode((WIDTH, HEIGHT))
            return result

