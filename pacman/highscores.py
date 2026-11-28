import json
import re
from pathlib import Path


class HighScoreStore:
    def __init__(self, filename):
        self.path = Path(filename)

    def load(self):
        if not self.path.is_file():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                return []
            scores = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                name = item.get("name")
                score = item.get("score")
                if self.valid_name(name) and isinstance(
                                score, int) and not isinstance(score, bool):
                    if score >= 0:
                        scores.append({"name": name.strip()[:10],
                                       "score": score})
            scores.sort(key=lambda item: item["score"], reverse=True)
            return scores[:10]
        except (OSError, json.JSONDecodeError):
            return []

    @staticmethod
    def valid_name(name):
        return (
            isinstance(name, str)
            and 0 < len(name) <= 10
            and re.fullmatch(r"[A-Za-z0-9 ]+", name) is not None
        )

    def add(self, name, score):
        name = name.strip()
        if not self.valid_name(name):
            return False
        if not isinstance(score, int) or isinstance(score, bool) or score < 0:
            return False
        scores = self.load()
        scores.append({"name": name[:10], "score": score})
        scores.sort(key=lambda item: item["score"], reverse=True)
        scores = scores[:10]
        try:
            self.path.write_text(json.dumps(scores, indent=2),
                                 encoding="utf-8")
            return True
        except OSError:
            return False
