from datetime import datetime
import json

import db
from flask import Flask
from flask import request

DB = db.DatabaseDriver()

app = Flask(__name__)


def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


@app.route("/")
def hello_world():
    return "Hello world!"


# your routes here
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
    user_id = DB.insert_user_table(name, username, balance)
    user = DB.get_user_by_id(user_id)
    user["transactions"] = DB.get_transactions_by_user_id(user_id)
    return success_response(user, 201)


@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found")
    user["transactions"] = DB.get_transactions_by_user_id(user_id)
    return success_response(user)


@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found")
    user["transactions"] = DB.get_transactions_by_user_id(user_id)
    DB.delete_user_by_id(user_id)
    return success_response(user)


@app.route("/api/transactions/", methods=["POST"])
def create_transaction():
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")
    message = body.get("message")
    accepted = body.get("accepted")
    if sender_id is None or receiver_id is None or amount is None or message is None:
        return failure_response("sender_id, receiver_id, amount, and message are required", 400)
    if accepted is not None and accepted is not True:
        return failure_response("accepted must be true or null", 400)
    transaction_id, error, code = DB.insert_transaction_table(
        sender_id, receiver_id, amount, message, accepted
    )
    if error is not None:
        return failure_response(error, code)
    return success_response(DB.get_transaction_by_id(transaction_id), 201)


@app.route("/api/transactions/<int:transaction_id>/", methods=["POST"])
def update_transaction(transaction_id):
    body = json.loads(request.data)
    accepted = body.get("accepted")
    if accepted is not True and accepted is not False:
        return failure_response("accepted must be true or false", 400)

    error, code = DB.update_transaction_by_id(transaction_id, accepted)
    if error is not None:
        return failure_response(error, code)
    return success_response(DB.get_transaction_by_id(transaction_id))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
