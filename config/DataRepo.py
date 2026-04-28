import os
import pygame
from config.classes import Tile, Player, Enemy, Endboss

""" graphical functions """

def set_display(width, height, name):
    """
        Initializes the Pygame display window and sets the title.

        Args:
            width (int): The width of the window in pixels.
            height (int): The height of the window in pixels.
            name (str): The text to display in the window's title bar.

        Returns:
            tuple: (pygame.Surface, int, int) representing the screen surface and its dimensions.
        """

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(name)
    return screen, width, height


def draw_health_bar(surf, x, y, current, max_val, width=200, height=20, color=(255, 0, 0)):
    """
        Renders a multi-layered health bar with a background, fill, and border.

        Args:
            surf (pygame.Surface): The surface to draw the bar onto.
            x (int): The x-coordinate for the top-left corner.
            y (int): The y-coordinate for the top-left corner.
            current (int): The current health value.
            max_val (int): The maximum health value.
            width (int, optional): Total width of the bar. Defaults to 200.
            height (int, optional): Total height of the bar. Defaults to 20.
            color (tuple, optional): RGB color for the health fill. Defaults to Red.
        """

    if max_val <= 0: return


    pygame.draw.rect(surf, (0, 0, 0), (x, y, width, height))


    ratio = current / max_val
    fill_width = int(width * ratio)

    # Draw Foreground (Red) - Only if fill_width > 0
    if fill_width > 0:
        pygame.draw.rect(surf, color, (x, y, fill_width, height))


    pygame.draw.rect(surf, (255, 255, 255), (x, y, width, height), 1)

def show_loading_screen(display, text="Agent generiert neues Level..."):
    """
        Displays a centered text message on a black background to indicate background processing.

        Args:
            display (pygame.Surface): The main display surface.
            text (str, optional): The loading message to display.
        """

    font = pygame.font.SysFont("Arial", 32)
    text_surf = font.render(text, True, (255, 255, 255))
    rect = text_surf.get_rect(center=(400, 300)) # Zentriert auf 800x600
    display.fill((0, 0, 0))
    display.blit(text_surf, rect)
    pygame.display.update()

def show_game_over_screen(display):
    """
        Renders a large 'GAME OVER' message in the center of the screen.

        Args:
            display (pygame.Surface): The main display surface.
        """
    font = pygame.font.SysFont("Arial", 64)
    text_surf = font.render("GAME OVER", True, (255, 0, 0))
    rect = text_surf.get_rect(center=(400, 300))
    display.fill((0, 0, 0))
    display.blit(text_surf, rect)
    pygame.display.update()


