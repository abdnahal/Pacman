import math
from pathlib import Path
import pygame


BLACK = (0, 0, 0)
BLUE = (30, 80, 255)
YELLOW = (255, 220, 0)
CYAN = (50, 255, 255)
WHITE = (255, 255, 255)


class Display:
    def __init__(self, width, height, tile_size):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.screen = pygame.display.set_mode((width, height))
        self.font = pygame.font.SysFont("arial", 36)
        self.small_font = pygame.font.SysFont("arial", 24)
        self.large_font = pygame.font.SysFont("arial", 64)
        self.mouth_progress = 0.0
        self.mouth_direction = 1
        self.background = self._load_image("background.png", (width, height))
        self.hat = self._load_image("hat.png", (
            int(tile_size * 1.15), int(tile_size * 0.75)
        ), alpha=True)

    def _load_image(self, name, scale, alpha=False):
        path = Path(__file__).resolve().parent.parent / name
        try:
            image = pygame.image.load(str(path))
            image = image.convert_alpha() if alpha else image.convert()
            return pygame.transform.smoothscale(image, scale)
        except (pygame.error, OSError):
            return None

    def draw_maze(self, maze):
        rows = len(maze)
        cols = len(maze[0]) if rows else 0
        for y in range(rows):
            for x in range(cols):
                walls = maze[y][x]
                left = x * self.tile_size
                top = y * self.tile_size
                if walls == 15:
                    pygame.draw.rect(
                        self.screen, CYAN,
                        (left, top, self.tile_size, self.tile_size)
                    )
                if walls & 1:
                    pygame.draw.line(self.screen, BLUE, (left, top),
                                     (left + self.tile_size, top), 10)
                if walls & 2:
                    pygame.draw.line(self.screen, BLUE,
                                     (left + self.tile_size, top),
                                     (left + self.tile_size, top + self.tile_size), 10)
                if walls & 4:
                    pygame.draw.line(self.screen, BLUE,
                                     (left, top + self.tile_size),
                                     (left + self.tile_size, top + self.tile_size), 10)
                if walls & 8:
                    pygame.draw.line(self.screen, BLUE, (left, top),
                                     (left, top + self.tile_size), 10)

    def draw_player(self, player):
        self.mouth_progress += 0.15 * self.mouth_direction
        if self.mouth_progress > 1.0:
            self.mouth_progress = 1.0
            self.mouth_direction = -1
        elif self.mouth_progress < 0.0:
            self.mouth_progress = 0.0
            self.mouth_direction = 1

        size = self.tile_size * 2
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        radius = self.tile_size // 3
        current_angle = 0.65 * self.mouth_progress
        points = [(center, center)]
        for i in range(21):
            angle = current_angle + i * (
                (2 * math.pi - 2 * current_angle) / 20
            )
            points.append((
                center + radius * math.cos(angle),
                center - radius * math.sin(angle),
            ))
        if len(points) > 2:
            pygame.draw.polygon(surface, YELLOW, points)

        if self.hat is not None:
            hat_y = center - radius + 2
            if player.angle == 180:
                hat_y = center + radius - 2
            hat_rect = self.hat.get_rect(center=(center, hat_y))
            surface.blit(self.hat, hat_rect)

        rotated = pygame.transform.rotate(surface, player.angle)
        rect = rotated.get_rect(center=(
            int(player.render_x * self.tile_size + self.tile_size // 2),
            int(player.render_y * self.tile_size + self.tile_size // 2),
        ))
        self.screen.blit(rotated, rect)

    def draw_text(self, text, y, font=None, color=WHITE, center=True):
        font = font or self.font
        label = font.render(text, True, color)
        rect = label.get_rect(center=(self.width // 2, y)) if center else label.get_rect(topleft=(40, y))
        self.screen.blit(label, rect)
        return rect

    def clear(self):
        if self.background is not None:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(BLACK)
