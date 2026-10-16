import sqlite3
from datetime import datetime

DB_NAME = "vault.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Create users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
    """)

    # Create memories table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            encrypted_content TEXT NOT NULL,
            sealed_until TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    conn.commit()
    conn.close()

def create_user(username, password_hash):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()

    conn.close()
    return user

def create_memory(user_id, title, encrypted_content, sealed_until):
    conn = get_connection()
    cur = conn.cursor()

    sealed_str = sealed_until.isoformat() if sealed_until else None

    cur.execute("""
        INSERT INTO memories (user_id, title, encrypted_content, sealed_until)
        VALUES (?, ?, ?, ?)
    """, (user_id, title, encrypted_content, sealed_str))

    conn.commit()
    conn.close()

def get_memories_for_user(user_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM memories
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    memories = cur.fetchall()
    conn.close()
    return memories

def get_memory_for_user(memory_id, user_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM memories
        WHERE id = ? AND user_id = ?
    """, (memory_id, user_id))

    memory = cur.fetchone()
    conn.close()
    return memory
