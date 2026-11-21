import pygame
import sys
from settings import WIDTH, HEIGHT, FPS, BG_COLOR, WINNING_BG_COLOR, WINNING_TEXT, WINNING_TEXT_COLOR, LEVELS
from objects import load_level

# python src/main.py

# python -m venv downTheRabbitHole
# downTheRabbitHole\Scripts\Activate
# pip install -r requirements.txt

pygame.init()

FONT = pygame.font.SysFont(None, 36, False, False)
text_surface = FONT.render(WINNING_TEXT, True, WINNING_TEXT_COLOR)
text_rect = text_surface.get_rect(center=(WIDTH/2, HEIGHT/2))
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen_rect = screen.get_rect()
clock = pygame.time.Clock()

current_level = 0
platforms, spikes, shooters, bullets, player, goal, npc = load_level(current_level)
gameOver = False

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for platform in platforms:
        platform.update(platforms, screen_rect, player.rect)

    for shooter in shooters:
        shooter.shoot(bullets)

    for bullet in bullets:
        bullet.update(platforms, screen_rect)
        bullets = [b for b in bullets if b.active]

    # Update player movement and collisions
    player.update(platforms, screen_rect)

    # Check all death conditions (Void, Spikes, or Bullets)
    died = player.rect.bottom >= screen_rect.bottom
    if not died:
        died = any(player.rect.colliderect(spike.rect) for spike in spikes)
    if not died:
        died = any(player.rect.colliderect(bullet.rect) for bullet in bullets)

    if died:
        platforms, spikes, shooters, bullets, player, goal, npc = load_level(current_level)
        continue

    # Check if player reached the goal
    if goal and player.rect.colliderect(goal.rect):
        if current_level < len(LEVELS) - 1:
            current_level = (current_level + 1) % len(LEVELS)
            platforms, spikes, shooters, bullets, player, goal, npc = load_level(current_level)
        else:
            screen.fill(WINNING_BG_COLOR)
            screen.blit(text_surface, text_rect)
            gameOver = True


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
        player.draw(screen)
        npc.draw(screen)

    pygame.display.flip()

pygame.quit()  # closes the game
sys.exit()     # closes the program