import pygame
import random
from settings import (
    TILE_SIZE,
    PLAYER_SIZE,
    PLAYER_SPEED,
    GRAVITY,
    JUMP_STRENGTH,
    MAX_FALL_SPEED,
    MOVING_SPEED,
    MOVING_RANGE,
    CRUMBLE_DELAY,
    CRUMBLE_RESPAWN,
    PHASE_SOLID_TIME,
    PHASE_GONE_TIME,
    SPIKE_HEIGHT,
    BULLET_WIDTH,
    BULLET_HEIGHT,
    BULLET_SPEED,
    SHOOT_INTERVAL,
    PLATFORM_COLOR,
    MOVING_COLOR,
    CRUMBLE_COLOR,
    PHASE_COLOR,
    SPIKE_COLOR,
    SHOOTER_COLOR,
    BULLET_COLOR,
    PLAYER_COLOR,
    GOAL_COLOR,
    NPC_COLOR,
    NPC_COMPLETED_COLOR,
    INTERACT_PADDING,
    LEVELS,
)

class Platform:
    def __init__(self, x, y, width=TILE_SIZE, height=TILE_SIZE, color=PLATFORM_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.is_solid = True
        self.dx = 0

    def onPlayerStand(self):
        pass

    def update(self, platforms, screen_rect, player_rect):
        pass

    def draw(self, surface, camera_x=0):
        if self.is_solid:
            pygame.draw.rect(surface, self.color, self.rect.move(-camera_x, 0))

class MovingPlatform(Platform):
    def __init__(self, x, y):
        super().__init__(x, y, width=TILE_SIZE * 2, color=MOVING_COLOR)
        self.start_x = x
        self.direction = 1

    def update(self, platforms, screen_rect, player_rect):
        old_x = self.rect.x
        self.rect.x += MOVING_SPEED * self.direction

        # Reverse at movement limits or screen edge
        if (self.rect.x >= self.start_x + MOVING_RANGE
            or self.rect.x <= self.start_x - MOVING_RANGE
            or self.rect.right >= screen_rect.right
            or self.rect.left <= screen_rect.left):
            self.direction *= -1

        # Reverse if hitting another solid platform
        for other in platforms:
            if other is not self and other.is_solid and self.rect.colliderect(other.rect):
                if self.direction > 0:
                    self.rect.right = other.rect.left
                else:
                    self.rect.left = other.rect.right
                self.direction *= -1

        # Store exact distance moved so the player can ride along
        self.dx = self.rect.x - old_x

class CrumblingPlatform(Platform):
    def __init__(self, x, y):
        super().__init__(x, y, color=CRUMBLE_COLOR)
        self.state = "idle"  # "idle" -> "shaking" -> "broken"
        self.timer = 0

    def onPlayerStand(self):
        if self.state == "idle":
            self.state = "shaking"
            self.timer = CRUMBLE_DELAY

    def update(self, platforms, screen_rect, player_rect):
        if self.state == "shaking":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "broken"
                self.is_solid = False
                self.timer = CRUMBLE_RESPAWN

        elif self.state == "broken":
            self.timer -= 1
            # Wait until timer finishes AND player isn't standing inside the space
            if self.timer <= 0 and not self.rect.colliderect(player_rect):
                self.state = "idle"
                self.is_solid = True

    def draw(self, surface, camera_x=0):
        draw_rect = self.rect.move(-camera_x, 0)
        if self.state == "idle":
            pygame.draw.rect(surface, self.color, draw_rect)
        elif self.state == "shaking":
            # Draw with a slight horizontal shake to warn the player
            shake_rect = draw_rect.move(random.randint(-2, 2), 0)
            pygame.draw.rect(surface, self.color, shake_rect)
        elif self.state == "broken":
            # Faint outline showing where the platform will reappear
            pygame.draw.rect(surface, self.color, draw_rect, 1)

class PhasingPlatform(Platform):
    def __init__(self, x, y):
        super().__init__(x, y, color=PHASE_COLOR)
        self.timer = PHASE_SOLID_TIME

    def update(self, platforms, screen_rect, player_rect):
        self.timer -= 1

        if self.is_solid and self.timer <= 0:
            self.is_solid = False
            self.timer = PHASE_GONE_TIME

        elif not self.is_solid and self.timer <= 0:
            # Only phase back in once the player isn't overlapping the hitbox
            if not self.rect.colliderect(player_rect):
                self.is_solid = True
                self.timer = PHASE_SOLID_TIME

    def draw(self, surface, camera_x=0):
        draw_rect = self.rect.move(-camera_x, 0)
        if self.is_solid:
            # Flicker during the final 0.5 seconds (30 frames) before vanishing
            if self.timer <= 30 and (self.timer // 4) % 2 == 0:
                pygame.draw.rect(surface, self.color, draw_rect, 2)
            else:
                pygame.draw.rect(surface, self.color, draw_rect)
        else:
            # Hollow outline while phased out
            pygame.draw.rect(surface, self.color, draw_rect, 2)

class Spike:
    def __init__(self, x, y):
        # Sits on the bottom half of the tile cell
        self.rect = pygame.Rect(
            x, y + (TILE_SIZE - SPIKE_HEIGHT), TILE_SIZE, SPIKE_HEIGHT
        )
        self.color = SPIKE_COLOR

    def draw(self, surface, camera_x=0):
        pygame.draw.rect(surface, self.color, self.rect.move(-camera_x, 0))

class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, BULLET_WIDTH, BULLET_HEIGHT)
        self.direction = direction  # -1 for left, 1 for right
        self.color = BULLET_COLOR
        self.active = True

    def update(self, platforms, screen_rect):
        self.rect.x += BULLET_SPEED * self.direction

        # Despawn if bullet leaves the screen
        if not screen_rect.colliderect(self.rect):
            self.active = False
            return

        # Despawn if bullet hits any solid wall or platform
        for platform in platforms:
            if platform.is_solid and self.rect.colliderect(platform.rect):
                self.active = False
                return

    def draw(self, surface, camera_x=0):
        pygame.draw.rect(surface, self.color, self.rect.move(-camera_x, 0))

class BulletShooter(Platform):
    def __init__(self, x, y, direction):
        super().__init__(x, y, color=SHOOTER_COLOR)
        self.direction = direction  # -1 for left, 1 for right
        self.timer = SHOOT_INTERVAL // 2  # Fires shortly after level loads

    def shoot(self, bullets):
        self.timer -= 1
        if self.timer <= 0:
            self.timer = SHOOT_INTERVAL
            bullet_y = self.rect.centery - (BULLET_HEIGHT // 2)
            if self.direction == -1:
                bullet_x = self.rect.left - BULLET_WIDTH
            else:
                bullet_x = self.rect.right
            bullets.append(Bullet(bullet_x, bullet_y, self.direction))

class Goal:
    def __init__(self, x, y, width=TILE_SIZE, height=TILE_SIZE):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GOAL_COLOR

    def draw(self, surface, camera_x=0):
        pygame.draw.rect(surface, self.color, self.rect.move(-camera_x, 0))

class NPC:
    def __init__(self, x, y, minigame_id):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        # Slightly larger invisible box so you don't have to pixel-perfect overlap
        self.interact_rect = self.rect.inflate(INTERACT_PADDING, INTERACT_PADDING)
        self.color = NPC_COLOR
        self.minigame_id = minigame_id
        self.player_nearby = False
        self.completed = False

    def update(self, player_rect):
        self.player_nearby = self.interact_rect.colliderect(player_rect)

    def draw(self, surface):
        color = NPC_COMPLETED_COLOR if self.completed else self.color
        pygame.draw.rect(surface, color, self.rect)

        # Show a visual cue when the player is close enough to press 'T'
        if self.player_nearby:
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
            prompt_box = pygame.Rect(self.rect.centerx - 5, self.rect.top - 14, 10, 10)
            pygame.draw.rect(surface, (255, 255, 255), prompt_box)

    
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.color = PLAYER_COLOR
        self.speed = PLAYER_SPEED
        self.vel_y = 0
        self.on_ground = False
        self.standing_on = None

    def update(self, platforms, screen_rect):
        keys = pygame.key.get_pressed()
        dx = 0

        # Horizontal input
        if keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_d]:
            dx += self.speed

        # Jump input (only allowed when standing on a surface)
        if self.standing_on and self.standing_on.is_solid:
            dx += self.standing_on.dx

        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            self.standing_on = None

        # Apply gravity up to terminal fall speed
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)

        # Horizontal movement & collision
        self.rect.x += dx
        for platform in platforms:
            if platform.is_solid and self.rect.colliderect(platform.rect):
                if dx > 0:
                    self.rect.right = platform.rect.left
                elif dx < 0:
                    self.rect.left = platform.rect.right

        # Vertical movement & collision
        self.rect.y += self.vel_y
        for platform in platforms:
            if platform.is_solid and self.rect.colliderect(platform.rect):
                if self.vel_y >0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        # Keep player inside the window, reset fall speed if touching the floor
        self.on_ground = self.rect.bottom >=screen_rect.bottom
        self.standing_on = None
        feet_sensor = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, 1)

        for platform in platforms:
            if platform.is_solid and feet_sensor.colliderect(platform.rect):
                self.on_ground = True
                self.standing_on = platform
                platform.onPlayerStand()
                break

        self.rect.clamp_ip(screen_rect)

    def draw(self, surface, camera_x=0):
        pygame.draw.rect(surface, self.color, self.rect.move(-camera_x, 0))

