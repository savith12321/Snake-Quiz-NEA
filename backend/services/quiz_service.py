from flask import Blueprint, jsonify, request
from db import DatabaseManager
from services.auth_utils import token_required, admin_required
import base64
import random
from algorithms.exp_calculation import calc_exp
quiz_bp = Blueprint("quiz", __name__)
db = DatabaseManager()


# ======================
# GET a random question with 4 choices
# ======================
@quiz_bp.route("/quiz/question", methods=["GET"])
@token_required
def get_question():
    """
    Optional query param: ?type=identify_by_image
    Returns a random question with 4 shuffled answer choices.
    """
    question_type = request.args.get("type")
    difficulty = request.args.get("difficulty", type=int)
    row = db.get_random_question(question_type, difficulty)

    if not row:
        return jsonify({"error": "No questions available"}), 404

    correct_answer = db.get_correct_answer(row["question_id"])
    if not correct_answer:
        return jsonify({"error": "Question has no correct answer set"}), 500

    wrong_answers = db.get_wrong_answers(row["question_type"], row["snake_id"], correct_answer["answer_text"])
    if len(wrong_answers) < 3:
        return jsonify({"error": "Not enough questions of this type to generate choices"}), 400

    choices = [
        {"answer_id": correct_answer["answer_id"], "answer_text": correct_answer["answer_text"]}
    ] + [
        {"answer_id": w["answer_id"], "answer_text": w["answer_text"]} for w in wrong_answers
    ]
    random.shuffle(choices)

    images = []
    if row["question_type"] == "identify_by_image":
        images = _encode_images(db.get_snake_images(row["snake_id"]))

    return jsonify({
        "question_id": row["question_id"],
        "question_type": row["question_type"],
        "question_text": row["question_text"],
        "snake_id": row["snake_id"],
        "images": images,
        "snake_description": row["description"] if row["question_type"] == "identify_by_description" else None,
        "choices": choices,
        "correct_answer_id": correct_answer["answer_id"]
    })


def _encode_images(images):
    result = []
    for img in images:
        data = img.get("image_data")
        if data:
            result.append({
                "image_id": img.get("image_id"),
                "is_primary": img.get("is_primary"),
                "image_base64": base64.b64encode(data).decode("utf-8")
            })
    return result


# ======================
# POST submit an answer
# ======================
@quiz_bp.route("/quiz/answer", methods=["POST"])
@token_required
def submit_answer():
    data = request.json
    if "question_id" not in data or  "answer_id" not in data:
        return jsonify({"error": "Invalid question or answer"}), 400
    question = db.get_question_by_id(data["question_id"])
    answer = db.get_answer(data["answer_id"])

    if not question or not answer:
        return jsonify({"error": "Invalid question or answer"}), 400

    correct_answer = db.get_correct_answer(data["question_id"])
    correct = (data["answer_id"] == correct_answer["answer_id"])
    if "quiz_id" in data and "user_id" in data:
        attempt_id = db.create_quiz_attempt(
            user_id=data["user_id"],
            snake_id=question["snake_id"],
            question_id=data["question_id"],
            answer_id=data["answer_id"],
            correct=correct,
            quiz_id=data.get("quiz_id")
        )

        return jsonify({
            "attempt_id": attempt_id,
            "correct": correct,
            "correct_answer_id": correct_answer["answer_id"],
            "correct_answer_text": correct_answer["answer_text"]
        })
    else:
        return jsonify({
            "correct": correct,
            "correct_answer_id": correct_answer["answer_id"],
            "correct_answer_text": correct_answer["answer_text"]
        })


# ======================
# POST start a quiz session
# ======================
@quiz_bp.route("/quiz/start", methods=["POST"])
@token_required
def start_quiz():
    """
    { "user_id": 1 }
    Creates a new quiz session and returns the quiz_id.
    """
    data = request.json
    quiz_id = db.create_quiz(data["user_id"])
    return jsonify({"quiz_id": quiz_id}), 201


