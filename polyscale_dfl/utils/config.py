import json
import os

class Config:
    """
    Simple configuration manager
    """
    def __init__(self, path=None):
        self.config = {}
        if path:
            self.load(path)

    def load(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                self.config = json.load(f)
        else:
            raise FileNotFoundError(f"Config file {path} not found")

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.config, f, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
