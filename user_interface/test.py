import os
import pygame
from config.DataRepo import set_display, get_asset_path
from config import classes



# ----------------------------------------------------------------------
#  KONSTANTEN & PFAD-DEFINITIONEN
# ----------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Pfade zu den Assets


SCARAB_PATH = get_asset_path("Scarab.png",BASE_DIR)
SPIDER_PATH = get_asset_path("Spider.png",BASE_DIR)
WASP_PATH = get_asset_path("Wasp.png",BASE_DIR)
HORNET_PATH = get_asset_path("Hornet.png",BASE_DIR)

SPRITE_WIDTH = 16
SPRITE_HEIGHT = 16
Y_POS_ROW_WALK = 16
Y_POS_ROW_STAND = 0
NUM_FRAMES = 4

SCALE_FACTOR = 4
MAX_MOVEMENT_SPEED_PIXELS_PER_SECOND = 150
ANIMATION_SPEED = 0.12

# Schuss-Einstellungen
BULLET_COOLDOWN = 0.3  # Sekunden zwischen den Schüssen
Bullet = classes.Bullet

# ----------------------------------------------------------------------
#   HILFSFUNKTIONEN
# ----------------------------------------------------------------------

def get_sprite(sheet, x, y, width, height):
    sprite = pygame.Surface([width, height], pygame.SRCALPHA)
    source_rect = pygame.Rect(x, y, width, height)
    sprite.blit(sheet, (0, 0), source_rect)
    return sprite


def load_and_scale_frames(sheet_path):
    try:
        sprite_sheet = pygame.image.load(sheet_path).convert_alpha()
    except pygame.error as e:
        print(f"Fehler beim Laden: {sheet_path}, {e}")
        pygame.quit()
        exit()

    walk_frames = []
    for i in range(NUM_FRAMES):
        frame = get_sprite(sprite_sheet, i * SPRITE_WIDTH, Y_POS_ROW_WALK, SPRITE_WIDTH, SPRITE_HEIGHT)
        scaled = pygame.transform.scale(frame, (SPRITE_WIDTH * SCALE_FACTOR, SPRITE_HEIGHT * SCALE_FACTOR))
        walk_frames.append(scaled)

    stand_frame = get_sprite(sprite_sheet, 0, Y_POS_ROW_STAND, SPRITE_WIDTH, SPRITE_HEIGHT)
    scaled_stand = pygame.transform.scale(stand_frame, (SPRITE_WIDTH * SCALE_FACTOR, SPRITE_HEIGHT * SCALE_FACTOR))

    return {"walk": tuple(walk_frames), "stand": (scaled_stand,)}


# ----------------------------------------------------------------------
#  HAUPTPROGRAMM
# ----------------------------------------------------------------------

def main():
    if not pygame.get_init():
        pygame.init()

    DEBUG_MODE = True
    font = pygame.font.Font(None, 20) if pygame.font.get_init() else None

    display, display_width, display_height = set_display(800, 400, "Robot Combat Test")

    options = {
        "Scarab": load_and_scale_frames(SCARAB_PATH),
        "Spider": load_and_scale_frames(SPIDER_PATH),
        "Wasp": load_and_scale_frames(WASP_PATH),
        "Hornet": load_and_scale_frames(HORNET_PATH),
    }
    frames = options["Spider"]

    # Charakter-Variablen
    sprite_rect = frames["stand"][0].get_rect(centerx=display_width // 2, bottom=display_height // 2)
    facing_right = True
    current_frame_index = 0.0

    # Projektil-Variablen
    bullets = []
    shoot_cooldown_timer = 0.0

    # Steuerungs-Flags
    moving_keys = {"left": False, "right": False, "up": False, "down": False}
    is_shooting = False

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0  # Delta Time in Sekunden

        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                if event.key == pygame.K_LEFT:
                    moving_keys["left"] = True
                    facing_right = False
                if event.key == pygame.K_RIGHT:
                    moving_keys["right"] = True
                    facing_right = True
                if event.key == pygame.K_UP:    moving_keys["up"] = True
                if event.key == pygame.K_DOWN:  moving_keys["down"] = True
                if event.key == pygame.K_SPACE: is_shooting = True
                if event.key == pygame.K_d:     DEBUG_MODE = not DEBUG_MODE

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:  moving_keys["left"] = False
                if event.key == pygame.K_RIGHT: moving_keys["right"] = False
                if event.key == pygame.K_UP:    moving_keys["up"] = False
                if event.key == pygame.K_DOWN:  moving_keys["down"] = False
                if event.key == pygame.K_SPACE: is_shooting = False

        # --- UPDATE LOGIK ---

        #  Bewegung
        dist = MAX_MOVEMENT_SPEED_PIXELS_PER_SECOND * dt
        if moving_keys["left"]:  sprite_rect.x -= dist
        if moving_keys["right"]: sprite_rect.x += dist
        if moving_keys["up"]:    sprite_rect.y -= dist
        if moving_keys["down"]:  sprite_rect.y += dist

        # Bildschirm-Grenzen
        sprite_rect.clamp_ip(pygame.Rect(0, 0, display_width, 350))  # Vereinfachte Begrenzung


        if shoot_cooldown_timer > 0:
            shoot_cooldown_timer -= dt

        if is_shooting and shoot_cooldown_timer <= 0:
            bullet_dir = 1 if facing_right else -1
            # Kugel startet etwas versetzt vom Zentrum des Roboters
            start_x = sprite_rect.right if facing_right else sprite_rect.left
            new_bullet = Bullet(start_x, sprite_rect.centery, bullet_dir)
            bullets.append(new_bullet)
            shoot_cooldown_timer = BULLET_COOLDOWN

        #  Projektile updaten
        for bullet in bullets[:]:
            bullet.update(dt)
            if bullet.rect.x < 0 or bullet.rect.x > display_width:
                bullets.remove(bullet)

        #  Animation
        is_moving = any(moving_keys.values())
        if is_moving:
            current_frame_index += dt / ANIMATION_SPEED
            if current_frame_index >= len(frames["walk"]):
                current_frame_index = 0
            current_frame = frames["walk"][int(current_frame_index)]
        else:
            current_frame = frames["stand"][0]

        if not facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)

        # --- RENDERING ---
        display.fill((50, 65, 70))

        # Kugeln zeichnen
        for bullet in bullets:
            bullet.draw(display)

        # Charakter zeichnen
        display.blit(current_frame, sprite_rect)

        # Debug Infos
        if DEBUG_MODE:
            pygame.draw.rect(display, (255, 0, 0), sprite_rect, 1)
            if font:
                fps = clock.get_fps()
                debug_txt = font.render(f"FPS: {fps:.1f} | Bullets: {len(bullets)}", True, (255, 255, 255))
                display.blit(debug_txt, (10, 10))

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()