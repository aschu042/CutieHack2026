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
        "teapot": run_teapot,
        "queen": run_queen,
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

    # Reveal 12 random safe (non-cat) tiles at the start
    safe_tiles = [
        (r, c)
        for r in range(rows)
        for c in range(cols)
        if solution_grid[r][c] != 4
    ]
    for r, c in random.sample(safe_tiles, min(12, len(safe_tiles))):
        revealed[r][c] = True

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


def run_teapot(screen, clock):
    width, height = 1000, 800
    screen = pygame.display.set_mode((width, height))
    font = pygame.font.SysFont(None, 40)

    teapot = pygame.image.load("sprites/Teapot.png").convert_alpha()
    teapot = pygame.transform.scale(teapot, (1300, 600))
    teapot_rect = teapot.get_rect(center=(width // 2 - 30, 250))

    cup1 = pygame.Rect(150, 550, 150, 150)
    cup2 = pygame.Rect(425, 550, 150, 150)
    cup3 = pygame.Rect(700, 550, 150, 150)

    drops = []
    tea_speed = 5
    spawn_locations = [
        (1, cup1.centerx),
        (2, cup2.centerx),
        (3, cup3.centerx + 30),
    ]

    spawn_times = []
    choices = []
    rounds = [1, 3, 5]
    round_index = 0
    result = None  # None while playing, True on win, False on loss
    status_text = "Watch the tea!"

    def start_round(num_drops, now):
        spawn_times.clear()
        choices.clear()
        # Schedules each drop 1.5 seconds apart so they don't overlap
        for i in range(num_drops):
            spawn_times.append(now + 1000 + i * 1500)

    # Start Round 1 (1 drop)
    start_round(rounds[round_index], pygame.time.get_ticks())

    while True:
        clock.tick(60)
        current_time = pygame.time.get_ticks()

        # 1. Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.display.set_mode((WIDTH, HEIGHT))
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Ignore clicks while drops are still scheduled/falling or after win/loss
                if spawn_times or drops or result is not None:
                    continue

                clicked_cup = None
                if cup1.collidepoint(event.pos):
                    clicked_cup = 1
                elif cup2.collidepoint(event.pos):
                    clicked_cup = 2
                elif cup3.collidepoint(event.pos):
                    clicked_cup = 3

                if clicked_cup and choices:
                    if clicked_cup == choices[0]:
                        choices.pop(0)
                        print(f"Correct! Cup {clicked_cup}")

                        # If all cups in this round were guessed correctly:
                        if not choices:
                            round_index += 1
                            if round_index < len(rounds):
                                status_text = f"Round {round_index + 1}: Watch the tea!"
                                start_round(rounds[round_index], current_time)
                            else:
                                result = True
                                status_text = "You win!"
                    else:
                        print(f"Wrong! Expected Cup {choices[0]}, got Cup {clicked_cup}")
                        status_text = "Wrong cup!"
                        result = False

        # 2. Update drops
        if spawn_times and current_time >= spawn_times[0]:
            spawn_times.pop(0)
            chosen_cup, chosen_x = random.choice(spawn_locations)
            choices.append(chosen_cup)
            new_drop = pygame.Rect(chosen_x - 10, 180, 20, 20)
            drops.append(new_drop)

        for drop in drops[:]:
            drop.y += tea_speed
            if drop.top > 530:
                drops.remove(drop)

        # Prompt the player once all drops for the round have finished falling
        if not spawn_times and not drops and result is None and choices:
            status_text = f"Your turn! Click {len(choices)} cup(s) in order"

        # 3. Draw everything
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (0, 255, 0), cup1)
        pygame.draw.rect(screen, (0, 255, 0), cup2)
        pygame.draw.rect(screen, (0, 255, 0), cup3)
        screen.blit(teapot, teapot_rect)

        for drop in drops:
            pygame.draw.rect(screen, (184, 149, 119), drop)

        text_surface = font.render(status_text, True, (255, 255, 255))
        screen.blit(text_surface, text_surface.get_rect(center=(width // 2, 745)))

        pygame.display.flip()

        # Pause briefly on win/loss so the player sees the result, then return
        if result is not None:
            pygame.time.delay(800)
            pygame.display.set_mode((WIDTH, HEIGHT))
            return result


def run_queen(screen, clock):
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    font = pygame.font.SysFont(None, 23)
    big_font = pygame.font.SysFont(None, 48)

    player = pygame.Rect(375, 500, 50, 50)
    queen = pygame.Rect(275, 50, 250, 250)

    dialogue = {
        "start": {
            "queen": "Who dares enter my garden?!",
            "responses": [
                ("I'm lost, Your Majesty.", "polite"),
                ("Oh great, more nonsense", "rude"),
            ],
        },
        "polite": {
            "queen": "Hmph. Good manners are rare. You may speak.",
            "responses": [
                ("Can you help me find the exit?", "help"),
            ],
        },
        "rude": {
            "queen": "Such rudeness! Off with her head! Right now!",
            "responses": [],
        },
        "help": {
            "queen": "Exit? What exit? This is my kingdom and by entering it you have become mine!",
            "responses": [
                ("But I wish to go home.", "leave"),
                ("Your not my queen, send me home", "bold"),
            ],
        },
        "bold": {
            "queen": "Bold words! Off with their head!",
            "responses": [
                ("Bring it on!", "leave"),
                ("Wait, I take it back!", "cowardly"),
            ],
        },
        "cowardly": {
            "queen": "Die",
            "responses": [],
        },
        "leave": {
            "queen": "Such hearasy!",
            "responses": [
                ("I must go home, this is not where I belong", "resolute"),
            ],
        },
        "resolute": {
            "queen": "You are so dispicable that even beheading isn't enough! I banish you",
            "responses": [],
        },
    }

    current_node = "start"
    result = None  # None while playing, True on "resolute", False on game over

    def get_response_buttons(node_key):
        responses = dialogue[node_key]["responses"]
        buttons = []
        for i, (text, next_node) in enumerate(responses):
            btn_rect = pygame.Rect(200, 368 + i * 42, 400, 34)
            buttons.append((btn_rect, text, next_node))
        return buttons

    response_buttons = get_response_buttons(current_node)

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.display.set_mode((WIDTH, HEIGHT))
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and result is None:
                for btn_rect, text, next_node in response_buttons:
                    if btn_rect.collidepoint(event.pos):
                        current_node = next_node
                        response_buttons = get_response_buttons(current_node)

                        if not dialogue[current_node]["responses"]:
                            result = current_node == "resolute"
                        break

        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, (0, 255, 0), player)
        pygame.draw.rect(screen, (0, 255, 0), queen)

        # 1. Draw the Queen's speech box and text
        queen_box = pygame.Rect(30, 310, 740, 46)
        pygame.draw.rect(screen, (240, 240, 240), queen_box)
        pygame.draw.rect(screen, (0, 0, 0), queen_box, 2)

        queen_text = font.render(dialogue[current_node]["queen"], True, (0, 0, 0))
        screen.blit(queen_text, queen_text.get_rect(center=queen_box.center))

        # 2. Draw response buttons OR the Game Over / Win status
        if result is None:
            for btn_rect, text, _ in response_buttons:
                bg_color = (200, 230, 255) if btn_rect.collidepoint(mouse_pos) else (230, 230, 230)
                pygame.draw.rect(screen, bg_color, btn_rect)
                pygame.draw.rect(screen, (0, 0, 0), btn_rect, 2)

                btn_text = font.render(text, True, (0, 0, 0))
                screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))
        else:
            if result:
                end_surface = big_font.render("YOU SURVIVED!", True, (0, 160, 0))
            else:
                end_surface = big_font.render("GAME OVER", True, (200, 0, 0))
            screen.blit(end_surface, end_surface.get_rect(center=(width // 2, 410)))

        pygame.display.flip()

        # Pause briefly so the player can read the Queen's final line, then return
        if result is not None:
            pygame.time.delay(1500)
            pygame.display.set_mode((WIDTH, HEIGHT))
            return result