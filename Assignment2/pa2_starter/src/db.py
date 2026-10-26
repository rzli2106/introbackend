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
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        """
        Secures a connection with the database and stores it into the instance variable 'conn'

        """
        self.conn = sqlite3.connect(
            "todo.db", check_same_thread=False
        )

    def create_users_table(self):
        """
        Using SQL, creates a users table
        """

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        name TEXT NOT NULL,
                                        username TEXT NOT NULL
                                        balance INTEGER NOT NULL
        
        );
        """

                                    )

    def delete_users_table(self):
        """
        Using SQL, delete the task table
        """

        self.conn.execute("DROP TABLE IF EXISTS users;")

    def get_all_users(self):
        """
        Using SQL, return all tasks in a table
        """

        cursor = self.conn.execute("SELECT * FROM task;")
        users_no_balance = []
        for row in cursor:
            users_no_balance.append({"id": row[0], "name": row[1], "username": row[2]})
        return users_no_balance

    def create_user(self, name, username, balance):
        """
        Using SQL, inserts a task into a task table
        """

        cursor = self.conn.execute("INSERT INTO users (name, username, balance) VALUES (?,?,?);"), {name, username, balance}

        self.conn.commit()
        return cursor.lastrowid

    



# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
