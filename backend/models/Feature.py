class Feature:
    def __init__(self, feature_id, name, description):
        self._feature_id = feature_id
        self._name = name
        self._description = description

    # ===== Getters =====
    @property
    def feature_id(self):
        return self._feature_id

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    # ===== Setters =====
    @feature_id.setter
    def feature_id(self, value):
        self._feature_id = value

    @name.setter
    def name(self, value):
        self._name = value

    @description.setter
    def description(self, value):
        self._description = value
