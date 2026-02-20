import pygame



class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 12, 4)
        self.color = (255, 200, 0)
        self.speed = 600
        self.direction = direction

    def update(self, dt):
        self.rect.x += self.speed * dt * self.direction

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


class Enemy:
    def __init__(self, x, y, frames, speed=100, distance=200):
        self.frames = frames
        self.rect = self.frames[0].get_rect(topleft=(x, y))
        self.start_x = x
        self.distance = distance
        self.speed = speed
        self.direction = 1
        self.anim_index = 0.0

    def update(self, dt):
        self.rect.x += self.speed * dt * self.direction
        if self.rect.x >= self.start_x + self.distance:
            self.direction = -1
        elif self.rect.x <= self.start_x:
            self.direction = 1
        self.anim_index += dt * 6

    def draw(self, surface):
        idx = int(self.anim_index) % len(self.frames)
        img = self.frames[idx]
        if self.direction == 1:
            img = pygame.transform.flip(img, True, False)
        surface.blit(img, self.rect)


class Tile:
    def __init__(self, x, y, size, image, is_wall=False, is_deadly=False):
        self.rect = pygame.Rect(x, y, size, size)
        self.image = image
        self.is_wall = is_wall
        self.is_deadly = is_deadly

    def draw(self, surface):
        surface.blit(self.image, self.rect)