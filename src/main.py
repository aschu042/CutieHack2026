import pygame
import sys
from settings import WIDTH, HEIGHT, FPS, BG_COLOR, WINNING_BG_COLOR, WINNING_TEXT, WINNING_TEXT_COLOR, LEVELS, WINNING_TEXT_TRUE, NPC_CHARS
from objects import load_level
from minigames import start_minigame

def draw_multiline_text(surface, text, pos, font, color):
    lines = text.splitlines()
    x, y = pos
    line_height = font.get_linesize()  # Gets the recommended height for a line

    for line in lines:
        line_surface = font.render(line, True, color)
        surface.blit(line_surface, (x - len(line), y))
        y += line_height  # Move down for the next line

total_npcs = sum(
    cell in NPC_CHARS
    for level in LEVELS
    for row in level
    for cell in row
)


def sync_npc_states(npcs, level_index, completed_npcs):
    for idx, npc in enumerate(npcs):
        if (level_index, idx) in completed_npcs:
            npc.completed = True

# python src/main.py
# python -m venv downTheRabbitHole
# downTheRabbitHole\Scripts\Activate
# pip install -r requirements.txt

pygame.init()

FONT = pygame.font.SysFont(None, 36, False, False)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen_rect = screen.get_rect()
clock = pygame.time.Clock()

current_level = 0
completed_npcs = set()
platforms, spikes, shooters, bullets, player, goal, npcs = load_level(current_level)
gameOver = False
sync_npc_states(npcs, current_level, completed_npcs)

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Trigger minigame when pressing 'T' near an NPC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
            for idx, npc in enumerate(npcs):
                if npc.player_nearby:
                    won = start_minigame(screen, clock, npc.minigame_id)
                    if won:
                        npc.completed = True
                        completed_npcs.add((current_level, idx))
                    break

    for platform in platforms:
        platform.update(platforms, screen_rect, player.rect)

    for shooter in shooters:
        shooter.shoot(bullets)

    for bullet in bullets:
        bullet.update(platforms, screen_rect)
    bullets = [b for b in bullets if b.active]

    # Update player movement and collisions
    player.update(platforms, screen_rect)

    for npc in npcs:
        npc.update(player.rect)

    # Check all death conditions (Void, Spikes, or Bullets)
    died = player.rect.bottom >= screen_rect.bottom
    if not died:
        died = any(player.rect.colliderect(spike.rect) for spike in spikes)
    if not died:
        died = any(player.rect.colliderect(bullet.rect) for bullet in bullets)

    if died:
        platforms, spikes, shooters, bullets, player, goal, npcs = load_level(current_level)
        sync_npc_states(npcs, current_level, completed_npcs)
        continue

    # Check if player reached the goal
    if goal and player.rect.colliderect(goal.rect):
        if current_level < len(LEVELS) - 1:
            current_level = (current_level + 1) % len(LEVELS)
            platforms, spikes, shooters, bullets, player, goal, npcs = load_level(current_level)
        else:
            screen.fill(WINNING_BG_COLOR)
            gameOver = True
            if len(completed_npcs) < len(NPC_CHARS):
                draw_multiline_text(screen, WINNING_TEXT, (2 * len(WINNING_TEXT), HEIGHT//2), FONT, WINNING_TEXT_COLOR)
            else:
                draw_multiline_text(screen, WINNING_TEXT_TRUE, (2 * len(WINNING_TEXT), HEIGHT//2), FONT, WINNING_TEXT_COLOR)
            


    # Render everything
    if not gameOver:
        screen.fill(BG_COLOR)
        for platform in platforms:
            platform.draw(screen)
        for spike in spikes:
            spike.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        if goal:
            goal.draw(screen)
        for npc in npcs:
            npc.draw(screen)
        player.draw(screen)

    pygame.display.flip()

pygame.quit()  # closes the game
sys.exit()     # closes the program
