import os
import pygame
from config.classes import Player, Tile, Enemy
from config.DataRepo import (
    set_display,
    load_all_animations,
    load_tileset_named_library,
    apply_tile_aliases,
    build_level,
    create_level_surface, show_loading_screen, let_agent_cook, draw_health_bar, get_level_map, show_start_screen
)
from config.database import init_db
from config.vania_tile_aliases import VANIA_TILE_ALIASES


def main():
    pygame.init()
    init_db()
    win_w, win_h = 800, 600
    TS = 36
    map_width = 64

    display, dw, dh = set_display(win_w, win_h, "Schaolin Vania")
    user_id = show_start_screen(display)

    # Dynamic pathing
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.normpath(os.path.join(base_dir, ".."))
    assets_vania = os.path.normpath(os.path.join(project_root, "assets", "Vania"))

    #  Load Assets
    # Pointing to the parent folder so all sub-folders (idle, walk, punch) are loaded into the dict
    player_path = os.path.join(assets_vania, "SPRITES", "player","sprites","idle")
    player_data = load_all_animations(player_path, scale_factor=2)

    # Placeholder for enemy data logic
    wizard_data = load_all_animations(os.path.join(assets_vania, "SPRITES", "wizard","idle-sprites"), scale_factor=2)
    angel_data = load_all_animations(os.path.join(assets_vania, "SPRITES", "angel","sprites"), scale_factor=2)
    ghoul_data = load_all_animations(os.path.join(assets_vania, "SPRITES", "burning-ghoul","sprites"), scale_factor=2)

    #  Tileset Setup
    tileset_path = os.path.join(assets_vania, "environment", "tileset.png")
    raw_tiles = load_tileset_named_library(tileset_path, source_size=16, target_size=TS)
    tile_library = apply_tile_aliases(raw_tiles, VANIA_TILE_ALIASES)

    #  Level Design
    level_map = get_level_map(win_h,TS,map_width)
    # Initialize Objects
    level_tiles, enemies, player = build_level(
        level_map, tile_library, TS, player_data, [wizard_data, angel_data, ghoul_data]
    )
    player.health = 100
    player.max_health = 100

    # Background Surface
    bg_path = os.path.join(assets_vania, "environment", "background.png")
    bg_img = pygame.image.load(bg_path).convert_alpha()
    level_surface = create_level_surface(level_map, tile_library, bg_img, TS)
    level_pixel_width = map_width * TS

    clock = pygame.time.Clock()
    camera_x = 0

    performance_tracker = {
        "punch": 0,
        "kick": 0,
        "crouchkick": 0,
        "damage_dealt": 0
    }

    # --- MAIN GAME LOOP ---
    while True:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # --- INPUT & STATE DETERMINATION ---
        keys = pygame.key.get_pressed()
        dx = 0
        requested_state = "stand"

        # Movement
        if keys[pygame.K_LEFT]:
            dx = -250
            requested_state = "walk"
        elif keys[pygame.K_RIGHT]:
            dx = 250
            requested_state = "walk"

        # Actions (Priority)
        if keys[pygame.K_f]:
            performance_tracker["punch"] += 1
            requested_state = "punch"
        elif keys[pygame.K_g]:
            performance_tracker["kick"] += 1
            requested_state = "kick"
        elif keys[pygame.K_h]:
            performance_tracker["crouchkick"] += 1
            requested_state = "crouchkick"
        elif keys[pygame.K_DOWN]:
            requested_state = "crouch"

        if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
            requested_state = "jump"
            player.jump()

        # Update state based on logic in classes.py
        player.change_state(requested_state)

        # --- PHYSICS & COLLISION ---
        # Horizontal Movement
        player.rect.x += dx * dt
        for t in [tile for tile in level_tiles if tile.is_wall]:
            if player.rect.colliderect(t.rect):
                if dx > 0:
                    player.rect.right = t.rect.left
                elif dx < 0:
                    player.rect.left = t.rect.right

        # Vertical Movement
        player.apply_gravity()
        player.on_ground = False
        for t in [tile for tile in level_tiles if tile.is_floor or tile.is_wall]:
            if player.rect.colliderect(t.rect):
                if player.velocity_y > 0:
                    player.rect.bottom = t.rect.top
                    player.velocity_y = 0
                    player.on_ground = True

        # --- UPDATES ---
        player.update(dt, dx)

        for e in enemies:
            e.update(dt,player.rect, level_tiles)



        if player.is_attacking():
            attack_zone = player.get_attack_rect()
            for e in enemies:
                # Check if the player's fist/foot overlaps the enemy body
                if attack_zone.colliderect(e.rect):
                    e.take_damage(25)
                    performance_tracker["damage_dealt"] += 25


        # Clean up dead enemies so they don't stay on screen
        enemies = [e for e in enemies if not e.is_dead]

        for e in enemies:
            if e.state == "attack" and e.rect.colliderect(player.rect):
                player.take_damage(10)

        if len(enemies) == 0:
            # instant show of loading screen while agent has been called
            show_loading_screen(display)

            # call agent over datarepo
            # gives current player data and level-map
            new_level_map = let_agent_cook(level_map, performance_tracker)

            if new_level_map:
                # clean up old world
                level_tiles.clear()
                enemies.clear()

                # update level map
                level_map = new_level_map

                # build new world with new data
                level_tiles, enemies, player = build_level(
                    level_map,
                    tile_library,
                    TS,
                    player_data,
                    [wizard_data, angel_data, ghoul_data]
                )
                player.health = 100
                player.max_health = 100

                # graphical surface
                level_surface = create_level_surface(level_map, tile_library, bg_img, TS)

                # reset for new round
                camera_x = 0
                for key in performance_tracker:
                    performance_tracker[key] = 0

        # Camera positioning
        target_cam_x = player.rect.centerx - win_w // 2
        camera_x = max(0, min(target_cam_x, level_pixel_width - win_w))


        # --- RENDERING ---
        display.fill((0, 0, 0))
        display.blit(level_surface, (-camera_x, 0))

        for e in enemies:
            display.blit(e.image, (int(e.rect.x - camera_x), int(e.rect.y)))



        display.blit(player.image, (player.rect.x - camera_x, player.rect.y))


        draw_health_bar(display, 20, 20, player.health, player.max_health, width=200, height=10, color=(255, 0, 0))

        pygame.display.update()


if __name__ == "__main__":
    main()