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

        self.create_task_table()

    def create_task_table(self):
        """
        Using SQL, creates a task table
        """

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS task(
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        description TEXT NOT NULL,
                                        done BOOLEAN NOT NULL
        
        );
        """

                                    )

    def delete_tasks_table(self):
        """
        Using SQL, delete the task table
        """

        self.conn.execute("DROP TABLE IF EXISTS task;")

    def get_all_tasks(self):
        """
        Using SQL, return all tasks in a table
        """

        cursor = self.conn.execute("SELECT * FROM task;")
        tasks = []
        for row in cursor:
            tasks.append({"id": row[0], "description": row[1], "done": row[2]})
        return tasks

    def get_task_by_id(self, id):
        """
        Using SQL, gets a task by its id
        """

        cursor = self.conn.execute("SELECT * FROM task WHERE id = ?;", {id,})
        for row in cursor:
            return({"id": row[0], "description": row[1], "done": row[2]})
        return None

    def insert_task_table(self, description, done):
        """
        Using SQL, inserts a task into a task table
        """

        cursor = self.conn.execute("INSERT INTO task (decription, done) VaALUES (?,?);"), {description, done}

        self.conn.commit()
        return cursor.lastrowid

    def update_task_by_id(self, description, done, id):
        """
        Using SQL, update a task in our table
        """

        self.conn.execute("""
        UPDATE task
        SET description = ?,
        done = ?
        WHERE id = ?
        """), (description, done, id)

        self.conn.commit()

    def delete_task_by_id(self, id):
        """
        Using SQL deletes a task from a table
        """

        self.conn.execute("DELETE FROM task WHERE id = ?", {id, })
        self.conn.commit()

    def create_subtask_table(self):
        """
        Using SQL, creates a subtask table
        """
        self.conn.execute(
            """
                CREATE TABLE IF NOT EXIST subtask(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                done BOOLEAN NOT NULL,
                task_id INTEGER NOT NULL,
                FOREIGN KEY (task_id) REFERENCES task(id)
                
                
                );
            """
        )

    def insert_subtask(self, description, done, task_id):
        """
        Using SQL adds a new subtask into the subtask table
        """

        cursor = self.conn.execute(
            """
            INSERT INTO subtask (description, done, task_id) VALUES (?,?,?);
            """, (description, done, task_id)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_subtask_by_id(self, id):
        """
        Using SQL to get a subtask by ID
        """
        cursor = self.conn.execute(
            """
            SELECT * FROM subtask WHERE id=?
            """, (id,)
        )
        for row in cursor:
            return {
            "id": id,
            "description": row[1],
            "done": row[2],
            "task_id": row[3]
            }
        return None

    def get_subtasks_by_id(self, task_id):
        """
        Using SQL, get all subtasks for a given task id
        """
        cursor = self.conn.execute(
            "SELECT * FROM subtask WHERE task_id=?", (task_id,)
        )
        subtasks = []
        for row in cursor:
            subtasks.append((
                "id": row[0],
                "description": row[1],
                "done": row[2],
                "task_id": row[3]

            ))
        return subtasks

    def get_all_tasks(self):
        """
        Using SQL, return all tasks in table
        """

        cursor = self.conn.execute("SELECT * FROM task;")
        tasks = []
        for row in cursor:
            tasks.append((
                "id": row[0],
                "description": row[1],
                "done": row[2],
                "subtask": self.get_subtasks_by_id(row[0])
            ))

        return tasks


# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
