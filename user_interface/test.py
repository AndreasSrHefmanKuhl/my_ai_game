import os
import pygame

from config.DataRepo import set_display

# ----------------------------------------------------------------------
#  KONSTANTEN & PFAD-DEFINITIONEN
# ----------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Normalisiert den Pfad zum Scarab.png Asset
SCARAB_PATH = os.path.normpath(
    os.path.join(
        BASE_DIR,
        "..",
        "assets",
        "Robot Warfare Asset Pack 22-11-24",
        "Robots",
        "Scarab.png",
    )
)

SPIDER_PATH = os.path.normpath(
            os.path.join(BASE_DIR,

                "..",
                "assets",
                "Robot Warfare Asset Pack 22-11-24",
                "Robots",
                "Spider.png",
            )
        )

WASP_PATH = os.path.normpath(
            os.path.join(BASE_DIR,
                "..",
                "assets",
                "Robot Warfare Asset Pack 22-11-24",
                "Robots",
                "Wasp.png",
            )
        )
HORNET_PATH = os.path.normpath(
            os.path.join(BASE_DIR,
                         "..",
                         "assets",
                         "Robot Warfare Asset Pack 22-11-24",
                         "Robots",
                         "Hornet.png",
                         )
        )


# Sprite-Spezifikationen
SPRITE_WIDTH = 22
SPRITE_HEIGHT = 24
Y_POS_ROW_WALK = 2 # Die zweite Reihe (Index 1) enthält die Lauf-Frames
Y_POS_ROW_STAND = 2  # Die erste Reihe (Index 0) enthält die Stand-Frames
NUM_FRAMES = 2

# Rendering- und Bewegungsparameter
SCALE_FACTOR = 2  # Skalierung (16x16 wird zu 64x64)
# Maximale Bewegungsgeschwindigkeit, wenn eine Taste gedrückt wird
MAX_MOVEMENT_SPEED_PIXELS_PER_SECOND = 150
# Animationsgeschwindigkeit (je niedriger der Wert, desto schneller der Frame-Wechsel)
ANIMATION_SPEED = 0.12


# ----------------------------------------------------------------------
#   EXTRAKTION
# ----------------------------------------------------------------------

def get_sprite(sheet, x, y, width, height):
    """Extrahiert ein Sprite aus dem Sheet mithilfe der blit-Methode."""

    # Stellt sicher, dass das Sprite transparent ist
    sprite = pygame.Surface([width, height], pygame.SRCALPHA)

    source_rect = pygame.Rect(x, y, width, height)

    # Kopiert den Bereich vom Spritesheet auf die neue Surface
    sprite.blit(sheet, (0, 0), source_rect)
    return sprite


# ----------------------------------------------------------------------
#  LADEN UND SKALIEREN DER FRAMES
# ----------------------------------------------------------------------

def load_and_scale_frames(sheet_path):
    """Lädt das Spritesheet und extrahiert die skalierten Walk- und Stand-Frames."""

    try:
        sprite_sheet = pygame.image.load(sheet_path).convert_alpha()
    except pygame.error as e:
        print(f"Fehler: Das Spritesheet konnte nicht geladen werden unter Pfad: {sheet_path}, {e}")
        pygame.quit()
        exit()

    walk_frames = []
    stand_frames = []

    # --- Lauf-Frames (Zeile 1) ---
    for i in range(NUM_FRAMES):
        frame = get_sprite(
            sprite_sheet,
            x=i * SPRITE_WIDTH,
            y=Y_POS_ROW_WALK,
            width=SPRITE_WIDTH,
            height=SPRITE_HEIGHT
        )
        # Skalierung mit Ganzzahl-Faktor (Pixel-Art-freundlich)
        scaled_frame = pygame.transform.scale(
            frame,
            (SPRITE_WIDTH * SCALE_FACTOR, SPRITE_HEIGHT * SCALE_FACTOR)
        )
        walk_frames.append(scaled_frame)

    # --- Stand-Frames (Zeile 0) ---
    # Nur ein Stand-Frame benötigt (den ersten der Zeile 0)
    stand_frame = get_sprite(
        sprite_sheet,
        x=0,
        y=Y_POS_ROW_STAND,
        width=SPRITE_WIDTH,
        height=SPRITE_HEIGHT
    )
    scaled_stand_frame = pygame.transform.scale(
        stand_frame,
        (SPRITE_WIDTH * SCALE_FACTOR, SPRITE_HEIGHT * SCALE_FACTOR)
    )
    stand_frames.append(scaled_stand_frame)



    return {
        "walk": tuple(walk_frames),
        "stand": tuple(stand_frames)  # Nur ein Element
    }


