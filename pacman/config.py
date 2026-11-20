import json
import re
from pathlib import Path


DEFAULTS = {
    "highscore_filename": "highscores.json",
    "lives": 3,
    "pacgum": 42,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90,
    "cheat_mode": False,
    "levels": [{"width": 25, "height": 15, "seed": 42}],
}


def _strip_comments(text):
    lines = []
    for line in text.splitlines():
        line = re.sub(r"\s+//.*$", "", line)
        if line.lstrip().startswith("#"):
            continue
        in_string = False
        escaped = False
        result = []
        for char in line:
            if escaped:
                result.append(char)
                escaped = False
            elif char == "\\" and in_string:
                result.append(char)
                escaped = True
            elif char == '"':
                in_string = not in_string
                result.append(char)
            elif char == "#" and not in_string:
                break
            else:
                result.append(char)
        lines.append("".join(result))
    return "\n".join(lines)


def _integer(value, minimum, maximum, default, name, warnings):
    if isinstance(value, bool) or not isinstance(value, int):
        warnings.append(f"{name}: invalid integer; using {default}")
        return default
    if value < minimum:
        warnings.append(f"{name}: value below {minimum}; clamped to {minimum}")
        return minimum
    if value > maximum:
        warnings.append(f"{name}: value above {maximum}; clamped to {maximum}")
        return maximum
    return value


def load_config(filename):
    warnings = []
    path = Path(filename)
    if not path.is_file():
        warnings.append(f"Configuration file '{filename}' was not found; using safe defaults")
        raw = {}
    elif path.suffix.lower() != ".json":
        raise ValueError("Configuration file must have a .json extension")
    else:
        try:
            raw = json.loads(_strip_comments(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError as exc:
            warnings.append(
                f"Invalid JSON in '{filename}' (line {exc.lineno}); using safe defaults"
            )
            raw = {}
        except OSError as exc:
            warnings.append(f"Could not read '{filename}' ({exc.strerror}); using safe defaults")
            raw = {}

    if not isinstance(raw, dict):
        warnings.append("Configuration root must be an object; using safe defaults")
        raw = {}

    config = {}
    config["highscore_filename"] = raw.get(
        "highscore_filename", DEFAULTS["highscore_filename"]
    )
    if not isinstance(config["highscore_filename"], str) or not config["highscore_filename"].strip():
        warnings.append("highscore_filename: invalid value; using highscores.json")
        config["highscore_filename"] = "highscores.json"
    else:
        config["highscore_filename"] = config["highscore_filename"].strip()

    integer_keys = (
        ("lives", 1, 99),
        ("pacgum", 0, 10000),
        ("points_per_pacgum", 0, 100000),
        ("points_per_super_pacgum", 0, 100000),
        ("points_per_ghost", 0, 100000),
        ("seed", 0, 2147483647),
        ("level_max_time", 1, 86400),
    )
    for key, minimum, maximum in integer_keys:
        config[key] = _integer(
            raw.get(key, DEFAULTS[key]), minimum, maximum, DEFAULTS[key], key, warnings
        )

    cheat = raw.get("cheat_mode", DEFAULTS["cheat_mode"])
    if not isinstance(cheat, bool):
        warnings.append("cheat_mode: invalid boolean; using false")
        cheat = False
    config["cheat_mode"] = cheat

    levels = raw.get("levels", DEFAULTS["levels"])
    if not isinstance(levels, list) or not levels:
        warnings.append("levels: invalid level array; using one safe level")
        levels = DEFAULTS["levels"]

    safe_levels = []
    for index, level in enumerate(levels[:20], start=1):
        if not isinstance(level, dict):
            warnings.append(f"level {index}: invalid object; using safe level values")
            level = {}
        width = _integer(level.get("width", 25), 10, 100, 25,
                          f"level {index} width", warnings)
        height = _integer(level.get("height", 15), 10, 100, 15,
                           f"level {index} height", warnings)
        seed = _integer(level.get("seed", config["seed"]), 0, 2147483647,
                        config["seed"], f"level {index} seed", warnings)
        safe_levels.append({"width": width, "height": height, "seed": seed})
    config["levels"] = safe_levels
    return config, warnings
