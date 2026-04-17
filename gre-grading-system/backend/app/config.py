"""Application configuration using pydantic-settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"
    
    # LangSmith
    langchain_tracing_v2: bool = True
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: str = ""
    langchain_project: str = "gre-grading-system"
    
    # Tavily
    tavily_api_key: str = ""
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/gre_grading"
    database_url_sync: str = "postgresql://postgres:password@localhost:5432/gre_grading"
    
    # Application
    debug: bool = False
    log_level: str = "INFO"
    
    # Grading Configuration
    num_graders: int = 3
    grader_temperatures: list[float] = [0.3, 0.5, 0.7]
    weak_area_threshold: float = 4.0
    weak_area_lookback: int = 5


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
