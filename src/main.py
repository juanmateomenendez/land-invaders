import pygame
import random
from pathlib import Path

def main():
    pygame.init()

    BASE_DIR = Path(__file__).resolve().parent.parent
    SPRITES_DIR = BASE_DIR / "assets" / "sprites"

    GAME_W, GAME_H = 720, 1280
    WIDTH, HEIGHT = GAME_W, GAME_H
    
    fullscreen = False
    window = pygame.display.set_mode((GAME_W, GAME_H))
    WIN_W, WIN_H = window.get_size()

    pygame.display.set_caption("LAND INVADERS")

    screen = pygame.Surface((GAME_W, GAME_H))

    clock = pygame.time.Clock()
    running = True

    score = 0

    game_state = "PLAYING"

    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 72)

    player_img = pygame.image.load(SPRITES_DIR / "player.png").convert_alpha()
    boat_img = pygame.image.load(SPRITES_DIR / "boat.png").convert_alpha()
    arrow_img = pygame.image.load(SPRITES_DIR / "arrow.png").convert_alpha()
    enemy_shot_img = pygame.image.load(SPRITES_DIR / "enemy_shot.png").convert_alpha()
    shield_img = pygame.image.load(SPRITES_DIR / "shield.png").convert_alpha()

    player_w, player_h = player_img.get_size()
    player_x = (WIDTH - player_w) // 2
    player_y = HEIGHT - player_h - 30
    player_speed = 6

    arrows = []
    arrow_w, arrow_h = arrow_img.get_size()
    arrow_speed = 10
    fire_delay = 300
    last_shot_time = 0

    enemy_shots = []
    enemy_shot_w, enemy_shot_h = enemy_shot_img.get_size()
    enemy_shot_speed = 6
    enemy_shot_delay = 900
    last_enemy_shot_time = 0

    shields = []
    shield_w, shield_h = shield_img.get_size()
    shield_y = player_y - 110
    shield_hp = 6

    shield_positions_x = [90, 250, 420, 570]

    danger_y = shield_y

    for x in shield_positions_x:
        shields.append({"x": x, "y": shield_y, "hp": shield_hp})

    boats = []
    boat_w, boat_h = boat_img.get_size()
    
    rows = 4
    cols = 6
    gap_x = 10
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
                
                if event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        window = pygame.display.set_mode((GAME_W, GAME_H))
                    WIN_W, WIN_H = window.get_size()

                # Restart
                if event.key == pygame.K_r:
                    score = 0
                    arrows = []
                    boats = []
                    enemy_shots = []
                    last_enemy_shot_time = 0
                    
                    player_x = (WIDTH - player_w) //2

                    shields = []
                    for x in shield_positions_x:
                            shields.append({"x": x, "y": shield_y, "hp": shield_hp})

                    for row in range(rows):
                        for col in range(cols):
                            x = offset_x + col * (boat_w + gap_x)
                            y = offset_y + row * (boat_h + gap_y)
                            boats.append({"x": x, "y": y})
                    fleet_dir = 1
                    fleet_speed = 2
                    game_state = "PLAYING"

                #Creating arrow input
                if event.key == pygame.K_SPACE and game_state == "PLAYING":
                    current_time = pygame.time.get_ticks()

                    if current_time - last_shot_time >= fire_delay:
                        arrow_x = player_x + player_w // 2 - arrow_w // 2
                        arrow_y = player_y - arrow_h
                        arrows.append({"x": arrow_x, "y": arrow_y})
                        last_shot_time = current_time
        
        

        # 2) Update (game logic)
        if game_state == "PLAYING":
            # Player movement
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

            # Shields block player arrows
            new_arrows = []

            for a in arrows:
                arrow_rect = pygame.Rect(a["x"], a["y"], arrow_w, arrow_h)
                blocked = False

                for s in shields:
                    shield_rect = pygame.Rect(s["x"], s["y"], shield_w, shield_h)
                    if arrow_rect.colliderect(shield_rect):
                        blocked = True
                        break

                if not blocked:
                    new_arrows.append(a)

            arrows = new_arrows

            # Boat movement
            hit_edge = False

            for b in boats:
                b["x"] += fleet_speed * fleet_dir
                if b["x"] <= 0 or b["x"] + boat_w >= WIDTH:
                    hit_edge = True

            if hit_edge:
                fleet_dir *= -1
                for b in boats:
                    b["y"] += fleet_drop

            # Enemy shoot spawn
            now = pygame.time.get_ticks()
            if boats and now - last_enemy_shot_time >= enemy_shot_delay:
                
                # Random boat from bottom
                columns = {}
                
                for b in boats:
                    col_x = b["x"]
                    if col_x not in columns:
                        columns[col_x] = []
                    columns[col_x].append(b)

                bottom_boats = []

                for col_boats in columns.values():
                    lowest = max(col_boats, key=lambda b: b["y"])
                    bottom_boats.append(lowest)

                shooter = random.choice(bottom_boats)

                shot_x = shooter["x"] + boat_w // 2 - enemy_shot_w // 2
                shot_y = shooter["y"] + boat_h
                enemy_shots.append({"x": shot_x, "y": shot_y})
                last_enemy_shot_time = now
            
            # Enemy shot movement
            for shot in enemy_shots:
                shot["y"] += enemy_shot_speed

            new_enemy_shots = []

            for shot in enemy_shots:
                shot_rect = pygame.Rect(shot["x"], shot["y"], enemy_shot_w, enemy_shot_h)
                blocked = False

                for s in shields:
                    shield_rect = pygame.Rect(s["x"], s["y"], shield_w, shield_h)
                    if shot_rect.colliderect(shield_rect):
                        s["hp"] -= 1
                        blocked = True
                        break

                if not blocked:
                    new_enemy_shots.append(shot)

            enemy_shots = new_enemy_shots

            shields = [s for s in shields if s["hp"] > 0]

            enemy_shots = [s for s in enemy_shots if s["y"] < HEIGHT]

            player_rect = pygame.Rect(player_x, player_y, player_w, player_h)
            
            for s in enemy_shots:
                shot_rect = pygame.Rect(s["x"], s["y"], enemy_shot_w, enemy_shot_h)
                if shot_rect.colliderect(player_rect):
                    game_state = "GAME_OVER"
                    break
            

                    
               
            # Collision logic
            new_arrows = []
            boats_to_remove = set()

            for a in arrows:
                arrow_rect = pygame.Rect(a["x"], a["y"], arrow_w, arrow_h)
                hit = False

                for i, b in enumerate(boats):
                    if i in boats_to_remove:
                        continue

                    boat_rect = pygame.Rect(b["x"], b["y"], boat_w, boat_h)

                    if arrow_rect.colliderect(boat_rect):
                        boats_to_remove.add(i)
                        score += 10
                        hit = True
                        break

                if not hit:
                    new_arrows.append(a)

            arrows = new_arrows
            boats = [b for i, b in enumerate(boats) if i not in boats_to_remove]

            #Win condition
            if len(boats) == 0 and game_state =="PLAYING":
                game_state = "WIN"

            #Lose condition
            for b in boats:
                if b["y"] + boat_h >= danger_y:
                    game_state = "GAME_OVER"
                    enemy_shots = []
                    break

            pass

        # 3) Draw
        screen.fill((10, 10, 10))

        score_text = font.render(f"Score: {score}", True, (230,230,230))
        screen.blit(score_text, (10,10))

        # Player draw
        screen.blit(player_img, (player_x, player_y))
        
        for s in shields:
            screen.blit(shield_img, (s["x"], s["y"]))
            
            # Shield HP Debug
            hp_text = font.render(str(s["hp"]), True, (130, 0, 0))
            screen.blit(hp_text, (s["x"] + 6, s["y"] + 6))

        for arrow in arrows:
            screen.blit(arrow_img, (a["x"], a["y"]))

        for b in boats:
            screen.blit(boat_img, (b["x"], b["y"]))
            
        for s in enemy_shots:
            screen.blit(enemy_shot_img, (s["x"], s["y"]))

        # DEBUG
        pygame.draw.line(
            screen,
            (200, 50, 50),
            (0, danger_y),
            (WIDTH, danger_y),
            2
            )
        

        # Win and Game Over States
        if game_state == "WIN":
            text = big_font.render("YOU WIN!", True, (230, 230, 230))
            hint = font.render("Press R to play again", True, (230, 230, 230))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 60))
            screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 10))

        if game_state == "GAME_OVER":
            text = big_font.render("GAME OVER", True, (230, 230, 230))
            hint = font.render("Press R to try again", True, (230, 230, 230))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 60))
            screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 10))

        scale = min(WIN_W / GAME_W, WIN_H / GAME_H)
        scaled_w = int(GAME_W * scale)
        scaled_h = int(GAME_H * scale)

        scaled_surface = pygame.transform.scale(screen, (scaled_w, scaled_h))

        x = (WIN_W - scaled_w) // 2
        y = (WIN_H - scaled_h) // 2

        window.fill((0, 0, 0))
        window.blit(scaled_surface, (x, y))
        pygame.display.flip()

        # 4) Timing (FPS)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
