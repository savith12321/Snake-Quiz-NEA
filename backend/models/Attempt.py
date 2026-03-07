class Attempt:
    def __init__(self, attempt_id, user_id, snake_id, correct, timestamp):
        self._attempt_id = attempt_id
        self._user_id = user_id
        self._snake_id = snake_id
        self._correct = bool(correct)
        self._timestamp = timestamp

    # ===== Getters =====
    @property
    def attempt_id(self):
        return self._attempt_id

    @property
    def user_id(self):
        return self._user_id

    @property
    def snake_id(self):
        return self._snake_id

    @property
    def correct(self):
        return self._correct

    @property
    def timestamp(self):
        return self._timestamp

    # ===== Persistence =====
    def save(self, db_manager):
        """
        Saves the attempt to the database.
        Returns True if successful, False otherwise.
        """
        if self._attempt_id is None:
            attempt_id = db_manager.create_attempt(self)
            if attempt_id:
                self._attempt_id = attempt_id
                return True
            return False
        return False  # Attempts should not be updated
