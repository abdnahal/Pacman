import sys

import pygame

from pacman.config import load_config
from pacman.game import Game


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py config.json")
        return 2

    try:
        config, warnings = load_config(sys.argv[1])
        game = Game(config, warnings)
        game.run()
        return 0
    except KeyboardInterrupt:
        print("Game interrupted.")
        return 0
    except (pygame.error, OSError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