# ======================
# POST finish a quiz session
# ======================
@quiz_bp.route("/quiz/<int:quiz_id>/finish", methods=["POST"])
@token_required
def finish_quiz(quiz_id):
    """
    Calculates the score from the attempts linked to this quiz.
    """
    quiz = db.get_quiz(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    score = db.finish_quiz(quiz_id)
    new_quiz = db.get_quiz(quiz_id)
    user_id = new_quiz["user_id"]
    started_at = new_quiz["started_at"]
    completed_at = new_quiz["completed_at"]
    diff_sum = db.get_quiz_difficulty_sum(quiz_id)
    db.add_exp(user_id, calc_exp(started_at, completed_at, score, diff_sum))
    return jsonify({
        "quiz_id": quiz_id,
        "score": score,
        "total": quiz["total"],
        "message": f"You scored {score} out of {quiz['total']}"
    })


# ======================
# GET all attempts for a quiz
# ======================
@quiz_bp.route("/quiz/<int:quiz_id>/attempts", methods=["GET"])
@token_required
def get_quiz_attempts(quiz_id):
    attempts = db.get_attempts_for_quiz(quiz_id)
    return jsonify([
        {
            "attempt_id": a["attempt_id"],
            "correct": bool(a["correct"]),
            "timestamp": a["timestamp"],
            "snake": a["common_name"],
            "question_type": a["question_type"],
            "question_text": a["question_text"],
            "chosen_answer": a["chosen_answer"]
        }
        for a in attempts
    ])


# ======================
# GET all past quiz sessions for a user
# ======================
@quiz_bp.route("/quiz/sessions/<int:user_id>", methods=["GET"])
@token_required
def get_quiz_sessions(user_id):
    quizzes = db.get_quiz_history_by_user(user_id)
    return jsonify([
        {
            "quiz_id": q["quiz_id"],
            "score": q["score"],
            "total": q["total"],
            "started_at": q["started_at"],
            "completed_at": q["completed_at"],
            "q_num": len(db.get_attempts_for_quiz(q["quiz_id"])),
            "last_diff": (db.get_attempts_for_quiz_last(q["quiz_id"])["difficulty"] if db.get_attempts_for_quiz_last(q["quiz_id"]) != None else 1) 
            - (1 if (db.get_attempts_for_quiz_last(q["quiz_id"]) != None and db.get_attempts_for_quiz_last(q["quiz_id"])["correct"] == 0) else 0)
        }
        for q in quizzes
    ])


# ======================
# GET full attempt history for a user (all time, not per quiz)
# ======================
@quiz_bp.route("/quiz/history/<int:user_id>", methods=["GET"])
@token_required
def get_quiz_history(user_id):
    rows = db.get_quiz_history(user_id)
    return jsonify([
        {
            "attempt_id": r["attempt_id"],
            "correct": bool(r["correct"]),
            "timestamp": r["timestamp"],
            "snake": r["common_name"],
            "snake_id": r["snake_id"],
            "question_type": r["question_type"],
            "question_text": r["question_text"],
            "chosen_answer": r["chosen_answer"]
        }
        for r in rows
    ])


# ======================
# ADMIN: Create a question
# ======================
@quiz_bp.route("/quiz/questions", methods=["POST"])
@admin_required
def create_question():
    """
    {
        "snake_id": 3,
        "question_type": "identify_by_image",
        "question_text": "What snake is this?",
        "correct_answer": "Spectacled Cobra",
        "difficulty": 2
    }
    """
    data = request.json
    question_id = db.create_question(
        snake_id=data["snake_id"],
        question_type=data["question_type"],
        question_text=data.get("question_text"),
        correct_answer=data["correct_answer"],
        difficulty=data.get("difficulty", 1)
    )
    return jsonify({"question_id": question_id}), 201


# ======================
# ADMIN: Get all questions
# ======================
@quiz_bp.route("/quiz/questions", methods=["GET"])
@admin_required
def get_all_questions():
    rows = db.get_all_questions()
    return jsonify([
        {
            "question_id": r["question_id"],
            "question_type": r["question_type"],
            "question_text": r["question_text"],
            "difficulty": r["difficulty"],
            "created_at": r["created_at"],
            "snake": r["common_name"],
            "snake_id": r["snake_id"]
        }
        for r in rows
    ])


# ======================
# ADMIN: Delete a question
# ======================
@quiz_bp.route("/quiz/questions/<int:question_id>", methods=["DELETE"])
@admin_required
def delete_question(question_id):
    db.delete_question(question_id)
    return jsonify({"status": "deleted"}), 200

@quiz_bp.route("/quiz/attempts/<int:quiz_id>", methods=["DELETE"])
@token_required
def delete_quiz_session(quiz_id):
    token = request.headers.get("Authorization")
    token_row = db.get_token(token)

    quiz = db.get_quiz(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    if token_row["role"] != "admin" and quiz["user_id"] != token_row["user_id"]:
        return jsonify({"error": "Forbidden"}), 403

    db.delete_quiz(quiz_id)
    return jsonify({"status": "deleted"}), 200