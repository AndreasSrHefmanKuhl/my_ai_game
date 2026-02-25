import os
import pygame
from config.classes import Player, Tile, Enemy, Bullet
from config.DataRepo import set_display, load_all_animations, load_tileset


def _ensure_anim_key(anim_dict: dict, required_key: str, fallback_key: str = "stand") -> dict:
    """
    Ensures anim_dict contains required_key.
    - If required_key exists: return as-is.
    - Else if fallback_key exists: alias required_key -> fallback_key frames.
    - Else if any key exists: alias required_key -> first available frames.
    - Else: return empty dict.
    """
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
    """Initializes game, loads assets, and handles the main game loop."""
    pygame.init()
    display, display_width, display_height = set_display(1080, 960, "Robot Warfare")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_robots = os.path.normpath(os.path.join(base_dir, "..", "assets", "Robot Warfare Asset Pack 22-11-24"))
    assets_vania = os.path.normpath(os.path.join(base_dir, "..", "assets", "Vania"))

    scarab_path = os.path.join(assets_robots, "Robots", "Scarab")
    hornet_path = os.path.join(assets_robots, "Robots", "Hornet")
    wasp_path = os.path.join(assets_robots, "Robots", "Wasp")
    tileset_path = os.path.join(assets_robots, "Tileset", "tileset_compressed.png")


    player_path = os.path.join(assets_vania, "SPRITES", "player", "idle")
    wizard_path = os.path.join(assets_vania, "SPRITES", "wizard", "idle-sprites")
    angel_path = os.path.join(assets_vania, "SPRITES", "angel", "sprites", "idle")

    scarab_data = load_all_animations(scarab_path, scale_factor=4)
    hornet_data = load_all_animations(hornet_path, scale_factor=4)
    wasp_data = load_all_animations(wasp_path, scale_factor=4)
    player_data = load_all_animations(player_path, scale_factor=4)
    wizard_data = load_all_animations(wizard_path, scale_factor=4)
    angel_data = load_all_animations(angel_path, scale_factor=4)

    player_data = _ensure_anim_key(player_data, required_key="stand")
    player_data = _ensure_anim_key(player_data, required_key="walk", fallback_key="stand")
    player_data = _ensure_anim_key(player_data, required_key= "punch", fallback_key="stand")
    player_data = _ensure_anim_key(player_data, required_key= "kick", fallback_key="stand")

    wizard_data = _ensure_anim_key(wizard_data, required_key="walk", fallback_key="stand")
    angel_data = _ensure_anim_key(angel_data, required_key="walk", fallback_key="stand")

    if not player_data or "stand" not in player_data:
        raise FileNotFoundError(f"Player animations not found/loaded from: {player_path}")
    if not wizard_data or "walk" not in wizard_data:
        raise FileNotFoundError(f"Wizard animations not found/loaded from: {wizard_path}")

    all_tile_images = load_tileset(tileset_path, 16, 48)

    level_map = [
        [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
        [10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 10],
        [10, 1, 1, 1, 1, 1, 154, 1, 1, 1, 1, 1, 1, 1, 1, 1, 153, 1, 1, 10],
        [10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 10],
        [10, 1, 153, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 138, 139, 1, 1, 1, 10],
        [10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 140, 141, 1, 1, 1, 10],
        [10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 154, 1, 1, 1, 1, 1, 1, 1, 10],
        [10, 1, 1, 1, 142, 143, 144, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 10],
        [10, 1, 1, 1, 145, 146, 147, 1, 1, 1, 1, 1, 1, 153, 1, 1, 1, 1, 1, 10],
        [10, 1, 1, 1, 148, 149, 150, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 10],
        [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    ]

    start_pos = (100, 48)
    level_tiles = []
    for r_idx, row in enumerate(level_map):
        for c_idx, t_idx in enumerate(row):
            if t_idx != -1:
                if t_idx < 0 or t_idx >= len(all_tile_images):
                    continue
                is_wall = (10 <= t_idx <= 11 or 138 <= t_idx <= 150)
                is_deadly = (12 <= t_idx <= 14)
                level_tiles.append(Tile(c_idx * 48, r_idx * 48, 48, all_tile_images[t_idx], tile_type="ground"))

    player = Player(start_pos[0], start_pos[1], player_data)


    wizard = Enemy(200, 0, wizard_data)
    angel = Enemy(200,0, angel_data)


    enemies = [wizard,angel]

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

        if kick_pressed and move_cooldown <= 0 :
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

        for b in bullets[:]:
            b.update(dt)
            if any(t.rect.colliderect(b.rect) for t in level_tiles if t.is_wall):
                bullets.remove(b)
                continue
            for e in enemies[:]:
                if b.rect.colliderect(e.rect):
                    enemies.remove(e)
                    if b in bullets:
                        bullets.remove(b)
                    break

        display.fill((30, 30, 35))
        for t in level_tiles:
            t.draw(display)
        for b in bullets:
            b.draw(display)
        for e in enemies:
            e.draw(display)
        display.blit(player.image, player.rect)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()