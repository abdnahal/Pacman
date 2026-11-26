# Pac-Man

## Run

The program requires exactly one JSON configuration argument:

```bash
python3 pac-man.py config.json
```

The resizable game window opens at the desktop resolution.

Missing or invalid configuration values use safe defaults and are reported in the
main menu. Unknown keys are ignored. JSON comments beginning with `#` or `//` are
supported.

Install the project dependencies and the assigned A-Maze-ing wheel:

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install mazegenerator-2.1.0-py3-none-any.whl
```

## Configuration

| Key | Default | Meaning |
|---|---:|---|
| `highscore_filename` | `highscores.json` | Persistent JSON highscore file |
| `levels` | one 25x15 level | Array of `{width, height, seed}` levels |
| `width` | 25 | Level width (10-100); supplied inside a level object |
| `height` | 15 | Level height (10-100); supplied inside a level object |
| `lives` | 3 | Starting lives |
| `pacgum` | 42 | Pac-gum item count |
| `points_per_pacgum` | 10 | Score for a normal Pac-gum |
| `points_per_super_pacgum` | 50 | Score for a super Pac-gum |
| `points_per_ghost` | 200 | Score for eating a ghost |
| `seed` | 42 | Default level seed |
| `level_max_time` | 90 | Maximum seconds per level |
| `cheat_mode` | false | Enables evaluation cheat keys |

## Maze integration

`pacman/maze.py` is the only maze integration layer. It imports the external
`mazegenerator.MazeGenerator` package and requests `perfect=False`. It does not
contain or copy a maze generator. Constructor or generation failures are displayed
without a traceback.

## Highscores

The JSON file contains at most ten entries sorted by score. Names are limited to
10 characters and alphanumeric characters or spaces. Corrupt or unreadable files
are treated as empty and save failures are reported safely.

## Cheat mode

With `"cheat_mode": true`:

- `F1` toggles invincibility.
- `F2` ends the run with a win.
- `F3` ends the run with a loss.

## Controls and screens

- Use the up/down arrows and Enter to navigate the main and pause menus.
- Use the arrow keys to move during a game. Press Escape to pause; press it
  again to resume.
- The main menu includes highscores and instructions. Press Escape on either
  screen to return to the menu.
- The in-game HUD shows score, lives, level, and remaining time. The timer
  pauses with the game and reaching zero ends the run.
- After a win or loss, enter a name and press Enter to save the score.

## Audio

- `background_music.ogg` plays in menus and `ingame_music.ogg` during gameplay.
- `menu_move.wav` and `menu_select.wav` provide menu navigation sounds.
- The supplied `.mp3`-named music files are WebM audio, so the game uses Ogg
  conversions of those files.

## Video backgrounds

The game uses `menu_background_4k30.mp4` on menus and result screens and
`game_background_4k30.mp4` during gameplay. These are 30 FPS playback copies
of `live menu.mp4` and `live background.mp4`, preserving 4K resolution while
reducing the decoding workload. Both videos loop silently; music is handled
separately.

Maze walls use warm stone textures in three nested outer, middle, and inner
tiers. The maze layout and collision logic are unchanged.

The player uses the cardinal-direction frames in `character movement.png`.
Closed/open frames alternate for up, down, left, and right; diagonal frames are
ignored.

## Project structure

- `pac-man.py`: command-line entry point.
- `pacman/config.py`: configuration parsing and validation.
- `pacman/maze.py`: external generator adapter.
- `pacman/highscores.py`: persistent score storage.
- `pacman/player.py`: movement state and partner game-logic hook.
- `pacman/display.py`: Pygame rendering and asset loading.
- `pacman/game.py`: menus, game loop, game-over/name entry, and screen routing.

Game logic such as item collection, ghost AI, collisions, wins, and losses should
extend `Game` and `Player`; rendering remains in `display.py`.
