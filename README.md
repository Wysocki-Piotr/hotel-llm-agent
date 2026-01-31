# Quick Start Guide

Follow these steps to set up the environment, configure the LLM provider, and launch the application.

## 0. Environment & Dependencies
Ensure you are in the project's root directory. Set up your virtual environment and install the required dependencies:

```bash
# Install dependencies
pip install -r requirements.txt
```

## 1. Create the .env file
Create a file named .env in the root directory and add your API key (generate from GROQ):
GROQ_API_KEY=your_actual_api_key_here

## 2. Choose model and configure config/settings.yaml
llm:
  provider: "groq"
  model_name: "llama-3.3-70b-versatile"  # Powerful and fast model
  temperature: 0.1
  base_url: "http://localhost:11434"     # Kept for compatibility (Ollama/VM)
  num_gpu: 99

database:
  url: "sqlite:///data/hotels.db"

logging:
  level: "INFO"
  file: "logs/agent.log"

### 3. Launch an app
```bash
streamlit run app/gui.py
```


