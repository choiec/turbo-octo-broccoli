from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlite_path: str = "./learner_portfolio.db"
    kuzu_path: str = "./knowledge_graph"
    openai_api_key: str = ""
    entra_tenant_id: str = ""
    entra_client_id: str = ""

    model_config = {"env_file": ".env"}


settings = Settings()
