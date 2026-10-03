"""The best score saved on this computer, or in the browser on the web build."""

import os
import sys
from pathlib import Path

_WEB_KEY = "red-moon-best"


def high_score_path():
    base = os.environ.get("LOCALAPPDATA")
    root = Path(base) / "TheRedMoon" if base else Path.home() / ".red-moon"
    return root / "best.txt"


def _web_storage():
    from platform import window

    return window.localStorage


def read_high_score():
    if sys.platform == "emscripten":
        try:
            raw = _web_storage().getItem(_WEB_KEY)
            if not raw:
                return 0
            return max(0, int(str(raw)))
        except (AttributeError, OSError, TypeError, ValueError):
            return 0
    try:
        return max(0, int(high_score_path().read_text(encoding="utf-8").strip()))
    except (OSError, ValueError):
        return 0


def note_arcade(game, score, note=""):
    """Leave this run for Melted Arcade, on the name signed in there."""
    if sys.platform != "emscripten":
        return
    try:
        import json
        import time

        storage = _web_storage()
        player = str(storage.getItem("melted-arcade-player") or "").strip()
        score = max(0, int(score))
        if not player or score <= 0:
            return
        raw = storage.getItem("melted-arcade-slips") or "[]"
        try:
            slips = json.loads(str(raw))
        except ValueError:
            slips = []
        if not isinstance(slips, list):
            slips = []
        slips.append({
            "game": str(game),
            "score": score,
            "player": player,
            "note": "win" if note == "win" else "",
            "at": int(time.time() * 1000),
        })
        storage.setItem("melted-arcade-slips", json.dumps(slips[-40:]))
    except Exception:
        return


def write_high_score(score):
    if sys.platform == "emscripten":
        try:
            _web_storage().setItem(_WEB_KEY, str(int(score)))
        except (AttributeError, OSError, TypeError, ValueError):
            pass
        return
    path = high_score_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(int(score)), encoding="utf-8")
