from flask import Blueprint, jsonify, request
from datetime import datetime
from db import DatabaseManager
from models.Attempt import Attempt
from services.auth_utils import token_required, admin_required

attempt_bp = Blueprint("attempts", __name__)
db = DatabaseManager()

@attempt_bp.route("/attempts", methods=["POST"])
@token_required
def create_attempt():
    data = request.json

    attempt = Attempt(
        attempt_id=None,
        user_id=data["user_id"],
        snake_id=data["snake_id"],
        correct=data["correct"],
        timestamp=datetime.now().isoformat()
    )

    attempt_id = db.create_attempt(attempt)
    return jsonify({"attempt_id": attempt_id})


@attempt_bp.route("/attempts/<int:user_id>", methods=["GET"])
@token_required
def get_attempts(user_id):
    attempts = db.get_attempts_by_user(user_id)
    return jsonify([
        {
            "attempt_id": a.attempt_id,
            "snake_id": a.snake_id,
            "correct": bool(a.correct),
            "timestamp": a.timestamp
        }
        for a in attempts
    ])
