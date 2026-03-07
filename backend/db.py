import sqlite3
import os
from datetime import datetime

from models.Snake import Snake
from models.Feature import Feature
from models.Region import Region
from models.Attempt import Attempt
from models.User import User


class DatabaseManager:
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    IMAGE_DIR = os.path.join(script_dir, "data", "images")

    def __init__(self, db_name="data/data.db"):
        # Get script directory
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        self.db_name = os.path.join(script_dir, db_name)

        # Ensure images directory exists
        os.makedirs(self.IMAGE_DIR, exist_ok=True)

        # Apply schema at startup
        self.apply_schema()

        # Delete expired tokens at startup
        self.delete_expired_tokens()

    # ======================
    # Connection
    # ======================
    def get_connection(self):
        conn = sqlite3.connect(
            self.db_name,
            timeout=10,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    # ======================
    # Apply schema from file
    # ======================
    def apply_schema(self):
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if not os.path.exists(schema_path):
            print(f"Warning: schema.sql not found at {schema_path}")
            return

        with self.get_connection() as conn, open(schema_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
            conn.executescript(sql_script)

    # ======================
    # Snake methods
    # ======================
    def add_snake(self, snake: Snake, images=None):
        """
        Adds a snake to the DB.
        images: list of bytes objects
        """
        with self.get_connection() as conn:
            cur = conn.execute("""
                INSERT INTO Snake (common_name, scientific_name, venom_level, description)
                VALUES (?, ?, ?, ?)
            """, (
                snake.common_name,
                snake.scientific_name,
                snake.venom_level,
                snake.description
            ))
            snake_id = cur.lastrowid

        # Save images if provided
        if images:
            for i, img_bytes in enumerate(images):
                self.add_snake_image(
                    snake_id=snake_id,
                    image_bytes=img_bytes,
                    is_primary=(i == 0)
                )

        return snake_id

    def update_snake(self, snake: Snake):
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE Snake
                SET common_name = ?, scientific_name = ?, venom_level = ?, description = ?
                WHERE snake_id = ?
            """, (
                snake.common_name,
                snake.scientific_name,
                snake.venom_level,
                snake.description,
                snake.snake_id
            ))

    def delete_snake(self, snake_id):
        # Delete associated images from disk
        images = self.get_snake_images(snake_id)
        for img in images:
            if img["image_id"]:
                try:
                    os.remove(img["file_path"])
                except FileNotFoundError:
                    pass

        with self.get_connection() as conn:
            conn.execute("DELETE FROM SnakeFeature WHERE snake_id = ?", (snake_id,))
            conn.execute("DELETE FROM SnakeRegion WHERE snake_id = ?", (snake_id,))
            conn.execute("DELETE FROM SnakeImage WHERE snake_id = ?", (snake_id,))
            conn.execute("DELETE FROM Snake WHERE snake_id = ?", (snake_id,))

    def get_snake_by_id(self, snake_id):
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM Snake WHERE snake_id = ?",
                (snake_id,)
            ).fetchone()
        if not row:
            return None
        return Snake(
            snake_id=row["snake_id"],
            common_name=row["common_name"],
            scientific_name=row["scientific_name"],
            venom_level=row["venom_level"],
            description=row["description"]
        )

    def get_all_snakes(self):
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM Snake").fetchall()
        return [
            Snake(
                snake_id=row["snake_id"],
                common_name=row["common_name"],
                scientific_name=row["scientific_name"],
                venom_level=row["venom_level"],
                description=row["description"]
            )
            for row in rows
        ]

    # ======================
    # Feature & Region
    # ======================
    def get_all_features(self):
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM Feature").fetchall()
        return [Feature(row["feature_id"], row["name"], row["description"]) for row in rows]

    def get_all_regions(self):
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM Region").fetchall()
        return [Region(row["region_id"], row["name"]) for row in rows]

    # ======================
    # Snake ↔ Feature / Region
    # ======================
    def link_snake_feature(self, snake_id, feature_id, weight):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO SnakeFeature (snake_id, feature_id, weight)
                VALUES (?, ?, ?)
            """, (snake_id, feature_id, weight))

    def unlink_snake_feature(self, snake_id, feature_id):
        with self.get_connection() as conn:
            conn.execute("""
                DELETE FROM SnakeFeature
                WHERE snake_id = ? AND feature_id = ?
            """, (snake_id, feature_id))

    def link_snake_region(self, snake_id, region_id):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO SnakeRegion (snake_id, region_id)
                VALUES (?, ?)
            """, (snake_id, region_id))

    def unlink_snake_region(self, snake_id, region_id):
        with self.get_connection() as conn:
            conn.execute("""
                DELETE FROM SnakeRegion
                WHERE snake_id = ? AND region_id = ?
            """, (snake_id, region_id))

    # ======================
    # User
    # ======================
    def create_user(self, user: User):
        try:
            with self.get_connection() as conn:
                cur = conn.execute("""
                    INSERT INTO User (username, role, password_hash, created_at)
                    VALUES (?, ?, ?, ?)
                """, (user.username, user.role, user.password_hash, user.created_at))
                return cur.lastrowid
        except sqlite3.IntegrityError:
            return None

    def update_user(self, user: User):
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE User
                SET username = ?, password_hash = ?
                WHERE user_id = ?
            """, (user.username, user.password_hash, user.user_id))

    def get_user_by_username(self, username):
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM User WHERE username = ?", (username,)).fetchone()
        if not row:
            return None
        return User(
            user_id=row["user_id"],
            username=row["username"],
            role=row["role"],
            password_hash=row["password_hash"],
            created_at=row["created_at"]
        )

    # ======================
    # Attempt
    # ======================
    def create_attempt(self, attempt: Attempt):
        with self.get_connection() as conn:
            cur = conn.execute("""
                INSERT INTO Attempt (user_id, snake_id, correct, timestamp)
                VALUES (?, ?, ?, ?)
            """, (attempt.user_id, attempt.snake_id, int(attempt.correct), attempt.timestamp))
            return cur.lastrowid

    def get_attempts_by_user(self, user_id):
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM Attempt
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """, (user_id,)).fetchall()
        return [Attempt(row["attempt_id"], row["user_id"], row["snake_id"], row["correct"], row["timestamp"]) for row in rows]

    # ======================
    # Auth Tokens
    # ======================
    def create_token(self, token, user_id, role, expires_at):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO AuthToken (token, user_id, role, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (token, user_id, role, datetime.now().isoformat(), expires_at))

    def get_token(self, token):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT token, user_id, role, expires_at
                FROM AuthToken
                WHERE token = ?
            """, (token,)).fetchone()

    def delete_token(self, token):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM AuthToken WHERE token = ?", (token,))

    def delete_tokens_for_user(self, user_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM AuthToken WHERE user_id = ?", (user_id,))

    def delete_expired_tokens(self):
        with self.get_connection() as conn:
            conn.execute("""
                DELETE FROM AuthToken
                WHERE expires_at <= ?
            """, (datetime.now().isoformat(),))

    # ======================
    # Snake Images
    # ======================
    def add_snake_image(self, snake_id, image_bytes, is_primary=False):
        """
        Add an image to a snake.
        Saves file to disk as IMAGE_DIR/<image_id>.png
        Returns the image_id.
        """
        os.makedirs(self.IMAGE_DIR, exist_ok=True)

        with self.get_connection() as conn:
            # If it's the first image, force primary
            existing_count = conn.execute(
                "SELECT COUNT(*) as cnt FROM SnakeImage WHERE snake_id = ?",
                (snake_id,)
            ).fetchone()["cnt"]

            if existing_count == 0:
                is_primary = True
            elif is_primary:
                conn.execute(
                    "UPDATE SnakeImage SET is_primary = 0 WHERE snake_id = ?",
                    (snake_id,)
                )

            # Insert DB record (temporary file_path)
            cur = conn.execute("""
                INSERT INTO SnakeImage (snake_id, file_path, is_primary, uploaded_at)
                VALUES (?, ?, ?, ?)
            """, (snake_id, "temp", int(is_primary), datetime.now().isoformat()))
            image_id = cur.lastrowid

            # Save file
            file_path = os.path.join(self.IMAGE_DIR, f"{image_id}.png")
            with open(file_path, "wb") as f:
                f.write(image_bytes)

            # Update DB with correct file_path
            conn.execute(
                "UPDATE SnakeImage SET file_path = ? WHERE image_id = ?",
                (file_path, image_id)
            )

            return image_id

    def get_snake_images(self, snake_id):
        """
        Return all images for a snake as a list of dicts:
        - image_id
        - file_path
        - is_primary
        - image_data (bytes)
        If no images exist, returns default.png.
        """
        default_path = os.path.join(self.IMAGE_DIR, "default.png")
        os.makedirs(self.IMAGE_DIR, exist_ok=True)
        if not os.path.exists(default_path):
            with open(default_path, "wb") as f:
                f.write(b"")

        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT image_id, file_path, is_primary
                FROM SnakeImage
                WHERE snake_id = ?
                ORDER BY is_primary DESC, image_id ASC
            """, (snake_id,)).fetchall()

        images = []
        if not rows:
            with open(default_path, "rb") as f:
                data = f.read()
            images.append({
                "image_id": None,
                "file_path": default_path,
                "is_primary": True,
                "image_data": data
            })
            return images

        for row in rows:
            file_path = row["file_path"]
            if not os.path.exists(file_path):
                file_path = default_path
            with open(file_path, "rb") as f:
                data = f.read()
            images.append({
                "image_id": row["image_id"],
                "file_path": file_path,
                "is_primary": bool(row["is_primary"]),
                "image_data": data
            })

        return images

    def delete_snake_image(self, image_id):
        """
        Delete DB record and image file
        """
        default_path = os.path.join(self.IMAGE_DIR, "default.png")
        with self.get_connection() as conn:
            row = conn.execute("SELECT file_path FROM SnakeImage WHERE image_id = ?", (image_id,)).fetchone()
            if not row:
                return False
            conn.execute("DELETE FROM SnakeImage WHERE image_id = ?", (image_id,))

        file_path = row["file_path"]
        if os.path.exists(file_path) and file_path != default_path:
            os.remove(file_path)
        return True

    def set_primary_snake_image(self, image_id):
        """
        Set a specific image as primary for its snake
        """
        with self.get_connection() as conn:
            row = conn.execute("SELECT snake_id FROM SnakeImage WHERE image_id = ?", (image_id,)).fetchone()
            if not row:
                return False
            snake_id = row["snake_id"]

            # Reset all to non-primary
            conn.execute("UPDATE SnakeImage SET is_primary = 0 WHERE snake_id = ?", (snake_id,))
            conn.execute("UPDATE SnakeImage SET is_primary = 1 WHERE image_id = ?", (image_id,))
            return True
    # ======================
    # Add multiple images to an existing snake
    # ======================
    def add_snake_images(self, snake_id, images: list[bytes]):
        """
        Adds multiple images to an existing snake.
        images: list of bytes
        Returns a list of image_ids.
        """
        image_ids = []
        for img_bytes in images:
            image_id = self.add_snake_image(snake_id, img_bytes)
            image_ids.append(image_id)
        return image_ids

