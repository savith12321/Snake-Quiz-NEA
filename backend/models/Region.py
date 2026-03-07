class Region:
    def __init__(self, region_id, name):
        self._region_id = region_id
        self._name = name

    # ===== Getters =====
    @property
    def region_id(self):
        return self._region_id

    @property
    def name(self):
        return self._name

    # ===== Setters =====
    @region_id.setter
    def region_id(self, value):
        self._region_id = value

    @name.setter
    def name(self, value):
        self._name = value
