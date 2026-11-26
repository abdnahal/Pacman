from collections import deque

from .level import Level
from .types import Position


def distance_map(
    level: Level,
    target: Position,
) -> dict[Position, int]:
    """Return shortest corridor distances from target."""
    if not level.is_walk(target):
        return {}

    distances = {target: 0}
    queue = deque([target])

    while queue:
        position = queue.popleft()

        for neighbor in level.neighbors(position):
            if neighbor not in distances:
                distances[neighbor] = distances[position] + 1
                queue.append(neighbor)

    return distances
