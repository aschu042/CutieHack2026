import sys
import pygame

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 26)

player = pygame.Rect(375, 500, 50, 50)
queen = pygame.Rect(275, 50, 250, 250)

# Each key holds what the Queen says and a list of (player_reply, next_key) choices
dialogue = {
    "start": {
        "queen": "Who dares enter my garden?!",
        "responses": [
            ("I'm lost, Your Majesty.", "polite"),
            ("I'm here to challenge you!", "bold"),
            ("Just passing through.", "leave"),
        ],
    },
    
}

current_node = "start"


def get_response_buttons(node_key):
    """Creates a clickable Rect for each premade response in the current node."""
    responses = dialogue[node_key]["responses"]
    buttons = []
    for i, (text, next_node) in enumerate(responses):
        btn_rect = pygame.Rect(200, 368 + i * 42, 400, 34)
        buttons.append((btn_rect, text, next_node))
    return buttons


response_buttons = get_response_buttons(current_node)

running = True
while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn_rect, text, next_node in response_buttons:
                if btn_rect.collidepoint(event.pos):
                    current_node = next_node
                    response_buttons = get_response_buttons(current_node)
                    break

    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, (0, 255, 0), player)
    pygame.draw.rect(screen, (0, 255, 0), queen)

    # 1. Draw the Queen's speech box and text
    queen_box = pygame.Rect(125, 310, 550, 46)
    pygame.draw.rect(screen, (240, 240, 240), queen_box)
    pygame.draw.rect(screen, (0, 0, 0), queen_box, 2)

    queen_text = font.render(dialogue[current_node]["queen"], True, (0, 0, 0))
    screen.blit(queen_text, queen_text.get_rect(center=queen_box.center))

    # 2. Draw the player's premade response buttons
    for btn_rect, text, _ in response_buttons:
        # Highlight button when hovering with the mouse
        bg_color = (200, 230, 255) if btn_rect.collidepoint(mouse_pos) else (230, 230, 230)
        pygame.draw.rect(screen, bg_color, btn_rect)
        pygame.draw.rect(screen, (0, 0, 0), btn_rect, 2)

        btn_text = font.render(text, True, (0, 0, 0))
        screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

    pygame.display.flip()

pygame.quit()
sys.exit()