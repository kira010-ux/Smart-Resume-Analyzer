"""SQLite persistence for completed resume analyses."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATABASE_PATH = Path(__file__).with_name("analyses.db")


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                resume_filename TEXT,
                job_title TEXT,
                match_score REAL NOT NULL,
                matched_skills_json TEXT NOT NULL,
                missing_skills_json TEXT NOT NULL,
                resume_skill_count INTEGER NOT NULL,
                job_required_skill_count INTEGER NOT NULL
            )
            """
        )


def save_analysis(
    result: dict[str, Any],
    *,
    resume_filename: str | None = None,
    job_title: str | None = None,
) -> int:
    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO analyses (
                timestamp, resume_filename, job_title, match_score,
                matched_skills_json, missing_skills_json,
                resume_skill_count, job_required_skill_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                resume_filename,
                job_title,
                result["match_score"],
                json.dumps(result["matched_skills"]),
                json.dumps(result["missing_skills"]),
                result["resume_skill_count"],
                result["job_required_skill_count"],
            ),
        )
        return int(cursor.lastrowid)


def list_analyses(limit: int = 25) -> list[dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute(
            "SELECT * FROM analyses ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()

    return [
        {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "resume_filename": row["resume_filename"],
            "job_title": row["job_title"],
            "match_score": row["match_score"],
            "matched_skills": json.loads(row["matched_skills_json"]),
            "missing_skills": json.loads(row["missing_skills_json"]),
            "resume_skill_count": row["resume_skill_count"],
            "job_required_skill_count": row["job_required_skill_count"],
        }
        for row in rows
    ]


init_db()
