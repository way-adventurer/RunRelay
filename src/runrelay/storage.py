from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .models import Experiment, Status


class Storage:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.db_path = root / "runrelay.db"
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS experiments (
                    id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )

    def put(self, experiment: Experiment) -> None:
        payload = json.dumps(experiment.to_dict(), ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO experiments (id, payload, created_at, status)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    payload=excluded.payload,
                    status=excluded.status
                """,
                (experiment.id, payload, experiment.created_at, experiment.status.value),
            )

    def get(self, experiment_id: str) -> Experiment | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM experiments WHERE id = ?", (experiment_id,)
            ).fetchone()
        return Experiment.from_dict(json.loads(row["payload"])) if row else None

    def list(self, statuses: Iterable[Status] | None = None) -> list[Experiment]:
        query = "SELECT payload FROM experiments"
        params: list[str] = []
        if statuses:
            values = [status.value for status in statuses]
            query += f" WHERE status IN ({','.join('?' for _ in values)})"
            params.extend(values)
        query += " ORDER BY created_at DESC"
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [Experiment.from_dict(json.loads(row["payload"])) for row in rows]

