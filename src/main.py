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
BIG_FONT = pygame.font.SysFont(None, 72, False, False)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen_rect = screen.get_rect()
clock = pygame.time.Clock()

card_img = pygame.image.load("sprites/Card.png").convert_alpha()
card_img = pygame.transform.scale(card_img, (40, 56))
health = 3

current_level = 0
completed_npcs = set()
platforms, spikes, shooters, bullets, player, goal, npcs = load_level(current_level)
gameOver = False
lost = False
sync_npc_states(npcs, current_level, completed_npcs)

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Restart if out of health
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and lost:
            health = 3
            current_level = 0
            completed_npcs.clear()
            platforms, spikes, shooters, bullets, player, goal, npcs = load_level(current_level)
            sync_npc_states(npcs, current_level, completed_npcs)
            lost = False

        # Trigger minigame when pressing 'T' near an NPC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_t and not gameOver and not lost:
            for idx, npc in enumerate(npcs):
                if npc.player_nearby:
                    won = start_minigame(screen, clock, npc.minigame_id)
                    if won is True:
                        npc.completed = True
                        completed_npcs.add((current_level, idx))
                    elif won is False:
                        health -= 1
                        if health <= 0:
                            lost = True
                    break

    if not lost:
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

        # Lose 1 health when hit by a bullet and remove the bullet so it doesn't hit multiple frames
        hit_bullets = [b for b in bullets if player.rect.colliderect(b.rect)]
        if hit_bullets:
            for b in hit_bullets:
                bullets.remove(b)
            health -= len(hit_bullets)
            if health <= 0:
                lost = True
                continue

        # Check level respawn conditions (Void or Spikes)
        died = player.rect.bottom >= screen_rect.bottom
        if not died:
            died = any(player.rect.colliderect(spike.rect) for spike in spikes)

        if died:
            platforms, spikes, shooters, bullets, player, goal, npcs = load_level(current_level)
            sync_npc_states(npcs, current_level, completed_npcs)
            continue

        # Check if player reached the goal
        if goal and player.rect.colliderect(goal.rect):
            if current_level < len(LEVELS) - 1:
                current_level = (current_level + 1) % len(LEVELS)
                platforms, spikes, shooters, bullets, player, goal, npcs = load_level(current_level)
                sync_npc_states(npcs, current_level, completed_npcs)
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

            # Draw health cards in top right
            for i in range(health):
                card_x = WIDTH - 20 - (i + 1) * (card_img.get_width() + 8)
                screen.blit(card_img, (card_x, 16))
    else:
        screen.fill((20, 0, 0))
        over_text = BIG_FONT.render("GAME OVER", True, (220, 40, 40))
        retry_text = FONT.render("Press R to Restart", True, (255, 255, 255))
        screen.blit(over_text, over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
        screen.blit(retry_text, retry_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))

    pygame.display.flip()

pygame.quit()  # closes the game
sys.exit()     # closes the program