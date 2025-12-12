class ModelVersioning:
    """
    Track different versions of the global model
    """
    def __init__(self):
        self.versions = []

    def save_version(self, round_number, state_dict):
        self.versions.append({"round": round_number, "weights": state_dict.copy()})

    def get_version(self, round_number):
        for v in self.versions:
            if v["round"] == round_number:
                return v["weights"]
        return None
