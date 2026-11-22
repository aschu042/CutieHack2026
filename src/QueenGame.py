import sys
import pygame

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 23)
big_font = pygame.font.SysFont(None, 48)

player = pygame.Rect(375, 500, 50, 50)
queen = pygame.Rect(275, 50, 250, 250)

# Each key holds what the Queen says and a list of (player_reply, next_key) choices
dialogue = {
    "start": {
        "queen": "Who dares enter my garden?!",
        "responses": [
            ("I'm lost, Your Majesty.", "polite"),
            ("Oh great, more nonsense", "rude"),
        ],
    },
    "polite": {
        "queen": "Hmph. Good manners are rare. You may speak.",
        "responses": [
            ("Can you help me find the exit?", "help"),
        ],
    },
    "rude": {
        "queen": "Such rudeness! Off with her head! Right now!",
        "responses": [],
    },
    "help": {
        "queen": "Exit? What exit? This is my kingdom and by entering it you have become mine!",
        "responses": [
            ("But I wish to go home.", "leave"),
            ("Your not my queen, send me home", "bold"),
        ],
    },
    "bold": {
        "queen": "Bold words! Off with their head!",
        "responses": [
            ("Bring it on!", "leave"),
            ("Wait, I take it back!", "cowardly"),
        ],
    },
    "cowardly": {
        "queen": "Die",
        "responses": [],
    },
    "leave": {
        "queen": "Such hearasy!",
        "responses": [
            ("I must go home, this is not where I belong", "resolute"),
        ],
    },
    "resolute": {
        "queen": "You are so dispicable that even beheading isn't enough! I banish you",
        "responses": [],
    },
}

current_node = "start"
game_state = "playing"  # "playing", "game_over", or "win"
restart_btn = pygame.Rect(300, 430, 200, 40)


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
            if game_state == "playing":
                for btn_rect, text, next_node in response_buttons:
                    if btn_rect.collidepoint(event.pos):
                        current_node = next_node
                        response_buttons = get_response_buttons(current_node)

                        # Check if we reached an end option (no responses left)
                        if not dialogue[current_node]["responses"]:
                            if current_node == "resolute":
                                game_state = "win"
                            else:
                                game_state = "game_over"
                        break
            else:
                # Reset back to the start when clicking "Try Again"
                if restart_btn.collidepoint(event.pos):
                    current_node = "start"
                    game_state = "playing"
                    response_buttons = get_response_buttons(current_node)

    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, (0, 255, 0), player)
    pygame.draw.rect(screen, (0, 255, 0), queen)

    # 1. Draw the Queen's speech box and text
    queen_box = pygame.Rect(30, 310, 740, 46)
    pygame.draw.rect(screen, (240, 240, 240), queen_box)
    pygame.draw.rect(screen, (0, 0, 0), queen_box, 2)

    queen_text = font.render(dialogue[current_node]["queen"], True, (0, 0, 0))
    screen.blit(queen_text, queen_text.get_rect(center=queen_box.center))

    # 2. Draw response buttons OR the Game Over / Win status
    if game_state == "playing":
        for btn_rect, text, _ in response_buttons:
            bg_color = (200, 230, 255) if btn_rect.collidepoint(mouse_pos) else (230, 230, 230)
            pygame.draw.rect(screen, bg_color, btn_rect)
            pygame.draw.rect(screen, (0, 0, 0), btn_rect, 2)

            btn_text = font.render(text, True, (0, 0, 0))
            screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))
    else:
        if game_state == "game_over":
            end_surface = big_font.render("GAME OVER", True, (200, 0, 0))
        else:
            end_surface = big_font.render("YOU SURVIVED!", True, (0, 160, 0))

        screen.blit(end_surface, end_surface.get_rect(center=(width // 2, 395)))

        btn_color = (200, 230, 255) if restart_btn.collidepoint(mouse_pos) else (230, 230, 230)
        pygame.draw.rect(screen, btn_color, restart_btn)
        pygame.draw.rect(screen, (0, 0, 0), restart_btn, 2)
        restart_text = font.render("Try Again", True, (0, 0, 0))
        screen.blit(restart_text, restart_text.get_rect(center=restart_btn.center))

    pygame.display.flip()

pygame.quit()
sys.exit()