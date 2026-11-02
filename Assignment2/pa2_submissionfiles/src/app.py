import json
from flask import Flask, request
import db

DB = db.DatabaseDriver()

app = Flask(__name__)


def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


@app.route("/")
def hello_world():
    return "Hello world!"


@app.route("/api/users/")
def get_users():
    return success_response({"users": DB.get_all_users()})


@app.route("/api/users/", methods=["POST"])
def create_user():
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    balance = body.get("balance", 0)
    if name is None or username is None:
        return failure_response("Name and username are required", 400)
    user_id = DB.create_user(name, username, balance)
    return success_response(DB.get_user_by_id(user_id), 201)


@app.route("/api/user/<int:user_id>/")
def get_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found")
    return success_response(user)


@app.route("/api/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found")
    DB.delete_user_by_id(user_id)
    return success_response(user)


@app.route("/api/send/", methods=["POST"])
def send_money():
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")
    if sender_id is None or receiver_id is None or amount is None:
        return failure_response("sender_id, receiver_id, and amount are required", 400)

    sender = DB.get_user_by_id(sender_id)
    receiver = DB.get_user_by_id(receiver_id)
    if sender is None or receiver is None:
        return failure_response("Sender or receiver not found")
    if amount > sender["balance"]:
        return failure_response("Sender does not have enough money", 400)

    DB.update_balance_by_id(sender_id, sender["balance"] - amount)
    DB.update_balance_by_id(receiver_id, receiver["balance"] + amount)
    return success_response(
        {"sender_id": sender_id, "receiver_id": receiver_id, "amount": amount}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
