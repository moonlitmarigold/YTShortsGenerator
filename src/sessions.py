import sqlite3
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from uuid import uuid4

from .generation_types.schemas import QuoteOutput

import logging
logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Status(str, Enum):
    """Lifecycle of a single generation run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    UPLOADED = "uploaded"


@dataclass
class SessionInfo:
    """One video-generation run. Steps fill in fields as the pipeline progresses,
    then hand the record to a SessionStore to persist."""

    generation_type: str
    id: str = field(default_factory=lambda: uuid4().hex)
    status: Status = Status.PENDING

    # Artifacts produced along the 7-step pipeline
    title: str | None = None
    script: str | None = None          # raw JSON blob from the Prompt step
    output: QuoteOutput | None = None  # parsed/validated Prompt output
    audio_path: str | None = None      # TTS narration
    video_path: str | None = None      # assembled 9:16 mp4
    thumbnail_path: str | None = None
    youtube_id: str | None = None      # set once uploaded
    error: str | None = None           # last failure, if any

    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


class SessionStore:
    """Small sqlite adapter for SessionInfo. `save()` upserts on id, so a step can
    call it after every stage. Usable as a context manager."""

    _COLUMNS = [f.name for f in fields(SessionInfo)]

    def __init__(self, db_path: Path | str = "sessions.db"):
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id              TEXT PRIMARY KEY,
                generation_type TEXT NOT NULL,
                status          TEXT NOT NULL,
                title           TEXT,
                script          TEXT,
                output          TEXT,
                audio_path      TEXT,
                video_path      TEXT,
                thumbnail_path  TEXT,
                youtube_id      TEXT,
                error           TEXT,
                created_at      TEXT NOT NULL,
                updated_at      TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    @staticmethod
    def _to_params(session: SessionInfo) -> dict:
        return {
            **{c: getattr(session, c) for c in SessionStore._COLUMNS},
            "status": session.status.value,
            "output": session.output.model_dump_json() if session.output else None,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
        }

    @staticmethod
    def _from_row(row: sqlite3.Row) -> SessionInfo:
        return SessionInfo(
            id=row["id"],
            generation_type=row["generation_type"],
            status=Status(row["status"]),
            title=row["title"],
            script=row["script"],
            output=QuoteOutput.model_validate_json(row["output"]) if row["output"] else None,
            audio_path=row["audio_path"],
            video_path=row["video_path"],
            thumbnail_path=row["thumbnail_path"],
            youtube_id=row["youtube_id"],
            error=row["error"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def save(self, session: SessionInfo) -> SessionInfo:
        """Insert a new session or update an existing one (matched on id)."""
        session.updated_at = _now()
        logger.debug('Saving session {} ({})'.format(session.id, session.status.value))
        self.conn.execute(
            """
            INSERT INTO sessions (
                id, generation_type, status, title, script, output, audio_path,
                video_path, thumbnail_path, youtube_id, error, created_at, updated_at
            ) VALUES (
                :id, :generation_type, :status, :title, :script, :output, :audio_path,
                :video_path, :thumbnail_path, :youtube_id, :error, :created_at, :updated_at
            )
            ON CONFLICT(id) DO UPDATE SET
                generation_type = excluded.generation_type,
                status          = excluded.status,
                title           = excluded.title,
                script          = excluded.script,
                output          = excluded.output,
                audio_path      = excluded.audio_path,
                video_path      = excluded.video_path,
                thumbnail_path  = excluded.thumbnail_path,
                youtube_id      = excluded.youtube_id,
                error           = excluded.error,
                updated_at      = excluded.updated_at
            """,
            self._to_params(session),
        )
        self.conn.commit()
        return session

    def get(self, session_id: str) -> SessionInfo | None:
        row = self.conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        return self._from_row(row) if row else None

    def list(self, status: Status | None = None) -> list[SessionInfo]:
        """All sessions, newest first, optionally filtered by status."""
        if status is None:
            rows = self.conn.execute(
                "SELECT * FROM sessions ORDER BY created_at DESC"
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM sessions WHERE status = ? ORDER BY created_at DESC",
                (status.value,),
            ).fetchall()
        return [self._from_row(r) for r in rows]

    def delete(self, session_id: str) -> None:
        self.conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return None
