import pygame

from user_interface.test import Y_POS_ROW


def get_sprite(sheet, x, y, width, height):
    """Extrahiert ein Sprite aus dem Sheet mithilfe der blit-Methode."""

    sprite = pygame.Surface([width, height], pygame.SRCALPHA)

    source_rect = pygame.Rect(x, y, width, height)

    sprite.blit(sheet, (0, 0), source_rect)
    return sprite


def walk(sheet_path,num_frames,scale_factor,width,height, y_pos_row ):

    try:
        sprite_sheet = pygame.image.load(sheet_path).convert_alpha()
    except pygame.error as e:
        print(f"Fehler: Das Spritesheet konnte nicht geladen werden unter Pfad: {sheet_path}")
        pygame.quit()
        exit()

    walk_frames = []
    for i in range(num_frames):
        frame = get_sprite(
            sprite_sheet,
            x = i *width,
            y=y_pos_row,
            width= width,
            height= height
        )
        scaled_frame = pygame.transform.scale(
            frame,
            (width * scale_factor, height * scale_factor)
        )
        walk_frames.append(scaled_frame)

    return tuple(walk_frames)


