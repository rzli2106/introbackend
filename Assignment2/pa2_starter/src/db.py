import sqlite3
from threading import RLock


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """Read and write users in the SQLite database."""

    def __init__(self):
        self.conn = sqlite3.connect("todo.db", check_same_thread=False)
        self.lock = RLock()
        self.create_users_table()

    def create_users_table(self):
        with self.lock, self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    balance INTEGER NOT NULL DEFAULT 0
                );
            """)

    def delete_users_table(self):
        with self.lock, self.conn:
            self.conn.execute("DROP TABLE IF EXISTS users;")

    def get_all_users(self):
        # Select only public fields so balances cannot leak into the response.
        with self.lock:
            rows = self.conn.execute(
                "SELECT id, name, username FROM users ORDER BY id;"
            ).fetchall()
        return [dict(zip(("id", "name", "username"), row)) for row in rows]

    def get_user_by_id(self, user_id):
        with self.lock:
            row = self.conn.execute(
                "SELECT id, name, username, balance FROM users WHERE id = ?;",
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        return dict(zip(("id", "name", "username", "balance"), row))

    def insert_user_table(self, name, username, balance=0):
        with self.lock, self.conn:
            cursor = self.conn.execute(
                "INSERT INTO users (name, username, balance) VALUES (?, ?, ?);",
                (name, username, balance),
            )
            return cursor.lastrowid

    def delete_user_by_id(self, user_id):
        with self.lock, self.conn:
            user = self.get_user_by_id(user_id)
            if user is not None:
                self.conn.execute("DELETE FROM users WHERE id = ?;", (user_id,))
            return user

    def send_money(self, sender_id, receiver_id, amount):
        """Check balances and transfer money in one transaction."""
        with self.lock, self.conn:
            # Acquire the SQLite write lock before checking either account.
            self.conn.execute("BEGIN IMMEDIATE;")
            if self.get_user_by_id(sender_id) is None:
                return "Sender not found", 404
            if self.get_user_by_id(receiver_id) is None:
                return "Receiver not found", 404
            cursor = self.conn.execute(
                "UPDATE users SET balance = balance - ? "
                "WHERE id = ? AND balance >= ?;",
                (amount, sender_id, amount),
            )
            if cursor.rowcount == 0:
                return "Insufficient balance", 400
            self.conn.execute(
                "UPDATE users SET balance = balance + ? WHERE id = ?;",
                (amount, receiver_id),
            )
        return None


DatabaseDriver = singleton(DatabaseDriver)
