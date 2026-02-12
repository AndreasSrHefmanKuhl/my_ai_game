import pygame

class Bullet:
    """Repräsentiert ein einzelnes Projektil."""

    def __init__(self, x, y, direction):
        # Erstellt ein kleines Rechteck für die Kugel
        self.rect = pygame.Rect(x, y, 12, 4)
        self.color = (255, 200, 0)  # Gold/Gelb
        self.speed = 500  # Pixel pro Sekunde
        self.direction = direction  # 1 für rechts, -1 für links

    def update(self, dt):
        """Bewegt die Kugel basierend auf der Zeit."""
        self.rect.x += self.speed * dt * self.direction

    def draw(self, surface):
        """Zeichnet die Kugel auf das Display."""
        pygame.draw.rect(surface, self.color, self.rect)

class Enemy:

    def __init__(self,x,y,direction):
        self.rect = pygame.rect

    def update(self,dt):
        self.rect.x