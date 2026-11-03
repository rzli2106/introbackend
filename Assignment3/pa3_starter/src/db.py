import sqlite3
from datetime import datetime

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
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
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
        self.conn.commit()
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

    def transfer_money(self, sender_id, receiver_id, amount):
        """
        Using SQL, transfers money if the sender has enough funds.
        The calling method commits the changes.
        """
        cursor = self.conn.execute("""
            UPDATE users
            SET balance = balance - ?
            WHERE id = ? AND balance >= ?;
        """, (amount, sender_id, amount))

        if cursor.rowcount == 0:
            return False

        self.conn.execute("""
            UPDATE users
            SET balance = balance + ?
            WHERE id = ?;
        """, (amount, receiver_id))

        return True

    def insert_transaction_table(self, sender_id, receiver_id, amount, message, accepted):
        """
        Using SQL, adds a transaction and transfers money if accepted.
        Returns the transaction id, error message, and error status.
        """
        if self.get_user_by_id(sender_id) is None:
            return None, "Sender not found", 404

        if self.get_user_by_id(receiver_id) is None:
            return None, "Receiver not found", 404

        if sender_id == receiver_id:
            return None, "Sender and receiver must be different.", 400

        if accepted is True:
            if not self.transfer_money(sender_id, receiver_id, amount):
                return None, "Sender is broke", 403

        timestamp = datetime.utcnow().isoformat() + "Z"

        cursor = self.conn.execute("""
            INSERT INTO transactions (
                timestamp, sender_id, receiver_id,
                amount, message, accepted
            )
            VALUES (?, ?, ?, ?, ?, ?);
        """, (
            timestamp, sender_id, receiver_id,
            amount, message, accepted
        ))
        self.conn.commit()

        return cursor.lastrowid, None, None

    def update_transaction_by_id(self, id, accepted):
        """
        Using SQL accepts a transaction or returns error
        """
        transaction = self.get_transaction_by_id(id)

        if transaction is None:
            return "Transaction not found!", 404

        if transaction["accepted"] is not None:
            return ("Cannot change a transaction that has already been accepted or denied.",403)

        if accepted:
            sender_id = transaction["sender_id"]
            receiver_id = transaction["receiver_id"]
            amount = transaction["amount"]

            if self.get_user_by_id(sender_id) is None:
                return "No sender found", 404

            if self.get_user_by_id(receiver_id) is None:
                return "No reciever found", 404

            if not self.transfer_money(sender_id, receiver_id, amount):
                return "Sender is broke", 403

        timestamp = datetime.utcnow().isoformat() + "Z"

        self.conn.execute("""
            UPDATE transactions
            SET accepted = ?, timestamp = ?
            WHERE id = ?;
        """, (accepted, timestamp, id))
        self.conn.commit()

        return None, None

    def get_transaction_by_id(self, id):
        """
        Using SQL to get transaction by id
        """
        cursor = self.conn.execute(
            "SELECT * FROM transactions WHERE id = ?;", (id,)
        )

        for row in cursor:
            accepted = None if row[6] is None else bool(row[6])
            return {"id": row[0], "timestamp": row[1], "sender_id": row[2], "receiver_id": row[3], "amount": row[4], "message": row[5], "accepted": accepted}
        return None

    def get_transactions_by_user_id(self, user_id):
        """
        Using SQL to get all transactions where user is sender or receiver
        """
        cursor = self.conn.execute(
            "SELECT * FROM transactions WHERE sender_id = ? OR receiver_id = ?;", (user_id, user_id)
        )
        transactions = []

        for row in cursor:
            accepted = None if row[6] is None else bool(row[6])
            transactions.append({"id": row[0], "timestamp": row[1], "sender_id": row[2], "receiver_id": row[3], "amount": row[4], "message": row[5], "accepted": accepted})
        return transactions


# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)