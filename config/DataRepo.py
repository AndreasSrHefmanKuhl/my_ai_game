import os
import pygame
from config.classes import Tile, Player, Enemy



def set_display(width, height, name):
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(name)
    return screen, width, height


def draw_health_bar(surf, x, y, current, max_val, width=200, height=20, color=(255, 0, 0)):
    if max_val <= 0: return

    # Draw Background (Black)
    pygame.draw.rect(surf, (0, 0, 0), (x, y, width, height))

    # Calculate width of red bar
    ratio = current / max_val
    fill_width = int(width * ratio)

    # Draw Foreground (Red) - Only if fill_width > 0
    if fill_width > 0:
        pygame.draw.rect(surf, color, (x, y, fill_width, height))

    # Draw a white outline so you can see the bar's shape
    pygame.draw.rect(surf, (255, 255, 255), (x, y, width, height), 1)

def show_loading_screen(display, text="Agent generiert neues Level..."):
    font = pygame.font.SysFont("Arial", 32)
    text_surf = font.render(text, True, (255, 255, 255))
    rect = text_surf.get_rect(center=(400, 300)) # Zentriert auf 800x600
    display.fill((0, 0, 0))
    display.blit(text_surf, rect)
    pygame.display.update()

def show_game_over_screen(display, player, enemies, score, high_score):
    font = pygame.font.SysFont("Arial", 64)
    text_surf = font.render("GAME OVER", True, (255, 0, 0))
    rect = text_surf.get_rect(center=(400, 300))
    display.fill((0, 0, 0))
    display.blit(text_surf, rect)
    pygame.display.update()

def show_start_screen(display, text = "Welcome to THE CASTLE!"):
    font = pygame.font.SysFont("Arial", 32)
    text_surf = font.render(text , True, (255, 255, 255))
    rect = text_surf.get_rect(center=(400, 300))
    display.fill((0, 0, 0))
    display.blit(text_surf, rect)
    pygame.display.update()




def load_all_animations(base_path, scale_factor=2, target_states=None):
    animations = {}
    if not os.path.exists(base_path): return {}

    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        if os.path.isdir(folder_path):
            frames = []
            for file in sorted(os.listdir(folder_path)):
                if file.endswith((".png", ".jpg")):
                    img = pygame.image.load(os.path.join(folder_path, file)).convert_alpha()
                    w, h = img.get_size()
                    img = pygame.transform.scale(img, (int(w * scale_factor), int(h * scale_factor)))
                    frames.append(img)

            if frames:
                # If target_states is provided, map folder name to the logic name
                state_name = folder.lower()
                if target_states and state_name in target_states:
                    state_name = target_states[state_name]
                animations[state_name] = frames
    return animations

def load_tileset_named_library(path, source_size=16, target_size=48):
    sheet = pygame.image.load(path).convert_alpha()
    library = {}
    idx = 0
    for y in range(0, sheet.get_height(), source_size):
        for x in range(0, sheet.get_width(), source_size):
            surf = pygame.Surface((source_size, source_size), pygame.SRCALPHA)
            surf.blit(sheet, (0, 0), (x, y, source_size, source_size))
            scaled = pygame.transform.scale(surf, (target_size, target_size))
            library[f"vania_{idx:03d}"] = scaled
            idx += 1
    return library

def apply_tile_aliases(raw_library, alias_dict):
    curated = {}
    for curated_name, raw_name in alias_dict.items():
        if raw_name in raw_library:
            curated[curated_name] = raw_library[raw_name]
    return curated

def get_level_map(win_h,tile_size,map_width):
    rows_needed = win_h // tile_size
    level_map = []
    for r in range(rows_needed):
        # Default row: Side walls with empty space in between
        row = ["wall1"] + ["."] * (map_width - 2) + ["wall1"]

        # --- GROUND FLOOR ---
        if r == rows_needed - 1:
            row = ["floor_ground"] + ["floor_ground1"] * map_width
        elif r == rows_needed - 2:
            row = ["floor_head"] * map_width
            row[3] = "P"
            row[25] = "E"
            row[30] = "E"
            for i in range(15, 18):
                row[i] = "dead_01"



        # --- PLATFORM 1 (Low, Left) ---
        elif r == rows_needed - 7:

            for i in range(5, 10):
                row[i] = "floor_head"
        elif r == rows_needed - 8:
            row[7] = "E"

        # --- PLATFORM 2 (Mid, Right) ---
        elif r == rows_needed - 9:
            for i in range(18, 24):
                row[i] = "floor_ground"
        elif r == rows_needed - 10:

            for i in range(18, 24):
                row[i] = "floor_head"
        elif r == rows_needed - 11:
            row[20] = "E"


        # --- PLATFORM 3 ----
        elif r == rows_needed - 15:
            # Create a 4-tile wide platform in the middle
            for i in range(12, 16):
                row[i] = "floor_head"
        elif r == rows_needed - 16:
            row[14] = "E"  # Enemy on high platform

        level_map.append(row)

    return level_map

