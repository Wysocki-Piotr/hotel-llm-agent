# Szybka Instrukcja użycia

## 0 środowisko + pobranie zależności

## 1 Utwórz plik .env z  zawartością: (jeżeli model lokalny to w ogole nie jest potrzebny)
        GOOGLE_API_KEY={tu wstaw klucz do api}
## 2 Jeżeli nie używasz lokalnego modelu llama 3.1:
#### w pliku config/settings.yaml
#### zamień :
        llm:
            provider: "ollama"
            model_name: "llama3.1"
            temperature: 0.3
            base_url: "http://localhost:11434" # Dla providera 'openai_compatible' (VM) lub Ollama
            num_gpu: 99, #wzięte z nikąd ale działa, coś koło 40 wystarczy
            num_ctx: 4096 #2048 bylo za małe, 8192 wolne
#### na model jakiego chcesz uzywać
## 3 Żeby odpalić gui wpisz w terminalu w głównym folderze projektu:
        streamlit run app/gui.py

## Trzymam kciuki, u mnie działa
