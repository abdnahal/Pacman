from .types import Direction, MazeGrid, Position
from .maze import MazeError
from typing import List
from collections import deque


class Level:
    def __init__(self, maze: MazeGrid) -> None:
        self.maze = maze
        if not self.maze:
            raise MazeError("Empty Maze!")
        self.width = len(maze[0])
        self.height = len(maze)
        if self.width == 0 or self.height == 0:
            raise MazeError("Width and height should be positive!")
        if not all(len(row) == self.width for row in maze):
            raise MazeError("Rows must have the same size")

        for row in maze:
            if not all(type(cell) is int and 0 <= cell <= 15 for cell in row):
                raise MazeError("Cells must be integers between 0 and 15")

        self.collectible = set()
        self.player_spawn = self._find_center_spawn(self.maze)
        self.reachable = self.reachable_from(self.player_spawn)
        self.ghost_spawn = self._get_corners()
        self.super_pacgums = set(self.ghost_spawn)
        self.pacgums: set[Position] = (self.reachable - self.super_pacgums)

    def in_bounds(self, position: Position) -> bool:
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walk(self, position: Position) -> bool:
        if not self.in_bounds(position):
            return False
        x, y = position
        return True if self.maze[y][x] != 15 else False

    def can_move(self, position: Position, direction: Direction) -> bool:
        if not self.in_bounds(position) or not self.is_walk(position):
            return False
        x, y = position
        dx, dy = direction.delta
        if (not self.in_bounds((x + dx, y + dy))
                or not self.is_walk((x + dx, y + dy))):
            return False
        source_cell = self.maze[y][x]
        destination_cell = self.maze[dy + y][dx + x]
        source_blocked = source_cell & direction.wall_bit
        destination_blocked = destination_cell & direction.opposite().wall_bit
        if source_blocked or destination_blocked:
            return False
        return True

    def neighbors(self, position: Position) -> List[Position]:
        jiran = []
        for direction in Direction:
            if self.can_move(position, direction):
                dx, dy = direction.delta
                x, y = position
                jiran.append((dx + x, dy + y))
        return jiran

    def reachable_from(self, start: Position) -> set[Position]:
        if not self.is_walk(start):
            return set()

        queue = deque([start])
        visited = set([start])

        while queue:
            pos = queue.popleft()
            for neighbor in self.neighbors(pos):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return visited

    def _get_corners(self) -> List[Position]:
        targets = [
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1),
        ]
        corners = []
        available = self.reachable.copy()
        if len(available) < 4:
            raise MazeError("Need four reachable cells for ghost spawns")
        for target in targets:
            if target in self.reachable:
                chosen = target
            else:
                chosen = min(available, key=lambda pos: (abs(
                    target[0] - pos[0]) + abs(target[1] - pos[1])))
            corners.append(chosen)
            available.remove(chosen)
        if len(corners) != 4:
            raise MazeError("Insufficient corners for ghost spawn!")
        return corners

    def collect(self, position: Position) -> str | None:
        if position in self.pacgums:
            self.pacgums.remove(position)
            return "normal"
        elif position in self.super_pacgums:
            self.super_pacgums.remove(position)
            return 'super'
        return None

    def is_complete(self) -> bool:
        return (not self.super_pacgums and not self.pacgums)

    @staticmethod
    def _find_center_spawn(maze) -> Position:
        height = len(maze)
        width = len(maze[0])
        center_x = width // 2
        center_y = height // 2
        open_cells = [
            (x, y)
            for y in range(height)
            for x in range(width)
            if maze[y][x] != 15
        ]
        if not open_cells:
            raise MazeError("Maze has no walkable player spawn")
        return min(
            open_cells,
            key=lambda position: (
                abs(position[0] - center_x) + abs(position[1] - center_y),
                abs(position[0] - center_x),
                abs(position[1] - center_y),
            ),
        )
