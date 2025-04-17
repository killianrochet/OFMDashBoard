import sqlite3
from typing import List, Tuple, Optional

try:
    from flask import g, has_app_context
except ImportError:
    g = None
    has_app_context = lambda: False

DB_PATH = "devices.db"

class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = self.get_connection(raw=True)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            model TEXT NOT NULL,
            status TEXT DEFAULT 'inactive',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            device_id TEXT UNIQUE,
            platform_version TEXT
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            scheduled_time TEXT NOT NULL,
            media_path TEXT NOT NULL,
            caption TEXT NOT NULL,
            post_type TEXT NOT NULL,
            account TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            device_id TEXT NOT NULL,
            is_active INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices(device_id)
        )
        ''')
        conn.commit()
        conn.close()

    def get_connection(self, raw: bool = False):
        if has_app_context() and not raw:
            if 'db_conn' not in g:
                g.db_conn = sqlite3.connect(self.db_path, check_same_thread=False)
            return g.db_conn
        else:
            return sqlite3.connect(self.db_path, check_same_thread=False)

    def close_connection(self, error=None):
        if has_app_context() and 'db_conn' in g:
            g.db_conn.close()

    def get_device_by_id(self, device_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
        return cursor.fetchone()

    def insert_device(self, name, model, device_id, platform_version):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO devices (name, model, device_id, platform_version) VALUES (?, ?, ?, ?)",
            (name, model, device_id, platform_version)
        )
        conn.commit()
        return cursor.lastrowid

    def get_devices(self) -> List[Tuple]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devices')
        return cursor.fetchall()

    def delete_device(self, device_id: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM devices WHERE id = ?', (device_id,))
        conn.commit()

    def update_device_status(self, device_id: int, status: str) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE devices SET status = ? WHERE id = ?', (status, device_id))
        conn.commit()

    def add_post(self, device_id: int, scheduled_time: str, media_path: str,
                caption: str, post_type: str, account: str) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO posts (device_id, scheduled_time, media_path, caption, post_type, account)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (device_id, scheduled_time, media_path, caption, post_type, account))
        conn.commit()
        return cursor.lastrowid

    def get_pending_posts(self, device_id: Optional[int] = None) -> List[Tuple]:
        conn = self.get_connection()
        cursor = conn.cursor()
        if device_id:
            cursor.execute('''
                SELECT * FROM posts 
                WHERE device_id = ? AND status = 'pending'
                ORDER BY scheduled_time ASC
            ''', (device_id,))
        else:
            cursor.execute('''
                SELECT * FROM posts 
                WHERE status = 'pending'
                ORDER BY scheduled_time ASC
            ''')
        return cursor.fetchall()

    def get_all_posts(self, device_id: Optional[int] = None) -> List[Tuple]:
        conn = self.get_connection()
        cursor = conn.cursor()
        if device_id:
            cursor.execute('''
                SELECT * FROM posts 
                WHERE device_id = ?
                ORDER BY scheduled_time ASC
            ''', (device_id,))
        else:
            cursor.execute('''
                SELECT * FROM posts 
                ORDER BY scheduled_time ASC
            ''')
        return cursor.fetchall()

    def update_post_status(self, post_id: int, status: str) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE posts SET status = ? WHERE id = ?', (status, post_id))
        conn.commit()


    def insert_account(self, device_id, username):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO accounts (device_id, username)
                VALUES (?, ?)
            """, (device_id, username))
            conn.commit()

    def insert_accounts_for_device(self, device_id: str, usernames: List[str]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for username in usernames:
                cursor.execute("""
                    INSERT OR IGNORE INTO accounts (device_id, username)
                    VALUES (?, ?)
                """, (device_id, username))
            conn.commit()

    def get_accounts_by_device(self, device_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username FROM accounts WHERE device_id = ?
            """, (device_id,))
            return [row[0] for row in cursor.fetchall()]

    def set_active_account(self, device_id: str, username: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE accounts SET is_active = 0 WHERE device_id = ?", (device_id,))
            cursor.execute("""
                UPDATE accounts SET is_active = 1
                WHERE device_id = ? AND username = ?
            """, (device_id, username))
            conn.commit()

    def get_active_account(self, device_id: str) -> Optional[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username FROM accounts WHERE device_id = ? AND is_active = 1
            """, (device_id,))
            row = cursor.fetchone()
            return row[0] if row else None