# ----------------------------------------------------------------------
#  HAUPTPROGRAMM (ANIMATION + BEWEGUNG)
# ----------------------------------------------------------------------

def main():
    if not pygame.get_init():
        pygame.init()

    # Debug-Flag und Font
    DEBUG_MODE = True
    try:
        font = pygame.font.Font(None, 20)
    except pygame.error:
        font = None

    # Fenster erstellen
   # screen_width = 800
    #screen_height = 400
    #screen = pygame.display.set_mode((screen_width, screen_height))
    #pygame.display.set_caption("")
    display,display_width,display_height = set_display(800,400,"test screen")
    # Frames laden
    Scarab_Frames = load_and_scale_frames(SCARAB_PATH)
    Spider_FRAMES = load_and_scale_frames(SPIDER_PATH)
    Wasp_Frames = load_and_scale_frames(WASP_PATH)
    Hornet_Frames = load_and_scale_frames(HORNET_PATH)




    if not Hornet_Frames["walk"]:
        return

    # Animations-Variablen
    current_frame_index = 0.0

    # Steuerungsvariablen
    moving_left = False
    moving_right = False
    moving_up = False
    moving_down = False
    shoot = False
    jump = False

    # Merkt sich die Richtung, in die der Scarab blickt (True=Rechts, False=Links)
    facing_right = True

    # Initialposition des Sprites: Mittig am unteren Bildschirmrand
    sprite_rect = Hornet_Frames["stand"][0].get_rect(
        centerx=display_width  // 2,
        bottom=display_height // 2,
    )

    clock = pygame.time.Clock()
    running = True

    while running:

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

        # UPDATE (Zeit-basiert)
        dt = clock.tick(60) / 1000.0  # Zeit seit dem letzten Frame in Sekunden

        # --- POSITION-UPDATE (Bewegung) ---
        distance_moved = MAX_MOVEMENT_SPEED_PIXELS_PER_SECOND * dt

        if moving_left:
            sprite_rect.x -= distance_moved
        if moving_right:
            sprite_rect.x += distance_moved
        if moving_down:
            sprite_rect.y += distance_moved
        if moving_up :
            sprite_rect.y -= distance_moved

        # Begrenzung auf den Bildschirmrand
        sprite_rect.left = max(sprite_rect.left, 0)
        sprite_rect.right = min(sprite_rect.right, display_width)
        sprite_rect.top = max(sprite_rect.top,-3)
        sprite_rect.y = min(sprite_rect.y,336)


        # --- FRAME-WECHSEL (Animation) ---

        # Prüft, ob sich der Scarab bewegt
        is_moving = moving_left or moving_right or moving_up or moving_down

        if is_moving:
            # Animation nur fortsetzen,

            current_frame_index += dt / ANIMATION_SPEED
            # Setzt den Index zurück
            if current_frame_index >= len(Hornet_Frames["walk"]):
                current_frame_index = 0

            # Holt den aktuellen Lauf-Frame
            current_frame = Hornet_Frames["walk"][int(current_frame_index)]

        else:
            # Wenn sich der Scarab nicht bewegt, zeige den Stand-Frame
            current_frame_index = 0.0  # Index zurücksetzen
            current_frame = Hornet_Frames["stand"][0]

        #  horizontale Spiegeln , wenn er nach links blickt (facing_right == False)
        if not facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)


        #  Rendering
        display.fill((50, 65, 70))

        # Rendert den aktuellen Frame an seiner bewegten Position
        display.blit(current_frame, sprite_rect)

        # DEBUG-AUSGABE
        if DEBUG_MODE:
            # Roter Rahmen um das Sprite-Rect
            pygame.draw.rect(display, (255, 0, 0), sprite_rect, 1)

            # FPS-Anzeige
            if font:
                fps = clock.get_fps()
                text_x = sprite_rect.centerx - 100
                text_y = sprite_rect.top - 20
                text = font.render(
                    f"FPS: {fps:.1f} | Pos: ({text_x}, {text_y}) | Moving: {is_moving}",
                    True, (255, 255, 255)
                )
                display.blit(text, (5, 5))

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()