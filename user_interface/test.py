import os
import pygame
from config.DataRepo import set_display


# ----------------------------------------------------------------------
#  KLASSEN DEFINITIONEN
# ----------------------------------------------------------------------

class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 12, 4)
        self.color = (255, 200, 0)
        self.speed = 600
        self.direction = direction

    def update(self, dt):
        self.rect.x += self.speed * dt * self.direction

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


class Enemy:
    def __init__(self, x, y, frames, speed=100, distance=200):
        self.frames = frames
        self.rect = self.frames[0].get_rect(topleft=(x, y))
        self.start_x = x
        self.distance = distance
        self.speed = speed
        self.direction = 1
        self.anim_index = 0.0

    def update(self, dt):
        self.rect.x += self.speed * dt * self.direction
        if self.rect.x >= self.start_x + self.distance:
            self.direction = -1
        elif self.rect.x <= self.start_x:
            self.direction = 1
        self.anim_index += dt * 6

    def draw(self, surface):
        idx = int(self.anim_index) % len(self.frames)
        img = self.frames[idx]
        if self.direction == 1:
            img = pygame.transform.flip(img, True, False)
        surface.blit(img, self.rect)


class Tile:
    def __init__(self, x, y, size, image, is_wall=False, is_deadly=False):
        self.rect = pygame.Rect(x, y, size, size)
        self.image = image
        self.is_wall = is_wall
        self.is_deadly = is_deadly

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# ----------------------------------------------------------------------
#  HILFSFUNKTIONEN
# ----------------------------------------------------------------------

def get_sprite(sheet, x, y, width, height):
    """Extrahiert einen präzisen Ausschnitt."""
    sprite = pygame.Surface([width, height], pygame.SRCALPHA)
    sprite.blit(sheet, (0, 0), pygame.Rect(x, y, width, height))
    return sprite


def load_tileset(path, source_size, target_size):
    sheet = pygame.image.load(path).convert_alpha()
    tiles = []
    for y in range(0, sheet.get_height(), source_size):
        for x in range(0, sheet.get_width(), source_size):
            img = get_sprite(sheet, x, y, source_size, source_size)
            tiles.append(pygame.transform.scale(img, (target_size, target_size)))
    return tiles


def load_robot(path, frame_w=16, frame_h=16, scale=4):
    """
    Lädt die ersten 2 Frames eines Roboters.
    Standardmäßig 16x16, für Hornet beim Aufruf 22x20 angeben.
    """
    sheet = pygame.image.load(path).convert_alpha()
    # Nur die ersten zwei Frames für die Flug-Animation
    f1 = get_sprite(sheet, 0, 0, frame_w, frame_h)
    f2 = get_sprite(sheet, frame_w, 0, frame_w, frame_h)

    frames = [pygame.transform.scale(f, (frame_w * scale, frame_h * scale)) for f in (f1, f2)]
    return {"walk": tuple(frames), "stand": frames[0]}


# ----------------------------------------------------------------------
#  MAIN PROGRAMM
# ----------------------------------------------------------------------

