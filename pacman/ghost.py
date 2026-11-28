from .level import Position, Level
from random import choice


class Ghost:
    """Store one ghost's position and movement state."""

    def __init__(self, spawn: Position) -> None:
        self.spawn = spawn
        self.grid_x, self.grid_y = spawn
        self.render_x, self.render_y = map(float, spawn)
        self.move_target: Position | None = None
        self.move_elapsed = 0.0
        self.move_duration = 0.0
        self.respawn_remaining: float = 0.0

    @property
    def position(self) -> Position:
        """Return the ghost's current grid position."""
        return self.grid_x, self.grid_y

    @property
    def active(self) -> bool:
        """Return whether the ghost can move and collide."""
        return self.respawn_remaining <= 0.0

    @property
    def moving(self) -> bool:
        return self.move_target is not None

    def move_to(self, destination: Position, duration: float) -> None:
        """Begin a smooth move to a neighboring cell."""
        if not self.active or self.moving:
            return
        self.move_target = destination
        self.move_elapsed = 0.0
        self.move_duration = duration

    def respawn(self, delay: float) -> None:
        """Temporarily remove this ghost before returning it to its spawn."""
        self.respawn_remaining = delay
        self.move_target = None
        self.move_elapsed = 0.0

    def update(self, elapsed: float) -> float:
        """Advance movement and return elapsed time left after a tile."""
        if self.respawn_remaining > 0.0:
            if elapsed < self.respawn_remaining:
                self.respawn_remaining -= elapsed
                return 0.0
            elapsed -= self.respawn_remaining
            self.respawn_remaining = 0.0
            self.grid_x, self.grid_y = self.spawn
            self.render_x, self.render_y = map(float, self.spawn)

        if self.move_target is None:
            return elapsed

        time_to_target = self.move_duration - self.move_elapsed
        if elapsed < time_to_target:
            self.move_elapsed += elapsed
            progress = self.move_elapsed / self.move_duration
            target_x, target_y = self.move_target
            self.render_x = self.grid_x + (target_x - self.grid_x) * progress
            self.render_y = self.grid_y + (target_y - self.grid_y) * progress
            return 0.0

        elapsed -= time_to_target
        self.move_elapsed = self.move_duration
        progress = self.move_elapsed / self.move_duration
        target_x, target_y = self.move_target
        self.render_x = self.grid_x + (target_x - self.grid_x) * progress
        self.render_y = self.grid_y + (target_y - self.grid_y) * progress
        self.grid_x, self.grid_y = self.move_target
        self.render_x, self.render_y = map(float, self.move_target)
        self.move_target = None
        self.move_elapsed = 0.0
        return elapsed

    def reset(self) -> None:
        """Restore the ghost to its initial position and active state."""
        self.grid_x, self.grid_y = self.spawn
        self.render_x, self.render_y = map(float, self.spawn)
        self.move_target = None
        self.move_elapsed = 0.0
        self.respawn_remaining = 0.0

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


class GreedyGhost(Ghost):
    def __init__(self, spawn):
        super().__init__(spawn)

    def choose_next_cell(self, level, distances, frightened) -> Position:
        """Choose a legal neighboring cell to chase or flee."""
        if frightened:
            return super().choose_next_cell(level, distances, frightened)
        if not self.active:
            return None

        if not frightened and distances.get(self.position) == 0:
            return None

        candidates = [position for position in level.neighbors(self.position)
                      if position in distances]
        if not candidates:
            return None
        close = [position for position in candidates
                 if distances[position] <= 3]
        if close:
            return choice(close)
        return choice(candidates)
