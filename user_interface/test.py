import os
import pygame

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

#
SPRITE_WIDTH = 16
SPRITE_HEIGHT = 16
Y_POS_ROW = 16  # Die zweite Reihe beginnt nach der 16 Pixel hohen ersten Reihe
NUM_FRAMES = 4

# Rendering- und Bewegungsparameter
SCALE_FACTOR = 4  # Skalierung (16x16 wird zu 64x64)
MOVEMENT_SPEED_PIXELS_PER_SECOND = 60  # Bewegungsgeschwindigkeit des Scarab


# ----------------------------------------------------------------------
#   EXTRAKTION
# ----------------------------------------------------------------------

def get_sprite(sheet, x, y, width, height):
    """Extrahiert ein Sprite aus dem Sheet mithilfe der blit-Methode."""

    sprite = pygame.Surface([width, height], pygame.SRCALPHA)

    source_rect = pygame.Rect(x, y, width, height)

    sprite.blit(sheet, (0, 0), source_rect)
    return sprite


# ----------------------------------------------------------------------
#  LADEN UND SKALIEREN DER FRAMES
# ----------------------------------------------------------------------

def scarab_walk():
    """Lädt das Spritesheet und extrahiert die vier skalierten Walk-Frames."""

    try:
        scarab_sprite_sheet = pygame.image.load(SCARAB_PATH).convert_alpha()
    except pygame.error as e:
        print(f"Fehler: Das Spritesheet konnte nicht geladen werden unter Pfad: {SCARAB_PATH}")
        pygame.quit()
        exit()

    walk_frames = []
    for i in range(NUM_FRAMES):
        frame = get_sprite(
            scarab_sprite_sheet,
            x=i * SPRITE_WIDTH,
            y=Y_POS_ROW,
            width=SPRITE_WIDTH,
            height=SPRITE_HEIGHT
        )
        # Skalierung mit Ganzzahl-Faktor (Pixel-Art-freundlich)
        scaled_frame = pygame.transform.scale(
            frame,
            (SPRITE_WIDTH * SCALE_FACTOR, SPRITE_HEIGHT * SCALE_FACTOR)
        )
        walk_frames.append(scaled_frame)

    return tuple(walk_frames)




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
    screen_width = 400
    screen_height = 200
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Scarab Walking Across Screen (16x16)")

    # Frames laden
    SCARAB_WALK_FRAMES = scarab_walk()

    if not SCARAB_WALK_FRAMES:
        return

    # Animations-Variablen
    current_frame_index = 0.0
    animation_speed = 0.12  # Wechselt den Frame alle 0.12 Sekunden

    # Position des Sprites: Start außerhalb des linken Rands
    start_x = -SCARAB_WALK_FRAMES[0].get_width()

    sprite_rect = SCARAB_WALK_FRAMES[0].get_rect(
        x=start_x,
        centery=screen.get_rect().centery
    )

    clock = pygame.time.Clock()
    running = True

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                # Schaltet den Debug-Modus (roter Rahmen und FPS) um
                elif event.key == pygame.K_d:
                    DEBUG_MODE = not DEBUG_MODE

        # Update (Zeit-basiert)
        dt = clock.tick(60) / 1000.0  # Zeit seit dem letzten Frame in Sekunden

        #  FRAME-WECHSEL (Animation)
        current_frame_index += dt / animation_speed
        if current_frame_index >= len(SCARAB_WALK_FRAMES):
            current_frame_index = 0

        #  POSITION-UPDATE
        # Berechnet die Strecke für dieses Zeitintervall (dt)
        distance_moved = MOVEMENT_SPEED_PIXELS_PER_SECOND * dt
        sprite_rect.x += distance_moved

        #  Setze den Scarab zurück, wenn er rechts verschwindet
        if sprite_rect.left > screen_width:
            sprite_rect.right = 0

            # Frame holen
        current_frame = SCARAB_WALK_FRAMES[int(current_frame_index)]

        # 3. Rendering
        screen.fill((50, 65, 70))

        # Rendert den aktuellen Frame an seiner bewegten Position
        screen.blit(current_frame, sprite_rect)

        # DEBUG-AUSGABE (Zur Überprüfung des Renderings und der Position)
        if DEBUG_MODE:
            # Roter Rahmen um das Sprite-Rect
            pygame.draw.rect(screen, (255, 0, 0), sprite_rect, 1)

            # FPS-Anzeige
            if font:
                fps = clock.get_fps()
                text = font.render(f"FPS: {fps:.1f} ", True, (255, 255, 255))
                screen.blit(text, (5,5))

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()