def build_level(level_data, tile_library, tile_size=48, player_data=None, enemy_data_list=None):
    level_tiles, enemies, player = [], [], None
    e_idx = 0
    for r_idx, row in enumerate(level_data):
        for c_idx, cell in enumerate(row):
            x, y = c_idx * tile_size, r_idx * tile_size
            if cell == "P" and player_data:
                player = Player(x, y, player_data)
            elif cell == "E" and enemy_data_list:
                # Use the enemy's own image height to align it to the BOTTOM of the tile
                temp_enemy = Enemy(x, y, enemy_data_list[e_idx % len(enemy_data_list)])
                temp_enemy.rect.bottom = y + tile_size
                enemies.append(temp_enemy)
                e_idx += 1
            elif cell in tile_library:
                level_tiles.append(Tile(x, y, tile_size, tile_library[cell], cell))
    return level_tiles, enemies, player


def create_level_surface(level_data, tile_library, background_img, tile_size=48):

    # Korrekte Berechnung der Dimensionen
    cols = len(level_data[0]) if level_data else 0
    rows = len(level_data)
    w, h = cols * tile_size, rows * tile_size

    surf = pygame.Surface((w, h)).convert_alpha()

    # Hintergrund auf die volle LEVEL-Größe skalieren, nicht nur Screen-Größe
    if background_img:
        scaled_bg = pygame.transform.scale(background_img, (w, h))
        surf.blit(scaled_bg, (0, 0))

    for r_idx, row in enumerate(level_data):
        for c_idx, cell in enumerate(row):
            if cell in tile_library:
                surf.blit(tile_library[cell], (c_idx * tile_size, r_idx * tile_size))
    return surf


def let_agent_cook(level_data,perfomance_tracker):

    from user_interface.agent import app
    from langchain_core.messages import HumanMessage

    """Sends current Gamedata to model and gives back from agent modified level data based on performance of the user"""


    prompt_content = f"""
    You are an Game Designer Agent for 2D platformer games like Castlevania or Super Metroid. 
    here are the current user-statistics: {perfomance_tracker}
    and the current level_layout: {level_data}

    Your Task: Raise the difficulty moderately based on the performance of the User.
    Place more enemies("E") on strategic places change the platforming-pattern.
    Take care that the player("P") will always be on startpoint Bottom_Left.
    Take care that player can solve the Level on harder Difficulty. Don't be unfair!
    Enemies has to stand on ground. They cant be somewhere in the air!
    You have to make platforming-patterns so the level will get more difficult. In order to make a platform use "way1" and "way2" tiles.  
    You can use the following tiles to create the new level: 
    - "way1","way2": way (player and enemies can ONLY walk on this tiles)
    - "wall1","wall2": wall(can not be used as way or platforming-tiles!)
    - "." : for showing the background image(needs to be filled for every empty tile place)
    - "E": for enemies
    - "P": for player
    
    Return ONLY the modified level_layout as a list of lists.
    """

    try:

        print("--- Agent wird aufgerufen ---")
        response = app.invoke({
            "messages": [HumanMessage(content=prompt_content)]
        })


        if response and "messages" in response:
            final_message = response["messages"][-1].content


            clean_content = final_message.replace("```python", "").replace("```", "").strip()

            # ectract List from string
            start = clean_content.find("[")
            end = clean_content.rfind("]") + 1
            if start != -1 and end > 0:
                clean_content = clean_content[start:end]
                return eval(clean_content)

    except Exception as e:
        print(f"Fehler im DataRepo/Agent-Workflow: {e}")

        #Fallback if Agent is not working
    return level_data


