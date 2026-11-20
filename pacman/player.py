import pygame


DIRECTIONS = {
    pygame.K_UP: (0, -1, 1),
    pygame.K_RIGHT: (1, 0, 2),
    pygame.K_DOWN: (0, 1, 4),
    pygame.K_LEFT: (-1, 0, 8),
}


class Player:
    def __init__(self, x, y, move_speed):
        self.grid_x = x
        self.grid_y = y
        self.render_x = float(x)
        self.render_y = float(y)
        self.current_direction = None
        self.requested_direction = None
        self.movement_progress = 0.0
        self.move_speed = move_speed
        self.angle = 0

    def set_direction(self, key):
        if key in DIRECTIONS:
            self.requested_direction = key

    def can_move(self, key, maze, cols, rows):
        dx, dy, wall_bit = DIRECTIONS[key]
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy
        if not (0 <= new_x < cols and 0 <= new_y < rows):
            return False
        return not (maze[self.grid_y][self.grid_x] & wall_bit) and maze[new_y][new_x] != 15

    def update(self, frame_time, maze, cols, rows, tile_size):
        if self.current_direction is not None and self.requested_direction is not None:
            current_dx, current_dy, _ = DIRECTIONS[self.current_direction]
            requested_dx, requested_dy, _ = DIRECTIONS[self.requested_direction]
            if (current_dx, current_dy) == (-requested_dx, -requested_dy):
                self.grid_x += current_dx
                self.grid_y += current_dy
                self.movement_progress = 1.0 - self.movement_progress
                self.current_direction = self.requested_direction

        distance = self.move_speed * frame_time / 1000 / tile_size
        while distance > 0:
            if self.current_direction is None:
                if self.requested_direction is None or not self.can_move(
                    self.requested_direction, maze, cols, rows
                ):
                    break
                self.current_direction = self.requested_direction

            if self.movement_progress == 0 and self.requested_direction is not None:
                if self.can_move(self.requested_direction, maze, cols, rows):
                    self.current_direction = self.requested_direction

            dx, dy, _ = DIRECTIONS[self.current_direction]
            distance_to_next = 1.0 - self.movement_progress
            step = min(distance, distance_to_next)
            self.movement_progress += step
            distance -= step

            if self.movement_progress >= 1.0:
                previous_direction = self.current_direction
                self.grid_x += dx
                self.grid_y += dy
                self.movement_progress = 0.0
                if self.requested_direction is not None and self.can_move(
                    self.requested_direction, maze, cols, rows
                ):
                    self.current_direction = self.requested_direction
                elif self.can_move(previous_direction, maze, cols, rows):
                    self.current_direction = previous_direction
                else:
                    self.current_direction = None

        if self.current_direction is None:
            self.render_x = float(self.grid_x)
            self.render_y = float(self.grid_y)
        else:
            dx, dy, _ = DIRECTIONS[self.current_direction]
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
