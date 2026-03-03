

import pygame



class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, anim_dict):
        super().__init__()
        # Speichert das gesamte Dictionary (z.B. {"walk": (...), "stand": (...)})
        self.animations = anim_dict
        self.state = "stand"
        self.frame_index = 0.0

        # Base speed (frames per tick at 60fps); override per-state below
        self.anim_speed = 0.15
        self.anim_speeds = {
            "stand": 0.15,
            "walk": 0.15,
            "punch": 0.15,  # existing
            "kick": 0.12,
            "crouch":0.15,
            "crouchkick":0.12,# slower kick (tweak 0.05..0.10)

        }

        # States that should finish before stand/walk can override them
        self.locked_states = {"punch", "kick","crouchkick","crouch"}

        self.flip = False


        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def change_state(self, new_state):
        """Wechselt den Status und setzt Animation zurück."""
        if new_state not in self.animations:
            return

        # If we're currently in a locked action state, don't let walk/stand interrupt it
        if self.state in self.locked_states and new_state != self.state:
            return

        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0.0

    def animate(self, dt):
        """Berechnet den Frame-Wechsel basierend auf Delta Time."""
        frames = self.animations[self.state]

        speed = self.anim_speeds.get(self.state, self.anim_speed)
        # Multiplikation mit 60, um die Geschwindigkeit bei dt zu normalisieren
        self.frame_index += speed * (dt * 60)

        if self.frame_index >= len(frames):
            if self.state in self.locked_states:
                self.state = "stand"
            self.frame_index = 0.0

        img = frames[int(self.frame_index)]
        self.image = pygame.transform.flip(img, self.flip, False)

    def update(self, dt, moving_x):
        """Zentrale Update-Logik für Blickrichtung und Animation."""
        if moving_x < 0:
            self.flip = True
        elif moving_x > 0:
            self.flip = False
        self.animate(dt)



class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, anim_dict, speed=100, distance=200):
        super().__init__()
        self.animations = anim_dict  # Erwartet das Dict (z.B. hornet_data)
        self.state = "walk"
        self.anim_index = 0.0
        self.anim_speed = 0.1

        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.start_x = x
        self.distance = distance
        self.speed = speed
        self.direction = 1

    def update(self, dt):
        """Bewegt den Gegner und steuert die Animation."""
        # Bewegung auf der X-Achse
        self.rect.x += self.speed * dt * self.direction

        # Patrouillen-Umkehrung
        if self.rect.x >= self.start_x + self.distance:
            self.direction = -1
        elif self.rect.x <= self.start_x:
            self.direction = 1

        # Animation abspielen
        frames = self.animations[self.state]
        self.anim_index += self.anim_speed * (dt * 60)
        if self.anim_index >= len(frames):
            self.anim_index = 0.0

        img = frames[int(self.anim_index)]
        # Feind schaut immer in die Richtung, in die er läuft
        self.image = pygame.transform.flip(img, self.direction == 1, False)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


#
class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 12, 4)
        self.color = (255, 200, 0)
        self.speed = 600
        self.direction = direction

    def update(self, dt):
        """Bewegt die Kugel."""
        self.rect.x += self.speed * dt * self.direction

    def draw(self, surface):
        """Zeichnet die Kugel (hier noch als Rect, Bild wäre auch möglich)."""
        pygame.draw.rect(surface, self.color, self.rect)



class Tile:
    def __init__(self, x, y, size, image, tile_type = "ground"):

        self.rect = pygame.Rect(x, y, size, size)
        self.image = image
        self.tile_type = tile_type

        self.is_wall = "wall" in tile_type or "solid" in tile_type
        self.is_deadly = "dead" in tile_type

    def draw(self, surface):
        """Zeichnet den Boden/Wand."""
        surface.blit(self.image, self.rect)

