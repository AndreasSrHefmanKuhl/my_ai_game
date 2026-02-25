import pygame
import os


def get_sprite(sheet, x, y, width, height):
    sprite = pygame.Surface([width, height], pygame.SRCALPHA)
    sprite.blit(sheet, (0, 0), pygame.Rect(x, y, width, height))
    return sprite


def is_tile_mostly_transparent(tile_surf: pygame.Surface, *, alpha_threshold: int = 10, max_solid_ratio: float = 0.01) -> bool:
    w, h = tile_surf.get_size()
    total = w * h
    if total <= 0:
        return True
    mask = pygame.mask.from_surface(tile_surf, alpha_threshold)
    solid = mask.count()
    return (solid / total) <= max_solid_ratio


def iter_tile_rects(sheet_w: int, sheet_h: int, tile_size: int, margin: int, spacing: int):
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
    name_prefix: str = "vania",
):
    """
    Tile viewer with margin + spacing support (for internet tilesets).

    NEW:
      - Left click: prints base key (e.g. 'vania_064')
      - Shift + Left click: prints alias template (e.g. '"tile_064": "vania_064",')

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

    display_w = 900
    display_h = 480
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

    cache_key = None
    tiles_scaled: list[pygame.Surface] = []
    tile_indices: list[int] = []
    is_empty: list[bool] = []

    last_click_msg = ""

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

    def tile_at_screen_pos(mx: int, my: int, visible: list[int]) -> int | None:
        """
        Returns the index into tiles_scaled/tile_indices (k) for the clicked tile,
        or None if click is outside any tile cell.
        """
        tile_draw_w = tile_size * zoom
        tile_draw_h = tile_size * zoom

        # reverse mapping from screen -> visible grid cell
        x0 = 20
        y0 = 50 + scroll_y

        rel_x = mx - x0
        rel_y = my - y0
        if rel_x < 0 or rel_y < 0:
            return None

        cell_w = tile_draw_w + 20
        cell_h = tile_draw_h + 30

        col = rel_x // cell_w
        row = rel_y // cell_h
        if col < 0 or col >= viewer_cols or row < 0:
            return None

        # ensure click is inside the tile rectangle (not in padding)
        in_cell_x = rel_x % cell_w
        in_cell_y = rel_y % cell_h
        if in_cell_x > tile_draw_w or in_cell_y > tile_draw_h:
            return None

        visible_idx = int(row * viewer_cols + col)
        if visible_idx < 0 or visible_idx >= len(visible):
            return None

        return visible[visible_idx]

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
                elif event.button == 1:
                    k = tile_at_screen_pos(*event.pos, visible)
                    if k is not None:
                        idx = tile_indices[k]
                        base_key = f"{name_prefix}_{idx:03d}"

                        mods = pygame.key.get_mods()
                        if mods & pygame.KMOD_SHIFT:
                            alias_name = f"tile_{idx:03d}"
                            line = f"\"{alias_name}\": \"{base_key}\","
                            print(line)
                            last_click_msg = line
                        else:
                            print(base_key)
                            last_click_msg = base_key

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

            txt = font.render(str(tile_indices[k]), True, (255, 255, 0))
            screen.blit(txt, (draw_x, draw_y - 20))

        hud = font.render(
            f"H hide_empty={hide_empty} | tile={tile_size} | margin={margin} | spacing={spacing} | "
            f"tiles={len(visible)}/{len(tile_indices)} | click=key | Shift+click=alias line",
            True,
            (220, 220, 220),
        )
        screen.blit(hud, (20, 10))

        if last_click_msg:
            hud2 = font.render(f"Last: {last_click_msg}", True, (200, 200, 255))
            screen.blit(hud2, (20, 28))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, ".."))
    final_path = os.path.normpath(os.path.join(base_dir, "assets", "Vania", "environment", "tileset.png"))

    if os.path.exists(final_path):
        show_tile_indices(
            final_path,
            tile_size=16,
            margin=0,
            spacing=0,
            zoom=3,
            hide_empty=True,
            name_prefix="vania",
        )
    else:
        print("\n[FEHLER] Datei existiert nicht unter diesem Pfad.")