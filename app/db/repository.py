import json
import sqlite3
from pathlib import Path
from typing import Any

from app.schemas.ticket import TicketInput, TriageAnalysis, StoredTicket


class TicketRepository:
    """SQLite repository for analyzed tickets."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._ensure_parent_dir()
        self.init_schema()

    def _ensure_parent_dir(self) -> None:
        path = Path(self.db_path)
        if path.parent != Path("."):
            path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    reported_by TEXT,
                    environment TEXT,
                    logs TEXT,
                    analysis_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def save(self, ticket: TicketInput, analysis: TriageAnalysis) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO tickets (
                    title,
                    description,
                    reported_by,
                    environment,
                    logs,
                    analysis_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket.title,
                    ticket.description,
                    ticket.reported_by,
                    ticket.environment,
                    ticket.logs,
                    analysis.model_dump_json(),
                ),
            )
            return int(cursor.lastrowid)

    def list_all(self) -> list[StoredTicket]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM tickets ORDER BY id DESC").fetchall()
        return [self._row_to_stored_ticket(row) for row in rows]

    def get(self, ticket_id: int) -> StoredTicket | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_stored_ticket(row)

    def delete(self, ticket_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
            return cursor.rowcount > 0

    def _row_to_stored_ticket(self, row: sqlite3.Row) -> StoredTicket:
        analysis_data: dict[str, Any] = json.loads(row["analysis_json"])
        return StoredTicket(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            reported_by=row["reported_by"],
            environment=row["environment"],
            logs=row["logs"],
            analysis=TriageAnalysis.model_validate(analysis_data),
            created_at=row["created_at"],
        )
