import yaml
from pathlib import Path

class Config:
    def __init__(self, path="config/config.yml"):
        self._data = self._load_config(path)

    def _load_config(self, path):
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found here: {config_path}, maybe you need to rename the config.example.yml to config.yml?")
        with config_path.open() as f:
            return yaml.safe_load(f)

    def __getattr__(self, name):
        # Allow attribute-style access: config.api_token
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"Config has no attribute '{name}'. Check again the config.example.yml to have an idea on how to structure it.")

config = Config()