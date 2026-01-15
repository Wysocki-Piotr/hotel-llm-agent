import os
import logging
from datetime import datetime
from dotenv import load_dotenv


def setup_env():
    """Ładuje zmienne środowiskowe z pliku .env i sprawdza klucze."""
    load_dotenv()

    # Opcjonalna walidacja - ostrzeż, jeśli brak kluczy, a nie używamy tylko Ollamy
    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        logging.warning("Nie wykryto kluczy API (GOOGLE/OPENAI) w pliku .env. Upewnij się, że to zamierzone.")


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