def show_start_screen(display, text="Welcome to THE CASTLE!"):
    """
        Runs an interactive menu loop for user authentication (Login, Register, Delete).

        Handles keyboard input for usernames and passwords, toggles between auth modes,
        and communicates with the database module.

        Args:
            display (pygame.Surface): The main display surface.
            text (str, optional): Initial greeting or feedback message.

        Returns:
            int: The unique user ID of the logged-in user.
        """
    from config.database import login_user, register_user
    font = pygame.font.SysFont("Arial", 28)
    input_font = pygame.font.SysFont("Arial", 24)

    username = ""
    password = ""
    active_field = "username"
    mode = "LOGIN"  # tracks whether logging in or registering
    logged_in_id = None

    while logged_in_id is None:
        display.fill((0, 0, 0))

        # Render Main Title/Feedback
        instr_surf = font.render(text, True, (255, 255, 255))
        display.blit(instr_surf, (400 - instr_surf.get_width() // 2, 100))

        # Render Current Mode
        mode_color = (0, 255, 255) if mode == "LOGIN" else (0, 255, 0) if mode == "REGISTER" else (255,0,0)
        mode_surf = font.render(f"MODE: {mode}", True, mode_color)
        display.blit(mode_surf, (400 - mode_surf.get_width() // 2, 180))

        # Render Input Boxes
        u_color = (255, 255, 0) if active_field == "username" else (200, 200, 200)
        p_color = (255, 255, 0) if active_field == "password" else (200, 200, 200)

        u_surf = input_font.render(f"Username: {username}", True, u_color)
        p_surf = input_font.render(f"Password: {'*' * len(password)}", True, p_color)

        display.blit(u_surf, (250, 250))
        display.blit(p_surf, (250, 300))

        # Instructions
        hint_text = f"TAB: Switch Field | L: Login Mode | R: Register Mode | D: Delete Mode"
        hint = input_font.render(hint_text, True, (150, 150, 150))
        enter_hint = input_font.render(f"Press ENTER to {mode.lower()}", True, (100, 100, 100))

        display.blit(hint, (400 - hint.get_width() // 2, 400))
        display.blit(enter_hint, (400 - enter_hint.get_width() // 2, 440))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                # Mode Switching
                if event.key == pygame.K_l:
                    mode = "LOGIN"
                elif event.key == pygame.K_r:
                    mode = "REGISTER"
                elif event.key == pygame.K_d:
                    mode = 'DELETE'

                # Logic Execution
                elif event.key == pygame.K_RETURN:
                    if mode == "LOGIN":
                        logged_in_id = login_user(username, password)
                        if not logged_in_id:
                            text = "Login Failed! Try again or register yourself please!"
                    else:

                        success = register_user(username, password)
                        if success:
                            text = "Registered! Now please Login."
                            mode = "LOGIN"
                        else:
                            text = "Registration Failed (User might exist)."



                elif event.key == pygame.K_TAB:
                    active_field = "password" if active_field == "username" else "username"

                elif event.key == pygame.K_BACKSPACE:
                    if active_field == "username":
                        username = username[:-1]
                    else:
                        password = password[:-1]
                else:
                    # Filter out non-printable characters or system keys
                    if event.unicode.isprintable():
                        if active_field == "username":
                            username += event.unicode
                        else:
                            password += event.unicode

    return logged_in_id



""" data loading functions """

def load_all_animations(base_path, scale_factor=2, target_states=None):
    """
        Recursively loads images from subfolders and organizes them into an animation dictionary.

        Args:
            base_path (str): Path to the directory containing state folders (e.g., 'idle', 'walk').
            scale_factor (int, optional): Multiplier to resize the images. Defaults to 2.
            target_states (dict, optional): Mapping to rename folder names to specific logic states.

        Returns:
            dict: A dictionary where keys are state names and values are lists of pygame.Surface objects.
        """
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
    """
        Slices a single tileset image into a library of individual scaled tiles.

        Args:
            path (str): File path to the tileset image.
            source_size (int, optional): The pixel size of tiles in the source image. Defaults to 16.
            target_size (int, optional): The pixel size to scale tiles to for the game. Defaults to 48.

        Returns:
            dict: A dictionary mapping generated names (e.g., 'vania_001') to scaled surfaces.
        """
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
    """
        Filters and renames a raw tile library into a curated set based on an alias mapping.

        Args:
            raw_library (dict): The full dictionary of loaded tiles.
            alias_dict (dict): Mapping of user-friendly names to the 'vania_xxx' keys.

        Returns:
            dict: The curated tile library.
        """
    curated = {}
    for curated_name, raw_name in alias_dict.items():
        if raw_name in raw_library:
            curated[curated_name] = raw_library[raw_name]
    return curated



""" level building functions"""


def get_level_map(win_h,tile_size,map_width):
    """
        Generates a static, hard-coded level map grid for initial testing or fallback.

        Args:
            win_h (int): Window height to determine the number of rows.
            tile_size (int): Size of individual tiles.
            map_width (int): The width of the level in tile units.

        Returns:
            list: A 2D list (list of lists) representing the tile grid.
        """
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
            row[30] = "E"




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
            row[20] = "E"

            for i in range(18, 24):
                row[i] = "floor_head"
        elif r == rows_needed - 11:
            row[20] = "E"


        # --- PLATFORM 3 ----
        elif r == rows_needed - 11:

            for i in range(12, 16):
                row[i] = "floor_head"
        elif r == rows_needed - 12:
            row[14] = "E"  # Enemy on high platform

        level_map.append(row)

    return level_map

def build_level(level_data, tile_library, tile_size=48, player_data=None, enemy_data_list=None):
    """
        Parses a 2D level map and instantiates the corresponding Sprite and Tile objects.

        Args:
            level_data (list): The 2D list representing the map.
            tile_library (dict): Dictionary of available tile surfaces.
            tile_size (int, optional): Dimension of tiles. Defaults to 48.
            player_data (dict, optional): Animation dictionary for the player.
            enemy_data_list (list/dict, optional): Animation assets for enemies and bosses.

        Returns:
            tuple: (list of Tiles, list of Enemies, Player object).
        """
    level_tiles, enemies, player = [], [], None
    e_idx = 0
    for r_idx, row in enumerate(level_data):
        for c_idx, cell in enumerate(row):
            x, y = c_idx * tile_size, r_idx * tile_size
            if cell == "P" and player_data:
                player = Player(x, y, player_data)
            elif cell == "E" and enemy_data_list:
                temp_enemy = Enemy(x, y, enemy_data_list[e_idx % len(enemy_data_list)])
                temp_enemy.rect.bottom = y + tile_size
                enemies.append(temp_enemy)
                e_idx += 1
            elif cell == "G":

                new_boss = Endboss(x, y, enemy_data_list["ghoul"])
                enemies.append(new_boss)
            elif cell in tile_library:
                level_tiles.append(Tile(x, y, tile_size, tile_library[cell], cell))
    return level_tiles, enemies, player


def create_level_surface(level_data, tile_library, background_img, tile_size=48):
    """
        Pre-renders the static tile map and background into a single large Surface for performance.

        Args:
            level_data (list): The 2D list representing the map.
            tile_library (dict): Dictionary of available tile surfaces.
            background_img (pygame.Surface): The image to use as the level background.
            tile_size (int, optional): Dimension of tiles. Defaults to 48.

        Returns:
            pygame.Surface: A single surface containing the entire rendered level background.
        """


    cols = len(level_data[0]) if level_data else 0
    rows = len(level_data)
    w, h = cols * tile_size, rows * tile_size

    surf = pygame.Surface((w, h)).convert_alpha()

   # Draw the background image if provided
    if background_img:
        scaled_bg = pygame.transform.scale(background_img, (w, h))
        surf.blit(scaled_bg, (0, 0))

    for r_idx, row in enumerate(level_data):
        for c_idx, cell in enumerate(row):
            if cell in tile_library:
                surf.blit(tile_library[cell], (c_idx * tile_size, r_idx * tile_size))
    return surf


""" ai agent intergated functions"""

def let_agent_cook(level_data,performance_tracker,boss_allowed=False):

    from user_interface.agent import app
    from langchain_core.messages import HumanMessage

    """
    Interfaces with an external LLM (AI Agent) to generate a dynamic level map.
    
    Passes the current map template and player performance data to the agent 
    to receive a modified, challenging level layout.

    Args:
        level_data (list): The current 2D level map template.
        performance_tracker (dict): Data regarding player health, kills, or speed.
        boss_allowed (bool, optional): Whether the agent is permitted to place a boss ('G').

    Returns:
        list: A new 2D list representing the AI-generated level map.
    """

    boss_rule = ""
    if boss_allowed:
        boss_rule = "CRITICAL: Place exactly ONE 'G' (Endboss) at the far right. It MUST be on a solid 'way' tile."
    else:
        boss_rule = "DO NOT place a 'G' tile. Use 'E' for standard enemies only."


        boss_text = "Place ONE 'G' (Boss) on a platform" if boss_allowed else "DO NOT use 'G'"

        prompt_content = f"""
        ACT AS: A professional 2D Metroidvania Level Designer.
        OBJECTIVE: Generate a valid, playable level map as a Python list of lists using these specific tiles:
        - 'P': Player Start 
        - 'E': Enemy (can be on a platform)
        - 'G': Boss (Only if allowed)
        - 'way1', 'way2': Platform tiles, Ground tiles
        - '.': Empty space

        CRITICAL LEVEL RULES:
        1. PLATFORM INTEGRITY: Every platform MUST be at least 4 tiles long. Never place a single tile or a 2-tile platform.
        2. ENEMY PLACEMENT:Number of enemies should fit to the length of the Level! Place enemies ('E') on platforms. Ensure there are at least 3 tiles of space for them to patrol before hitting an edge or a wall.
        3. VERTICALITY: Jumps between platforms should be no more than 2 tiles high and 3 tiles wide to ensure the player can reach them.
        4. MAP FLOW: Start 'P' on the far left and 'exit' on the far right. Create a clear path of platforms from start to finish.
        5. NO TRAPS: Do not surround 'P' or 'exit' with walls.
        6. {boss_rule}
        7. Player(P) must be in level map at all times, enemies must be in level map at least 3 tiles away from player(P).
        8. Level must be playable. Means no platform are on top of each other, except you want to build stairs. 
        9. GOAL: Generate a level map that will challe nge the player based on its {performance_tracker}
        PLAYER PERFORMANCE DATA: {performance_tracker}
        BOSS ALLOWED: {boss_text}

        CURRENT MAP TEMPLATE :
        {level_data}

        RETURN ONLY the Python list of lists. same like {level_data}, No explanation, no markdown, just the code.
        """
    try:

        print("--- Agent wird aufgerufen ---")
        response = app.invoke({
            "messages": [HumanMessage(content=prompt_content)]
        })


        if response and "messages" in response:
            final_message = response["messages"][-1].content


            clean_content = final_message.replace("```python", "").replace("```", "").strip()

            # extract List from string
            start = clean_content.find("[")
            end = clean_content.rfind("]") + 1
            if start != -1 and end > 0:
                clean_content = clean_content[start:end]
                return eval(clean_content)

    except Exception as e:
        print(f"Fehler im DataRepo/Agent-Workflow: {e}")

    print(level_data)

        #Fallback if Agent is not working
    return level_data




