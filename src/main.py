import pygame
import sys
from settings import WIDTH, HEIGHT, FPS, BG_COLOR, LEVELS
from objects import load_level

# python src/main.py

# python -m venv downTheRabbitHole
# downTheRabbitHole\Scripts\Activate
# pip install -r requirements.txt

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen_rect = screen.get_rect()
clock = pygame.time.Clock()

current_level = 0
platforms, player, goal = load_level(current_level)

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update player movement and collisions
    player.update(platforms, screen_rect)

    # Check if player reached the goal
    if goal and player.rect.colliderect(goal.rect):
        current_level = (current_level + 1) % len(LEVELS)
        platforms, player, goal = load_level(current_level)

    # Render everything
    screen.fill(BG_COLOR)
    for platform in platforms:
        platform.draw(screen)
    if goal:
        goal.draw(screen)
    player.draw(screen)

    pygame.display.flip()

pygame.quit()  # closes the game
sys.exit()     # closes the program