import os
import pygame
from config.classes import Player, Tile, Enemy
from config.DataRepo import (
    set_display,
    load_all_animations,
    load_tileset_named_library,
    apply_tile_aliases,
    build_level,
    create_level_surface
)
from config.vania_tile_aliases import VANIA_TILE_ALIASES


def main():
    pygame.init()

    # 1. Setup Fenster
    win_w, win_h = 800, 600
    display, dw, dh = set_display(win_w, win_h, "Schaolin Vania")

    # Pfad-Logik
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.normpath(os.path.join(base_dir, ".."))
    assets_vania = os.path.normpath(os.path.join(project_root, "assets", "Vania"))

    # 2. Assets laden
    player_data = load_all_animations(os.path.join(assets_vania, "SPRITES", "player","sprites", "idle"), scale_factor=2)
    wizard_data = load_all_animations(os.path.join(assets_vania, "SPRITES", "wizard", "idle-sprites"), scale_factor=2)
    angel_data = load_all_animations(os.path.join(assets_vania, "SPRITES", "angel", "sprites", "idle"), scale_factor=2)
    ghoul_data = load_all_animations(os.path.join(assets_vania, "SPRITES", "burning-ghoul", "sprites"), scale_factor=2)

    # 3. Tileset-Vorbereitung
    TS = 48
    tileset_path = os.path.join(assets_vania, "environment", "tileset.png")
    raw_tiles = load_tileset_named_library(tileset_path, source_size=16, target_size=TS)
    tile_library = apply_tile_aliases(raw_tiles, VANIA_TILE_ALIASES)

    # 4. Level-Map Design
    # Wir berechnen die Anzahl der Zeilen passend zur Fensterhöhe
    rows_needed = win_h // TS
    map_width = 64

    level_map = []
    for r in range(rows_needed):
        if r == rows_needed - 1:
            level_map.append(["floor_head"] * map_width)
        elif r == rows_needed - 2:
            # Player und Gegner Reihe
            row = ["."] * map_width
            row[2] = "P"
            row[22] = "E"
            row[42] = "E"
            level_map.append(row)
        else:
            # Wände an den Seiten
            level_map.append(["wall1"] + ["."] * (map_width - 2) + ["wall1"])

    # 5. Objekte initialisieren
    level_tiles, enemies, player = build_level(
        level_map, tile_library, TS, player_data, [wizard_data, angel_data, ghoul_data]
    )

    # Hintergrund laden
    bg_path = os.path.join(assets_vania, "environment", "background.png")
    bg_img = pygame.image.load(bg_path).convert_alpha()

    # WICHTIG: Erstelle die Level-Surface mit der korrekten Gesamtbreite (64 * 48)
    # Wir nutzen bg_img hier, damit es über die ganze Level-Länge skaliert wird
    level_surface = create_level_surface(level_map, tile_library, bg_img, TS)
    level_pixel_width = map_width * TS

    clock = pygame.time.Clock()
    camera_x = 0

    while True:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # --- INPUT ---
        keys = pygame.key.get_pressed()
        dx, state = 0, "stand"

        if keys[pygame.K_f]:
            state = "punch"
        elif keys[pygame.K_g]:
            state = "kick"
        elif keys[pygame.K_DOWN]:
            state = "crouch"

        if keys[pygame.K_LEFT]:
            dx = -250
            state = "walk"
        elif keys[pygame.K_RIGHT]:
            dx = 250
            state = "walk"

        if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
            player.jump()

        # --- PHYSIK & KOLLISION ---
        # Horizontal
        player.rect.x += dx * dt
        for t in [tile for tile in level_tiles if tile.is_wall]:
            if player.rect.colliderect(t.rect):
                if dx > 0:
                    player.rect.right = t.rect.left
                elif dx < -0:
                    player.rect.left = t.rect.right

        # Vertikal
        player.apply_gravity()
        player.on_ground = False
        for t in [tile for tile in level_tiles if tile.is_floor or tile.is_wall]:
            if player.rect.colliderect(t.rect):
                if player.velocity_y > 0:
                    player.rect.bottom = t.rect.top
                    player.velocity_y = 0
                    player.on_ground = True
                elif player.velocity_y < 0 and t.is_wall:
                    player.rect.top = t.rect.bottom
                    player.velocity_y = 0

        # --- UPDATES ---
        player.change_state(state)
        player.update(dt, dx)
        for e in enemies:
            e.update(dt)

        # --- KAMERA BERECHNUNG ---
        # Die Kamera versucht den Spieler in der Mitte zu halten
        target_camera_x = player.rect.centerx - win_w // 2
        # Sanftes Folgen (Lerp)
        camera_x += (target_camera_x - camera_x) * 0.1
        # Kamera-Grenzen (nicht aus der Map herausscrollen)
        camera_x = max(0, min(camera_x, level_pixel_width - win_w))

        # --- ZEICHNEN ---
        display.fill((30, 30, 30))  # Fallback Hintergrundfarbe

        # 1. Level-Surface (beinhaltet BG und Tiles) mit Kamera-Offset
        display.blit(level_surface, (-camera_x, 0))

        # 2. Gegner zeichnen
        for e in enemies:
            display.blit(e.image, (e.rect.x - camera_x, e.rect.y))

        # 3. Player zeichnen
        display.blit(player.image, (player.rect.x - camera_x, player.rect.y))

        pygame.display.update()


if __name__ == "__main__":
    main()