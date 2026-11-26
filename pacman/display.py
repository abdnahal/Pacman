import math
from pathlib import Path
import pygame


BLACK = (0, 0, 0)
BLUE = (30, 80, 255)
YELLOW = (255, 220, 0)
CYAN = (50, 255, 255)
WHITE = (255, 255, 255)
PACGUM = (255, 220, 190)
SUPER_PACGUM = (255, 255, 120)
GHOST_COLORS = (
    (255, 50, 70),
    (255, 150, 210),
    (50, 230, 255),
    (255, 170, 45),
)
HUD_HEIGHT = 36


class Display:
    def __init__(self, width, height, tile_size):
        self.width = width
        self.height = height + HUD_HEIGHT
        self.tile_size = tile_size
        self.logical_size = (width, self.height)
        self.window_size = (width * 5, height * 5)
        self.screen = pygame.display.set_mode(
            self.window_size,
            pygame.RESIZABLE,
        )
        self.canvas = pygame.Surface(self.logical_size)
        self.font = pygame.font.SysFont("arial", 36)
        self.small_font = pygame.font.SysFont("arial", 24)
        self.large_font = pygame.font.SysFont("arial", 64)
        self.mouth_progress = 0.0
        self.mouth_direction = 1
        self.background = self._load_image("background.png", self.logical_size)
        self.hat = self._load_image("hat.png", (
            int(tile_size * 1.15), int(tile_size * 0.75)
        ), alpha=True)

    def resize(self, width, height):
        width = max(320, width)
        height = max(240, height)
        self.window_size = (width, height)
        self.screen = pygame.display.set_mode(
            self.window_size,
            pygame.RESIZABLE,
        )

    def present(self):
        logical_width, logical_height = self.logical_size
        window_width, window_height = self.screen.get_size()
        scale = min(
            window_width / logical_width,
            window_height / logical_height,
        )
        scaled_size = (
            max(1, int(logical_width * scale)),
            max(1, int(logical_height * scale)),
        )
        scaled = pygame.transform.smoothscale(self.canvas, scaled_size)
        self.screen.fill(BLACK)
        left = (window_width - scaled_size[0]) // 2
        top = (window_height - scaled_size[1]) // 2
        self.screen.blit(scaled, (left, top))
        pygame.display.flip()

    def set_logical_size(self, width, height, tile_size):
        self.width = width
        self.height = height + HUD_HEIGHT
        self.tile_size = tile_size
        self.logical_size = (width, self.height)
        self.canvas = pygame.Surface(self.logical_size)
        self.background = self._load_image(
            "background.png",
            self.logical_size,
        )
        self.hat = self._load_image(
            "hat.png",
            (
                int(tile_size * 1.15),
                int(tile_size * 0.75),
            ),
            alpha=True,
        )

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
                top = y * self.tile_size + HUD_HEIGHT
                if walls == 15:
                    pygame.draw.rect(
                        self.canvas,
                        CYAN,
                        (left, top, self.tile_size, self.tile_size),
                    )
                if walls & 1:
                    pygame.draw.line(
                        self.canvas, BLUE,
                        (left, top),
                        (left + self.tile_size, top),
                        10,
                    )
                if walls & 2:
                    pygame.draw.line(
                        self.canvas, BLUE,
                        (left + self.tile_size, top),
                        (left + self.tile_size, top + self.tile_size),
                        10,
                    )
                if walls & 4:
                    pygame.draw.line(
                        self.canvas, BLUE,
                        (left, top + self.tile_size),
                        (left + self.tile_size, top + self.tile_size),
                        10,
                    )
                if walls & 8:
                    pygame.draw.line(
                        self.canvas, BLUE,
                        (left, top),
                        (left, top + self.tile_size),
                        10,
                    )

    def _tile_center(self, position):
        x, y = position
        return (
            x * self.tile_size + self.tile_size // 2,
            y * self.tile_size + HUD_HEIGHT + self.tile_size // 2,
        )

    def draw_pacgums(self, positions):
        radius = max(2, self.tile_size // 10)
        for position in positions:
            pygame.draw.circle(
                self.canvas, PACGUM, self._tile_center(position), radius
            )

    def draw_super_pacgums(self, positions):
        radius = max(4, self.tile_size // 5)
        for position in positions:
            center = self._tile_center(position)
            pygame.draw.circle(self.canvas, SUPER_PACGUM, center, radius)
            pygame.draw.circle(self.canvas, WHITE, center, max(2, radius // 2))

    def draw_ghosts(self, positions):
        radius = max(5, int(self.tile_size * 0.38))
        for index, position in enumerate(positions):
            center_x, center_y = self._tile_center(position)
            color = GHOST_COLORS[index % len(GHOST_COLORS)]
            pygame.draw.circle(
                self.canvas, color, (center_x, center_y - radius // 4), radius
            )
            pygame.draw.rect(
                self.canvas,
                color,
                (center_x - radius, center_y - radius // 4, radius * 2, radius),
            )
            pygame.draw.polygon(self.canvas, color, [
                (center_x - radius, center_y + radius // 2),
                (center_x - radius, center_y + radius),
                (center_x - radius // 2, center_y + radius * 3 // 4),
                (center_x, center_y + radius),
                (center_x + radius // 2, center_y + radius * 3 // 4),
                (center_x + radius, center_y + radius),
                (center_x + radius, center_y + radius // 2),
            ])

            eye_y = center_y - radius // 4
            eye_offset = radius // 2
            for eye_x in (center_x - eye_offset, center_x + eye_offset):
                pygame.draw.circle(
                    self.canvas, WHITE, (eye_x, eye_y), max(2, radius // 3)
                )
                pygame.draw.circle(
                    self.canvas,
                    BLUE,
                    (eye_x + max(1, radius // 8), eye_y),
                    max(1, radius // 6),
                )

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
            int(
                player.render_y * self.tile_size
                + HUD_HEIGHT
                + self.tile_size // 2
            ),
        ))
        self.canvas.blit(rotated, rect)

    def draw_hud(self, text):
        pygame.draw.rect(self.canvas, BLACK, (0, 0, self.width, HUD_HEIGHT))
        self.draw_text(text, 4, self.small_font, center=False)

    def draw_text(self, text, y, font=None, color=WHITE, center=True):
        font = font or self.font
        label = font.render(text, True, color)
        rect = label.get_rect(center=(self.width // 2, y)) if center else label.get_rect(topleft=(40, y))
        self.canvas.blit(label, rect)
        return rect

    def clear(self):
        if self.background is not None:
            self.canvas.blit(self.background, (0, 0))
        else:
            self.canvas.fill(BLACK)
