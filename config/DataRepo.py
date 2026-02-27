import os
import json
import pygame

from config.classes import Tile


def set_display(width, height, name):
    """Sets the window dimensions and title."""
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(name)
    return screen, width, height


def get_sprite(sheet, x, y, width, height):
    """Extracts a single surface from a spritesheet."""
    sprite = pygame.Surface([width, height], pygame.SRCALPHA)
    sprite.blit(sheet, (0, 0), pygame.Rect(x, y, width, height))
    return sprite


def load_tileset(path, source_size, target_size):
    """Cuts a tileset into a list of scaled images."""
    sheet = pygame.image.load(path).convert_alpha()
    tiles = []
    for y in range(0, sheet.get_height(), source_size):
        for x in range(0, sheet.get_width(), source_size):
            img = get_sprite(sheet, x, y, source_size, source_size)
            tiles.append(pygame.transform.scale(img, (target_size, target_size)))
    return tiles


def load_all_animations(base_path, scale_factor=2):
    """
    Scans subfolders and loads all images into a dictionary.
    Keys are folder names (e.g., 'walk', 'stand').

    Also supports the case where base_path directly contains .png frames:
    those frames will be returned under the key 'stand'.
    """
    animation_data = {}
    if not os.path.exists(base_path):
        return {}

    direct_pngs = sorted([f for f in os.listdir(base_path) if f.lower().endswith(".png")])
    if direct_pngs:
        frames = []
        for file_name in direct_pngs:
            img_path = os.path.join(base_path, file_name)
            img = pygame.image.load(img_path).convert_alpha()
            w, h = img.get_size()
            scaled_img = pygame.transform.scale(img, (w * scale_factor, h * scale_factor))
            frames.append(scaled_img)
        if frames:
            animation_data["stand"] = tuple(frames)

    for category in os.listdir(base_path):
        category_path = os.path.join(base_path, category)
        if os.path.isdir(category_path):
            frames = []
            file_names = sorted(os.listdir(category_path))
            for file_name in file_names:
                if file_name.endswith(".png"):
                    img_path = os.path.join(category_path, file_name)
                    img = pygame.image.load(img_path).convert_alpha()
                    w, h = img.get_size()
                    scaled_img = pygame.transform.scale(img, (w * scale_factor, h * scale_factor))
                    frames.append(scaled_img)

            if frames:
                animation_data[category] = tuple(frames)

    return animation_data


def load_tile_library(path, size=10):
    """function to load all tiles in a folder and name their keys as the file name"""
    tile_library = {}

    if not os.path.exists(path):
        return {}

    for file in os.listdir(path):
        if file.endswith(".png"):
            name = os.path.splitext(file)[0]
            img = pygame.image.load(os.path.join(path, file)).convert_alpha()
            tile_library[name] = pygame.transform.scale(img, (size, size))

    return tile_library


def load_vania_collides_local_ids(map_json_path: str) -> set[int]:
    """
    Reads assets/Vania/map/map.json and returns local tile indices (0-based)
    that have {"collides": true}.
    """
    if not os.path.exists(map_json_path):
        return set()

    with open(map_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tilesets = data.get("tilesets", [])
    if not tilesets:
        return set()

    tileprops = (tilesets[0].get("tileproperties") or {})
    collides_local_ids: set[int] = set()

    for local_id_str, props in tileprops.items():
        if (props or {}).get("collides") is True:
            try:
                collides_local_ids.add(int(local_id_str))
            except ValueError:
                continue

    return collides_local_ids


def load_tileset_named_library(
    tileset_path: str,
    *,
    tile_size: int = 16,
    target_size: int = 48,
    name_prefix: str = "vania",
    collides_local_ids: set[int] | None = None, # Kann jetzt leer bleiben
) -> dict[str, dict]:
    sheet = pygame.image.load(tileset_path).convert_alpha()
    tile_library: dict[str, dict] = {}

    i = 0
    for y in range(0, sheet.get_height(), tile_size):
        for x in range(0, sheet.get_width(), tile_size):
            tile_name = f"{name_prefix}_{i:03d}"
            img = get_sprite(sheet, x, y, tile_size, tile_size)
            img = pygame.transform.scale(img, (target_size, target_size))

            # Standardmäßig ist alles "ground" (keine Kollision)
            tile_library[tile_name] = {"image": img, "tile_type": "ground"}
            i += 1
    return tile_library


def apply_tile_aliases(
    base_library: dict[str, dict],
    aliases: dict[str, str],
    *,
    strict: bool = True,
) -> dict[str, dict]:
    """
    Creates a curated library using human-friendly names by aliasing to base keys.

    aliases example:
      {
        "floor_stone": "vania_010",
        "wall_stone": "vania_064",
      }

    Returns a NEW dict keyed by curated names, each value being the same entry
    structure {"image": Surface, "tile_type": "..."} as in base_library.
    """
    curated: dict[str, dict] = {}

    for curated_name, base_key in aliases.items():
        entry = base_library.get(base_key)
        if entry is None:
            if strict:
                raise KeyError(f"Alias '{curated_name}' points to missing base tile '{base_key}'")
            continue
        curated[curated_name] = entry

    return curated


def build_level(level_data, tile_library, tile_size=10):
    """
    level_data: 2D list of strings (tile names), e.g. "floor_stone" or "empty"
    tile_library: {name: {"image": Surface, "tile_type": str}} OR {name: Surface}
    """
    level_tiles = []

    for row_idx, row in enumerate(level_data):
        for col_idx, tile_name in enumerate(row):
            if not tile_name or tile_name == "empty":
                continue

            entry = tile_library.get(tile_name)
            if entry is None:
                continue

            if isinstance(entry, dict):
                image = entry["image"]
                tile_type = entry.get("tile_type", tile_name)
            else:
                image = entry
                tile_type = tile_name

            x = col_idx * tile_size
            y = row_idx * tile_size

            new_tile = Tile(x, y, tile_size, image, tile_type=tile_type)
            level_tiles.append(new_tile)

    return level_tiles
