import os
import pygame
from config.classes import Tile, Player, Enemy

def set_display(width, height, name):
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(name)
    return screen, width, height

def load_all_animations(base_path, scale_factor=2):
    animations = {}
    if not os.path.exists(base_path): return {}
    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        if os.path.isdir(folder_path):
            frames = []
            for file in sorted(os.listdir(folder_path)):
                if file.endswith((".png", ".jpg")):
                    img = pygame.image.load(os.path.join(folder_path, file)).convert_alpha()
                    w, h = img.get_size()
                    img = pygame.transform.scale(img, (int(w * scale_factor), int(h * scale_factor)))
                    frames.append(img)
            if frames: animations[folder.lower()] = frames
    return animations

def load_tileset_named_library(path, source_size=16, target_size=48):
    sheet = pygame.image.load(path).convert_alpha()
    library = {}
    idx = 0
    for y in range(0, sheet.get_height(), source_size):
        for x in range(0, sheet.get_width(), source_size):
            surf = pygame.Surface((source_size, source_size), pygame.SRCALPHA)
            surf.blit(sheet, (0, 0), (x, y, source_size, source_size))
            scaled = pygame.transform.scale(surf, (target_size, target_size))
            library[f"vania_{idx:03d}"] = scaled
            idx += 1
    return library

def apply_tile_aliases(raw_library, alias_dict):
    curated = {}
    for curated_name, raw_name in alias_dict.items():
        if raw_name in raw_library:
            curated[curated_name] = raw_library[raw_name]
    return curated

def build_level(level_data, tile_library, tile_size=48, player_data=None, enemy_data_list=None):
    level_tiles, enemies, player = [], [], None
    e_idx = 0
    for r_idx, row in enumerate(level_data):
        for c_idx, cell in enumerate(row):
            x, y = c_idx * tile_size, r_idx * tile_size
            if cell == "P" and player_data:
                player = Player(x, y, player_data)
            elif cell == "E" and enemy_data_list:
                enemies.append(Enemy(x, y, enemy_data_list[e_idx % len(enemy_data_list)]))
                e_idx += 1
            elif cell in tile_library:
                level_tiles.append(Tile(x, y, tile_size, tile_library[cell], cell))
    return level_tiles, enemies, player


def create_level_surface(level_data, tile_library, background_img, tile_size=48):
    # Korrekte Berechnung der Dimensionen
    cols = len(level_data[0]) if level_data else 0
    rows = len(level_data)
    w, h = cols * tile_size, rows * tile_size

    surf = pygame.Surface((w, h)).convert_alpha()


    if background_img:
        scaled_bg = pygame.transform.scale(background_img, (w, h))
        surf.blit(scaled_bg, (0, 0))

    for r_idx, row in enumerate(level_data):
        for c_idx, cell in enumerate(row):
            if cell in tile_library:
                surf.blit(tile_library[cell], (c_idx * tile_size, r_idx * tile_size))
    return surf