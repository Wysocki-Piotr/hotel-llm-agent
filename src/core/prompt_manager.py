from pathlib import Path

import yaml
from langchain_core.prompts import ChatPromptTemplate


class PromptManager:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)

    def load_template(self, prompt_name: str) -> ChatPromptTemplate:
        file_path = self.prompts_dir / f"{prompt_name}.yaml"
        if not file_path.exists():
            raise FileNotFoundError(f"Nie znaleziono promptu: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return ChatPromptTemplate.from_template(data["template"])


prompt_manager = PromptManager()
