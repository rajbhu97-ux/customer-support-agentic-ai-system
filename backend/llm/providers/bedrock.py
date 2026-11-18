
from .base import BaseLLMProvider
from config.settings import settings
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.caches.in_memory import InMemoryCache
from langchain_core.globals import set_llm_cache
from langchain_aws import ChatBedrock

LLM_PROVIDER = "bedrock"

class BedRockProvider(BaseLLMProvider):

    def __init__(self):
        self._llm_cache: dict[float, BaseChatModel] = {}
        if settings.ENABLE_LLM_CACHE:
            set_llm_cache(InMemoryCache())
        self.validate_config()

    @property
    def provider_name(self) -> str:
        return LLM_PROVIDER

    def validate_config(self) -> None:
        if not settings.AWS_REGION:
            raise ValueError("AWS_REGION is required for Bedrock provider")
    
    def get_llm(self, temperature: float= 0.0) -> BaseChatModel:

        if temperature in self._llm_cache:
            return self._llm_cache[temperature]

        model = ChatBedrock(
            model_id=settings.BEDROCK_MODEL_ID,
            region_name=settings.AWS_REGION,
            model_kwargs={
                "temperature":temperature,
                "max_token": 2048
            },
            credentials_profile_name=
                settings.AWS_PROFILE_NAME
        )
        self._llm_cache[temperature] = model
        return model


    