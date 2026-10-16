
from .base import BaseLLMProvider
from config.settings import settings
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.caches.in_memory import InMemoryCache
from langchain_core.globals import set_llm_cache

LLM_PROVIDER = "google"

class GoogleProvider(BaseLLMProvider):

    def __init__(self):
        self._llm_cache: dict[float, BaseChatModel] = {}
        if settings.ENABLE_LLM_CACHE:
            set_llm_cache(InMemoryCache())
        self.validate_config()

    @property
    def provider_name(self) -> str:
        return LLM_PROVIDER

    def validate_config(self) -> None:
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required for Google provider")
    
    def get_llm(self, temperature: float= 0.0) -> BaseChatModel:

        if temperature in self._llm_cache:
            return self._llm_cache[temperature]

        model = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL_NAME,
            temperature=temperature,
            google_api_key=settings.GOOGLE_API_KEY
        )
        self._llm_cache[temperature] = model
        return model


    