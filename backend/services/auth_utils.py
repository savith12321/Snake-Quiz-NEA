from flask import request, jsonify
from functools import wraps
from datetime import datetime
from db import DatabaseManager

db = DatabaseManager()
db.delete_expired_tokens()

# check if there is a valid token
def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        # check if the user has provided a token
        if not token:
            return jsonify({"error": "Token is requred to access this data"}), 401

        token_row = db.get_token(token)
        # check if the user has provided a real token and it exsists in the database
        if not token_row:
            return jsonify({"error": "Invalid token"}), 401
        # check if token is expired
        if token_row["expires_at"] and token_row["expires_at"] < datetime.now().isoformat():
            db.delete_token(token)
            return jsonify({"error": "Token expired, Please try logging in again"}), 401

        return func(*args, **kwargs)
    return wrapper

# check if the token belongs to a admin user
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        token_row = db.get_token(token)
        print(token)
        # check if the token exsists
        if not token_row:
            return jsonify({"error": "Invalid token provided"}), 401
        # check if it is an admin token
        if token_row["role"] != "admin":
            return jsonify({"error": "Admin access required"}), 403

        return func(*args, **kwargs)
    return wrapper
