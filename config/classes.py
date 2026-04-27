
import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, anim_dict):
        super().__init__()
        self.animations = anim_dict
        self.state = "stand"
        self.frame_index = 0.0
        self.health = 100
        self.max_health = 100
        self.is_dead = False

        # Physik-Variablen
        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_speed = -14
        self.on_ground = False
        self.is_crouching = False

        self.anim_speeds = {
            "stand": 0.15, "walk": 0.15, "punch": 0.15,
            "kick": 0.12, "crouch": 0.15, "crouchkick": 0.12,"jump":0.15
        }
        self.locked_states = {"punch", "kick", "crouchkick","crouch","jump"}
        self.flip = False
        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def take_damage(self, amount):
        self.health -= amount
        if self.health == 0:
            self.health = 0
            self.is_dead = True
            self.state = "dead"

    def apply_gravity(self):
        """Zieht den Spieler nach unten."""
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

    def jump(self):
        """Springt, wenn der Spieler auf dem Boden steht."""
        if self.on_ground:
            self.velocity_y = self.jump_speed
            self.on_ground = False

    def get_attack_rect(self):
        """Calculates a hitbox in front of the player based on direction."""
        # Create a rect slightly larger/further out than the body
        hitbox = self.rect.copy()
        hitbox.width = 5  # Reach of the punch/kick

        if self.flip:  # Facing Left
            hitbox.right = self.rect.left
        else:  # Facing Right
            hitbox.left = self.rect.right

        return hitbox

    def is_attacking(self):
        """Returns True if the player is in a combat animation frame."""
        return self.state in ["punch", "kick", "crouchkick"]

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
        self.is_floor = any(word in tile_type for word in ["way", "floor", "head", "ground"])
        self.is_deadly = "dead" in tile_type


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, anim_dict):
        super().__init__()
        self.animations = anim_dict
        self.state = "walk"
        self.anim_index = 0.0
        self.health = 100
        self.max_health = 100
        self.is_dead = False

        # Behavior Variables
        self.speed = 2
        self.direction = 1  # 1 for Right, -1 for Left
        self.detection_range = 5
        self.attack_range = 50
        self.attack_cooldown = 0

        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def take_damage(self, amount):
        """Reduces health and checks for death."""
        self.health -= amount
        if self.health == 0:
            self.is_dead = True

    def update(self, dt, player_rect, level_tiles):
        # Update Cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # Distance to Player
        dist_x = player_rect.centerx - self.rect.centerx
        distance = abs(dist_x)

        # Logic Branching - Passing level_tiles to every state
        if distance < self.attack_range:
            self.attack()
        elif distance < self.detection_range:
            self.chase(dist_x, level_tiles)
        else:
            self.patrol(level_tiles)

        # Animation Handling
        frames = self.animations.get(self.state, self.animations.get("walk"))
        if frames:
            self.anim_index += 0.15 * (dt * 60)
            if self.anim_index >= len(frames):
                if self.state == "attack":
                    self.state = "walk"
                self.anim_index = 0.0
            img = frames[int(self.anim_index)]
            self.image = pygame.transform.flip(img, self.direction < 0, False)

    def patrol(self, level_tiles):
        self.state = "walk"
        move_step = self.direction * self.speed

        # 1. Predict Horizontal Position
        next_rect = self.rect.copy()
        next_rect.x += move_step

        # 2. Wall Detection (Any solid tile)
        hit_wall = any(t.rect.colliderect(next_rect) for t in level_tiles if t.is_wall)

        # 3. Edge Detection (The "Sensor" Box)
        # We place a small box exactly where the next step's feet would be
        sensor_width = 10
        sensor_x = next_rect.right if self.direction > 0 else next_rect.left - sensor_width
        # Look slightly below the enemy's feet
        sensor_rect = pygame.Rect(sensor_x, self.rect.bottom + 2, sensor_width, 10)

        # If it's solid (is_floor or is_wall), there is ground
        has_ground = any(sensor_rect.colliderect(t.rect) for t in level_tiles if (t.is_floor or t.is_wall))

        # 4. Turn logic
        if hit_wall or not has_ground:
            self.direction *= -1
            # Prevent "jittering" by nudging the enemy away from the edge immediately
            self.rect.x += self.direction * 2
        else:
            self.rect.x += move_step

    def chase(self, dist_x, level_tiles):
        new_dir = 1 if dist_x > 0 else -1
        move_speed = self.speed * 1.5

        # Predicted next position
        next_rect = self.rect.copy()
        next_rect.x += new_dir * move_speed

        # Reuse the Area Sensor logic
        sensor_w = 5
        s_x = next_rect.right if new_dir > 0 else next_rect.left - sensor_w
        sensor_rect = pygame.Rect(s_x, self.rect.bottom - 5, sensor_w, 5)

        walkable = [t for t in level_tiles if t.is_floor or t.is_wall]
        has_ground = any(sensor_rect.colliderect(t.rect) for t in walkable)
        hit_wall = any(next_rect.colliderect(t.rect) for t in walkable if t.is_wall)

        if has_ground and not hit_wall:
            self.state = "walk"
            self.direction = new_dir
            self.rect.x += self.direction * move_speed
        else:
            # If the chase path is blocked, patrol so can turn around
            self.patrol(level_tiles)

    def attack(self):
        if self.attack_cooldown <= 0:
            self.state = "attack"
            self.attack_cooldown = 0.85  # Seconds between hits

class Endboss(pygame.sprite.Sprite):
    """
    High-health boss entity with unique animations.
    Unlike standard enemies, it doesn't patrol; it guards the exit.
    """
    def __init__(self, x, y, anim_dict):
        super().__init__()
        self.animations = anim_dict
        self.state = "idle"
        self.frame_index = 0.0
        self.health = 500
        self.max_health = 500
        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_boss = True

    def update(self):

        self.frame_index += 0.1
        if self.frame_index >= len(self.animations[self.state]):
            self.frame_index = 0
        self.image = self.animations[self.state][int(self.frame_index)]
