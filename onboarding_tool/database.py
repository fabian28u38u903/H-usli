"""
Kunden-Datenbank via SQLite.
Speichert Kundendaten, Analyse-Status und Report-Pfade.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "customers.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Erstellt die Datenbank und Tabellen falls nicht vorhanden."""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                niche TEXT NOT NULL,
                service TEXT NOT NULL,
                target_audience TEXT,
                benefits TEXT,         -- JSON array
                keywords_de TEXT,      -- JSON array
                keywords_en TEXT,      -- JSON array
                contact_email TEXT,
                contact_name TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                -- pending | running | done | error
                report_path TEXT,
                error_message TEXT,
                started_at TEXT,
                finished_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        conn.commit()


# ── Kunden CRUD ──────────────────────────────────────────────────────────────

def create_customer(data: dict) -> int:
    now = datetime.now().isoformat()
    with get_conn() as conn:
        cursor = conn.execute("""
            INSERT INTO customers
              (name, niche, service, target_audience, benefits,
               keywords_de, keywords_en, contact_email, contact_name,
               created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data["name"],
            data["niche"],
            data.get("service", ""),
            data.get("target_audience", ""),
            json.dumps(data.get("benefits", []), ensure_ascii=False),
            json.dumps(data.get("keywords_de", []), ensure_ascii=False),
            json.dumps(data.get("keywords_en", []), ensure_ascii=False),
            data.get("contact_email", ""),
            data.get("contact_name", ""),
            now, now,
        ))
        conn.commit()
        return cursor.lastrowid


def get_customer(customer_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()
    if not row:
        return None
    return _row_to_customer(row)


def list_customers() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM customers ORDER BY created_at DESC"
        ).fetchall()
    return [_row_to_customer(r) for r in rows]


def update_customer(customer_id: int, data: dict):
    now = datetime.now().isoformat()
    with get_conn() as conn:
        conn.execute("""
            UPDATE customers SET
              name=?, niche=?, service=?, target_audience=?,
              benefits=?, keywords_de=?, keywords_en=?,
              contact_email=?, contact_name=?, updated_at=?
            WHERE id=?
        """, (
            data["name"],
            data["niche"],
            data.get("service", ""),
            data.get("target_audience", ""),
            json.dumps(data.get("benefits", []), ensure_ascii=False),
            json.dumps(data.get("keywords_de", []), ensure_ascii=False),
            json.dumps(data.get("keywords_en", []), ensure_ascii=False),
            data.get("contact_email", ""),
            data.get("contact_name", ""),
            now,
            customer_id,
        ))
        conn.commit()


def delete_customer(customer_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM analyses WHERE customer_id=?", (customer_id,))
        conn.execute("DELETE FROM customers WHERE id=?", (customer_id,))
        conn.commit()


def _row_to_customer(row) -> dict:
    d = dict(row)
    d["benefits"] = json.loads(d.get("benefits") or "[]")
    d["keywords_de"] = json.loads(d.get("keywords_de") or "[]")
    d["keywords_en"] = json.loads(d.get("keywords_en") or "[]")
    return d


# ── Analysen CRUD ────────────────────────────────────────────────────────────

def create_analysis(customer_id: int) -> int:
    now = datetime.now().isoformat()
    with get_conn() as conn:
        cursor = conn.execute("""
            INSERT INTO analyses (customer_id, status, created_at)
            VALUES (?, 'pending', ?)
        """, (customer_id, now))
        conn.commit()
        return cursor.lastrowid


def update_analysis_status(analysis_id: int, status: str,
                            report_path: str = None, error: str = None):
    now = datetime.now().isoformat()
    with get_conn() as conn:
        if status == "running":
            conn.execute(
                "UPDATE analyses SET status=?, started_at=? WHERE id=?",
                (status, now, analysis_id)
            )
        elif status in ("done", "error"):
            conn.execute("""
                UPDATE analyses SET status=?, finished_at=?,
                  report_path=?, error_message=?
                WHERE id=?
            """, (status, now, report_path, error, analysis_id))
        else:
            conn.execute(
                "UPDATE analyses SET status=? WHERE id=?",
                (status, analysis_id)
            )
        conn.commit()


def get_latest_analysis(customer_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("""
            SELECT * FROM analyses
            WHERE customer_id=?
            ORDER BY created_at DESC LIMIT 1
        """, (customer_id,)).fetchone()
    return dict(row) if row else None


def list_analyses(customer_id: int) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM analyses
            WHERE customer_id=?
            ORDER BY created_at DESC
        """, (customer_id,)).fetchall()
    return [dict(r) for r in rows]


# DB beim Import initialisieren
init_db()
