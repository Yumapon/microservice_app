import yaml

class Config:
    def __init__(self, file_path="config.yaml"):
        with open(file_path, "r") as f:
            self._data = yaml.safe_load(f)

    @property
    def keycloak(self):
        return self._data["keycloak"]

    @property
    def session(self):
        return self._data["session"]
