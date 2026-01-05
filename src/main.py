import pygame

def main():
    pygame.init()

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("LAND INVADERS")

    clock = pygame.time.Clock()
    running = True

    player_w, player_h = 60, 20
    player_x = (WIDTH - player_w) // 2
    player_y = HEIGHT - 60
    player_speed = 6

    while running:
        # 1) Events (input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2) Update (game logic) — empty for now
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += player_speed

        player_x = max(0, min(WIDTH - player_w, player_x))
        # 3) Draw
        screen.fill((10, 10, 20))  # dark background
        pygame.display.flip()
        pygame.draw.rect(screen, (220, 220, 80), (player_x, player_y, player_w, player_h))

        # 4) Timing (FPS)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
