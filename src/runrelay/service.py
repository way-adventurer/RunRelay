from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .executor import ExecutorError, LocalExecutor, SSHExecutor
from .git import capture
from .models import Experiment, Status, TERMINAL_STATUSES
from .storage import Storage
from .wake import make_wake_backend


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RunRelayService:
    def __init__(self, root: Path):
        self.root = root
        self.storage = Storage(root)
        self.local = LocalExecutor()
        self.ssh = SSHExecutor()

    def _executor(self, experiment: Experiment):
        return self.local if experiment.host == "local" else self.ssh

    def submit(
        self,
        *,
        host: str,
        workdir: str,
        command: str,
        name: str | None = None,
        artifacts: list[str] | None = None,
        source_dir: str | None = None,
        wake_backend: str = "noop",
        session_id: str | None = None,
        continuation_prompt: str | None = None,
        wake_command: str | None = None,
    ) -> Experiment:
        if wake_backend == "codex-cli" and not session_id:
            raise ValueError("codex-cli wake backend requires --session")
        if wake_backend == "command" and not wake_command:
            raise ValueError("command wake backend requires --wake-command")
        experiment_id = (
            f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        )
        local_dir = self.root / "experiments" / experiment_id
        experiment = Experiment(
            id=experiment_id,
            name=name,
            host=host,
            workdir=workdir,
            command=command,
            created_at=now(),
            local_dir=str(local_dir),
            remote_dir=f"$HOME/.runrelay/jobs/{experiment_id}" if host != "local" else None,
            artifacts=artifacts or [],
            wake_backend=wake_backend,
            session_id=session_id,
            continuation_prompt=continuation_prompt,
            wake_command=wake_command,
            **capture(source_dir or Path.cwd()),
        )
        local_dir.mkdir(parents=True, exist_ok=True)
        self.storage.put(experiment)
        executor = self._executor(experiment)
        try:
            experiment.status = Status.STARTING
            self.storage.put(experiment)
            result = executor.submit(experiment)
            if isinstance(result, tuple):
                experiment.pid, experiment.remote_dir = result
            else:
                experiment.pid = result
            experiment.status = Status.RUNNING
            experiment.started_at = now()
            self.storage.put(experiment)
        except Exception as exc:
            experiment.status = Status.FAILED
            experiment.ended_at = now()
            experiment.last_error = str(exc)
            self.storage.put(experiment)
            raise
        return experiment

    def get(self, experiment_id: str) -> Experiment:
        experiment = self.storage.get(experiment_id)
        if not experiment:
            raise KeyError(f"Unknown experiment: {experiment_id}")
        return experiment

    def refresh(self, experiment_id: str) -> Experiment:
        experiment = self.get(experiment_id)
        if experiment.status in TERMINAL_STATUSES:
            return experiment
        try:
            state = self._executor(experiment).status(experiment)
        except ExecutorError as exc:
            experiment.last_error = str(exc)
            self.storage.put(experiment)
            return experiment
        experiment.status = state.status
        if state.pid:
            experiment.pid = state.pid
        if state.exit_code is not None:
            experiment.exit_code = state.exit_code
        if state.detail:
            experiment.last_error = state.detail
        if state.status in TERMINAL_STATUSES:
            experiment.ended_at = experiment.ended_at or now()
            if state.status != Status.CANCELLED and experiment.wake_status == "PENDING":
                try:
                    experiment.wake_detail = make_wake_backend(experiment).wake(experiment)
                    experiment.wake_status = "SENT"
                except Exception as exc:
                    experiment.wake_status = "FAILED"
                    experiment.wake_detail = str(exc)
        self.storage.put(experiment)
        return experiment

    def list(self) -> list[Experiment]:
        experiments = self.storage.list()
        for experiment in experiments:
            if experiment.status not in TERMINAL_STATUSES:
                self.refresh(experiment.id)
        return self.storage.list()

    def cancel(self, experiment_id: str) -> Experiment:
        experiment = self.get(experiment_id)
        if experiment.status in TERMINAL_STATUSES:
            return experiment
        self._executor(experiment).cancel(experiment)
        experiment.status = Status.CANCELLED
        experiment.ended_at = now()
        experiment.wake_status = "SKIPPED"
        self.storage.put(experiment)
        return experiment

    def logs(self, experiment_id: str) -> tuple[str, str]:
        experiment = self.refresh(experiment_id)
        return self._executor(experiment).logs(experiment)

    def wait(
        self, experiment_id: str, interval: float = 5.0, timeout: float | None = None
    ) -> Experiment:
        started = time.monotonic()
        while True:
            experiment = self.refresh(experiment_id)
            if experiment.status in TERMINAL_STATUSES:
                return experiment
            if timeout is not None and time.monotonic() - started >= timeout:
                return experiment
            time.sleep(max(0.1, interval))

    def daemon(self, interval: float = 5.0) -> None:
        while True:
            for experiment in self.storage.list():
                if experiment.status not in TERMINAL_STATUSES:
                    self.refresh(experiment.id)
            time.sleep(max(0.1, interval))
