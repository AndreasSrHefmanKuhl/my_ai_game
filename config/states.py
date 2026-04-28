import pygame
import os
from config.database import login_user, register_user, init_db, delete_user
from config.DataRepo import (
    load_all_animations, load_tileset_named_library, apply_tile_aliases,
    get_level_map, build_level, create_level_surface, let_agent_cook,
    draw_health_bar
)
from config.vania_tile_aliases import VANIA_TILE_ALIASES


class GameStateManager:
    def __init__(self, display):
        self.display = display
        self.level_count = 0  # Track levels passed
        self.user_id = None
        self.current_state = MenuState(self.display)

    def update(self, dt, events):
        next_state = self.current_state.update(dt, events)

        # Handle the transition to a new level
        if isinstance(next_state, LoadingState):

            boss_ready = (self.level_count >= 3)
            next_state.boss_allowed = boss_ready

            # Increment count for the level that is about to be cooked
            self.level_count += 1
            print(f"Moving to Level {self.level_count}. Boss Status: {boss_ready}")

        if next_state:
            # Sync user_id across states
            if hasattr(next_state, 'user_id'):
                if self.user_id: next_state.user_id = self.user_id
            self.current_state = next_state

    def draw(self):
        self.current_state.draw(self.display)


class MenuState:
    def __init__(self, display):
        self.display = display
        self.font = pygame.font.SysFont("Arial", 28)
        self.input_font = pygame.font.SysFont("Arial", 24)
        self.username = ""
        self.password = ""
        self.active_field = "username"
        self.mode = "LOGIN"
        self.feedback_text = "L: Login | R: Register | D: Delete Account"
        self.msg_color = (255, 255, 255)

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    self.mode = "LOGIN"
                    self.msg_color = (255, 255, 255)
                elif event.key == pygame.K_r:
                    self.mode = "REGISTER"
                    self.msg_color = (255, 255, 255)
                elif event.key == pygame.K_d:
                    self.mode = "DELETE"
                    self.msg_color = (255, 150, 0)

                elif event.key == pygame.K_TAB:
                    self.active_field = "password" if self.active_field == "username" else "username"
                elif event.key == pygame.K_BACKSPACE:
                    if self.active_field == "username":
                        self.username = self.username[:-1]
                    else:
                        self.password = self.password[:-1]

                elif event.key == pygame.K_RETURN:
                    if self.mode == "DELETE":
                        uid = login_user(self.username, self.password)
                        if uid:
                            success, msg = delete_user(uid)
                            self.feedback_text = msg
                            if success: self.mode = "LOGIN"; self.msg_color = (100, 255, 100)
                        else:
                            self.feedback_text = "Delete Failed: User not found."
                            self.msg_color = (255, 100, 100)

                    elif self.mode == "LOGIN":
                        uid = login_user(self.username, self.password)
                        if uid:
                            return PlayState(self.display, uid)
                        else:
                            self.feedback_text = "Login Failed!"; self.msg_color = (255, 100, 100)

                    elif self.mode == "REGISTER":
                        success, msg = register_user(self.username, self.password)
                        self.feedback_text = msg
                        if success: self.mode = "LOGIN"; self.msg_color = (100, 255, 100)
                else:
                    if event.unicode.isprintable():
                        if self.active_field == "username":
                            self.username += event.unicode
                        else:
                            self.password += event.unicode
        return None

    def draw(self, screen):
        screen.fill((20, 20, 30))
        t_surf = self.font.render(f"--- {self.mode} ---", True, (255, 255, 255))
        f_surf = self.input_font.render(self.feedback_text, True, self.msg_color)
        screen.blit(t_surf, (400 - t_surf.get_width() // 2, 80))
        screen.blit(f_surf, (400 - f_surf.get_width() // 2, 140))

        u_col = (255, 255, 0) if self.active_field == "username" else (200, 200, 200)
        p_col = (255, 255, 0) if self.active_field == "password" else (200, 200, 200)
        screen.blit(self.input_font.render(f"User: {self.username}", True, u_col), (250, 250))
        screen.blit(self.input_font.render(f"Pass: {'*' * len(self.password)}", True, p_col), (250, 310))


class PlayState:
    def __init__(self, display, user_id, level_map=None):
        self.display = display
        self.user_id = user_id
        self.TS = 32
        self.map_width = 64
        self.camera_x = 0
        self.performance_tracker = {"punch": 0, "kick": 0, "damage_dealt": 0}

        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.normpath(os.path.join(base_dir, ".."))
        assets_vania = os.path.join(project_root, "assets", "Vania")

        # Load Animations
        self.player_data = load_all_animations(os.path.join(assets_vania, "SPRITES", "player", "sprites", "idle"), 2)
        self.enemy_data = [
            load_all_animations(os.path.join(assets_vania, "SPRITES", "wizard", "idle-sprites"), 2),
            load_all_animations(os.path.join(assets_vania, "SPRITES", "angel", "sprites"), 2),
            load_all_animations(os.path.join(assets_vania, "SPRITES", "burning-ghoul", "sprites"), 2)
        ]

        tileset_path = os.path.join(assets_vania, "environment", "tileset.png")
        raw_tiles = load_tileset_named_library(tileset_path, 16, self.TS)
        self.tile_library = apply_tile_aliases(raw_tiles, VANIA_TILE_ALIASES)
        bg_img = pygame.image.load(os.path.join(assets_vania, "environment", "background.png")).convert_alpha()

        self.level_map = level_map if level_map else get_level_map(600, self.TS, self.map_width)
        self.level_tiles, self.enemies, self.player = build_level(
            self.level_map, self.tile_library, self.TS, self.player_data, self.enemy_data
        )
        self.level_surface = create_level_surface(self.level_map, self.tile_library, bg_img, self.TS)

    def update(self, dt, events):
        keys = pygame.key.get_pressed()
        dx = 0
        requested_state = "stand"

        if keys[pygame.K_LEFT]:
            dx = -250; requested_state = "walk"
        elif keys[pygame.K_RIGHT]:
            dx = 250; requested_state = "walk"

        if keys[pygame.K_f]:
            requested_state = "punch"; self.performance_tracker["punch"] += 1
        elif keys[pygame.K_g]:
            requested_state = "kick"; self.performance_tracker["kick"] += 1
        elif keys[pygame.K_UP] or keys[pygame.K_SPACE]:
            self.player.jump(); requested_state = "jump"

        self.player.change_state(requested_state)
        self.player.rect.x += dx * dt

        # Horizontal Wall Collisions
        for t in [tile for tile in self.level_tiles if tile.is_wall]:
            if self.player.rect.colliderect(t.rect):
                if dx > 0:
                    self.player.rect.right = t.rect.left
                elif dx < 0:
                    self.player.rect.left = t.rect.right

        # Gravity and Vertical Collisions
        self.player.apply_gravity()
        self.player.on_ground = False
        for t in [tile for tile in self.level_tiles if tile.is_floor or tile.is_wall]:
            if self.player.rect.colliderect(t.rect):
                if self.player.velocity_y > 0:
                    self.player.rect.bottom = t.rect.top
                    self.player.velocity_y = 0
                    self.player.on_ground = True

        self.player.update(dt, dx)
        for e in self.enemies: e.update(dt, self.player.rect, self.level_tiles)

        # Combat
        if self.player.is_attacking():
            zone = self.player.get_attack_rect()
            for e in self.enemies:
                if zone.colliderect(e.rect):
                    e.take_damage(2.5)
                    self.performance_tracker["damage_dealt"] += 2.5

        self.enemies = [e for e in self.enemies if not e.is_dead]

        if self.player.health <= 0: return GameOverState(self.display, self.user_id)
        if len(self.enemies) == 0: return LoadingState(self.display, self.user_id, self.level_map,
                                                       self.performance_tracker)

        target_x = self.player.rect.centerx - 400
        self.camera_x = max(0, min(target_x, (self.map_width * self.TS) - 800))
        return None

    def draw(self, screen):

        screen.blit(self.level_surface, (-self.camera_x, 0))
        for e in self.enemies:
            screen.blit(e.image, (int(e.rect.x - self.camera_x), int(e.rect.y)))
        screen.blit(self.player.image, (self.player.rect.x - self.camera_x, self.player.rect.y))
        draw_health_bar(screen, 20, 20, self.player.health, 100, height=10)
        pygame.display.flip()


class LoadingState:
    def __init__(self, display, user_id, old_map, tracker):
        self.display = display
        self.user_id = user_id
        self.old_map = old_map
        self.tracker = tracker
        self.boss_allowed = False  # Set by GameStateManager right before update

    def update(self, dt, events):
        self.draw(self.display)
        pygame.display.flip()

        new_map = let_agent_cook(self.old_map, self.tracker, self.boss_allowed)

        player_exists = any('P' in row for row in new_map)

        if not player_exists:
            print("Agent forgot the player! Retrying...")
            return self

        return PlayState(self.display, self.user_id, new_map)

    def draw(self, screen):
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont("Arial", 32)
        txt = font.render("Agent is cooking the level...", True, (255, 255, 255))
        screen.blit(txt, (400 - txt.get_width() // 2, 300))
        pygame.display.flip()


class GameOverState:
    def __init__(self, display, user_id):
        self.display = display
        self.user_id = user_id

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                return MenuState(self.display)
        return None

    def draw(self, screen):
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont("Arial", 64)
        surf = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(surf, (400 - surf.get_width() // 2, 300))