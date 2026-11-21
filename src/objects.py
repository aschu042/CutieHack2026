import pygame
from settings import (
    TILE_SIZE,
    PLAYER_SIZE,
    PLAYER_SPEED,
    GRAVITY,
    JUMP_STRENGTH,
    MAX_FALL_SPEED,
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
        self.vel_y = 0
        self.on_ground = False

    def update(self, platforms, screen_rect):
        keys = pygame.key.get_pressed()
        dx = 0

        # Horizontal input
        if keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_d]:
            dx += self.speed

        # Jump input (only allowed when standing on a surface)
        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

        # Apply gravity up to terminal fall speed
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)

        # 1. Horizontal movement & collision
        self.rect.x += dx
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dx > 0:
                    self.rect.right = platform.rect.left
                elif dx < 0:
                    self.rect.left = platform.rect.right

        # 2. Vertical movement & collision
        self.rect.y += self.vel_y
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  # Falling -> land on top of platform
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Jumping -> bonk head on bottom of platform
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        # Keep player inside the window and reset fall speed if touching the floor
        if self.rect.bottom >= screen_rect.bottom:
            self.rect.bottom = screen_rect.bottom
            self.vel_y = 0
            self.on_ground = True

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