from pathlib import Path

import yaml


class Config:
    _instance = None
    _config_data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._load_config()
        return cls._instance

    @classmethod
    def _load_config(cls):
        config_path = Path("config/settings.yaml")
        if not config_path.exists():
            raise FileNotFoundError(f"Brak pliku konfiguracji: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            cls._config_data = yaml.safe_load(f)

    @property
    def llm(self):
        return self._config_data.get("llm", {})

    @property
    def db_url(self):
        return self._config_data.get("database", {}).get("url", "sqlite:///data/hotels.db")


config = Config()
