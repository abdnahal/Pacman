import importlib


class MazeError(Exception):
    pass


def load_maze(width, height, seed):
    """Load and adapt the assigned external A-Maze-ing package."""
    try:
        module = importlib.import_module("mazegenerator")
        generator_class = getattr(module, "MazeGenerator", None)
        if generator_class is None:
            raise MazeError("External package does not provide MazeGenerator")

        try:
            generator = generator_class(
                size=(width, height), perfect=False, seed=seed
            )
        except TypeError as exc:
            raise MazeError(
                "External MazeGenerator constructor is incompatible"
            ) from exc

        maze = getattr(generator, "maze", None)
        entry = getattr(generator, "maze_entry", (0, 0))
        exit_cell = getattr(generator, "maze_exit", None)
        if not isinstance(maze, list) or len(maze) != height:
            raise MazeError("External package returned an invalid maze")
        if any(not isinstance(row, list) or len(row) != width for row in maze):
            raise MazeError("External package returned an invalid maze size")
        return maze, entry, exit_cell
    except MazeError:
        raise
    except ImportError as exc:
        raise MazeError(
            "External A-Maze-ing package is not installed"
        ) from exc
    except Exception as exc:
        raise MazeError(
            f"External maze generator failed: {exc}"
        ) from exc
