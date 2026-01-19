import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from pathlib import Path  # Pamiętaj o imporcie!


def setup_env():
    """Ładuje zmienne środowiskowe z pliku .env i sprawdza klucze."""

    #ścieżka do pliku .env w głównym folderze
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)

    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GROQ_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        logging.warning(f"Nie wykryto kluczy API w pliku: {env_path}. Upewnij się, że plik istnieje i ma zmienne.")

def setup_logging():
    """Konfiguruje logowanie do pliku i konsoli."""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Nazwa pliku z dzisiejszą datą
    log_filename = f"{log_dir}/agent_{datetime.now().strftime('%Y-%m-%d')}.log"

    # Konfiguracja formatu - file handler (plik) + stream handler (konsola)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    logging.info("System logowania zainicjalizowany.")