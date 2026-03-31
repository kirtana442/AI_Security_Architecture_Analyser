# Handles database connection, table initialisation and CRUD

import sqlite3
import uuid
from datetime import datetime,timezone
from typing import Optional

DB_PATH = "ai_security.db"

def get_connection() -> sqlite3.Connection:
    #return sqlite3 connection with row_factory set to Row 
    #(instead of returning tuple it returns dictionary with keys as coloumn names)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Create the architectures table if it does not already exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS architectures (
                id          TEXT PRIMARY KEY,
                architecture_text TEXT NOT NULL,
                created_at  TEXT NOT NULL,
                status      TEXT NOT NULL DEFAULT 'received'
            )
            """
        )
        conn.commit()

def insert_architecture(architecture_text: str) -> dict:
    """
    Insert a new architecture record and return the created row as a dict.
 
    Args:
        architecture_text: The raw architecture description submitted by the client.
 
    Returns:
        A dict with keys: id, architecture_text, created_at, status.
    """

    record_id = str(uuid.uuid4()) # helps in decoupling and preventing IDOR, conflicts in changing database,
    created_at = datetime.now(timezone.utc).isoformat()
    status = "recieved"

    with get_connection() as conn:
        conn.execute("INSERT INTO architectures (id, architecture_text, created_at, status) VALUES (?,?,?,?)",
                     (record_id, architecture_text, created_at, status),
                     )
        conn.commit()

        return {
            "id" : record_id,
            "architecture_text": architecture_text,
            "created_at": created_at,
            "status": status,
        }
    
def fetch_architecture(record_id: str) -> Optional[dict]: #Optional says dict|None helps in preventing null dereferencing and frontend error handling
    """
    Retrieve an architecture record by its UUID.
 
    Args:
        record_id: The UUID string of the record to fetch.
 
    Returns:
        A dict with record fields, or None if not found.
    """

    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, architecture_text, created_at, status FROM architectures where id = ?",
            (record_id,),
        ).fetchone()

        if row is None:
            return None
        
        return dict(row) # while row_factory returns dict like sqlite3.Row object still need to convert to dict