import os
import sqlite3

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Venmo app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        """
        Secures a connection with the database and stores it into the instance variable 'conn'
        """
        self.conn = sqlite3.connect(
            "todo.db", check_same_thread=False
        )
        self.create_users_table()

    def create_users_table(self):
        """
        Using SQL, creates a users table
        """
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS task(
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        name TEXT NOT NULL,
                                        username TEXT NOT NULL,
                                        balance INT NOT NULL
        
        );
        """

                                    )

    def delete_users_table(self):
        """
        Using SQL, deletes the users table
        """
        self.conn.execute("DROP TABLE IF EXISTS users;")
        self.conn.commit()

    def get_all_users(self):
        """
        Using SQL, returns all users without their balances
        """
        cursor = self.conn.execute("SELECT id, name, username FROM users;")
        users = []
        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2]})
        return users

    def create_user(self, name, username, balance):
        """
        Using SQL, inserts a user into the users table
        """
        cursor = self.conn.execute(
            "INSERT INTO users (name, username, balance) VALUES (?, ?, ?);",
            (name, username, balance),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_user_by_id(self, user_id):
        """
        Using SQL, returns the user with the given id
        """
        cursor = self.conn.execute("SELECT * FROM users WHERE id = ?;", (user_id))
        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "balance": row[3]}
        return None

    def delete_user_by_id(self, user_id):
        """
        Using SQL, deletes the user with the given id
        """
        self.conn.execute("DELETE FROM users WHERE id = ?;", (user_id))
        self.conn.commit()

    def update_balance_by_id(self, user_id, balance):
        """
        Using SQL, sets the balance of the user with the given id
        """
        self.conn.execute(
            "UPDATE users SET balance = ? WHERE id = ?;", (balance, user_id)
        )
        self.conn.commit()


# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
