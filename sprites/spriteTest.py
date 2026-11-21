import pygame
import sys

# python src/main.py

# python -m venv downTheRabbitHole
# downTheRabbitHole\Scripts\Activate
# pip install -r requirements.txt

pygame.init()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Option A: Load an external image (with transparency)
        self.image = pygame.image.load("sprites/Rabbit.png").convert_alpha()
        ## for the card self.image = pygame.transform.scale(self.image, (100, 100))
        
        # Set the position using its rectangle
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        # Add movement or animation logic here
        pass


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # makes the screen
clock = pygame.time.Clock()  # sets the timing

player = Player(0, 0)
all_sprites = pygame.sprite.Group()
all_sprites.add(player)


speed = 5

running = True
while running:
    clock.tick(60)  #60 fps

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # checks if game window has been closed, if it has been stop running
            running = False

    keys = pygame.key.get_pressed()  # gets input from keybaord
    if keys[pygame.K_w]:
        player.rect.y -= speed
    if keys[pygame.K_s]:
        player.rect.y += speed
    if keys[pygame.K_a]:
        player.rect.x -= speed
    if keys[pygame.K_d]:
        player.rect.x += speed

    screen.fill((50, 50, 50))  # clears the screen
    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()  # updates the screen as needed

pygame.quit()  # closes the game
sys.exit()     # closes the program