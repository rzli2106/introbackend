from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table = db.Table(
    "association",
    db.Model.metadata, 
    db.Column("task_id", db.Integer)

)


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
    subtasks = db.relationship("Subtask", cascade="delete")
    categories = db.relationship("Category", secondary=association_table, back_populates = "tasks")


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
            "subtasks": [s.serialize() for s in self.subtasks],
            "categories": [c.simpleserialize() for c in self.categories]
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

class Category(db.Model):
    """
    Category Model
    """
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    description = db.Column(db.String, nullable = False)
    color = db.Column(db.String, nullable = False)
    tasks = db.Relationship("Task", secondary = association_table, backpopulates="categories")

    def __init__ (self, **kwargs):
        """
        Initializes a category object
        """
        self.description = kwargs.get("description", "")
        self.color = kwargs.get("color", "")

    def serialize(self):
        """
        Serializes a Category object
        """
        return {
            "id": self.id,
            "description": self.description,
            "color": self.color,
            "tasks": [t.serialize() for t in self.tasks]
        }

    def simple_serialize(self):
        """
        Serializes a Category object
        """
        return {
            "id": self.id,
            "description": self.description,
            "color": self.color
        }