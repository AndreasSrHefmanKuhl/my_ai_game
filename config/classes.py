import pygame


class Player(pygame.sprite.Sprite):
    """
        Represents the main playable character with physics, health, and combat logic.
        """
    def __init__(self, x, y, anim_dict):
        """
                Initializes the player at the specified coordinates.

                Args:
                    x (int): Starting x-coordinate.
                    y (int): Starting y-coordinate.
                    anim_dict (dict): Dictionary mapping state strings to lists of pygame.Surface frames.
                """

        super().__init__()
        self.animations = anim_dict
        self.state = "stand"
        self.frame_index = 0.0
        self.health = 100
        self.max_health = 100
        self.is_dead = False

        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_speed = -14
        self.on_ground = False
        self.is_crouching = False

        self.anim_speeds = {
            "stand": 0.15, "walk": 0.15, "punch": 0.15,
            "kick": 0.12, "crouch": 0.15, "crouchkick": 0.12, "jump": 0.15
        }
        self.locked_states = {"punch", "kick", "crouchkick", "crouch", "jump"}
        self.flip = False
        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def take_damage(self, amount):
        """
                Reduces player health and triggers the dead state if health drops to zero.

                Args:
                    amount (float): The amount of health points to deduct.
                """

        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            self.state = "dead"

    def apply_gravity(self):
        """Calculates and applies downward vertical velocity to the player's rectangle."""

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

    def jump(self):
        """Applies upward velocity if the player is currently on the ground."""
        if self.on_ground:
            self.velocity_y = self.jump_speed
            self.on_ground = False

    def get_attack_rect(self):
        """
                Calculates the active hit area for attacks based on the current facing direction.

                Returns:
                    pygame.Rect: A 30-pixel wide collision box projected in front of the player.
                """

        hitbox = self.rect.copy()
        hitbox.width = 30  # Increased from 5 to 30 for better gameplay
        if self.flip:
            hitbox.right = self.rect.left
        else:
            hitbox.left = self.rect.right
        return hitbox

    def is_attacking(self):
        """Checks if the player is currently in a punching, kicking, or crouch-kicking state."""
        return self.state in ["punch", "kick", "crouchkick"]

    def change_state(self, new_state):
        """
                Safely transitions to a new animation state.

                Transitions are blocked if the player is currently in a 'locked' state
                (e.g., mid-attack) unless the state is finished.
                """
        if new_state not in self.animations: return
        if self.state in self.locked_states and new_state != self.state: return
        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0.0

    def update(self, dt, moving_x):
        """
                Updates animation frames, sprite flipping, and state resets based on movement.

                Args:
                    dt (float): Delta time since the last frame.
                    moving_x (float): The horizontal direction/velocity the player is moving.
                """
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
    """
        Represents a static environmental object with specific collision properties.
        """
    def __init__(self, x, y, size, image, tile_type="ground"):
        """
                Initializes a tile and parses its type to set physical attributes.

                Args:
                    x (int): X-coordinate.
                    y (int): Y-coordinate.
                    size (int): Dimensions of the square tile.
                    image (pygame.Surface): The visual texture of the tile.
                    tile_type (str): Metadata string used to determine if the tile is a
                                     wall, floor, or deadly hazard.
                """
        self.rect = pygame.Rect(x, y, size, size)
        self.image = image
        self.tile_type = tile_type
        self.is_wall = "wall" in tile_type or "brick" in tile_type
        self.is_floor = any(word in tile_type for word in ["way", "floor", "head", "ground"])
        self.is_deadly = "dead" in tile_type


class Enemy(pygame.sprite.Sprite):
    """
        Base AI character that patrols a fixed area and chases the player upon detection.
        """
    def __init__(self, x, y, anim_dict):
        """
                        Initializes enemy AI with detection, patrol, and attack parameters.

                        Args:
                            x (int): Initial x-position.
                            y (int): Initial y-position.
                            anim_dict (dict): Dictionary of animation frames.
                        """

        super().__init__()
        self.animations = anim_dict
        self.state = "walk"
        self.anim_index = 0.0
        self.health = 100
        self.max_health = 100
        self.is_dead = False

        self.speed = 2
        self.direction = 1
        self.detection_range = 240  # 5 tiles * 48px
        self.attack_range = 50
        self.attack_cooldown = 0


        self.walked_distance = 0
        self.max_patrol_distance = 144  # 3 tiles * 48px

        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def take_damage(self, amount):
        """Reduces enemy health and flags them as dead if health is zero."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.is_dead = True

    def update(self, dt, player_rect, level_tiles):
        """
                Main AI brain: Switches between attacking, chasing, and patrolling
                based on the proximity of the player's rect.
                """
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        dist_x = player_rect.centerx - self.rect.centerx
        distance = abs(dist_x)

        if distance < self.attack_range:
            self.attack()
        elif distance < self.detection_range:
            self.chase(dist_x, level_tiles)
        else:
            self.patrol(level_tiles)

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
        """
        Moves the enemy back and forth within a specific range.
        Reverses direction if a wall is hit or the patrol distance is exceeded.
        """
        self.state = "walk"
        move_step = self.direction * self.speed

        next_rect = self.rect.copy()
        next_rect.x += move_step

        hit_wall = any(t.rect.colliderect(next_rect) for t in level_tiles if t.is_wall)

        self.walked_distance += abs(move_step)

        if hit_wall or self.walked_distance >= self.max_patrol_distance:
            self.direction *= -1
            self.walked_distance = 0
            self.rect.x += self.direction * 2
        else:
            self.rect.x += move_step

    def chase(self, dist_x, level_tiles):
        """
                        Moves toward the player's x-position.
                        Includes 'cliff detection' to prevent the AI from falling off platforms.
                        """

        new_dir = 1 if dist_x > 0 else -1
        move_speed = self.speed * 1.5


        next_rect = self.rect.copy()
        next_rect.x += new_dir * move_speed


        # Create a small sensor rect in front of the enemy, below its feet
        sensor_x = next_rect.right if new_dir > 0 else next_rect.left - 10
        edge_sensor = pygame.Rect(sensor_x, self.rect.bottom + 2, 10, 10)

        walkable_tiles = [t for t in level_tiles if t.is_floor or t.is_wall]
        has_ground_ahead = any(edge_sensor.colliderect(t.rect) for t in walkable_tiles)

        #  Standard Wall Detection
        hit_wall = any(next_rect.colliderect(t.rect) for t in walkable_tiles if t.is_wall)


        if has_ground_ahead and not hit_wall:
            self.state = "walk"
            self.direction = new_dir
            self.rect.x += self.direction * move_speed
        else:
            # If about to fall or hit a wall, stop chasing and patrol (turn around)
            self.patrol(level_tiles)

    def attack(self):


        """Triggers the attack state and resets the attack cooldown timer."""
        if self.attack_cooldown <= 0:
            self.state = "attack"
            self.attack_cooldown = 0.85


class Endboss(pygame.sprite.Sprite):
    """
        A high-health boss entity with distinct animation logic.
        """
    def __init__(self, x, y, anim_dict):
        """Initializes the boss with 500 starting health points."""

        super().__init__()
        self.animations = anim_dict
        self.state = "walk"
        self.frame_index = 0.0
        self.health = 500
        self.max_health = 500
        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, dt):
        """Updates the boss's animation frames based on delta time."""
        self.frame_index += 0.1 * (dt * 60)
        if self.frame_index >= len(self.animations[self.state]):
            self.frame_index = 0
        self.image = self.animations[self.state][int(self.frame_index)]