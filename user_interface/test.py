import os
import pygame
from config.classes import Player, Tile, Enemy, Bullet
from config.DataRepo import set_display, load_all_animations
from config.DataRepo import (
    load_vania_collides_local_ids,
    load_tileset_named_library,
    apply_tile_aliases,
    build_level,
)
from config.vania_tile_aliases import VANIA_TILE_ALIASES


def _ensure_anim_key(anim_dict: dict, required_key: str, fallback_key: str = "stand") -> dict:
    if not anim_dict:
        return {}
    if required_key in anim_dict:
        return anim_dict
    if fallback_key in anim_dict:
        anim_dict = dict(anim_dict)
        anim_dict[required_key] = anim_dict[fallback_key]
        return anim_dict
    first_key = next(iter(anim_dict.keys()))
    anim_dict = dict(anim_dict)
    anim_dict[required_key] = anim_dict[first_key]
    return anim_dict


def main():
    pygame.init()
    display, display_width, display_height = set_display(1000, 800, "Schaolin Vania")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.normpath(os.path.join(base_dir, ".."))


    assets_vania = os.path.normpath(os.path.join(project_root, "assets", "Vania"))

    # --- Load animations ---


    player_path = os.path.join(assets_vania, "SPRITES", "player", "idle")
    wizard_path = os.path.join(assets_vania, "SPRITES", "wizard", "idle-sprites")
    angel_path = os.path.join(assets_vania, "SPRITES", "angel", "sprites", "idle")


    player_data = load_all_animations(player_path, scale_factor=4)
    wizard_data = load_all_animations(wizard_path, scale_factor=4)
    angel_data = load_all_animations(angel_path, scale_factor=4)

    player_data = _ensure_anim_key(player_data, required_key="stand")
    player_data = _ensure_anim_key(player_data, required_key="walk", fallback_key="stand")
    player_data = _ensure_anim_key(player_data, required_key="punch", fallback_key="stand")
    player_data = _ensure_anim_key(player_data, required_key="kick", fallback_key="stand")

    wizard_data = _ensure_anim_key(wizard_data, required_key="walk", fallback_key="stand")
    angel_data = _ensure_anim_key(angel_data, required_key="walk", fallback_key="stand")

    if not player_data or "stand" not in player_data:
        raise FileNotFoundError(f"Player animations not found/loaded from: {player_path}")
    if not wizard_data or "walk" not in wizard_data:
        raise FileNotFoundError(f"Wizard animations not found/loaded from: {wizard_path}")

    # --- Load VANIA tileset for level building (strings) ---
    vania_tileset_path = os.path.join(assets_vania, "environment", "tileset.png")
    vania_map_json_path = os.path.join(assets_vania, "map", "map.json")

    collides_ids = load_vania_collides_local_ids(vania_map_json_path)
    base_library = load_tileset_named_library(
        vania_tileset_path,
        tile_size=16,
        target_size=48,
        name_prefix="vania",
        collides_local_ids=collides_ids,
    )
    tile_library = apply_tile_aliases(base_library, VANIA_TILE_ALIASES, strict=True)

    # --- STRING level map  ---
    level_map = [
        ["bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl","bg_br_bl"],
        ["bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl"],
        ["bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl"],
        ["bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl"],
        ["bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl"],
        ["bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl"],
        ["bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl"],
        ["bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl"],
        ["bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl"],
        ["bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl"],
        ["bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl"],
        ["bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl"],
        ["bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl", "bg_br_bl",
         "bg_br_bl", "bg_br_bl", "bg_br_bl"],


    ]

    start_pos = (10, 48)
    level_tiles = build_level(level_map, tile_library, tile_size=48)

    player = Player(start_pos[0], start_pos[1], player_data)
    wizard = Enemy(200, 0, wizard_data)
    angel = Enemy(200, 0, angel_data)
    enemies = [wizard, angel]

    bullets = []
    move_cooldown = 0.0
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        move_cooldown = max(0.0, move_cooldown - dt)

        kick_pressed = False
        punch_pressed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                kick_pressed = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                punch_pressed = True

        keys = pygame.key.get_pressed()
        dx, dy, state = 0, 0, "stand"

        if keys[pygame.K_LEFT]:
            dx, state = -250, "walk"
        elif keys[pygame.K_RIGHT]:
            dx, state = 250, "walk"
        if keys[pygame.K_UP]:
            dy = -250
        if keys[pygame.K_DOWN]:
            dy = 250

        if kick_pressed and move_cooldown <= 0:
            move_cooldown = 0.3
            player.change_state("kick")
        elif punch_pressed and move_cooldown <= 0:
            move_cooldown = 0.2
            player.change_state("punch")
        else:
            player.change_state(state)

        old_x = player.rect.x
        player.rect.x += dx * dt
        for t in [tile for tile in level_tiles if tile.is_wall]:
            if player.rect.colliderect(t.rect):
                player.rect.x = old_x

        old_y = player.rect.y
        player.rect.y += dy * dt
        for t in level_tiles:
            if t.is_wall and player.rect.colliderect(t.rect):
                player.rect.y = old_y
            if t.is_deadly and player.rect.colliderect(t.rect):
                player.rect.topleft = start_pos

        player.update(dt, dx)

        for e in enemies:
            e.update(dt)
            if player.rect.colliderect(e.rect):
                player.rect.topleft = start_pos

        display.fill((30, 30, 35))
        for t in level_tiles:
            t.draw(display)
        for e in enemies:
            e.draw(display)
        display.blit(player.image, player.rect)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()