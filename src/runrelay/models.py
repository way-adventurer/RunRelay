from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Status(str, Enum):
    PENDING = "PENDING"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    LOST = "LOST"


TERMINAL_STATUSES = {Status.COMPLETED, Status.FAILED, Status.CANCELLED, Status.LOST}


@dataclass
class Experiment:
    id: str
    host: str
    workdir: str
    command: str
    status: Status = Status.PENDING
    name: str | None = None
    created_at: str = ""
    started_at: str | None = None
    ended_at: str | None = None
    pid: int | None = None
    exit_code: int | None = None
    local_dir: str = ""
    remote_dir: str | None = None
    git_repo: str | None = None
    git_branch: str | None = None
    git_commit: str | None = None
    git_dirty: bool | None = None
    artifacts: list[str] = field(default_factory=list)
    wake_backend: str = "noop"
    wake_status: str = "PENDING"
    wake_detail: str | None = None
    session_id: str | None = None
    continuation_prompt: str | None = None
    wake_command: str | None = None
    last_error: str | None = None
    monitor_pid: int | None = None
    monitor_status: str = "PENDING"

    def to_dict(self) -> dict[str, Any]:
        result = dict(self.__dict__)
        result["status"] = self.status.value
        return result

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Experiment":
        value = dict(value)
        value["status"] = Status(value["status"])
        value.setdefault("artifacts", [])
        return cls(**value)
