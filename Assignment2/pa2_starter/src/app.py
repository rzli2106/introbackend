from flask import Flask, jsonify, request
import db

DB = db.DatabaseDriver()
app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello world!"


def request_body():
    # The provided tests send JSON without a Content-Type header.
    body = request.get_json(force=True, silent=True)
    return body if isinstance(body, dict) else None


@app.route("/api/users/")
def get_users():
    return jsonify({"users": DB.get_all_users()}), 200


@app.route("/api/users/", methods=["POST"])
def create_user():
    body = request_body()
    if body is None:
        return jsonify({"error": "Request body must be a JSON object"}), 400
    for field in ("name", "username"):
        value = body.get(field)
        if not isinstance(value, str) or not value.strip():
            return jsonify({"error": field + " is required and must be a nonempty string"}), 400
    balance = body.get("balance", 0)
    if type(balance) is not int or not 0 <= balance <= 9223372036854775807:
        return jsonify({"error": "balance must be a nonnegative SQLite integer"}), 400
    user_id = DB.insert_user_table(body["name"], body["username"], balance)
    return jsonify(DB.get_user_by_id(user_id)), 201


@app.route("/api/user/<int:user_id>/")
def get_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200


@app.route("/api/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    user = DB.delete_user_by_id(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200


@app.route("/api/send/", methods=["POST"])
def send_money():
    body = request_body()
    if body is None:
        return jsonify({"error": "Request body must be a JSON object"}), 400
    for field in ("sender_id", "receiver_id", "amount"):
        if body.get(field) is None:
            return jsonify({"error": field + " is required"}), 400
        if type(body[field]) is not int or not 0 <= body[field] <= 9223372036854775807:
            return jsonify({"error": field + " must be a nonnegative SQLite integer"}), 400
    result = DB.send_money(body["sender_id"], body["receiver_id"], body["amount"])
    if result is not None:
        message, status = result
        return jsonify({"error": message}), status
    return jsonify({field: body[field] for field in ("sender_id", "receiver_id", "amount")}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
