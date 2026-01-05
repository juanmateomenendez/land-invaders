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

    arrows = []
    arrow_w, arrow_h = 6, 18
    arrow_speed = 10

    boats = []
    boat_w, boat_h = 48, 24
    
    rows = 4
    cols = 10
    gap_x = 14
    gap_y = 14
    offset_x = 60
    offset_y = 60

    for row in range(rows):
        for col in range(cols):
            x = offset_x + col * (boat_w + gap_x)
            y = offset_y + row * (boat_h + gap_y)
            boats.append({"x": x, "y": y})

    fleet_dir = 1
    fleet_speed = 2
    fleet_drop = 24

    while running:
        # 1) Events (input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                #Creating arrow input
                if event.key == pygame.K_SPACE:
                    arrow_x = player_x + player_w // 2 - arrow_w // 2
                    arrow_y = player_y - arrow_h
                    arrows.append({"x": arrow_x, "y": arrow_y})

        # 2) Update (game logic) — empty for now
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += player_speed

        player_x = max(0, min(WIDTH - player_w, player_x))

        # Arrow movement
        for arrow in arrows:
            arrow["y"] -= arrow_speed
        #Arrow cleanup
        arrows = [a for a in arrows if a["y"] > -arrow_h]

        hit_edge = False
        for b in boats:
            b["x"] += fleet_speed * fleet_dir
            if b["x"] <= 0 or b["x"] + boat_w >= WIDTH:
                hit_edge = True
        if hit_edge:
            fleet_dir *= -1
            for b in boats:
                b["y"] += fleet_drop

        # 3) Draw
        screen.fill((10, 10, 10))
        pygame.draw.rect(
            screen, 
            (220, 220, 80), 
            (player_x, player_y, player_w, player_h)
            )
        for arrow in arrows:
            pygame.draw.rect(
                screen, 
                (40, 40, 40), 
                (arrow["x"], arrow["y"], arrow_w, arrow_h)
                )
        for b in boats:
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (b["x"], b["y"], boat_w, boat_h)
                )
        pygame.display.flip()

        # 4) Timing (FPS)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
