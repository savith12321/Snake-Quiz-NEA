class Snake:
    def __init__(self, snake_id, common_name, scientific_name, venom_level, description):
        self._snake_id = snake_id
        self._common_name = common_name
        self._scientific_name = scientific_name
        self._venom_level = venom_level
        self._description = description

    # ===== Getters and Setters =====
    @property
    def snake_id(self):
        return self._snake_id

    @snake_id.setter
    def snake_id(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("snake_id must be an integer or None")
        self._snake_id = value

    @property
    def common_name(self):
        return self._common_name

    @common_name.setter
    def common_name(self, value):
        if not value:
            raise ValueError("common_name cannot be empty")
        self._common_name = value

    @property
    def scientific_name(self):
        return self._scientific_name

    @scientific_name.setter
    def scientific_name(self, value):
        if not value:
            raise ValueError("scientific_name cannot be empty")
        self._scientific_name = value

    @property
    def venom_level(self):
        return self._venom_level

    @venom_level.setter
    def venom_level(self, value):
        allowed = ['non-venomous', 'mild', 'high']
        if value not in allowed:
            raise ValueError(f"venom_level must be one of {allowed}")
        self._venom_level = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    def save(self, db):
        """
        Full sync with database
        """
        if self._snake_id is None:
            self._snake_id = db.add_snake(self)
        else:
            db.update_snake(self)

    def is_venomous(self):
        return self._venom_level != "non-venomous"

    def __str__(self):
        return f"{self._common_name} ({self._scientific_name}) - {self._venom_level}"
