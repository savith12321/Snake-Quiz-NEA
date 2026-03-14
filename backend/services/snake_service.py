from flask import Blueprint, jsonify, request
from db import DatabaseManager
from models.Snake import Snake
from services.auth_utils import token_required, admin_required
import base64
import os

snake_bp = Blueprint("snakes", __name__)
db = DatabaseManager()

# ======================
# Path to default image
# ======================
DEFAULT_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../data/images/default.png")
os.makedirs(os.path.dirname(DEFAULT_IMAGE_PATH), exist_ok=True)
if not os.path.exists(DEFAULT_IMAGE_PATH):
    # Create empty default if missing
    with open(DEFAULT_IMAGE_PATH, "wb") as f:
        f.write(b"")


# ======================
# Helper to encode image bytes
# ======================
def encode_image(img_bytes):
    """
    Takes image bytes and returns a base64 string.
    If img_bytes is None, loads default.png
    """
    if img_bytes is None:
        with open(DEFAULT_IMAGE_PATH, "rb") as f:
            img_bytes = f.read()
    return base64.b64encode(img_bytes).decode("utf-8")


# ======================
# GET all snakes
# ======================
@snake_bp.route("/snakes", methods=["GET"])
#@token_required
def get_all_snakes():
    snakes = db.get_all_snakes()
    result = []

    for s in snakes:
        images = db.get_snake_images(s.snake_id)
        if not images:
            images = [{"image_id": None, "file_path": DEFAULT_IMAGE_PATH, "is_primary": True, "image_data": None}]
        result.append({
            "snake_id": s.snake_id,
            "common_name": s.common_name,
            "scientific_name": s.scientific_name,
            "venom_level": s.venom_level,
            "description": s.description,
            "images": [
                {
                    "image_id": img.get("image_id"),
                    "file_path": img.get("file_path", DEFAULT_IMAGE_PATH),
                    "is_primary": img.get("is_primary", True),
                    "image_base64": encode_image(img.get("image_data"))
                }
                for img in images
            ]
        })
    return jsonify(result)


# ======================
# GET single snake
# ======================
@snake_bp.route("/snakes/<int:snake_id>", methods=["GET"])
@token_required
def get_snake(snake_id):
    snake = db.get_snake_by_id(snake_id)
    if not snake:
        return jsonify({"error": "Snake not found"}), 404

    images = db.get_snake_images(snake_id)
    if not images:
        images = [{"image_id": None, "file_path": DEFAULT_IMAGE_PATH, "is_primary": True, "image_data": None}]

    return jsonify({
        "snake_id": snake.snake_id,
        "common_name": snake.common_name,
        "scientific_name": snake.scientific_name,
        "venom_level": snake.venom_level,
        "description": snake.description,
        "images": [
            {
                "image_id": img.get("image_id"),
                "file_path": img.get("file_path", DEFAULT_IMAGE_PATH),
                "is_primary": img.get("is_primary", True),
                "image_base64": encode_image(img.get("image_data"))
            }
            for img in images
        ]
    })


# ======================
# CREATE snake with images
# ======================
@snake_bp.route("/snakes", methods=["POST"])
@admin_required
def create_snake():
    """
    Expects JSON:
    {
        "common_name": "Cobra",
        "scientific_name": "Naja naja",
        "venom_level": "high",
        "description": "Deadly snake",
        "images": [
            {
                "image_base64": "iVBORw0KGgoAAAANS..."
            }
        ]
    }
    """
    data = request.json

    snake = Snake(
        snake_id=None,
        common_name=data["common_name"],
        scientific_name=data["scientific_name"],
        venom_level=data["venom_level"],
        description=data.get("description")
    )

    # Prepare images safely as bytes only
    images = []
    for img in data.get("images", []):
        image_b64 = img.get("image_base64")
        if image_b64:
            images.append(base64.b64decode(image_b64))

    # Add snake + images
    snake_id = db.add_snake(snake, images=images)
    return jsonify({"snake_id": snake_id}), 201


