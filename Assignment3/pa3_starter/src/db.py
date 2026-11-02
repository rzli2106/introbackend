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
    Database driver for the Venmo (Full) app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        """
        Secures a connection with the database and stores it into the
        instance variable `conn`
        """
        self.conn = sqlite3.connect("todo.db", check_same_thread=False)
        self.create_user_table()
        self.create_transaction_table()

    def create_user_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                balance INTEGER NOT NULL
            );
        """)
        self.conn.commit()

    def get_all_users(self):
        """
        Using SQL, gets all users in the user table
        """
        cursor = self.conn.execute("SELECT * FROM users;")
        users = []

        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2]})
        return users

    def insert_user_table(self, name, username, balance):
        """
        Using SQL, adds a new user in the user table
        """
        cursor = self.conn.execute("INSERT INTO users (name, username, balance) VALUES (?, ?, ?);", (name, username, balance))
        self.conn.commit()
        return cursor.lastrowid

    def get_user_by_id(self, id):
        """
        Using SQL to get user by id
        """
        cursor = self.conn.execute(
            "SELECT * FROM users WHERE id = ?;", (id,)
        )

        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2],"balance": row[3]}
        return None

    def delete_user_by_id(self, id):
        """
        Using SQL to delete user
        """
        self.conn.execute(
            "DELETE FROM users WHERE id = ?;", (id,)
        )
#Transactions
    def create_transaction_table(self):
        """
        Using SQL creates a transactions table
        """
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                message TEXT NOT NULL,
                accepted BOOLEAN,
                FOREIGN KEY(sender_id) REFERENCES users(id),
                FOREIGN KEY(receiver_id) REFERENCES users(id)
            );
        """)
        self.conn.commit()






# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)