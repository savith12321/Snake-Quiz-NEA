from datetime import datetime


class User:
    def __init__(self, user_id, username, role, password_hash, created_at=None):
        self._user_id = user_id
        self._username = username
        self.role = role  # use setter
        self._password_hash = password_hash
        self._created_at = created_at or datetime.now().isoformat()

    # ===== Getters & Setters =====

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("user_id must be an integer or None")
        self._user_id = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        if not value:
            raise ValueError("username cannot be empty")
        self._username = value

    # 🔐 ROLE GETTER & SETTER
    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, value):
        if value not in ("user", "admin"):
            raise ValueError("role must be 'user' or 'admin'")
        self._role = value

    @property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, value):
        if not value:
            raise ValueError("password_hash cannot be empty")
        self._password_hash = value

    @property
    def created_at(self):
        return self._created_at

    # ===== Persistence =====
    def save(self, db_manager):
        if self._user_id is None:
            user_id = db_manager.create_user(self)
            if user_id:
                self._user_id = user_id
                return True
            return False
        else:
            db_manager.update_user(self)
            return True

    def __str__(self):
        return f"{self._username} [{self._role}] (created {self._created_at})"
