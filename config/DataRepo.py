import os

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

def get_asset_path(filename,BASE_DIR):
    return os.path.normpath(
        os.path.join(BASE_DIR, "..", "assets", "Robot Warfare Asset Pack 22-11-24", "Robots", filename)
    )


def get_sprite(sheet, x , y, width, height):
    """Extrahiert ein Sprite aus dem Sheet mithilfe der blit-Methode."""

    sprite = pygame.Surface([width, height], pygame.SRCALPHA)

    source_rect = pygame.Rect(x, y, width, height)

    sprite.blit(sheet, (0, 0), source_rect)
    return sprite


def load_scale_walk_stand(sheet_path,num_frames,scale_factor,width,height, y_pos_row,y_pos_stand,y_pos_sh ):

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

def load_scale_shoot(sheet_path,num_frames,scale_factor,width,height, y_pos_shoot):

    try:
        sprite_sheet = pygame.image.load(sheet_path).convert_alpha()
    except pygame.error as e:
        print(f"Fehler: Das Spritesheet konnte nicht geladen werden unter Pfad: {sheet_path}")
        pygame.quit()
        exit()

    shooting_frames = []

    for i in range(num_frames):

        shoot_frame = get_sprite(
        sheet_path,
        x=i*width,
        y = y_pos_shoot,
        width=width,
        height=height
    )

        scaled_shoot_frame = pygame.transform.scale(
            shoot_frame,
            (width * scale_factor, height * scale_factor)
        )
        shooting_frames.append(scaled_shoot_frame)#

    return tuple(shooting_frames)





def load_scale_jump(sheet_path,num_frames,scale_factor,width,height,y_pos_jump):

    #TO DO function

    try:
        sprite_sheet = pygame.image.load(sheet_path).convert_alpha()
    except pygame.error as e:
        print(f"Fehler: Das Spritesheet konnte nicht geladen werden unter Pfad: {sheet_path}")
        pygame.quit()
        exit()

    jumping_frames=[]

    for i in range(num_frames):
        jump_frame= get_sprite(
            sheet_path,
            x=i*width,
            y = y_pos_jump,
            width=width,
            height=height
        )
        scaled_jump_frame = pygame.transform.scale(
            jump_frame,
            (width * scale_factor, height * scale_factor)
        )
        jumping_frames.append(scaled_jump_frame)

        return tuple(jumping_frames)

def initial_controll(DEBUG_MODE):



        #  Input-Erkennung(event handling)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_d:
                    DEBUG_MODE = not DEBUG_MODE

                # Bewegungssteuerung
                elif event.key == pygame.K_DOWN:
                    moving_down = True

                elif event.key == pygame.K_UP:
                    moving_up = True

                elif event.key == pygame.K_LEFT:
                    moving_left = True
                    facing_right = False

                elif event.key == pygame.K_RIGHT:
                    moving_right = True
                    facing_right = True

            elif event.type == pygame.KEYUP:
                # Setzt die Bewegung zurück, wenn die Taste losgelassen wird
                if event.key == pygame.K_LEFT:
                    moving_left = False
                elif event.key == pygame.K_RIGHT:
                    moving_right = False
                elif event.key == pygame.K_UP:
                    moving_up = False
                elif event.key == pygame.K_DOWN:
                    moving_down = False

            return moving_up,moving_left,moving_down,moving_right,facing_right



