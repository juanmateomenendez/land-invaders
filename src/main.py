import pygame

def main():
    pygame.init()

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("LAND INVADERS")

    clock = pygame.time.Clock()
    running = True

    while running:
        # 1) Events (input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2) Update (game logic) — empty for now

        # 3) Draw
        screen.fill((10, 10, 20))  # dark background
        pygame.display.flip()

        # 4) Timing (FPS)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
