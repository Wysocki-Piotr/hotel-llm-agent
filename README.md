# Szybka Instrukcja użycia

## 0 środowisko + pobranie zależności

## 1 Jeżeli masz klucz API od groka - utwórz .env i tam wstaw
        GROQ_API_KEY={tu wstaw klucz do api}
Wtedy w: config/settings.yaml:
llm:
  llm:
  provider: "groq"
  model_name: "llama-3.3-70b-versatile"  # To jest ten potężny, szybki model
  temperature: 0.1
  base_url: "http://localhost:11434" # Dla providera 'openai_compatible' (VM) lub Ollama
  num_gpu: 99

database:
  url: "sqlite:///data/hotels.db"

logging:
  level: "INFO"
  file: "logs/agent.log"
## 2 Jeżeli używasz lokalnego modelu llama 3.1:
#### w pliku config/settings.yaml
#### ustaw :
        llm:
            provider: "ollama"
            model_name: "llama3.1"
            temperature: 0.3
            base_url: "http://localhost:11434" # Dla providera 'openai_compatible' (VM) lub Ollama
            num_gpu: 99, #wzięte z nikąd ale działa, coś koło 40 wystarczy
            num_ctx: 4096 #2048 bylo za małe, 8192 wolne

## 3 Żeby odpalić gui wpisz w terminalu w głównym folderze projektu:
        streamlit run app/gui.py

## Trzymam kciuki, u mnie działa
