from enum import Enum
from typing import Tuple


Position = tuple[int, int]
MazeGrid = list[list[int]]


class Direction(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 4
    LEFT = 8

    @property
    def delta(self) -> Position:
        offsets = {
            Direction.UP: (0, -1),
            Direction.DOWN: (0, 1),
            Direction.RIGHT: (1, 0),
            Direction.LEFT: (-1, 0)
        }
        return offsets[self]

    @property
    def wall_bit(self) -> int:
        return self.value

    def opposite(self) -> "Direction":
        opps = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }
        return opps[self]