def build_level(grid):
    platforms = []
    spikes = []
    shooters = []
    bullets = []
    npcs = []
    player = Player(0, 0)
    goal = None
    
    for row_idx, row in enumerate(grid):
        for col_idx, cell in enumerate(row):
            x = col_idx * TILE_SIZE
            y = row_idx * TILE_SIZE

            if cell == "#":
                platforms.append(Platform(x, y))
            elif cell == "M":
                platforms.append(MovingPlatform(x, y))
            elif cell == "C":
                platforms.append(CrumblingPlatform(x, y))
            elif cell == "F":
                platforms.append(PhasingPlatform(x, y))
            elif cell == "P":
                player.rect.topleft = (x, y)
            elif cell == "G":
                goal = Goal(x, y)
            elif cell == "^":
                spikes.append(Spike(x, y))
            elif cell == "L":
                shooter = BulletShooter(x, y, direction=-1)
                platforms.append(shooter)
                shooters.append(shooter)
            elif cell == "R":
                shooter = BulletShooter(x, y, direction=1)
                platforms.append(shooter)
                shooters.append(shooter)
            elif cell == "N":
                npcs.append(NPC(x, y + 8, minigame_id = "speedrun"))

    return platforms, spikes, shooters, bullets, player, goal, npcs

def load_level(level_index):
    return build_level(LEVELS[level_index])