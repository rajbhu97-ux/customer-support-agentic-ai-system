from pydantic_settings import BaseSettings
from typing import Optional, Literal
from pathlib import Path
from pydantic import model_validator


# Data path 
BASE_DIR: Path = Path(__file__).parent.parent
DATA_DIR: Path =  BASE_DIR / "data/raw"
SCENARIOS_DIR: Path = BASE_DIR / "data/scenarios"
PROMPTS_DIR: Path = BASE_DIR / "config/prompts"

class Settings(BaseSettings):

    # google model name
    LLM_MODEL_NAME: str = "gemini-1.5-flash"
    LLM_PROVIDER: str = "Google"

    # Memory config
    SESSION_TTL_SECONDS: int = 3600
    MAX_HISTORY_TURNS: int = 20

    # Agent config
    MAX_AGENT_STEPS: int = 10
    MAX_TOOL_RETRIES: int = 3
    AGENT_TIMEOUT_SECONDS: int = 60

    # Feature flag
    ENABLE_LONG_TERM_MEMORY: bool = False
    ENABLE_LLM_CACHE: bool = True
    ENABLE_GUARDRAILS: bool = True
    MOCK_LLM: bool = True

    # API parameter
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Observability 
    ENABLE_TRACING: bool = False
    LOG_LEVEL: Literal["INFO", "DEBUG", "WARNING", "ERROR"] = "INFO"
    LANGCHAIN_TRACING_V2: bool = True

    # endpoints
    LANGCHAIN_ENDPOINT: str = 'https://api.smith.langchain.com'
    GOOGLE_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

    # environment variables
    LANGCHAIN_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None


    @model_validator(mode='after')
    def check_api_key(self):
        if not self.GOOGLE_API_KEY and not self.MOCK_LLM:
            raise ValueError("GOOGLE_API_KEY is required when MOCK_LLM is false")
        return self

    class Config:
        env_file = ".env"


settings = Settings()