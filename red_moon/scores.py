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
