import os

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama


# from langchain_openai import ChatOpenAI

def get_llm(llm_config: dict) -> BaseChatModel:
    provider = llm_config.get("provider", "ollama")
    model = llm_config.get("model_name", "llama3.1")
    temp = llm_config.get("temperature", 0.3)
    base_url = llm_config.get("base_url")

    if provider == "ollama":
        return ChatOllama(
            model=model,
            temperature=temp,
            base_url=base_url or "http://localhost:11434"
        )

    elif provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temp,
            google_api_key=api_key
        )

    # elif provider == "openai_compatible":
    #     # Idealne dla vLLM na zdalnej maszynie
    #     return ChatOpenAI(
    #         model=model,
    #         temperature=temp,
    #         openai_api_base=base_url,
    #         api_key="EMPTY"
    #     )

    else:
        raise ValueError(f"Nieznany provider LLM: {provider}")
