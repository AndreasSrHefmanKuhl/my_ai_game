import pygame
import os


# ----------------------------------------------------------------------
#  PRÄZISIONS-HILFSFUNKTION
# ----------------------------------------------------------------------

def get_sprite(sheet, x, y, width, height):
    sprite = pygame.Surface([width, height], pygame.SRCALPHA)
    sprite.blit(sheet, (0, 0), pygame.Rect(x, y, width, height))
    return sprite


def show_tile_indices(tileset_path, source_size=16):
    pygame.init()

    # 1. ERST das Fenster erstellen
    zoom = 3
    display_w = 900
    display_h = 700
    screen = pygame.display.set_mode((display_w, display_h))
    pygame.display.set_caption("Tile Index Viewer - Mausrad zum Scrollen")

    # 2. DANACH das Bild laden und konvertieren
    try:
        sheet = pygame.image.load(tileset_path).convert_alpha()
    except Exception as e:
        print(f"\n[!!!] PYGAME LOAD ERROR: {e}")
        return

    font = pygame.font.SysFont("Arial", 14, bold=True)

    # Berechnung der Tiles
    tiles_per_row_in_sheet = sheet.get_width() // source_size
    rows_in_sheet = sheet.get_height() // source_size
    total_tiles = tiles_per_row_in_sheet * rows_in_sheet

    # Anzeige-Gitter
    viewer_cols = 10
    scroll_y = 0
    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill((40, 40, 45))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: scroll_y += 50
                if event.button == 5: scroll_y -= 50

        # Tiles zeichnen
        for i in range(total_tiles):
            grid_x = (i % tiles_per_row_in_sheet) * source_size
            grid_y = (i // tiles_per_row_in_sheet) * source_size

            draw_x = (i % viewer_cols) * (source_size * zoom + 20) + 40
            draw_y = (i // viewer_cols) * (source_size * zoom + 30) + 50 + scroll_y

            if -100 < draw_y < display_h:
                tile_surf = get_sprite(sheet, grid_x, grid_y, source_size, source_size)
                scaled_tile = pygame.transform.scale(tile_surf, (source_size * zoom, source_size * zoom))

                pygame.draw.rect(screen, (60, 60, 65), (draw_x, draw_y, source_size * zoom, source_size * zoom), 1)
                screen.blit(scaled_tile, (draw_x, draw_y))

                txt = font.render(str(i), True, (255, 255, 0))
                screen.blit(txt, (draw_x, draw_y - 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


# ----------------------------------------------------------------------
#  SYSTEMATISCHE PFAD-DIAGNOSE
# ----------------------------------------------------------------------

if __name__ == "__main__":
    #  Wo bin ich?
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\n1. Skript-Standort: {script_dir}")

    # Gehe eine Ebene hoch zum Hauptverzeichnis
    base_dir = os.path.abspath(os.path.join(script_dir, ".."))
    print(f"2. Hauptverzeichnis (base_dir): {base_dir}")

    # Liste alle Ordner im Hauptverzeichnis auf (zum Abgleichen)
    print(f"3. Ordner im Hauptverzeichnis: {os.listdir(base_dir)}")

    #
    # Prüfe hier die Schreibweise! (Ist es 'Assets' oder 'assets'?)
    target_rel_path = os.path.join("assets", "Robot Warfare Asset Pack 22-11-24", "Tileset", "tileset_compressed.png")
    final_path = os.path.join(base_dir, target_rel_path)
    final_path = os.path.normpath(final_path)

    print(f"4. Vollständiger Zielpfad: {final_path}")

    # 5. Letzter Check & Start
    if os.path.exists(final_path):
        print("\n[ERFOLG] Datei gefunden! Starte Viewer...")
        show_tile_indices(final_path)
    else:
        print("\n[FEHLER] Datei existiert nicht unter diesem Pfad.")

        # Test: Existiert wenigstens der assets Ordner?
        assets_path = os.path.join(base_dir, "assets")
        if not os.path.exists(assets_path):
            print(f"HINWEIS: Der Ordner '{assets_path}' wurde nicht gefunden. Schreibweise prüfen!")