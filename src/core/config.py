from pathlib import Path
import yaml
import os



class Config:
    _instance = None
    _config_data = None
    _project_root = None  # Dodajemy zmienną na root projektu

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._load_config()
        return cls._instance

    @classmethod
    def _load_config(cls):

        current_file = Path(__file__)  # src/core/config.py
        cls._project_root = current_file.parent.parent.parent  # hotel-llm-agent/

        config_path = cls._project_root / "config" / "settings.yaml"

        if not config_path.exists():
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
        url = self._config_data.get("database", {}).get("url", "sqlite:///data/hotels.db")

        if url.startswith("sqlite:///data/"):
            db_path = self._project_root / "data" / "hotels.db"
            return f"sqlite:///{db_path}"

        return url


config = Config()