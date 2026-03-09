from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlite_path: str = "./data/learner_portfolio.db"
    db_reset_on_startup: bool = False
    falkordb_host: str = "localhost"
    falkordb_port: int = 56379
    falkordb_graph: str = "knowledge_graph"
    openai_api_key: str = ""
    entra_tenant_id: str = ""
    entra_client_id: str = ""

    model_config = {"env_file": ".env"}


settings = Settings()
