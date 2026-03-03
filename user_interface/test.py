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
    # Fenstergröße definieren
    win_w, win_h = 1000, 800
    display, dw, dh = set_display(win_w, win_h, "Schaolin Vania")

    # Pfad-Logik (Deine Original-Struktur)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.normpath(os.path.join(base_dir, ".."))
    assets_vania = os.path.normpath(os.path.join(project_root, "assets", "Vania"))

    # Assets laden - Zeigt auf Hauptordner für alle Animationen
    player_data = load_all_animations(os.path.join(assets_vania, "SPRITES", "player","idle"), scale_factor=3)
    wizard_data = load_all_animations(os.path.join(assets_vania, "SPRITES", "wizard","idle-sprites"), scale_factor=3)

    # Tiles laden
    TS = 48
    tileset_path = os.path.join(assets_vania, "environment", "tileset.png")
    raw_tiles = load_tileset_named_library(tileset_path, source_size=16, target_size=TS)
    tile_library = apply_tile_aliases(raw_tiles, VANIA_TILE_ALIASES)

    # Deine Map (P = Start, E = Gegner)
    level_map = [
        ["brick"] * 21,
        ["wall1"] + ["."] * 19 + ["wall1"],
        ["wall1"] + ["."] * 19 + ["wall1"],
        ["wall1"] + ["."] * 5 + ["E"] + ["."] * 13 + ["wall1"],
        ["wall1", "P"] + ["."] * 18 + ["wall1"],
        ["way", "way1", "way2", "floor_head", "floor_ground", "floor_ground1"] + ["way"] * 15
    ]

    # Level-Objekte erstellen
    level_tiles, enemies, player = build_level(level_map, tile_library, TS, player_data, [wizard_data])

    # Hintergrund laden & auf FENSTERGRÖSSE skalieren
    bg_path = os.path.join(assets_vania, "environment", "background.png")
    bg_img = pygame.image.load(bg_path).convert_alpha()
    bg_img = pygame.transform.scale(bg_img, (win_w, win_h))

    # Das fertige Level-Bild (Background + Tiles)
    level_surface = create_level_surface(level_map, tile_library, bg_img, TS)

    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                return

        # --- DEINE ORIGINAL-STEUERUNG ---
        keys = pygame.key.get_pressed()
        dx, state = 0, "stand"

        # Angriffe
        if keys[pygame.K_f]:
            state = "punch"
        elif keys[pygame.K_g]:
            state = "kick"
        elif keys[pygame.K_h] and keys[pygame.K_DOWN]:
            state = "crouchkick"
        elif keys[pygame.K_DOWN]:
            state = "crouch"
        # Bewegung
        elif keys[pygame.K_LEFT]:
            dx = -250
            state = "walk"
        elif keys[pygame.K_RIGHT]:
            dx = 250
            state = "walk"

        # Sprung
        if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
            player.jump()

        # --- PHYSIK & KOLLISION ---
        # Horizontal
        old_x = player.rect.x
        player.rect.x += dx * dt
        for t in [tile for tile in level_tiles if tile.is_wall]:
            if player.rect.colliderect(t.rect):
                player.rect.x = old_x

        # Vertikal (Schwerkraft)
        player.on_ground = False
        player.apply_gravity()
        for t in [tile for tile in level_tiles if tile.is_floor or tile.is_wall]:
            if player.rect.colliderect(t.rect):
                if player.velocity_y > 0:  # Landen
                    player.rect.bottom = t.rect.top
                    player.velocity_y, player.on_ground = 0, True
                elif player.velocity_y < 0 and t.is_wall:  # Kopf anstoßen
                    player.rect.top = t.rect.bottom
                    player.velocity_y = 0

        # Animation & Gegner Update
        player.change_state(state)
        player.update(dt, dx)
        for e in enemies:
            e.update(dt)

        # --- ZEICHNEN ---
        # 1. Level-Hintergrund (mit allen Tiles)
        display.blit(level_surface, (0, 0))

        # 2. Gegner & Player
        for e in enemies:
            e.draw(display)
        if player:
            display.blit(player.image, player.rect)

        pygame.display.update()


if __name__ == "__main__":
    main()