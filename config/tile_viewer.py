import pygame
import os


# ----------------------------------------------------------------------
#  PRÄZISIONS-HILFSFUNKTION
# ----------------------------------------------------------------------

def get_sprite(sheet, x, y, width, height):
    sprite = pygame.Surface([width, height], pygame.SRCALPHA)
    sprite.blit(sheet, (0, 0), pygame.Rect(x, y, width, height))
    return sprite


def is_tile_mostly_transparent(tile_surf: pygame.Surface, *, alpha_threshold: int = 10, max_solid_ratio: float = 0.01) -> bool:
    """
    Returns True if the tile is basically empty.
    - alpha_threshold: pixels with alpha > this are considered 'solid'
    - max_solid_ratio: if solid_pixels/total_pixels <= this => empty
    """
    w, h = tile_surf.get_size()
    total = w * h
    if total <= 0:
        return True
    mask = pygame.mask.from_surface(tile_surf, alpha_threshold)
    solid = mask.count()
    return (solid / total) <= max_solid_ratio


def iter_tile_rects(sheet_w: int, sheet_h: int, tile_size: int, margin: int, spacing: int):
    """
    Yield (index, x, y, w, h) for each tile rect using margin/spacing rules.
    Stops when a tile would go out of bounds.
    """
    if tile_size <= 0:
        return

    y = margin
    i = 0
    while y + tile_size <= sheet_h:
        x = margin
        while x + tile_size <= sheet_w:
            yield i, x, y, tile_size, tile_size
            i += 1
            x += tile_size + spacing
        y += tile_size + spacing


def show_tile_indices(
    tileset_path: str,
    *,
    tile_size: int = 16,
    zoom: int = 3,
    viewer_cols: int = 10,
    margin: int = 0,
    spacing: int = 0,
    hide_empty: bool = True,
    alpha_threshold: int = 10,
    max_solid_ratio: float = 0.01,
):
    """
    Tile viewer with margin + spacing support (for internet tilesets).

    Controls:
      - Mouse wheel: scroll
      - H: toggle hide_empty
      - [: tile_size -= 1
      - ]: tile_size += 1
      - ,: spacing -= 1
      - .: spacing += 1
      - -: margin -= 1
      - =: margin += 1
      - ESC: quit
    """
    pygame.init()

    display_w = 1600
    display_h = 1400
    screen = pygame.display.set_mode((display_w, display_h))
    pygame.display.set_caption("Tile Index Viewer (margin/spacing)")

    try:
        sheet = pygame.image.load(tileset_path).convert_alpha()
    except Exception as e:
        print(f"\n[!!!] PYGAME LOAD ERROR: {e}")
        return

    font = pygame.font.SysFont("Arial", 14, bold=True)

    scroll_y = 0
    running = True
    clock = pygame.time.Clock()

    # Cache generated tiles for the current parameters
    cache_key = None
    tiles_scaled: list[pygame.Surface] = []
    tile_indices: list[int] = []      # the tile "i" index in reading order
    is_empty: list[bool] = []

    def rebuild_cache():
        nonlocal cache_key, tiles_scaled, tile_indices, is_empty
        key = (tile_size, margin, spacing, zoom, alpha_threshold, max_solid_ratio)
        if key == cache_key:
            return
        cache_key = key

        tiles_scaled = []
        tile_indices = []
        is_empty = []

        for i, x, y, w, h in iter_tile_rects(sheet.get_width(), sheet.get_height(), tile_size, margin, spacing):
            raw = get_sprite(sheet, x, y, w, h)
            empty = is_tile_mostly_transparent(raw, alpha_threshold=alpha_threshold, max_solid_ratio=max_solid_ratio)
            tiles_scaled.append(pygame.transform.scale(raw, (tile_size * zoom, tile_size * zoom)))
            tile_indices.append(i)
            is_empty.append(empty)

        print(
            f"[tile_viewer] rebuilt: tile_size={tile_size} margin={margin} spacing={spacing} "
            f"tiles={len(tile_indices)} hide_empty={hide_empty}"
        )

    def visible_list():
        if not hide_empty:
            return list(range(len(tile_indices)))
        return [k for k in range(len(tile_indices)) if not is_empty[k]]

    while running:
        rebuild_cache()
        visible = visible_list()

        screen.fill((40, 40, 45))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    scroll_y += 50
                elif event.button == 5:
                    scroll_y -= 50

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_h:
                    hide_empty = not hide_empty
                    scroll_y = 0

                elif event.key == pygame.K_LEFTBRACKET:
                    tile_size = max(1, tile_size - 1)
                    scroll_y = 0
                    cache_key = None
                elif event.key == pygame.K_RIGHTBRACKET:
                    tile_size = tile_size + 1
                    scroll_y = 0
                    cache_key = None

                elif event.key == pygame.K_COMMA:
                    spacing = max(0, spacing - 1)
                    scroll_y = 0
                    cache_key = None
                elif event.key == pygame.K_PERIOD:
                    spacing = spacing + 1
                    scroll_y = 0
                    cache_key = None

                elif event.key == pygame.K_MINUS:
                    margin = max(0, margin - 1)
                    scroll_y = 0
                    cache_key = None
                elif event.key == pygame.K_EQUALS:
                    margin = margin + 1
                    scroll_y = 0
                    cache_key = None

        tile_draw_w = tile_size * zoom
        tile_draw_h = tile_size * zoom

        for visible_idx, k in enumerate(visible):
            draw_x = (visible_idx % viewer_cols) * (tile_draw_w + 20) + 20
            draw_y = (visible_idx // viewer_cols) * (tile_draw_h + 30) + 50 + scroll_y

            if draw_y < -tile_draw_h - 60 or draw_y > display_h + 60:
                continue

            pygame.draw.rect(screen, (60, 60, 65), (draw_x, draw_y, tile_draw_w, tile_draw_h), 1)
            screen.blit(tiles_scaled[k], (draw_x, draw_y))

            # Important: this is the index in reading order -> corresponds to vania_{index:03d}
            txt = font.render(str(tile_indices[k]), True, (255, 255, 0))
            screen.blit(txt, (draw_x, draw_y - 20))

        hud = font.render(
            f"H hide_empty={hide_empty} | tile={tile_size} | margin={margin} | spacing={spacing} | "
            f"tiles={len(visible)}/{len(tile_indices)} |  [ ] tile  , . spacing  - = margin",
            True,
            (220, 220, 220),
        )
        screen.blit(hud, (20, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, ".."))
    final_path = os.path.normpath(os.path.join(base_dir, "assets", "Vania", "environment", "tileset.png"))

    if os.path.exists(final_path):
        # Vania is a clean grid: tile_size=16, margin=0, spacing=0
        show_tile_indices(final_path, tile_size=16, margin=0, spacing=0, zoom=3, hide_empty=True)
    else:
        print("\n[FEHLER] Datei existiert nicht unter diesem Pfad.")