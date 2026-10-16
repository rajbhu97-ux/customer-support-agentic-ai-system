from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel
from typing import Type, Any

class BaseLLMProvider(ABC):

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def validate_config(self) -> None:
        pass

    @abstractmethod
    def get_llm(self, temperature: float = 0.0) -> BaseChatModel:
        pass

    def get_structured_llm(self, structure: Type[Any], temperature: float = 0.0):
        return self.get_llm(temperature).with_structured_output(structure)