def main():
    pygame.init()
    display, display_width, display_height = set_display(1080, 960, "Robot Warfare - Animation Fix")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS = os.path.normpath(os.path.join(BASE_DIR, "..", "assets", "Robot Warfare Asset Pack 22-11-24"))

    TILESET_PATH = os.path.join(ASSETS, "Tileset", "tileset_compressed.png")
    SCARAB_PATH = os.path.join(ASSETS, "Robots", "Scarab.png")
    HORNET_PATH = os.path.join(ASSETS, "Robots", "Hornet.png")
    WASP_PATH = os.path.join(ASSETS, "Robots", "Wasp.png")


    all_tile_images = load_tileset(TILESET_PATH, 16, 48)

    # HIER GRÖSSEN ANGEBEN:
    scarab_data = load_robot(SCARAB_PATH, 16, 16, 4)
    wasp_data = load_robot(WASP_PATH, 16, 16, 4)
    hornet_data = load_robot(HORNET_PATH, 22, 20, 4)  # Hornet ist die Ausnahme

    level_data = [
        [10, 10, 10, 10, 10, 10, 10, 10, 10, 10,10,10,10,10,10,10,10,10,10,10],
        [10,1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 10],
        [10, 1, 1, 1, 1, 1, 154, 1, 1, 1, 1, 1, 1, 1, 1, 1, 153, 1, 1, 10],
        [10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 10],
        [10, 1, 153, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 138, 139, 1, 1, 1, 10],
        [10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 148, 149, 1, 1, 1, 10],
        [10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 154, 1, 1, 1, 1, 1, 1, 1, 10],
        [10, 1, 1, 1, 1, 153, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 10],
        [10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 153, 1, 1, 1, 1, 1, 10],
        [10, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 10],
        [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
        ]

    START_POS = (100, 48)
    level_tiles = []
    for r_idx, row in enumerate(level_data):
        for c_idx, t_idx in enumerate(row):
            if t_idx != -1:
                level_tiles.append(
                    Tile(c_idx * 48, r_idx * 48, 48, all_tile_images[t_idx], (10 <= t_idx <= 11), (12 <= t_idx <= 14)))

    sprite_rect = scarab_data["stand"].get_rect(topleft=START_POS)

    # Gegner mit den korrekten "walk" frames aus der robot_data
    enemies = [
        Enemy(400, 48, hornet_data["walk"], speed=120, distance=200),
        Enemy(200, 96, wasp_data["walk"], speed=80, distance=100)
    ]

    bullets = []
    facing_right = True
    moving = {"L": False, "R": False, "U": False, "D": False}
    shoot_cooldown = 0
    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60) / 1000.0
        if shoot_cooldown > 0: shoot_cooldown -= dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:  moving["L"], facing_right = True, False
                if event.key == pygame.K_RIGHT: moving["R"], facing_right = True, True
                if event.key == pygame.K_UP:    moving["U"] = True
                if event.key == pygame.K_DOWN:  moving["D"] = True
                if event.key == pygame.K_SPACE and shoot_cooldown <= 0:
                    bullets.append(Bullet(sprite_rect.centerx, sprite_rect.centery, 1 if facing_right else -1))
                    shoot_cooldown = 0.3
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:  moving["L"] = False
                if event.key == pygame.K_RIGHT: moving["R"] = False
                if event.key == pygame.K_UP:    moving["U"] = False
                if event.key == pygame.K_DOWN:  moving["D"] = False

        # Spieler Bewegung & Wand-Kollision
        old_x = sprite_rect.x
        if moving["L"]: sprite_rect.x -= 250 * dt
        if moving["R"]: sprite_rect.x += 250 * dt
        for t in level_tiles:
            if t.is_wall and sprite_rect.colliderect(t.rect): sprite_rect.x = old_x

        old_y = sprite_rect.y
        if moving["U"]: sprite_rect.y -= 250 * dt
        if moving["D"]: sprite_rect.y += 250 * dt
        for t in level_tiles:
            if t.is_wall and sprite_rect.colliderect(t.rect): sprite_rect.y = old_y
            if t.is_deadly and sprite_rect.colliderect(t.rect): sprite_rect.topleft = START_POS

        # Gegner & Kugeln
        for e in enemies:
            e.update(dt)
            if sprite_rect.colliderect(e.rect): sprite_rect.topleft = START_POS

        for b in bullets[:]:
            b.update(dt)
            if any(t.rect.colliderect(b.rect) for t in level_tiles if t.is_wall):
                bullets.remove(b)
                continue
            for e in enemies[:]:
                if b.rect.colliderect(e.rect):
                    enemies.remove(e)
                    if b in bullets: bullets.remove(b)

        # Rendering
        display.fill((30, 30, 35))
        for t in level_tiles: t.draw(display)
        for b in bullets: b.draw(display)
        for e in enemies: e.draw(display)

        # Scarab Animation
        is_moving = any(moving.values())
        p_idx = int(pygame.time.get_ticks() / 150) % 2
        img = scarab_data["walk"][p_idx] if is_moving else scarab_data["stand"]
        if not facing_right: img = pygame.transform.flip(img, True, False)
        display.blit(img, sprite_rect)

        pygame.display.update()


if __name__ == "__main__":
    main()