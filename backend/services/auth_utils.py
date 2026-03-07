from flask import request, jsonify
from functools import wraps
from datetime import datetime
from db import DatabaseManager

db = DatabaseManager()
db.delete_expired_tokens()

def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Unauthorized"}), 401

        token_row = db.get_token(token)
        if not token_row:
            return jsonify({"error": "Unauthorized"}), 401

        if token_row["expires_at"] and token_row["expires_at"] < datetime.now().isoformat():
            db.delete_token(token)
            return jsonify({"error": "Token expired"}), 401

        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        token_row = db.get_token(token)
        print(token)
        if not token_row:
            return jsonify({"error": "Unauthorized"}), 401

        if token_row["role"] != "admin":
            return jsonify({"error": "Admin access required"}), 403

        return func(*args, **kwargs)
    return wrapper
