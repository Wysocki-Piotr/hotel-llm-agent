import os

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq


# from langchain_openai import ChatOpenAI

def get_llm(llm_config: dict) -> BaseChatModel:
    provider = llm_config.get("provider", "ollama")
    model = llm_config.get("model_name", "llama3.1")
    temp = llm_config.get("temperature", 0.3)
    base_url = llm_config.get("base_url")

    if provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temp,
            google_api_key=api_key
        )

    elif provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Brak GROQ_API_KEY w pliku .env")
        
        return ChatGroq(
            model_name=model,
            temperature=temp,
            api_key=api_key
        )

    else:
        raise ValueError(f"Nieznany provider LLM: {provider}")
