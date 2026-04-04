from flask import Blueprint, jsonify, request
from datetime import datetime
from db import DatabaseManager
from models.User import User
from services.auth_utils import token_required, admin_required
from werkzeug.security import generate_password_hash
user_bp = Blueprint("users", __name__)
db = DatabaseManager()

@user_bp.route("/users", methods=["POST"])
#@admin_required
def create_user():
    data = request.json
    password_hash = generate_password_hash(data["password"])
    user = User(
        user_id=None,
        username=data["username"],
        role = data["role"],
        password_hash=password_hash,
        created_at=datetime.now().isoformat()
    )

    user_id = db.create_user(user)
    return jsonify({"user_id": user_id}), 200


@user_bp.route("/users/<string:username>", methods=["GET"])
@admin_required
def get_user(username):
    user = db.get_user_by_username(username)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user_id": user.user_id,
        "username": user.username,
        "created_at": user.created_at
    }), 200
