from __future__ import annotations

import os
from pathlib import Path


def state_dir(explicit: str | None = None) -> Path:
    value = explicit or os.environ.get("RUNRELAY_HOME") or "~/.runrelay"
    path = Path(value).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    (path / "experiments").mkdir(parents=True, exist_ok=True)
    return path

