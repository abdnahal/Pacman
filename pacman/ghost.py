from .level import Position, Level


class Ghost:
    """Store one ghost's position and movement state."""

    def __init__(self, spawn: Position) -> None:
        self.spawn = spawn
        self.grid_x, self.grid_y = spawn
        self.respawn_remaining: float = 0.0

    @property
    def position(self) -> Position:
        """Return the ghost's current grid position."""
        return self.grid_x, self.grid_y

    @property
    def active(self) -> bool:
        """Return whether the ghost can move and collide."""
        return self.respawn_remaining <= 0.0

    def choose_next_cell(
        self,
        level: Level,
        distances: dict[Position, int],
        frightened: bool,
    ) -> Position | None:
        """Choose a legal neighboring cell to chase or flee."""
        if not self.active:
            return None

        if not frightened and distances.get(self.position) == 0:
            return None

        candidates = [
            position
            for position in level.neighbors(self.position)
            if position in distances
        ]

        if not candidates:
            return None

        if frightened:
            return max(candidates, key=lambda pos: distances[pos])

        return min(candidates, key=lambda pos: distances[pos])
