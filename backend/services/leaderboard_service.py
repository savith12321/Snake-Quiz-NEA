from flask import Blueprint, jsonify
from db import DatabaseManager
from services.auth_utils import token_required

leaderboard_bp = Blueprint("leaderboard", __name__)
db = DatabaseManager()


def merge_sort(users):
    if len(users) <= 1:
        return users

    mid = len(users) // 2
    left = merge_sort(users[:mid])
    right = merge_sort(users[mid:])

    return merge(left, right)


def merge(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i]["exp"] >= right[j]["exp"]:  # descending
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


@leaderboard_bp.route("/leaderboard", methods=["GET"])
@token_required
def get_leaderboard():
    users = db.get_all_users_exp()
    sorted_users = merge_sort(users)

    return jsonify([
        {"rank": i + 1, "username": u["username"], "exp": u["exp"]}
        for i, u in enumerate(sorted_users)
    ]), 200