import pygame
from settings import (
    TILE_SIZE,
    PLAYER_SIZE,
    PLAYER_SPEED,
    PLATFORM_COLOR,
    PLAYER_COLOR,
    GOAL_COLOR,
    LEVELS,
)

class Platform:
    def __init__(self, x, y, width=TILE_SIZE, height=TILE_SIZE):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = PLATFORM_COLOR

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class Goal:
    def __init__(self, x, y, width=TILE_SIZE, height=TILE_SIZE):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GOAL_COLOR

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.color = PLAYER_COLOR
        self.speed = PLAYER_SPEED

    def update(self, platforms, screen_rect):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_d]:
            dx += self.speed
        if keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_s]:
            dy += self.speed

        # Horizontal movement & collision
        self.rect.x += dx
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dx > 0:
                    self.rect.right = platform.rect.left
                elif dx < 0:
                    self.rect.left = platform.rect.right

        # Vertical movement & collision
        self.rect.y += dy
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dy > 0:
                    self.rect.bottom = platform.rect.top
                elif dy < 0:
                    self.rect.top = platform.rect.bottom

        # Keep player inside the window
        self.rect.clamp_ip(screen_rect)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

def load_level(level_index):
    platforms = []
    player = Player(0, 0)
    goal = None

    grid = LEVELS[level_index]
    for row_idx, row in enumerate(grid):
        for col_idx, cell in enumerate(row):
            x = col_idx * TILE_SIZE
            y = row_idx * TILE_SIZE

            if cell == "#":
                platforms.append(Platform(x, y))
            elif cell == "P":
                player.rect.topleft = (x, y)
            elif cell == "G":
                goal = Goal(x, y)

    return platforms, player, goal