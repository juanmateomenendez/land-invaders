import pygame
import math
import random
from pathlib import Path

def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.init()

    BASE_DIR = Path(__file__).resolve().parent.parent
    SPRITES_DIR = BASE_DIR / "assets" / "sprites"
    SOUNDS_DIR = BASE_DIR / "assets" / "sounds"
    FONTS_DIR = BASE_DIR / "assets" / "fonts"

    GAME_W, GAME_H = 720, 1280
    WIDTH, HEIGHT = GAME_W, GAME_H

    UI_PAD = 20
    BORDER_W = 4
    GREEN = (00, 230, 00)
    TEXT = (00, 230, 00)
    BG = (10, 10, 10)
    
    fullscreen = False
    window = pygame.display.set_mode((GAME_W, GAME_H))
    WIN_W, WIN_H = window.get_size()

    pygame.display.set_caption("LAND INVADERS")

    screen = pygame.Surface((GAME_W, GAME_H))

    def iblit(surface, img, x, y):
        surface.blit(img, (int(x), int(y)))

    def draw_center_text(surface, text_surf, y):
        surface.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, y))

    def reset_game():
        nonlocal score, arrows, boats, enemy_shots, shields, explosions, pending_win
        nonlocal last_shot_time, last_enemy_shot_time
        nonlocal player_x, fleet_dir, fleet_speed, last_fleet_step_time
        score = 0
        arrows = []
        boats = []
        enemy_shots = []
        last_shot_time = 0
        last_enemy_shot_time = 0
        last_fleet_step_time = 0
        explosions = []
        pending_win = False

        player_x = (WIDTH - player_w) // 2

        
        shields = []
        for x in shield_positions_x:
            shields.append ({"x": x, "y": shield_y, "hp": shield_hp})

        for row in range(rows):
            for col in range(cols):
                x = offset_x + col * (boat_w + gap_x)
                y = offset_y + row * (boat_h + gap_y)
                boats.append({"x": x, "y": y})

        fleet_dir = 1
        fleet_speed = 20

    clock = pygame.time.Clock()
    running = True
    score = 0

    font = pygame.font.Font(FONTS_DIR / "AtariClassicChunky-PxXP.ttf", 20)
    big_font = pygame.font.Font(FONTS_DIR / "AtariClassicChunky-PxXP.ttf", 40)

    # Load sprites
    player_img = pygame.image.load(SPRITES_DIR / "player.png").convert_alpha()
    boat_img = pygame.image.load(SPRITES_DIR / "boat.png").convert_alpha()
    arrow_img = pygame.image.load(SPRITES_DIR / "arrow.png").convert_alpha()
    shield_sheet = pygame.image.load(SPRITES_DIR / "shield_sheet.png").convert_alpha()
    explosion_sheet = pygame.image.load(SPRITES_DIR / "explosion.png").convert_alpha()

    title_frames = [
        pygame.image.load(SPRITES_DIR / "title_01.png"),
        pygame.image.load(SPRITES_DIR / "title_02.png"),
        pygame.image.load(SPRITES_DIR / "title_03.png")
    ]

    firework_frames = [
        pygame.image.load(SPRITES_DIR / "firework_01.png").convert_alpha(),
        pygame.image.load(SPRITES_DIR / "firework_02.png").convert_alpha(),
        pygame.image.load(SPRITES_DIR / "firework_03.png").convert_alpha(),
        pygame.image.load(SPRITES_DIR / "firework_04.png").convert_alpha(),
        pygame.image.load(SPRITES_DIR / "firework_05.png").convert_alpha(),
        pygame.image.load(SPRITES_DIR / "firework_06.png").convert_alpha(),
        pygame.image.load(SPRITES_DIR / "firework_07.png").convert_alpha(),
        pygame.image.load(SPRITES_DIR / "firework_08.png").convert_alpha()
    ]

    shield_states = []
    shield_state_w = 50
    shield_state_h = 47

    num_states = shield_sheet.get_width() // shield_state_w
    assert shield_sheet.get_width() % shield_state_w == 0, "Shield sheet width not divisible by state width"

    for i in range(num_states):
        frame = shield_sheet.subsurface(
            pygame.Rect(i * shield_state_w, 0, shield_state_w, shield_state_h)
        )
        shield_states.append(frame)

    cannonball_img = pygame.image.load(
    SPRITES_DIR / "cannonball.png"
    ).convert_alpha()

    scale_factor = 0.70
    cw, ch = cannonball_img.get_size()
    cannonball_img = pygame.transform.scale(
        cannonball_img,
        (int(cw * scale_factor), int(ch * scale_factor))
    )
    
    enemy_shot_imgs = [
        cannonball_img,
        pygame.image.load(SPRITES_DIR / "bible.png").convert_alpha(),
        pygame.image.load(SPRITES_DIR / "blanket.png").convert_alpha(),
        pygame.image.load(SPRITES_DIR / "crucifix.png").convert_alpha(),
        pygame.image.load(SPRITES_DIR / "treaty.png").convert_alpha()
    ]

    enemy_shot_weights = [
        60, # cannonball
        10, # others vvv
        10,
        10,
        10
    ]

    explosion_frames = []

    frame_w = 40
    frame_h = 40
    num_frames = explosion_sheet.get_width() // frame_w

    for i in range(num_frames):
        frame = explosion_sheet.subsurface(
            pygame.Rect(i * frame_w, 0, frame_w, frame_h)
        )
        explosion_frames.append(frame)

    #Load sounds
    snd_shoot = pygame.mixer.Sound(SOUNDS_DIR / "shoot.wav")
    snd_enemy_shoot = pygame.mixer.Sound(SOUNDS_DIR / "enemy_shoot.wav")
    snd_hit = pygame.mixer.Sound(SOUNDS_DIR / "hit.wav")
    snd_shield_hit = pygame.mixer.Sound(SOUNDS_DIR / "shield_hit.wav")
    snd_win = pygame.mixer.Sound(SOUNDS_DIR / "win.wav")
    snd_game_over = pygame.mixer.Sound(SOUNDS_DIR / "game_over.ogg")

    music_start = SOUNDS_DIR / "start-music.ogg"
    music_game = SOUNDS_DIR / "game-music.ogg"

    # pygame.mixer.music.load(SOUNDS_DIR / "game-music.ogg")
    # pygame.mixer.music.set_volume(0.3)
    # pygame.mixer.music.play(loops=-1)

    # Sound volume
    snd_shoot.set_volume(0.4)
    snd_enemy_shoot.set_volume(0.35)
    snd_hit.set_volume(0.5)
    snd_shield_hit.set_volume(0.4)
    snd_win.set_volume(0.6)
    snd_game_over.set_volume(0.6)

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
    enemy_shot_speed = 6
    enemy_shot_delay = 900
    last_enemy_shot_time = 0

    shields = []
    shield_w, shield_h = shield_state_w, shield_state_h
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
    fleet_speed = 20
    fleet_drop = 24
    fleet_step_delay = 125
    last_fleet_step_time = 0

    EXPLOSION_SPEED = 60
    FIREWORK_SPEED = 160

    title_frame = 0
    TITLE_SPEED = 500
    last_title_time = 0

    HINT_LINES = ["PRESS START", "TO FIGHT", "THE COLONIZERS"]

    HINT_Y_OFFSET = 40      
    HINT_LINE_SPACING = 8    
    HINT_FADE_SPEED = 1.5   
    HINT_FLICKER_SPEED = 3


    explosions = []

    reset_game()

    def play_music(path, volume=0.3, loops=-1, fade_ms=0):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)

    play_music(music_start, volume=0.3)
    game_state = "START"
    pending_win = False

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
                if event.key == pygame.K_r and game_state in ("WIN", "GAME_OVER"):
                    reset_game()
                    snd_game_over.stop()
                    snd_win.stop()
                    play_music(music_game, volume=0.3)
                    game_state = "PLAYING"

                #Creating arrow input
                if event.key == pygame.K_SPACE:
                    if game_state == "START":
                        reset_game()
                        snd_game_over.stop()
                        snd_win.stop()
                        play_music(music_game, volume=0.3)
                        game_state = "PLAYING"
                        
                    elif game_state == "PLAYING":
                        current_time = pygame.time.get_ticks()
                        if current_time - last_shot_time >= fire_delay:
                            arrow_x = player_x + player_w // 2 - arrow_w // 2
                            arrow_y = player_y - arrow_h
                            arrows.append({"x": arrow_x, "y": arrow_y})
                            snd_shoot.play()
                            last_shot_time = current_time

        # 2) Update (game logic)

        if game_state == "START":
            now = pygame.time.get_ticks()

            if now - last_title_time > TITLE_SPEED:
                title_frame = (title_frame + 1) % len(title_frames)
                last_title_time = now

        if game_state == "PLAYING":
            now = pygame.time.get_ticks()

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

            for e in explosions[:]:
                if now - e["last_time"] > e["speed"]:
                    e["frame"] += 1
                    e["last_time"] = now

                    if e["frame"] >= len(e["frames"]):
                        if e.get("next_frames") is not None:
                            e["frames"] = e["next_frames"]
                            e["speed"] = e.get("next_speed", e["speed"])
                            e["frame"] = 0
                            e["next_frames"] = None
                        else:
                            explosions.remove(e)


            # Boat movement
            hit_edge = False
            margin = 20
            left_bound = UI_PAD + margin
            right_bound = WIDTH - UI_PAD - margin

            if now - last_fleet_step_time >= fleet_step_delay:
                for b in boats:
                    b["x"] += fleet_speed * fleet_dir
                    if b["x"] <= left_bound or b["x"] + boat_w >= right_bound:
                        hit_edge = True

                if hit_edge:
                    fleet_dir *= -1
                    for b in boats:
                        b["y"] += fleet_drop
                
                last_fleet_step_time = now

            # Enemy shoot spawn
            if (not pending_win) and boats and now - last_enemy_shot_time >= enemy_shot_delay:
                
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

                img = random.choices(
                    enemy_shot_imgs,
                    weights=enemy_shot_weights,
                    k=1
                )[0]

                w, h = img.get_size()

                shot_x = shooter["x"] + boat_w // 2 - w // 2
                shot_y = shooter["y"] + boat_h

                enemy_shots.append({
                    "x": shot_x,
                    "y": shot_y,
                    "w": w,
                    "h": h,
                    "img": img
                })

                snd_enemy_shoot.play()
                last_enemy_shot_time = now
            
            # Enemy shot movement
            for shot in enemy_shots:
                shot["y"] += enemy_shot_speed

            new_enemy_shots = []

            for shot in enemy_shots:
                shot_rect = pygame.Rect(shot["x"], shot["y"], shot["w"], shot["h"])
                blocked = False

                for s in shields:
                    shield_rect = pygame.Rect(s["x"], s["y"], shield_w, shield_h)
                    if shot_rect.colliderect(shield_rect):
                        s["hp"] -= 1
                        blocked = True
                        snd_shield_hit.play()
                        break

                if not blocked:
                    new_enemy_shots.append(shot)

            enemy_shots = new_enemy_shots

            shields = [s for s in shields if s["hp"] > 0]

            enemy_shots = [s for s in enemy_shots if s["y"] < HEIGHT]
            player_rect = pygame.Rect(player_x, player_y, player_w, player_h)

        
            # Collision logic

            for s in enemy_shots:
                shot_rect = pygame.Rect(s["x"], s["y"], s["w"], s["h"])
                if shot_rect.colliderect(player_rect) and not pending_win:
                    if game_state != "GAME_OVER":
                        game_state = "GAME_OVER"
                        pygame.mixer.music.fadeout(2000)
                        snd_game_over.play(loops=-1)
                        break

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
                        snd_hit.play()
                        remaining_after_hit = len(boats) - (len(boats_to_remove))
                        will_win = (remaining_after_hit == 0)
                        if will_win:
                            pending_win = True
                        explosions.append({
                            "cx": b["x"] + boat_w // 2,
                            "cy": b["y"] + boat_h // 2,
                            "frames": explosion_frames,
                            "frame": 0,
                            "speed": EXPLOSION_SPEED,
                            "last_time": pygame.time.get_ticks(),
                            "next_frames": firework_frames if will_win else None,
                            "next_speed": FIREWORK_SPEED
                            })
                        break


                if not hit:
                    new_arrows.append(a)

            arrows = new_arrows
            boats = [b for i, b in enumerate(boats) if i not in boats_to_remove]

            #Win condition
            if pending_win and len(explosions) == 0 and game_state =="PLAYING":
                game_state = "WIN"
                pending_win = False
                pygame.mixer.music.fadeout(2000)
                snd_win.play(loops=-1)

            #Lose condition
            for b in boats:
                if b["y"] + boat_h >= danger_y:
                    if game_state != "GAME_OVER":
                        game_state = "GAME_OVER"
                        enemy_shots = []
                        pygame.mixer.music.fadeout(2000)
                        snd_game_over.play(loops=-1)
                        break

            pass

        # 3) DRAW
        screen.fill(BG)

        for e in explosions:
            img = e["frames"][e["frame"]]
            w, h = img.get_size()
            x = int(e["cx"] - w // 2)
            y = int(e["cy"] - h // 2)
            screen.blit(img, (x, y))

        pygame.draw.rect(
            screen,
            GREEN,
            pygame.Rect(UI_PAD, UI_PAD, WIDTH - UI_PAD * 2, HEIGHT - UI_PAD * 2),
            BORDER_W
        )

        if game_state == "START":

            title_img = title_frames[title_frame]
            draw_center_text(screen, title_img, HEIGHT // 2 - 550)

            # Hint text with fade and flicker
            now_s = pygame.time.get_ticks() / 1000.0
            pulse = (math.sin(now_s * HINT_FADE_SPEED * 2 * math.pi) + 1) / 2
            base_alpha = int(80 + pulse * 175)
            flicker = (math.sin(now_s * HINT_FLICKER_SPEED * 2 * math.pi) + 1) / 2
            alpha = max(0, min(255, base_alpha - int(flicker * 50)))

            line_h = big_font.get_height()
            block_h = len(HINT_LINES) * line_h + (len(HINT_LINES) - 1) * HINT_LINE_SPACING
            start_y = HEIGHT // 2 - block_h // 2 + HINT_Y_OFFSET

            for i, line in enumerate(HINT_LINES):
                surf = big_font.render(line, True, GREEN)
                surf.set_alpha(alpha)
                draw_center_text(screen, surf, start_y + i * (line_h + HINT_LINE_SPACING))


        if game_state != "START":
            score_text = font.render(f"SCORE: {score}", True, TEXT)
            screen.blit(score_text, (UI_PAD + 8, UI_PAD + 8))

            # Player draw
            iblit(screen, player_img, player_x, player_y)
            
            for s in shields:
                idx = shield_hp - s["hp"]   # 6hp->0, 5hp->1, ... 1hp->5
                idx = max(0, min(len(shield_states) - 1, idx))
                iblit(screen, shield_states[idx], s["x"], s["y"])

                
                # Shield HP Debug
                hp_text = font.render(str(s["hp"]), True, (130, 0, 0))
                screen.blit(hp_text, (s["x"] + 6, s["y"] + 6))

            for arrow in arrows:
                iblit(screen, arrow_img, arrow["x"], arrow["y"])

            for b in boats:
                iblit(screen, boat_img, b["x"], b["y"])
                
            for s in enemy_shots:
                iblit(screen, s["img"], s["x"], s["y"])

        # Win and Game Over States
        if game_state == "WIN":
            text = big_font.render("YOU WIN!", True, TEXT)
            hint = font.render("Press R to play again", True, TEXT)

            draw_center_text(screen, text, HEIGHT // 2 - 120)
            draw_center_text(screen, hint, HEIGHT // 2 + 10)

        if game_state == "GAME_OVER":
            text = big_font.render("GAME OVER", True, TEXT)
            hint = font.render("Press R to try again", True, TEXT)

            draw_center_text(screen, text, HEIGHT // 2 - 120)
            draw_center_text(screen, hint, HEIGHT // 2 + 10)

        scale = min(WIN_W // GAME_W, WIN_H // GAME_H)
        if scale < 1:
            scale = 1
        scaled_w = GAME_W * scale
        scaled_h = GAME_H * scale

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