# ======================
# UPDATE snake
# ======================
@snake_bp.route("/snakes/<int:snake_id>", methods=["PUT"])
@admin_required
def update_snake(snake_id):
    data = request.json
    snake = db.get_snake_by_id(snake_id)

    if not snake:
        return jsonify({"error": "Snake not found"}), 404

    snake.common_name = data["common_name"]
    snake.scientific_name = data["scientific_name"]
    snake.venom_level = data["venom_level"]
    snake.description = data.get("description")

    db.update_snake(snake)
    return jsonify({"status": "updated"})


# ======================
# DELETE snake
# ======================
@snake_bp.route("/snakes/<int:snake_id>", methods=["DELETE"])
@admin_required
def delete_snake(snake_id):     
    snake = db.get_snake_by_id(snake_id)

    if not snake:
        return jsonify({"error": "Snake not found"}), 404

    db.delete_snake(snake_id)
    return jsonify({"status": "deleted"}), 200

# ======================
# ADD images to existing snake
# ======================
@snake_bp.route("/snakes/<int:snake_id>/images", methods=["POST"])
@admin_required
def add_snake_images(snake_id):
    """
    Expects JSON:
    {
        "images": [
            { "image_base64": "iVBORw0KGgo..." },
            ...
        ]
    }
    Returns a list of newly created image_ids.
    """
    if not db.get_snake_by_id(snake_id):
        return jsonify({"error": "Snake not found"}), 404

    data = request.json
    image_ids = []

    for img in data.get("images", []):
        image_b64 = img.get("image_base64")
        if image_b64:
            img_bytes = base64.b64decode(image_b64)
            image_id = db.add_snake_image(snake_id, img_bytes)
            image_ids.append(image_id)

    if not image_ids:
        return jsonify({"error": "No valid images provided"}), 400

    return jsonify({"image_ids": image_ids}), 201


# ======================
# SET primary image
# ======================
@snake_bp.route("/snakes/<int:snake_id>/images/<int:image_id>/primary", methods=["PUT"])
@admin_required
def set_primary_image(snake_id, image_id):
    """
    Marks the given image as the primary image for the snake.
    All other images for the snake are demoted to non-primary.
    """
    if not db.get_snake_by_id(snake_id):
        return jsonify({"error": "Snake not found"}), 404

    success = db.set_primary_snake_image(image_id)
    if not success:
        return jsonify({"error": "Image not found"}), 404

    return jsonify({"status": "primary image updated"}), 200


# ======================
# DELETE a single image
# ======================
@snake_bp.route("/snakes/<int:snake_id>/images/<int:image_id>", methods=["DELETE"])
@admin_required
def delete_snake_image(snake_id, image_id):
    """
    Deletes a specific image by image_id.
    Refuses if it is the only image for the snake (to avoid an imageless snake).
    """
    if not db.get_snake_by_id(snake_id):
        return jsonify({"error": "Snake not found"}), 404

    images = db.get_snake_images(snake_id)
    real_images = [img for img in images if img["image_id"] is not None]

    if len(real_images) <= 1:
        return jsonify({"error": "Cannot delete the only image. Add another image first."}), 400

    success = db.delete_snake_image(image_id)
    if not success:
        return jsonify({"error": "Image not found"}), 404

    return jsonify({"status": "image deleted"}), 200

# ======================
# GET images for a snake
# ======================
@snake_bp.route("/snakes/<int:snake_id>/images", methods=["GET"])
@token_required
def get_snake_images(snake_id):
    """
    Returns all images for a snake as a list of base64-encoded objects.
    {
        "images": [
            {
                "image_id": 1,
                "is_primary": true,
                "image_base64": "iVBORw0KGgo..."
            },
            ...
        ]
    }
    """
    if not db.get_snake_by_id(snake_id):
        return jsonify({"error": "Snake not found"}), 404

    images = db.get_snake_images(snake_id)

    return jsonify({
        "images": [
            {
                "image_id": img.get("image_id"),
                "is_primary": img.get("is_primary", False),
                "image_base64": encode_image(img.get("image_data"))
            }
            for img in images
        ]
    }), 200