import pygame

#------------------------------------------------------------------------------------
# Graphical functions
#------------------------------------------------------------------------------------
def set_display(width,height,name):
    screen_width = width
    screen_height = height
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(f"{name}")
    return screen,screen_width,screen_height


def get_sprite(sheet, x , y, width, height):
    """Extrahiert ein Sprite aus dem Sheet mithilfe der blit-Methode."""

    sprite = pygame.Surface([width, height], pygame.SRCALPHA)

    source_rect = pygame.Rect(x, y, width, height)

    sprite.blit(sheet, (0, 0), source_rect)
    return sprite


def load_scale_walk_stand(sheet_path,num_frames,scale_factor,width,height, y_pos_row,y_pos_stand ):

    try:
        sprite_sheet = pygame.image.load(sheet_path).convert_alpha()
    except pygame.error as e:
        print(f"Fehler: Das Spritesheet konnte nicht geladen werden unter Pfad: {sheet_path}")
        pygame.quit()
        exit()

    walk_frames = []
    stands_frames =[]

    for i in range(num_frames):

        walk_frame = get_sprite(
            sprite_sheet,
            x = i *width,
            y=y_pos_row,
            width= width,
            height= height
        )
        scaled_frame = pygame.transform.scale(
            walk_frame,
            (width * scale_factor, height * scale_factor)
        )
        walk_frames.append(scaled_frame)

        stand_frame = get_sprite(
            sprite_sheet,
            x=0,
            y=y_pos_stand,
            width=width,
            height=height
        )
        scaled_stand_frame = pygame.transform.scale(
            stand_frame,
            (width * scale_factor, height * scale_factor)
        )
        stands_frames.append(scaled_stand_frame)

    return {
        "walk":tuple(walk_frames),
        "stand":tuple(stands_frames)
    }


