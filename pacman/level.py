from .types import Direction, MazeGrid, Position
from .game import MazeError
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
        equal = all(True for row in maze if len(row) == self.width)
        if not equal:
            raise MazeError("Invalid row detected, \
rows should have the same size!")
        for row in self.maze:
            cells = all(True for cell in row if 15 >= cell >= 0)
            if not cells:
                raise MazeError("Invalid Maze cells detected!")
        self.collectible = set()

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
        source_cell = self.maze[y][x]
        destination_cell = self.maze[dy + y][dx + x]
        if not self.in_bounds((dx, dy)) or not self.is_walk((dx, dy)):
            return False
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
