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
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        self.db_name = os.path.join(script_dir, db_name)

        os.makedirs(self.IMAGE_DIR, exist_ok=True)
        self.apply_schema()
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
        os.makedirs(self.IMAGE_DIR, exist_ok=True)

        with self.get_connection() as conn:
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

            cur = conn.execute("""
                INSERT INTO SnakeImage (snake_id, file_path, is_primary, uploaded_at)
                VALUES (?, ?, ?, ?)
            """, (snake_id, "temp", int(is_primary), datetime.now().isoformat()))
            image_id = cur.lastrowid

            file_path = os.path.join(self.IMAGE_DIR, f"{image_id}.png")
            with open(file_path, "wb") as f:
                f.write(image_bytes)

            conn.execute(
                "UPDATE SnakeImage SET file_path = ? WHERE image_id = ?",
                (file_path, image_id)
            )

            return image_id

    def get_snake_images(self, snake_id):
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
        with self.get_connection() as conn:
            row = conn.execute("SELECT snake_id FROM SnakeImage WHERE image_id = ?", (image_id,)).fetchone()
            if not row:
                return False
            snake_id = row["snake_id"]
            conn.execute("UPDATE SnakeImage SET is_primary = 0 WHERE snake_id = ?", (snake_id,))
            conn.execute("UPDATE SnakeImage SET is_primary = 1 WHERE image_id = ?", (image_id,))
            return True

    def add_snake_images(self, snake_id, images: list[bytes]):
        image_ids = []
        for img_bytes in images:
            image_id = self.add_snake_image(snake_id, img_bytes)
            image_ids.append(image_id)
        return image_ids

    # ======================
    # Quiz - Questions
    # ======================
    def get_random_question(self, question_type=None, difficulty=None):
        with self.get_connection() as conn:
            if question_type and difficulty:
                return conn.execute("""
                    SELECT q.*, s.common_name, s.scientific_name, s.venom_level, s.description
                    FROM Question q
                    JOIN Snake s ON q.snake_id = s.snake_id
                    WHERE q.question_type = ? AND q.difficulty = ?
                    ORDER BY RANDOM() LIMIT 1
                """, (question_type, difficulty)).fetchone()
            elif difficulty:
                return conn.execute("""
                    SELECT q.*, s.common_name, s.scientific_name, s.venom_level, s.description
                    FROM Question q
                    JOIN Snake s ON q.snake_id = s.snake_id
                    WHERE q.difficulty = ?
                    ORDER BY RANDOM() LIMIT 1
                """, (difficulty,)).fetchone()
            elif question_type:
                return conn.execute("""
                    SELECT q.*, s.common_name, s.scientific_name, s.venom_level, s.description
                    FROM Question q
                    JOIN Snake s ON q.snake_id = s.snake_id
                    WHERE q.question_type = ?
                    ORDER BY RANDOM() LIMIT 1
                """, (question_type,)).fetchone()
            return conn.execute("""
                SELECT q.*, s.common_name, s.scientific_name, s.venom_level, s.description
                FROM Question q
                JOIN Snake s ON q.snake_id = s.snake_id
                ORDER BY RANDOM() LIMIT 1
            """).fetchone()

    def get_correct_answer(self, question_id):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT * FROM Answer
                WHERE question_id = ? AND is_correct = 1
                LIMIT 1
            """, (question_id,)).fetchone()

    def get_wrong_answers(self, question_type, exclude_snake_id, correct_answer_text):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT a.answer_id, a.answer_text
                FROM Answer a
                JOIN Question q ON a.question_id = q.question_id
                WHERE q.question_type = ?
                AND q.snake_id != ?
                AND a.is_correct = 1
                AND a.answer_text != ?
                ORDER BY RANDOM()
                LIMIT 3
            """, (question_type, exclude_snake_id, correct_answer_text)).fetchall()

    def get_answer(self, answer_id):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT * FROM Answer
                WHERE answer_id = ?
            """, (answer_id,)).fetchone()

    def get_question_by_id(self, question_id):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT * FROM Question WHERE question_id = ?
            """, (question_id,)).fetchone()

    def create_question(self, snake_id, question_type, question_text, correct_answer, difficulty=1):
        with self.get_connection() as conn:
            cur = conn.execute("""
                INSERT INTO Question (snake_id, question_type, question_text, difficulty, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (snake_id, question_type, question_text, difficulty, datetime.now().isoformat()))
            question_id = cur.lastrowid
            conn.execute("""
                INSERT INTO Answer (question_id, answer_text, is_correct)
                VALUES (?, ?, 1)
            """, (question_id, correct_answer))
        return question_id

    def delete_question(self, question_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM Question WHERE question_id = ?", (question_id,))

    def get_all_questions(self):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT q.question_id, q.question_type, q.question_text, q.difficulty, q.created_at,
                    s.common_name, s.snake_id
                FROM Question q
                JOIN Snake s ON q.snake_id = s.snake_id
                ORDER BY q.created_at DESC
            """).fetchall()

    # ======================
    # Quiz - Attempts
    # ======================
    def create_quiz_attempt(self, user_id, snake_id, question_id, answer_id, correct, quiz_id=None):
        with self.get_connection() as conn:
            cur = conn.execute("""
                INSERT INTO Attempt (user_id, snake_id, question_id, answer_id, correct, timestamp, quiz_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, snake_id, question_id, answer_id, int(correct), datetime.now().isoformat(), quiz_id))
            return cur.lastrowid

    def get_quiz_history(self, user_id):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT
                    a.attempt_id, a.correct, a.timestamp,
                    s.common_name, s.snake_id,
                    q.question_type, q.question_text,
                    ans.answer_text AS chosen_answer
                FROM Attempt a
                JOIN Snake s ON a.snake_id = s.snake_id
                LEFT JOIN Question q ON a.question_id = q.question_id
                LEFT JOIN Answer ans ON a.answer_id = ans.answer_id
                WHERE a.user_id = ?
                ORDER BY a.timestamp DESC
            """, (user_id,)).fetchall()

    # ======================
    # Quiz - Sessions
    # ======================
    def create_quiz(self, user_id):
        with self.get_connection() as conn:
            cur = conn.execute("""
                INSERT INTO Quiz (user_id, score, total, started_at)
                VALUES (?, 0, 10, ?)
            """, (user_id, datetime.now().isoformat()))
            return cur.lastrowid

    def finish_quiz(self, quiz_id):
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT COUNT(*) as score FROM Attempt
                WHERE quiz_id = ? AND correct = 1
            """, (quiz_id,)).fetchone()
            score = row["score"]
            conn.execute("""
                UPDATE Quiz
                SET score = ?, completed_at = ?
                WHERE quiz_id = ?
            """, (score, datetime.now().isoformat(), quiz_id))
        return score

    def get_quiz(self, quiz_id):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT * FROM Quiz WHERE quiz_id = ?
            """, (quiz_id,)).fetchone()

    def get_quiz_history_by_user(self, user_id):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT * FROM Quiz
                WHERE user_id = ?
                ORDER BY started_at DESC
            """, (user_id,)).fetchall()

    def get_attempts_for_quiz(self, quiz_id):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT
                    a.attempt_id, a.correct, a.timestamp,
                    s.common_name, s.snake_id,
                    q.question_type, q.question_text,
                    ans.answer_text AS chosen_answer
                FROM Attempt a
                JOIN Snake s ON a.snake_id = s.snake_id
                LEFT JOIN Question q ON a.question_id = q.question_id
                LEFT JOIN Answer ans ON a.answer_id = ans.answer_id
                WHERE a.quiz_id = ?
                ORDER BY a.timestamp ASC
            """, (quiz_id,)).fetchall()

    def get_attempt_by_id(self, attempt_id):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT * FROM Attempt WHERE attempt_id = ?
            """, (attempt_id,)).fetchone()

    def delete_attempt(self, attempt_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM Quiz WHERE attempt_id = ?", (attempt_id,))
            conn.commit()
            print("Deleted attempt", attempt_id)