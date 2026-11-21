import pygame

# Grid dimensions and window sizing
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

# Colors (R, G, B)
GRID_LINE_COLOR = (60, 60, 60)
TILE_COLORS = {
    0: (0, 255, 0),   # Cleared
    5: (50, 50, 50),  # Untouched
    6: (255, 0, 0),   # Flag
}

pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

def load_tile(filename):
    img = pygame.image.load(filename).convert_alpha()
    if filename == "sprites/Cat.png":
        return pygame.transform.scale(img, (tileSize + 37, tileSize + 37))
    return pygame.transform.scale(img, (tileSize, tileSize))


# States 1, 2, 3, 4, and 7 are centered images
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

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            col = mouse_x // tileSize
            row = mouse_y // tileSize
            revealed[row][col] = True
            if event.button == 1 and not flagged[row][col]:  # Left click reveals unflagged tiles
                revealed[row][col] = True
            elif event.button == 3:                          # Right click toggles color 6
                flagged[row][col] = not flagged[row][col]
                if not flagged[row][col]:
                    revealed[row][col] = False

    # Pass 1: Draw base rectangles and grid lines
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(
                col * tileSize,
                row * tileSize,
                tileSize,
                tileSize
            )

            if flagged[row][col]:
                color = TILE_COLORS[6]
            elif not revealed[row][col]:
                color = 5
            else:
                tile_type = solution_grid[row][col]
                # Uses TILE_COLORS for 0, 6; falls back to color 0 under images
                color = TILE_COLORS.get(tile_type, TILE_COLORS[0])

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1)

    # Pass 2: Draw centered images for revealed states 1, 2, 3, 4, and 7
    for row in range(rows):
        for col in range(cols):
            if revealed[row][col] and not flagged[row][col]:
                tile_type = solution_grid[row][col]
                if tile_type in TILE_IMAGES:
                    tile_rect = pygame.Rect(
                        col * tileSize,
                        row * tileSize,
                        tileSize,
                        tileSize
                    )
                    img = TILE_IMAGES[tile_type]
                    img_rect = img.get_rect(center=tile_rect.center)
                    screen.blit(img, img_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()