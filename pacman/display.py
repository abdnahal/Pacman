from pathlib import Path

import pygame


BLACK = (0, 0, 0)
BLUE = (30, 80, 255)
YELLOW = (255, 220, 0)
WHITE = (255, 255, 255)
PACGUM = (255, 220, 190)
SUPER_PACGUM = (255, 255, 120)
PLAYER_FRAME_RECTS = {
    "right": ((197, 48, 203, 191), (427, 48, 202, 191)),
    "left": ((198, 285, 203, 184), (429, 285, 205, 184)),
    "down": ((207, 523, 181, 202), (448, 523, 181, 202)),
    "up": ((201, 777, 190, 179), (441, 778, 188, 177)),
}
PLAYER_DIRECTIONS = {0: "right", 90: "up", 180: "left", 270: "down"}
STONE_WALL_TIERS = (
    ((126, 87, 58), (61, 42, 30), (195, 151, 106), (83, 56, 38)),
    ((143, 119, 87), (68, 57, 43), (210, 187, 145), (94, 77, 56)),
    ((169, 153, 123), (82, 72, 55), (232, 217, 184), (112, 98, 73)),
)
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
        desktop_sizes = pygame.display.get_desktop_sizes()
        self.window_size = (
            desktop_sizes[0] if desktop_sizes else (width * 5, height * 5)
        )
        self.screen = pygame.display.set_mode(
            self.window_size,
            pygame.RESIZABLE,
        )
        self.canvas = pygame.Surface(self.logical_size, pygame.SRCALPHA)
        self.scaled_canvas = None
        self.scaled_canvas_size = None
        self.maze_surface = None
        self.cached_maze = None
        self.font = pygame.font.SysFont("arial", 36)
        self.small_font = pygame.font.SysFont("arial", 24)
        self.large_font = pygame.font.SysFont("arial", 64)
        self.mouth_progress = 0.0
        self.mouth_direction = 1
        self.player_frames = self._load_player_frames(tile_size)
        self.backgrounds = {
            "menu": self._load_background("menu_background.png"),
            "game": self._load_background("game_background.png"),
        }
        self.active_background = "menu"
        self.background = pygame.transform.scale(
            self.backgrounds[self.active_background], self.window_size
        )

    def resize(self, width, height):
        width = max(320, width)
        height = max(240, height)
        self.window_size = (width, height)
        self.screen = pygame.display.set_mode(
            self.window_size,
            pygame.RESIZABLE,
        )
        self.background = pygame.transform.scale(
            self.backgrounds[self.active_background], self.window_size
        )

    def present(self):
        logical_width, logical_height = self.logical_size
        window_width, window_height = self.screen.get_size()
        self.screen.blit(self.background, (0, 0))

        scale = min(
            window_width / logical_width,
            window_height / logical_height,
        )
        scaled_size = (
            max(1, int(logical_width * scale)),
            max(1, int(logical_height * scale)),
        )
        if self.scaled_canvas_size != scaled_size:
            self.scaled_canvas = pygame.Surface(scaled_size, pygame.SRCALPHA)
            self.scaled_canvas_size = scaled_size
        pygame.transform.scale(
            self.canvas, scaled_size, self.scaled_canvas
        )
        left = (window_width - scaled_size[0]) // 2
        top = (window_height - scaled_size[1]) // 2
        self.screen.blit(self.scaled_canvas, (left, top))
        pygame.display.flip()

    def set_logical_size(self, width, height, tile_size):
        self.width = width
        self.height = height + HUD_HEIGHT
        self.tile_size = tile_size
        self.logical_size = (width, self.height)
        self.canvas = pygame.Surface(self.logical_size, pygame.SRCALPHA)
        self.scaled_canvas = None
        self.scaled_canvas_size = None
        self.maze_surface = None
        self.cached_maze = None
        self.player_frames = self._load_player_frames(tile_size)

    def _load_player_frames(self, tile_size):
        path = Path(__file__).resolve().parent.parent / "character movement.png"
        try:
            sheet = pygame.image.load(str(path)).convert_alpha()
        except (pygame.error, OSError) as exc:
            raise OSError(f"Could not load player animation sheet: {path}") from exc

        sprite_size = max(1, int(tile_size * 1.2))
        frames = {}
        for direction, rectangles in PLAYER_FRAME_RECTS.items():
            frames[direction] = []
            for bounds in rectangles:
                rect = pygame.Rect(bounds)
                if not sheet.get_rect().contains(rect):
                    raise ValueError(
                        f"Player frame {direction} is outside animation sheet: {rect}"
                    )
                cropped = sheet.subsurface(rect).copy()
                scale = min(
                    sprite_size / cropped.get_width(),
                    sprite_size / cropped.get_height(),
                )
                scaled_size = (
                    max(1, round(cropped.get_width() * scale)),
                    max(1, round(cropped.get_height() * scale)),
                )
                scaled = pygame.transform.scale(cropped, scaled_size)
                frame = pygame.Surface(
                    (sprite_size, sprite_size), pygame.SRCALPHA
                )
                frame.blit(scaled, scaled.get_rect(center=(sprite_size // 2,) * 2))
                frames[direction].append(frame)
        return frames

    def _load_background(self, name):
        path = Path(__file__).resolve().parent.parent / name
        try:
            return pygame.image.load(str(path)).convert()
        except (pygame.error, OSError) as exc:
            raise OSError(f"Could not load background image: {path}") from exc

    def draw_maze(self, maze):
        if self.maze_surface is None or maze != self.cached_maze:
            self.maze_surface = pygame.Surface(
                self.logical_size, pygame.SRCALPHA
            )
            self._render_maze(maze, self.maze_surface)
            self.cached_maze = [row[:] for row in maze]
        self.canvas.blit(self.maze_surface, (0, 0))

    def _render_maze(self, maze, surface):
        rows = len(maze)
        cols = len(maze[0]) if rows else 0
        for y in range(rows):
            for x in range(cols):
                walls = maze[y][x]
                left = x * self.tile_size
                top = y * self.tile_size + HUD_HEIGHT
                tier = self._wall_tier(x, y, cols, rows)
                if walls == 15:
                    self._draw_stone_block(surface, left, top, tier)
                if walls & 1 or (y > 0 and maze[y - 1][x] & 4):
                    self._draw_stone_wall(
                        surface,
                        (left, top),
                        (left + self.tile_size, top),
                        tier,
                    )
                if walls & 8 or (x > 0 and maze[y][x - 1] & 2):
                    self._draw_stone_wall(
                        surface,
                        (left, top),
                        (left, top + self.tile_size),
                        tier,
                    )
                if x == cols - 1 and walls & 2:
                    self._draw_stone_wall(
                        surface,
                        (left + self.tile_size, top),
                        (left + self.tile_size, top + self.tile_size),
                        tier,
                    )
                if y == rows - 1 and walls & 4:
                    self._draw_stone_wall(
                        surface,
                        (left, top + self.tile_size),
                        (left + self.tile_size, top + self.tile_size),
                        tier,
                    )

    def _wall_tier(self, x, y, cols, rows):
        depth = min(x, y, cols - 1 - x, rows - 1 - y)
        max_depth = max(1, min(cols, rows) // 2)
        if depth * 3 < max_depth:
            return 0
        if depth * 3 < max_depth * 2:
            return 1
        return 2

    def _draw_stone_wall(self, surface, start, end, tier):
        base, shadow, highlight, mortar = STONE_WALL_TIERS[tier]
        thickness = max(6, self.tile_size // (4 + tier))
        horizontal = start[1] == end[1]
        offset = max(1, thickness // 3)
        shadow_offset = (0, offset) if horizontal else (offset, 0)
        highlight_offset = (
            (0, -offset) if horizontal else (-offset, 0)
        )
        shadow_start = (
            start[0] + shadow_offset[0],
            start[1] + shadow_offset[1],
        )
        shadow_end = (
            end[0] + shadow_offset[0],
            end[1] + shadow_offset[1],
        )
        highlight_start = (
            start[0] + highlight_offset[0],
            start[1] + highlight_offset[1],
        )
        highlight_end = (
            end[0] + highlight_offset[0],
            end[1] + highlight_offset[1],
        )
        pygame.draw.line(
            surface, shadow, shadow_start, shadow_end, thickness + 2
        )
        pygame.draw.line(surface, base, start, end, thickness)
        pygame.draw.line(
            surface,
            highlight,
            highlight_start,
            highlight_end,
            max(1, thickness // 4),
        )

        midpoint = (
            (start[0] + end[0]) // 2,
            (start[1] + end[1]) // 2,
        )
        if horizontal:
            joint_start = (midpoint[0], midpoint[1] - thickness // 2 + 1)
            joint_end = (midpoint[0], midpoint[1] + thickness // 2 - 1)
        else:
            joint_start = (midpoint[0] - thickness // 2 + 1, midpoint[1])
            joint_end = (midpoint[0] + thickness // 2 - 1, midpoint[1])
        pygame.draw.line(
            surface, mortar, joint_start, joint_end, max(1, thickness // 8)
        )

        if tier == 0:
            for fraction in (0.25, 0.75):
                position = (
                    int(start[0] + (end[0] - start[0]) * fraction),
                    int(start[1] + (end[1] - start[1]) * fraction),
                )
                merlon_size = max(3, thickness // 3)
                if horizontal:
                    merlon = pygame.Rect(
                        position[0] - merlon_size // 2,
                        position[1] - thickness // 2,
                        merlon_size,
                        thickness,
                    )
                else:
                    merlon = pygame.Rect(
                        position[0] - thickness // 2,
                        position[1] - merlon_size // 2,
                        thickness,
                        merlon_size,
                    )
                pygame.draw.rect(surface, highlight, merlon)
                pygame.draw.rect(surface, base, merlon.inflate(-2, -2))

    def _draw_stone_block(self, surface, left, top, tier):
        base, shadow, highlight, mortar = STONE_WALL_TIERS[tier]
        block = pygame.Rect(left, top, self.tile_size, self.tile_size)
        inset = max(2, self.tile_size // 10)
        pygame.draw.rect(surface, shadow, block)
        pygame.draw.rect(surface, base, block.inflate(-inset * 2, -inset * 2))
        pygame.draw.line(
            surface,
            highlight,
            (left + inset, top + inset),
            (left + self.tile_size - inset, top + inset),
            max(1, inset // 2),
        )
        pygame.draw.line(
            surface,
            mortar,
            (left + self.tile_size // 2, top + inset),
            (left + self.tile_size // 2, top + self.tile_size - inset),
            max(1, inset // 3),
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

    def draw_ghosts(self, ghosts, frightened=False):
        radius = max(5, int(self.tile_size * 0.38))
        for index, ghost in enumerate(ghosts):
            if not ghost.active:
                continue
            center_x = round(ghost.render_x * self.tile_size + self.tile_size // 2)
            center_y = round(
                ghost.render_y * self.tile_size
                + HUD_HEIGHT
                + self.tile_size // 2
            )
            color = (
                (55, 85, 235)
                if frightened
                else GHOST_COLORS[index % len(GHOST_COLORS)]
            )
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
                    BLUE if not frightened else WHITE,
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

        direction = PLAYER_DIRECTIONS.get(player.angle)
        if direction is None:
            raise ValueError(f"Unsupported player direction angle: {player.angle}")
        frame_index = int(self.mouth_progress >= 0.5)
        frame = self.player_frames[direction][frame_index]
        rect = frame.get_rect(center=(
            int(player.render_x * self.tile_size + self.tile_size // 2),
            int(
                player.render_y * self.tile_size
                + HUD_HEIGHT
                + self.tile_size // 2
            ),
        ))
        self.canvas.blit(frame, rect)

    def draw_hud(self, text):
        pygame.draw.rect(self.canvas, BLACK, (0, 0, self.width, HUD_HEIGHT))
        self.draw_text(text, 4, self.small_font, center=False)

    def draw_text(self, text, y, font=None, color=WHITE, center=True):
        font = font or self.font
        label = font.render(text, True, color)
        rect = label.get_rect(center=(self.width // 2, y)) if center else label.get_rect(topleft=(40, y))
        self.canvas.blit(label, rect)
        return rect

    def clear(self, background="menu"):
        if background != self.active_background:
            self.active_background = background
            self.background = pygame.transform.scale(
                self.backgrounds[background], self.screen.get_size()
            )
        self.canvas.fill((0, 0, 0, 0))
