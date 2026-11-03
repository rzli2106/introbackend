from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# implement database model classes
class Task(db.Model):
    """
    Task model
    Has a one-to-many relationship with the Subtask Model
    Has a many-to-many relationship with the Category model

    """

    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String, nullable=False)
    done = db.Column(db.Boolean, nullabe = False)

    def __init__(self, **kwargs):
        """
        Initialize Task object/entry
        """ 
        self.description = kwargs.get("description", "")
        self.done = kwargs.get("done", False)

    def serialize(self):
        """
        Serialize a task object
        """
        return {
            "id" : self.id,
            "description" : self.description,
            "done" : self.done,
        }

class Subtask(db.Model):
    """
    Subtask model
    """

    __tablename__ = "subtasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String, nullable = False)
    done = db.Column(db.Boolean, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("task_id"), nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize Subtask object
        """
        self.description = kwargs.get("description", "")
        self.done = kwargs.get("done", False)
        self.task_id = kwargs.get("task_id")


    def serialize(self):
        """
        Serialize a Subtask object
        """

        return {
            "id" : self.id,
            "description" : self.description,
            "done" : self.done,
            "task_id" : self.task_id
        }
    