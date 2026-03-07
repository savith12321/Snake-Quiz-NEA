from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from services.auth_utils import token_required
import secrets

from db import DatabaseManager
from models.User import User

auth_bp = Blueprint("auth", __name__)
db = DatabaseManager()


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.json

    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Missing fields"}), 400

    password_hash = generate_password_hash(data["password"])

    user = User(
        user_id=None,
        username=data["username"],
        password_hash=password_hash,
        role="user",
        created_at=datetime.now().isoformat()
    )

    user_id = db.create_user(user)

    if user_id is None:
        return jsonify({"error": "Username already exists"}), 409

    return jsonify({"user_id": user_id}), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    user = db.get_user_by_username(data.get("username"))

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not check_password_hash(user.password_hash, data.get("password")):
        return jsonify({"error": "Invalid credentials"}), 401

    token = secrets.token_hex(16)
    expires_at = (datetime.now() + timedelta(hours=2)).isoformat()

    db.create_token(
        token=token,
        user_id=user.user_id,
        role=user.role,
        expires_at=expires_at
    )

    return jsonify({
        "token": token,
        "expires_at": expires_at,
        "role": user.role
    })


@auth_bp.route("/auth/logout", methods=["POST"])
@token_required
def logout():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "Missing token"}), 400
    print(token)
    db.delete_token(token)
    return jsonify({"status": "logged out"})
