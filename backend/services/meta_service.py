from flask import Blueprint, jsonify

meta_bp = Blueprint("meta", __name__)

@meta_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200
