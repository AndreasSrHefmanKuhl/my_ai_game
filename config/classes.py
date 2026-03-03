
import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, anim_dict):
        super().__init__()
        self.animations = anim_dict
        self.state = "stand"
        self.frame_index = 0.0

        # Physik-Variablen
        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_speed = -14
        self.on_ground = False
        self.is_crouching = False

        self.anim_speeds = {
            "stand": 0.15, "walk": 0.15, "punch": 0.15,
            "kick": 0.12, "crouch": 0.15, "crouchkick": 0.12
        }
        self.locked_states = {"punch", "kick", "crouchkick"}
        self.flip = False
        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def apply_gravity(self):
        """Zieht den Spieler nach unten."""
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

    def jump(self):
        """Springt, wenn der Spieler auf dem Boden steht."""
        if self.on_ground:
            self.velocity_y = self.jump_speed
            self.on_ground = False

    def change_state(self, new_state):
        if new_state not in self.animations: return
        if self.state in self.locked_states and new_state != self.state: return
        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0.0

    def update(self, dt, moving_x):
        if moving_x < 0:
            self.flip = True
        elif moving_x > 0:
            self.flip = False

        frames = self.animations[self.state]
        speed = self.anim_speeds.get(self.state, 0.15)
        self.frame_index += speed * (dt * 60)

        if self.frame_index >= len(frames):
            if self.state in self.locked_states:
                self.state = "stand"
            self.frame_index = 0.0

        img = frames[int(self.frame_index)]
        self.image = pygame.transform.flip(img, self.flip, False)


class Tile:
    def __init__(self, x, y, size, image, tile_type="ground"):
        self.rect = pygame.Rect(x, y, size, size)
        self.image = image
        self.tile_type = tile_type
        # Logik für Kollision
        self.is_wall = "wall" in tile_type or "brick" in tile_type
        self.is_floor = "way" in tile_type or "floor" in tile_type
        self.is_deadly = "dead" in tile_type


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, anim_dict):
        super().__init__()
        self.animations = anim_dict
        self.state = "walk"
        self.anim_index = 0.0
        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, dt):
        frames = self.animations[self.state]
        self.anim_index += 0.15 * (dt * 60)
        if self.anim_index >= len(frames): self.anim_index = 0.0
        self.image = frames[int(self.anim_index)]

    def draw(self, surface):
        surface.blit(self.image, self.rect)