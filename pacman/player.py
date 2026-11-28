import pygame
from .types import Direction
from .level import Level

DIRECTIONS = {
    pygame.K_UP: Direction.UP,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
}


class Player:
    def __init__(self, x, y, move_speed, maze):
        self.grid_x = x
        self.grid_y = y
        self.render_x = float(x)
        self.render_y = float(y)
        self.current_direction = None
        self.requested_direction = None
        self.movement_progress = 0.0
        self.move_speed = move_speed
        self.angle = 0
        self.maze = maze
        self.level = Level(maze)

    def set_direction(self, key):
        if key in DIRECTIONS:
            self.requested_direction = DIRECTIONS[key]

    def update(self, frame_time, tile_size):
        if (self.current_direction is not None
                and self.requested_direction is not None):
            current_dx, current_dy = self.current_direction.delta
            requested_dx, requested_dy = self.requested_direction.delta
            if (current_dx, current_dy) == (-requested_dx, -requested_dy):
                self.grid_x += current_dx
                self.grid_y += current_dy
                self.movement_progress = 1.0 - self.movement_progress
                self.current_direction = self.requested_direction

        distance = self.move_speed * frame_time / 1000 / tile_size
        while distance > 0:
            if self.current_direction is None:
                if self.requested_direction is None or not self.level.can_move(
                    (self.grid_x, self.grid_y), self.requested_direction
                ):
                    break
                self.current_direction = self.requested_direction

            if (self.movement_progress == 0
                    and self.requested_direction is not None):
                if self.level.can_move((self.grid_x, self.grid_y),
                                       self.requested_direction):
                    self.current_direction = self.requested_direction

            dx, dy = self.current_direction.delta
            distance_to_next = 1.0 - self.movement_progress
            step = min(distance, distance_to_next)
            self.movement_progress += step
            distance -= step

            if self.movement_progress >= 1.0:
                previous_direction = self.current_direction
                self.grid_x += dx
                self.grid_y += dy
                self.movement_progress = 0.0
                if (self.requested_direction is not None 
                    and self.level.can_move(
                        (self.grid_x, self.grid_y), self.requested_direction
                        )):
                    self.current_direction = self.requested_direction
                elif self.level.can_move((self.grid_x, self.grid_y),
                                         previous_direction):
                    self.current_direction = previous_direction
                else:
                    self.current_direction = None

        if self.current_direction is None:
            self.render_x = float(self.grid_x)
            self.render_y = float(self.grid_y)
        else:
            dx, dy = self.current_direction.delta
            if dx == 1:
                self.angle = 0
            elif dx == -1:
                self.angle = 180
            elif dy == -1:
                self.angle = 90
            else:
                self.angle = 270
            self.render_x = self.grid_x + dx * self.movement_progress
            self.render_y = self.grid_y + dy * self.movement_progress
