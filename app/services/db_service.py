"""Servicio de persistencia con SQLite para tickets de asesores, historial y usuarios."""

import aiosqlite
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.config import get_settings

settings = get_settings()
# Extraer la ruta del archivo SQLite a partir de database_url
DB_PATH = settings.database_url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")


_db_initialized = False


async def init_db():
    """Inicializa las tablas necesarias en la base de datos SQLite."""
    global _db_initialized
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                document_number TEXT,
                phone TEXT,
                created_at TEXT,
                updated_at TEXT
            );
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS advisor_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                document_number TEXT,
                name TEXT,
                phone TEXT,
                details TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            );
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                agent TEXT,
                created_at TEXT
            );
        """)
        await db.commit()
        _db_initialized = True


async def ensure_db():
    if not _db_initialized:
        await init_db()


async def save_user(
    user_id: str,
    name: Optional[str] = None,
    document_number: Optional[str] = None,
    phone: Optional[str] = None,
):
    """Crea o actualiza información básica del usuario."""
    await ensure_db()
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, name, document_number, phone, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                name = COALESCE(excluded.name, users.name),
                document_number = COALESCE(excluded.document_number, users.document_number),
                phone = COALESCE(excluded.phone, users.phone),
                updated_at = excluded.updated_at;
        """, (user_id, name, document_number, phone, now, now))
        await db.commit()


async def create_advisor_ticket(
    user_id: str,
    document_number: str,
    name: str,
    phone: str,
    details: str,
) -> int:
    """Registra una nueva solicitud para que un asesor empresarial contacte al emprendedor."""
    await ensure_db()
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO advisor_tickets (user_id, document_number, name, phone, details, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
        """, (user_id, document_number, name, phone, details, now))
        await db.commit()
        return cursor.lastrowid


async def get_advisor_tickets(limit: int = 50) -> List[Dict[str, Any]]:
    """Obtiene los tickets registrados para asesores humanos."""
    await ensure_db()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM advisor_tickets ORDER BY id DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def save_message_log(session_id: str, role: str, content: str, agent: Optional[str] = None):
    """Guarda mensajes en el historial para auditoría."""
    await ensure_db()
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO chat_history (session_id, role, content, agent, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, role, content, agent, now))
        await db.commit()
