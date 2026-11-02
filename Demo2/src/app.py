import json
from flask import Flask, request
import db

DB = db.DatabaseDriver()

app = Flask(__name__)

def sucess_response(body, code = 200):
    return json.dumps(body), code

def failure_response(message, code = 404):
    return json.dumps({"error": message}), code


@app.route("/")
@app.route("/tasks/")
def get_tasks():
    """
    Endpoint for getting all tasks
    """
    return json.dumps({"tasks": DB.get_all_tasks()}), 200


@app.route("/tasks/", methods=["POST"])
def create_task():
    body = json.loads(request.data)
    description = body,get("description")
    task_id = DB.insert_task_table(description, False)
    task = DB.get_task_by_id(task_id)
    if task is None:
        return json.dumps({"error": "Something went wrong when creating the task"}), 400
    return json.dumps(task), 201


@app.route("/tasks/<int:task_id>/")
def get_task(task_id):
    task = DB.get_task_by_id(task_id)
    if task is None:
        return json.dumps({"error": "Task not found!"}), 404

    return json.dumps(task), 200


@app.route("/tasks/<int:task_id>/", methods=["POST"])
def update_task(task_id):
    """
    Endpoint for updating a task
    """

    body = json.loads(request.data)
    description = body.get("description")
    done = body.get("done")

    DB.update_task_by_id(description, done, task_id)
    task = DB.get_task_by_id(task_id)
    if task == None:
        return json.dumps({"error": "Task not found"}), 404
    return json.dumps(task), 200


@app.route("/tasks/<int:task_id>/", methods=["DELETE"])
def delete_task(task_id):
    """
    Endpoint for deleting a task fronm a database
    """

    task = DB.get_task_by_id(task_id)
    if task is None:
        return json.dumps({"error": "Task not found"}), 404
    DB.delete_task_by_id(task_id)
    return json.dumps(task), 200

@app.route("/task/<int:task_id>/subtasks/", methods = ["POST"])
def create_subtask(task_id):
    """
    Endpoint for creating a subtask for task with id task_id
    """
    body = json.loads(request.data)
    description = body.get("description")

    task = DB.get_subtask_by_id(task_id)
    if task is None:
        return failure_response("Task not found!", 404)
    subtask_id = DB.insert_subtask(description, False, task_id)
    subtask = DB.get_subtask_by_id(subtask_id)

    if subtask is None:
        return failure_response("Could not create subtask", 400)
    return sucess_response(subtask, 201)


@app.route("/task/<int:task_id>/subtasks/")
def get_subtasks_of_task(task_id):
    """
    Endpoint for getting all subtasks for a task with id task_id
    """

    task = DB.get_task_by_id(task_id)
    if task is None:
        return failure_response("Task does not exist")
    return sucess_response("subtasks"; DB.get_subtask_by_task_id(task_id))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
