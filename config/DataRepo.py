import os
import pygame


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

    # If there are PNGs directly in base_path, treat them as a default animation
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

    # Scan subfolders
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
    """ function to load all tiles in a folder and name their keys as the file name"""

    tile_library = {}

    if not os.path.exists(path):
        return {}

    for file in os.listdir(path):
        if file.endswith(".png"):
            name = os.path.splitext(file)[0] # e.g floor_wooden...e
            img = pygame.image.load(os.path.join(path, file)).convert_alpha()
            tile_library[name] = pygame.transform.scale(img, (size, size))

    return tile_library